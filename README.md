# Procesamiento de Datos en Tiempo Real (Streaming) — Grupo Cordillera

Arquitectura Lambda completa para Grupo Cordillera — **Evaluación Parcial N° 3** de **Big Data (AVY1101)** en Duoc UC. Pipeline batch + streaming web + IoT aforo + ML forecasting con dashboards en Streamlit y React.

---

## Stack Tecnológico

| Componente | Tecnología |
| :--------- | :--------- |
| **Cloud** | GCP — BigQuery, Pub/Sub, Cloud Storage |
| **Streaming Web** | Python (producer/consumer) + Pub/Sub |
| **IoT Aforo** | Python (producer/consumer) + Pub/Sub + 30 sucursales geolocalizadas en 4 zonas |
| **ML** | LightGBM — Forecasting ventas por sucursal (lag_1, estacionalidad, tendencia) |
| **Dashboard 1** | Streamlit (Python) — 4 tabs (Batch, Speed, IoT, ML) |
| **Dashboard 2** | React + Vite + TypeScript + Tailwind + Recharts + Leaflet |
| **Backend API** | FastAPI — 9 endpoints (batch, streaming, aforo, ML predict) |
| **Orquestación** | run_simulation.py + start_streamlit.sh + start_react.sh |

## Arquitectura

```
Orígenes → Pub/Sub → Consumers (micro-batching) → BigQuery → FastAPI → Dashboards
                                                              → LightGBM → model.pkl → FastAPI → React
```

- **Capa Batch**: `fact_ventas` (1.2M registros, 2016-2026, 31 sucursales)
- **Capa Speed**: `fact_sesiones_web_streaming` (eventos web en vivo)
- **Capa IoT**: `fact_aforo_streaming` (sensores de aforo, 30 sucursales, 4 zonas)
- **ML**: `model_ventas.pkl` servido vía `/api/ml/predict`, entrenado con LightGBM

## Estructura del Repositorio

```
Unidad1/              — Propuesta y caso semestral
Unidad2/              — Capa Batch (scripts, SQL, ETL)
Unidad3/
  ├── scripts/
  │   ├── app.py                 — Dashboard Streamlit (4 tabs)
  │   ├── streaming_producer.py   — Publica eventos web a Pub/Sub
  │   ├── streaming_consumer.py   — Consume y escribe a BigQuery
  │   └── run_simulation.py       — Orquestador de 4 procesos
  ├── aforo/
  │   ├── aforo_producer.py       — Sensor IoT de ocupación (30 sucursales, 4 zonas)
  │   └── aforo_consumer.py       — Consume aforo y escribe a BigQuery
  ├── api/
  │   └── main.py                 — FastAPI backend (9 endpoints, carga modelo ML)
  ├── frontend/                   — React + Vite dashboard (5 tabs, mapa Leaflet)
  ├── notebooks/
  │   ├── lightgbm_forecast_ventas.ipynb — ML forecasting + serving local
  │   └── model_ventas.pkl        — Modelo entrenado (se carga automáticamente)
  └── Evaluacion3/
      └── Informe_Tecnico_Ev3.md  — Informe técnico completo
data/                 — Datos sintéticos (CSV, JSON, logs)
start_streamlit.sh    — Script: Streamlit + web streaming
start_react.sh        — Script: React + FastAPI + aforo + web + ML
```

## Cómo Ejecutar

### Streamlit (Batch + Speed + IoT + ML)
```bash
./start_streamlit.sh
# http://localhost:8501
```

### React (completo: web + IoT + ML + FastAPI)
```bash
./start_react.sh
# Backend: http://localhost:8000
# Frontend: http://localhost:5173
```

### Notebook ML (solo si se necesita reentrenar)
```bash
source .venv/bin/activate
pip install lightgbm matplotlib scikit-learn pandas-gbq
jupyter notebook Unidad3/notebooks/lightgbm_forecast_ventas.ipynb
```

## Datos

- **1.2M** transacciones de ventas sintéticas (2016-2026)
- **300K** sesiones web simuladas
- **30** sucursales físicas geolocalizadas en 4 zonas (Norte, Centro, Sur, Austral)
- **Streaming**: eventos web + sensores IoT en vivo con Pub/Sub
- **ML**: 31 predicciones únicas por sucursal servidas vía API REST

## Integrantes

Héctor Águila V. — Big Data (AVY1101) - Duoc UC
