from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import bigquery
import pickle
import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

SUCURSALES = {
    0: "E-Commerce", 1: "Arica", 2: "Iquique", 3: "Antofagasta", 4: "Copiapó",
    5: "La Serena", 6: "Valparaíso", 7: "Viña del Mar", 8: "Santiago Centro",
    9: "Providencia", 10: "Las Condes", 11: "Rancagua", 12: "Talca", 13: "Curicó",
    14: "Chillán", 15: "Concepción", 16: "Los Ángeles", 17: "Temuco", 18: "Valdivia",
    19: "Osorno", 20: "Puerto Montt", 21: "Castro", 22: "Coyhaique", 23: "Punta Arenas",
    24: "Calama", 25: "San Antonio", 26: "Quilpué", 27: "San Bernardo", 28: "Maipú",
    29: "La Florida", 30: "Puerto Varas",
}

MODEL_PATH = Path(__file__).parent.parent / "notebooks" / "model_ventas.pkl"
model = None
if MODEL_PATH.exists():
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)

app = FastAPI(title="BigData API - Grupo Cordillera")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client: bigquery.Client | None = None

PROJECT_DATASET = "cordillerabi.grupo_cordillera_dw"


@app.on_event("startup")
async def startup():
    global client
    client = bigquery.Client()


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/api/batch/kpis")
async def batch_kpis():
    query = f"""
        SELECT
            COUNT(*) AS total_tx,
            SUM(monto_clp) AS total_revenue,
            ROUND(AVG(monto_clp), 2) AS avg_ticket
        FROM {PROJECT_DATASET}.fact_ventas
    """
    df = client.query(query).to_dataframe()
    return df.iloc[0].to_dict()


@app.get("/api/streaming/kpis")
async def streaming_kpis():
    query = f"""
        SELECT
            COUNT(DISTINCT session_id) AS total_sessions,
            COUNTIF(event_type = 'view_product') AS view_count,
            COUNTIF(event_type = 'add_to_cart') AS cart_count,
            COUNTIF(event_type = 'purchase') AS purchase_count
        FROM {PROJECT_DATASET}.fact_sesiones_web_streaming
    """
    df = client.query(query).to_dataframe()
    return df.iloc[0].to_dict()


@app.get("/api/streaming/devices")
async def streaming_devices():
    query = f"""
        SELECT device, COUNT(*) as count
        FROM {PROJECT_DATASET}.fact_sesiones_web_streaming
        GROUP BY device ORDER BY count DESC
    """
    df = client.query(query).to_dataframe()
    return df.to_dict(orient="records")


@app.get("/api/payment/methods")
async def payment_methods():
    query = f"""
        SELECT metodo_pago, COUNT(*) as count
        FROM {PROJECT_DATASET}.fact_ventas
        GROUP BY metodo_pago ORDER BY count DESC
    """
    df = client.query(query).to_dataframe()
    return df.to_dict(orient="records")


@app.get("/api/aforo/current")
async def aforo_current():
    query = f"""
        SELECT *
        FROM {PROJECT_DATASET}.fact_aforo_streaming
        QUALIFY ROW_NUMBER() OVER (PARTITION BY id_sucursal ORDER BY timestamp DESC) = 1
    """
    df = client.query(query).to_dataframe()
    return df.to_dict(orient="records")


@app.get("/api/aforo/history")
async def aforo_history(
    id_sucursal: str = Query(...),
    limit: int = Query(50, ge=1, le=1000),
):
    query = f"""
        SELECT *
        FROM {PROJECT_DATASET}.fact_aforo_streaming
        WHERE id_sucursal = @id_sucursal
        ORDER BY timestamp DESC
        LIMIT @limit
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("id_sucursal", "STRING", id_sucursal),
            bigquery.ScalarQueryParameter("limit", "INT64", limit),
        ]
    )
    df = client.query(query, job_config=job_config).to_dataframe()
    return df.to_dict(orient="records")


@app.get("/api/sales/monthly")
async def sales_monthly():
    query = f"""
        SELECT
            SUBSTR(CAST(fecha AS STRING), 1, 7) AS month,
            SUM(monto_clp) AS total
        FROM {PROJECT_DATASET}.fact_ventas
        GROUP BY month
        ORDER BY month
    """
    df = client.query(query).to_dataframe()
    return df.to_dict(orient="records")


@app.get("/api/sales/sucursal")
async def sales_sucursal():
    query = f"""
        SELECT
            id_sucursal,
            SUM(monto_clp) AS total
        FROM {PROJECT_DATASET}.fact_ventas
        GROUP BY id_sucursal
        ORDER BY id_sucursal
    """
    df = client.query(query).to_dataframe()
    df['nombre_sucursal'] = df['id_sucursal'].map(SUCURSALES).fillna("Desconocida")
    return df.to_dict(orient="records")


@app.get("/api/sales/recent")
async def sales_recent(limit: int = Query(8, ge=1, le=100)):
    query = f"""
        SELECT *
        FROM {PROJECT_DATASET}.fact_ventas
        ORDER BY fecha DESC
        LIMIT @limit
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("limit", "INT64", limit),
        ]
    )
    df = client.query(query, job_config=job_config).to_dataframe()
    return df.to_dict(orient="records")


@app.get("/api/ml/predict")
async def ml_predict():
    if model is None:
        return {"error": "Modelo no entrenado. Ejecutá el notebook LightGBM primero."}
    try:
        query = f"""
            SELECT id_sucursal, DATE_TRUNC(fecha, MONTH) as mes,
                   SUM(monto_clp) as ventas, COUNT(*) as num_tx, AVG(monto_clp) as ticket_promedio
            FROM {PROJECT_DATASET}.fact_ventas
            GROUP BY 1, 2 ORDER BY 1, 2
        """
        df = client.query(query).to_dataframe()
        df['mes'] = pd.to_datetime(df['mes'])
        feats = pd.DataFrame()
        feats['id_sucursal'] = df['id_sucursal'].astype('category')
        feats['month_sin'] = np.sin(2 * np.pi * df['mes'].dt.month / 12)
        feats['month_cos'] = np.cos(2 * np.pi * df['mes'].dt.month / 12)
        feats['quarter'] = df['mes'].dt.quarter
        feats['year'] = df['mes'].dt.year
        feats['trend'] = (df['mes'].dt.year - 2016) * 12 + df['mes'].dt.month
        feats['num_tx'] = df['num_tx']
        feats['ticket_promedio'] = df['ticket_promedio'].fillna(0)
        for lag in [1, 2, 3, 12]:
            feats[f'lag_{lag}'] = df.groupby('id_sucursal')['ventas'].shift(lag)
        feats['rolling_3'] = df.groupby('id_sucursal')['ventas'].transform(lambda x: x.rolling(3, min_periods=1).mean())
        feats = feats.dropna()
        preds = model.predict(feats)
        result = feats[['id_sucursal']].copy()
        result['prediccion'] = preds
        result = result.groupby('id_sucursal', observed=False)['prediccion'].last().reset_index()
        result['prediccion'] = result['prediccion'].round(0).astype(int)
        actuals = df.groupby('id_sucursal')['ventas'].last().reset_index()
        actuals.columns = ['id_sucursal', 'real_ultimo_mes']
        final = result.merge(actuals, on='id_sucursal', how='left')
        final['real_ultimo_mes'] = final['real_ultimo_mes'].fillna(0).astype(int)
        final['nombre_sucursal'] = final['id_sucursal'].map(SUCURSALES).fillna("Desconocida")
        return final.to_dict(orient="records")
    except Exception as e:
        return {"error": str(e)}
