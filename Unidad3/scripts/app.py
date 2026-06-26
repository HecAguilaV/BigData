import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from google.cloud import bigquery
import time

# 1. Page Configuration
st.set_page_config(
    page_title="Grupo Cordillera Analytics",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. Theme Toggle Session State
if "theme" not in st.session_state:
    st.session_state.theme = st.query_params.get("theme", "light")

def toggle_theme():
    new_theme = "light" if st.session_state.theme == "dark" else "dark"
    st.session_state.theme = new_theme
    st.query_params["theme"] = new_theme
    st.query_params["manual"] = "true"

IS_DARK = st.session_state.theme == "dark"

# 3. CSS Design System Injection
theme_variables = f"""
:root {{
    --bg: {"#09090b" if IS_DARK else "#ffffff"};
    --bg-subtle: {"#0c0c0f" if IS_DARK else "#f9fafb"};
    --card: {"#0c0c0f" if IS_DARK else "#ffffff"};
    --card-hover: {"#131316" if IS_DARK else "#f4f4f5"};
    --border: {"#1e1e24" if IS_DARK else "#e4e4e7"};
    --border-subtle: {"#16161a" if IS_DARK else "#f0f0f2"};
    --text: {"#fafafa" if IS_DARK else "#09090b"};
    --text-muted: #71717a;
    --text-dim: {"#52525b" if IS_DARK else "#a1a1aa"};
    --accent: #2563eb;
    --accent-muted: #1d4ed8;
    --green: {"#22c55e" if IS_DARK else "#16a34a"};
    --green-muted: {"rgba(34,197,94,0.12)" if IS_DARK else "rgba(22,163,74,0.08)"};
    --red: {"#ef4444" if IS_DARK else "#dc2626"};
    --red-muted: {"rgba(239,68,68,0.12)" if IS_DARK else "rgba(220,38,38,0.08)"};
    --amber: {"#f59e0b" if IS_DARK else "#d97706"};
    --amber-muted: {"rgba(245,158,11,0.12)" if IS_DARK else "rgba(217,119,6,0.08)"};
    --shadow: {"none" if IS_DARK else "0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.03)"};
    --radius: 10px;
}}
"""

st.markdown(f"""
<style>
    {theme_variables}
    
    /* Hide default streamlit headers/footers */
    header[data-testid="stHeader"], #MainMenu, footer, [data-testid="stToolbar"],
    [data-testid="stDecoration"], [data-testid="stStatusWidget"], .stDeployButton,
    div[data-testid="stSidebarCollapsedControl"] {{
        display: none !important;
    }}
    
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .main, .block-container, section[data-testid="stMain"] {{
        background-color: var(--bg) !important;
        color: var(--text) !important;
        font-family: 'DM Sans', -apple-system, sans-serif !important;
    }}
    
    .block-container {{
        padding: 1.5rem 2.5rem 3rem !important;
        max-width: 1380px !important;
        margin: 0 auto;
    }}
    
    /* Custom columns gaps */
    [data-testid="stHorizontalBlock"] {{
        gap: 1.25rem !important;
    }}
    [data-testid="stVerticalBlock"] > div:has(> [data-testid="stHorizontalBlock"]) {{
        margin-bottom: 0.5rem !important;
    }}
    
    /* Brand Header */
    .brand-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid var(--border);
    }}
    .brand-title {{
        font-size: 1.4rem;
        font-weight: 700;
        letter-spacing: -0.03em;
        color: var(--text);
    }}
    .brand-subtitle {{
        font-size: 0.8rem;
        color: var(--text-muted);
    }}
    
    /* Metric Cards */
    .metric-card {{
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1.1rem 1.3rem;
        box-shadow: var(--shadow);
        transition: transform 0.2s, border-color 0.2s;
    }}
    .metric-card:hover {{
        transform: translateY(-2px);
        border-color: var(--text-dim);
    }}
    .metric-label {{
        font-size: 0.75rem;
        color: var(--text-muted);
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.3rem;
    }}
    .metric-value {{
        font-size: 1.65rem;
        font-weight: 700;
        color: var(--text);
        letter-spacing: -0.03em;
    }}
    .metric-delta {{
        font-size: 0.72rem;
        font-weight: 500;
        margin-top: 0.3rem;
        padding: 2px 8px;
        border-radius: 6px;
        display: inline-flex;
        align-items: center;
        gap: 3px;
    }}
    .delta-up {{ color: var(--green); background: var(--green-muted); }}
    .delta-down {{ color: var(--red); background: var(--red-muted); }}
    
    /* Chart Container Wrappers */
    .chart-wrap {{
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1.2rem;
        box-shadow: var(--shadow);
        margin-bottom: 1.25rem;
    }}
    .chart-title {{
        font-size: 0.85rem;
        font-weight: 600;
        color: var(--text);
        margin-bottom: 0.2rem;
    }}
    .chart-subtitle {{
        font-size: 0.72rem;
        color: var(--text-dim);
        margin-bottom: 0.8rem;
    }}
    
    /* Custom Tabs */
    button[data-baseweb="tab"] {{
        background: transparent !important;
        color: var(--text-muted) !important;
        font-size: 0.835rem !important;
        font-weight: 500 !important;
        padding: 0.55rem 1.2rem !important;
        border: 1px solid transparent !important;
        border-radius: 7px !important;
        transition: all 0.2s;
    }}
    button[data-baseweb="tab"]:hover {{
        color: var(--text) !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: var(--text) !important;
        background: var(--card) !important;
        border-color: var(--border) !important;
    }}
    [data-baseweb="tab-highlight"], [data-baseweb="tab-border"] {{
        display: none !important;
    }}
    [data-baseweb="tab-list"] {{
        gap: 6px !important;
        background: var(--bg-subtle) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        padding: 4px;
        margin-bottom: 1.5rem;
    }}
    
    /* Theme Toggle Button */
    div.stButton > button {{
        background: var(--card) !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        font-size: 0.78rem !important;
        font-weight: 500 !important;
        padding: 0.35rem 0.8rem !important;
        box-shadow: var(--shadow) !important;
        transition: all 0.2s !important;
    }}
    div.stButton > button:hover {{
        border-color: var(--text-dim) !important;
        background: var(--card-hover) !important;
    }}
</style>
""", unsafe_allow_html=True)

# 4. BigQuery Client & Cache Helpers
@st.cache_data
def fetch_sales_kpis(where_clause: str):
    client = bigquery.Client(project="cordillerabi")
    query = f"""
    SELECT 
        COUNT(*) as total_tx,
        COALESCE(SUM(monto_clp), 0) as total_revenue,
        COALESCE(AVG(monto_clp), 0) as avg_ticket,
        COALESCE(SUM(cantidad), 0) as total_qty
    FROM `cordillerabi.grupo_cordillera_dw.fact_ventas`
    {where_clause}
    """
    df = client.query(query).to_dataframe()
    if not df.empty:
        return df.iloc[0].to_dict()
    return {"total_tx": 0, "total_revenue": 0, "avg_ticket": 0, "total_qty": 0}

@st.cache_data
def fetch_sales_monthly(where_clause: str):
    client = bigquery.Client(project="cordillerabi")
    query = f"""
    SELECT 
        DATE(DATE_TRUNC(fecha, MONTH)) as fecha, 
        COALESCE(SUM(monto_clp), 0) as monto_clp
    FROM `cordillerabi.grupo_cordillera_dw.fact_ventas`
    {where_clause}
    GROUP BY 1
    ORDER BY 1
    """
    return client.query(query).to_dataframe()

@st.cache_data
def fetch_sales_sucursal(where_clause: str):
    client = bigquery.Client(project="cordillerabi")
    query = f"""
    SELECT 
        id_sucursal, 
        COALESCE(SUM(monto_clp), 0) as monto_clp
    FROM `cordillerabi.grupo_cordillera_dw.fact_ventas`
    {where_clause}
    GROUP BY 1
    ORDER BY 2 DESC
    """
    return client.query(query).to_dataframe()

@st.cache_data
def fetch_sales_pago(where_clause: str):
    client = bigquery.Client(project="cordillerabi")
    query = f"""
    SELECT 
        metodo_pago, 
        COUNT(*) as count
    FROM `cordillerabi.grupo_cordillera_dw.fact_ventas`
    {where_clause}
    GROUP BY 1
    ORDER BY 2 DESC
    """
    return client.query(query).to_dataframe()

@st.cache_data
def fetch_sales_recent(where_clause: str, limit: int = 8):
    client = bigquery.Client(project="cordillerabi")
    query = f"""
    SELECT 
        id_transaccion, 
        fecha, 
        id_sucursal, 
        monto_clp, 
        metodo_pago
    FROM `cordillerabi.grupo_cordillera_dw.fact_ventas`
    {where_clause}
    ORDER BY fecha DESC
    LIMIT {limit}
    """
    return client.query(query).to_dataframe()

@st.cache_data(ttl=2)
def fetch_streaming_kpis():
    client = bigquery.Client(project="cordillerabi")
    query = """
    SELECT 
        COUNT(*) as total_sessions,
        COUNTIF(event_type = 'view_product') as view_count,
        COUNTIF(event_type = 'add_to_cart') as cart_count,
        COUNTIF(event_type = 'purchase') as purchase_count
    FROM `cordillerabi.grupo_cordillera_dw.fact_sesiones_web_streaming`
    """
    df = client.query(query).to_dataframe()
    if not df.empty:
        return df.iloc[0].to_dict()
    return {"total_sessions": 0, "view_count": 0, "cart_count": 0, "purchase_count": 0}

@st.cache_data(ttl=2)
def fetch_streaming_devices():
    client = bigquery.Client(project="cordillerabi")
    query = """
    SELECT 
        device, 
        COUNT(*) as count
    FROM `cordillerabi.grupo_cordillera_dw.fact_sesiones_web_streaming`
    GROUP BY 1
    ORDER BY 2 DESC
    """
    return client.query(query).to_dataframe()

@st.cache_data(ttl=2)
def fetch_streaming_recent(limit: int = 10):
    client = bigquery.Client(project="cordillerabi")
    query = f"""
    SELECT 
        session_id, 
        timestamp, 
        ip_anonima, 
        id_anonimo_cliente, 
        event_type, 
        sku_product, 
        device
    FROM `cordillerabi.grupo_cordillera_dw.fact_sesiones_web_streaming`
    ORDER BY timestamp DESC
    LIMIT {limit}
    """
    return client.query(query).to_dataframe()

@st.cache_data(ttl=5)
def fetch_aforo_current():
    client = bigquery.Client(project="cordillerabi")
    query = """
    SELECT *
    FROM (
        SELECT *, ROW_NUMBER() OVER (PARTITION BY id_sucursal ORDER BY timestamp DESC) as rn
        FROM `cordillerabi.grupo_cordillera_dw.fact_aforo_streaming`
    )
    WHERE rn = 1
    ORDER BY id_sucursal
    """
    return client.query(query).to_dataframe()

@st.cache_data(ttl=5)
def fetch_aforo_recent(limit: int = 50):
    client = bigquery.Client(project="cordillerabi")
    query = f"""
    SELECT timestamp, id_sucursal, nombre_sucursal, aforo_actual, capacidad_maxima,
           porcentaje_ocupacion, personas_entran, personas_salen
    FROM `cordillerabi.grupo_cordillera_dw.fact_aforo_streaming`
    ORDER BY timestamp DESC
    LIMIT {limit}
    """
    return client.query(query).to_dataframe()

# 5. Plotly Default Layout Theme Config
PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans, sans-serif", color="#09090b" if not IS_DARK else "#fafafa", size=10),
    margin=dict(l=10, r=10, t=30, b=10),
    xaxis=dict(
        gridcolor="rgba(0,0,0,0.04)" if not IS_DARK else "rgba(255,255,255,0.03)",
        zerolinecolor="rgba(0,0,0,0.04)" if not IS_DARK else "rgba(255,255,255,0.03)",
        tickfont=dict(size=9, color="#71717a" if not IS_DARK else "#a1a1aa"),
    ),
    yaxis=dict(
        gridcolor="rgba(0,0,0,0.04)" if not IS_DARK else "rgba(255,255,255,0.03)",
        zerolinecolor="rgba(0,0,0,0.04)" if not IS_DARK else "rgba(255,255,255,0.03)",
        tickfont=dict(size=9, color="#71717a" if not IS_DARK else "#a1a1aa"),
    ),
    legend=dict(
        font=dict(size=11, color="#09090b" if not IS_DARK else "#fafafa")
    )
)

# 6. Sidebar (Configuration & Controls)
st.sidebar.markdown(f"### ◆ Filtros y Controles")

# Channel Filter
channel_filter = st.sidebar.multiselect(
    "Canal de Venta",
    options=["Todos", "E-Commerce", "Tienda Física"],
    default=["Todos"]
)

# Payment Method Filter
payment_filter = st.sidebar.multiselect(
    "Método de Pago",
    options=["Todos", "Webpay", "Efectivo", "Tarjeta Débito", "Tarjeta Crédito"],
    default=["Todos"]
)

auto_refresh = st.sidebar.checkbox("Live Streaming (30s)", value=True)
st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    **Capa Speed & Batch**  
    Grupo Cordillera  
    *Duoc UC 2026*
    """
)

# Build SQL WHERE clause dynamically
def build_where_clause(channels, payments):
    conditions = []
    
    # Process Channel
    if channels and "Todos" not in channels:
        sub_conds = []
        if "E-Commerce" in channels:
            sub_conds.append("id_sucursal = 0")
        if "Tienda Física" in channels:
            sub_conds.append("id_sucursal > 0")
        if sub_conds:
            conditions.append(f"({' OR '.join(sub_conds)})")
            
    # Process Payment
    if payments and "Todos" not in payments:
        pago_map = {
            "Tarjeta Débito": "tarjeta_debito",
            "Tarjeta Crédito": "tarjeta_credito",
            "Efectivo": "efectivo",
            "Webpay": "transferencia"
        }
        mapped_pagos = [pago_map[p] for p in payments if p in pago_map]
        if mapped_pagos:
            pago_list = ", ".join([f"'{p}'" for p in mapped_pagos])
            conditions.append(f"metodo_pago IN ({pago_list})")
        
    if conditions:
        return "WHERE " + " AND ".join(conditions)
    return ""

where_clause = build_where_clause(channel_filter, payment_filter)
where_clause_pago = build_where_clause(channel_filter, ["Todos"])

# 7. Brand Header Layout
head_left, head_right = st.columns([8, 2])
with head_left:
    st.markdown("""
    <div class="brand-header">
        <div>
            <div class="brand-title">Grupo Cordillera — Analítica Omnicanal</div>
            <div class="brand-subtitle">Consolidado Lambda (Capa Batch histórica & Capa Speed real-time)</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
with head_right:
    theme_btn_label = "☀️ Modo Claro" if IS_DARK else "🌙 Modo Oscuro"
    st.button(theme_btn_label, on_click=toggle_theme, width='stretch')

# 8. Fetch Batch Data
try:
    kpis = fetch_sales_kpis(where_clause)
    df_monthly = fetch_sales_monthly(where_clause)
    df_suc = fetch_sales_sucursal(where_clause)
    df_pago = fetch_sales_pago(where_clause_pago)
    df_recent_sales = fetch_sales_recent(where_clause, limit=8)
    
    # Convert dates to datetime
    if not df_monthly.empty:
        df_monthly['fecha'] = pd.to_datetime(df_monthly['fecha'])
    if not df_recent_sales.empty:
        df_recent_sales['fecha'] = pd.to_datetime(df_recent_sales['fecha'])
        
    # Fetch streaming data
    streaming_kpis = fetch_streaming_kpis()
    df_devices = fetch_streaming_devices()
    df_recent_sessions = fetch_streaming_recent(limit=10)
    if not df_recent_sessions.empty:
        df_recent_sessions['timestamp'] = pd.to_datetime(df_recent_sessions['timestamp'])
        
    # Fetch aforo IoT data
    df_aforo = fetch_aforo_current()
    df_aforo_log = fetch_aforo_recent(limit=50)
    if not df_aforo_log.empty:
        df_aforo_log['timestamp'] = pd.to_datetime(df_aforo_log['timestamp'])
        
except Exception as e:
    st.sidebar.error(f"Error conectando a BigQuery: {e}")
    st.sidebar.info("Asegurate de estar autenticado en la terminal usando `gcloud auth application-default login`")
    st.stop()

# 9. Main Navigation Tabs
tab_sales, tab_streaming, tab_aforo, tab_ml = st.tabs(["📊 Capa Batch: Ventas Transaccionales", "⚡ Capa Speed: Monitoreo Streaming", "📡 Capa IoT: Aforo en Vivo", "🤖 ML: Pronóstico Ventas"])

# ==================== TAB 1: BATCH SALES ====================
with tab_sales:
    # Compute KPIs
    total_tx = kpis.get("total_tx", 0)
    total_revenue = kpis.get("total_revenue", 0)
    avg_ticket = kpis.get("avg_ticket", 0)
    
    # Calculate E-Commerce share (Sucursal 0) dynamically
    ecom_rev = df_suc[df_suc['id_sucursal'] == 0]['monto_clp'].sum() if not df_suc.empty else 0
    ecom_share = (ecom_rev / total_revenue * 100) if total_revenue > 0 else 0
    
    # KPI Cards Row
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Transacciones Totales</div>
            <div class="metric-value">{total_tx:,.0f}</div>
            <div class="metric-delta delta-up">↑ 100% histórico</div>
        </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Monto Facturado (CLP)</div>
            <div class="metric-value">${total_revenue:,.0f}</div>
            <div class="metric-delta delta-up">↑ Omnicanal</div>
        </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Ticket Promedio</div>
            <div class="metric-value">${avg_ticket:,.0f}</div>
            <div class="metric-delta delta-up">↑ Valor medio</div>
        </div>
        """, unsafe_allow_html=True)
    with k4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Participación E-Commerce</div>
            <div class="metric-value">{ecom_share:.1f}%</div>
            <div class="metric-delta delta-up" style="color: var(--green); background: var(--green-muted);">⚡ Canal Digital</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    
    # Graphs Row 1 (Temporal + Sucursal)
    g1, g2 = st.columns(2)
    
    with g1:
        st.markdown("""
        <div class="chart-wrap">
            <div class="chart-title">Evolución de Ingresos Mensuales</div>
            <div class="chart-subtitle">Facturación agrupada por mes en la serie histórica</div>
        """, unsafe_allow_html=True)
        
        if not df_monthly.empty:
            fig_line = px.line(df_monthly, x='fecha', y='monto_clp', color_discrete_sequence=['#2563eb'])
            fig_line.update_traces(mode="lines+markers", line=dict(width=3), marker=dict(size=6))
            fig_line.update_layout(PLOT_LAYOUT)
            st.plotly_chart(fig_line, width='stretch', config={"displayModeBar": False})
        else:
            st.info("No hay datos disponibles para el filtro seleccionado.")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with g2:
        st.markdown("""
        <div class="chart-wrap">
            <div class="chart-title">Desempeño Comercial por Sucursal</div>
            <div class="chart-subtitle">Ingresos acumulados (Destacando canal E-Commerce en verde)</div>
        """, unsafe_allow_html=True)
        
        if not df_suc.empty:
            # Sort bottom-up for horizontal bars
            df_suc_sorted = df_suc.sort_values(by='monto_clp', ascending=True)
            df_suc_sorted['sucursal_label'] = df_suc_sorted['id_sucursal'].apply(lambda x: "E-Commerce" if x == 0 else f"Sucursal {x}")
            df_suc_sorted['tipo_canal'] = df_suc_sorted['id_sucursal'].apply(lambda x: "E-Commerce" if x == 0 else "Tienda Física")
            
            color_map = {"E-Commerce": "#10b981", "Tienda Física": "#2563eb"}
            fig_bar = px.bar(
                df_suc_sorted.tail(10), 
                x='monto_clp', 
                y='sucursal_label', 
                orientation='h',
                color='tipo_canal',
                color_discrete_map=color_map,
                category_orders={"sucursal_label": df_suc_sorted['sucursal_label'].tolist()}
            )
            fig_bar.update_layout(
                PLOT_LAYOUT,
                showlegend=True,
                legend=dict(
                    title="",
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            fig_bar.update_traces(
                text=df_suc_sorted.tail(10)['monto_clp'].apply(lambda x: f"${x:,.0f}"),
                textposition="inside",
                textfont=dict(size=9, color="#ffffff"),
            )
            st.plotly_chart(fig_bar, width='stretch', config={"displayModeBar": False})
        else:
            st.info("No hay datos disponibles para el filtro seleccionado.")
        st.markdown("</div>", unsafe_allow_html=True)
        
    # Graphs Row 2 (Payment method + Recent Table)
    g3, g4 = st.columns(2)
    
    with g3:
        st.markdown("""
        <div class="chart-wrap">
            <div class="chart-title">Participación de Métodos de Pago</div>
            <div class="chart-subtitle">Proporción de transacciones según canal de pago preferido</div>
        """, unsafe_allow_html=True)
        
        if not df_pago.empty:
            fig_pie = px.pie(df_pago, values='count', names='metodo_pago', hole=0.4,
                             color_discrete_sequence=['#2563eb', '#0891b2', '#059669', '#7c3aed'])
            fig_pie.update_layout(PLOT_LAYOUT)
            st.plotly_chart(fig_pie, width='stretch', config={"displayModeBar": False})
        else:
            st.info("No hay datos disponibles.")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with g4:
        st.markdown("""
        <div class="chart-wrap">
            <div class="chart-title">Últimas Transacciones Procesadas</div>
            <div class="chart-subtitle">Registros recientes limpios cargados al Data Warehouse</div>
        """, unsafe_allow_html=True)
        
        if not df_recent_sales.empty:
            display_df = df_recent_sales.copy()
            display_df['canal'] = display_df['id_sucursal'].apply(
                lambda x: "E-Commerce" if x == 0 else f"Tienda {x}"
            )
            display_df['metodo_pago'] = display_df['metodo_pago'].str.replace("_", " ").str.upper()
            st.dataframe(
                display_df[['id_transaccion', 'fecha', 'canal', 'monto_clp', 'metodo_pago']],
                column_config={
                    "id_transaccion": st.column_config.TextColumn("ID Transacción"),
                    "fecha": st.column_config.DatetimeColumn("Fecha", format="YYYY-MM-DD HH:mm"),
                    "canal": st.column_config.TextColumn("Canal"),
                    "monto_clp": st.column_config.NumberColumn("Monto (CLP)", format="$%,.0f"),
                    "metodo_pago": st.column_config.TextColumn("Pago"),
                },
                hide_index=True,
                width='stretch',
                height=382,
            )
        else:
            st.info("No hay transacciones recientes para este filtro.")
        
        st.markdown("</div>", unsafe_allow_html=True)

# ==================== TAB 2: STREAMING / SPEED ====================
with tab_streaming:
    total_sessions = streaming_kpis.get("total_sessions", 0)
    view_count = streaming_kpis.get("view_count", 0)
    cart_count = streaming_kpis.get("cart_count", 0)
    purchase_count = streaming_kpis.get("purchase_count", 0)

    st.markdown("""
    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 1rem; margin-top: -0.5rem;">
        <span style="width: 10px; height: 10px; background-color: #2563eb; border-radius: 50%; display: inline-block; animation: pulse 1.5s infinite;"></span>
        <span style="font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #2563eb;">Streaming en Vivo</span>
    </div>
    <style>
        @keyframes pulse {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(37, 99, 235, 0.7); }
            70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(37, 99, 235, 0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(37, 99, 235, 0); }
        }
    </style>
    """, unsafe_allow_html=True)

    sk1, sk2, sk3, sk4 = st.columns(4)
    with sk1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Sesiones Web Totales</div>
            <div class="metric-value">{total_sessions:,.0f}</div>
            <div class="metric-delta delta-up">⚡ Live Stream</div>
        </div>
        """, unsafe_allow_html=True)
    with sk2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Visualizaciones Producto</div>
            <div class="metric-value">{view_count:,.0f}</div>
            <div class="metric-delta delta-up">⚡ View events</div>
        </div>
        """, unsafe_allow_html=True)
    with sk3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Añadidos al Carrito</div>
            <div class="metric-value">{cart_count:,.0f}</div>
            <div class="metric-delta delta-up">⚡ Cart events</div>
        </div>
        """, unsafe_allow_html=True)
    with sk4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Conversiones (Compras)</div>
            <div class="metric-value">{purchase_count:,.0f}</div>
            <div class="metric-delta delta-up">⚡ Purchase events</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    s_g1, s_g2 = st.columns(2)

    with s_g1:
        st.markdown("""
        <div class="chart-wrap">
            <div class="chart-title">Embudo de Conversión Web Real-Time</div>
            <div class="chart-subtitle">Tasa de conversión de sesiones unificadas (Batch + Live Streaming)</div>
        """, unsafe_allow_html=True)
        funnel_data = dict(
            number=[view_count, cart_count, purchase_count],
            stage=["1. Visitas Productos", "2. Carrito de Compras", "3. Transacciones Completadas"]
        )
        fig_funnel = go.Figure(go.Funnel(
            y=funnel_data["stage"],
            x=funnel_data["number"],
            textinfo="value+percent initial",
            marker=dict(color=["#2563eb", "#3b82f6", "#10b981"]),
            textfont=dict(family="DM Sans, sans-serif", size=10, color="#ffffff"),
            connector=dict(fillcolor="rgba(255,255,255,0.03)" if IS_DARK else "rgba(0,0,0,0.03)")
        ))
        fig_funnel.update_layout(PLOT_LAYOUT)
        st.plotly_chart(fig_funnel, width='stretch', config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    with s_g2:
        st.markdown("""
        <div class="chart-wrap">
            <div class="chart-title">Dispositivos Utilizados</div>
            <div class="chart-subtitle">Distribución porcentual de accesos al e-commerce</div>
        """, unsafe_allow_html=True)
        if not df_devices.empty:
            fig_dev_pie = px.pie(df_devices, values='count', names='device', hole=0.4,
                                 color_discrete_sequence=['#2563eb', '#059669', '#d97706'])
            fig_dev_pie.update_layout(PLOT_LAYOUT)
            st.plotly_chart(fig_dev_pie, width='stretch', config={"displayModeBar": False})
        else:
            st.info("No hay datos disponibles.")
        st.markdown("</div>", unsafe_allow_html=True)

    # Full Width Live Log Table
    st.markdown("""
    <div class="chart-wrap">
        <div class="chart-title">Auditoría de Ingesta en Línea (Pub/Sub logs)</div>
        <div class="chart-subtitle">Monitoreo de telemetría web con normalización, seudonimización y anonimización de IP en vivo</div>
    """, unsafe_allow_html=True)
    if not df_recent_sessions.empty:
        st.dataframe(
            df_recent_sessions[['session_id', 'timestamp', 'ip_anonima', 'id_anonimo_cliente', 'event_type', 'sku_product', 'device']],
            column_config={
                "session_id": st.column_config.TextColumn("ID Sesión"),
                "timestamp": st.column_config.DatetimeColumn("Timestamp", format="YYYY-MM-DD HH:mm:ss"),
                "ip_anonima": st.column_config.TextColumn("IP Enmascarada"),
                "id_anonimo_cliente": st.column_config.TextColumn("Cliente Seudonimizado"),
                "event_type": st.column_config.TextColumn("Evento"),
                "sku_product": st.column_config.TextColumn("SKU Producto"),
                "device": st.column_config.TextColumn("Dispositivo"),
            },
            hide_index=True,
            width='stretch',
            height=400,
        )
    else:
        st.info("Esperando eventos en tiempo real...")
    st.markdown("</div>", unsafe_allow_html=True)

# ==================== TAB 3: IOT AFORO ====================
with tab_aforo:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 1rem;">
        <span style="width: 10px; height: 10px; background-color: #10b981; border-radius: 50%; display: inline-block; animation: pulse 1.5s infinite;"></span>
        <span style="font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #10b981;">Sensores IoT — Aforo en Tiempo Real</span>
    </div>
    """, unsafe_allow_html=True)
    
    if not df_aforo.empty and not df_aforo_log.empty:
        total_aforo = int(df_aforo['aforo_actual'].sum())
        total_capacidad = int(df_aforo['capacidad_maxima'].sum())
        avg_ocupacion = df_aforo['porcentaje_ocupacion'].mean()
        
        a1, a2, a3, a4 = st.columns(4)
        with a1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Ocupación Total</div>
                <div class="metric-value">{total_aforo:,} / {total_capacidad:,}</div>
                <div class="metric-delta delta-up">📡 Sensores IoT</div>
            </div>
            """, unsafe_allow_html=True)
        with a2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Promedio Ocupación</div>
                <div class="metric-value">{avg_ocupacion:.1f}%</div>
                <div class="metric-delta delta-up">⚡ Live</div>
            </div>
            """, unsafe_allow_html=True)
        with a3:
            sucursales_sobre = len(df_aforo[df_aforo['porcentaje_ocupacion'] >= 80])
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Sucursales sobre 80%</div>
                <div class="metric-value">{sucursales_sobre}</div>
                <div class="metric-delta delta-up">🔴 Alta demanda</div>
            </div>
            """, unsafe_allow_html=True)
        with a4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Última Lectura</div>
                <div class="metric-value">{df_aforo_log['timestamp'].iloc[0].strftime('%H:%M:%S')}</div>
                <div class="metric-delta delta-up">⏱️ Actualizado</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
        
        ag1, ag2 = st.columns(2)
        
        with ag1:
            st.markdown("""
            <div class="chart-wrap">
                <div class="chart-title">Ocupación por Sucursal</div>
                <div class="chart-subtitle">Porcentaje de aforo actual vs capacidad máxima</div>
            """, unsafe_allow_html=True)
            df_aforo_bar = df_aforo.sort_values('porcentaje_ocupacion', ascending=True)
            fig_aforo = px.bar(
                df_aforo_bar,
                x='porcentaje_ocupacion',
                y='nombre_sucursal',
                orientation='h',
                color='porcentaje_ocupacion',
                color_continuous_scale=['#10b981', '#f59e0b', '#ef4444'],
                range_color=[0, 100],
                text=df_aforo_bar['porcentaje_ocupacion'].apply(lambda x: f'{x:.0f}%'),
            )
            fig_aforo.update_traces(textposition='inside', textfont=dict(size=9, color='white'))
            fig_aforo.update_layout(
                PLOT_LAYOUT,
                xaxis=dict(title="", range=[0, 105]),
                yaxis=dict(title=""),
                coloraxis_showscale=False,
            )
            st.plotly_chart(fig_aforo, width='stretch', config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)
        
        with ag2:
            st.markdown("""
            <div class="chart-wrap">
                <div class="chart-title">Flujo de Personas</div>
                <div class="chart-subtitle">Entradas y salidas por sucursal (última lectura)</div>
            """, unsafe_allow_html=True)
            df_flow = df_aforo.copy()
            fig_flow = go.Figure()
            fig_flow.add_trace(go.Bar(
                name="Entran",
                y=df_flow['nombre_sucursal'],
                x=df_flow['personas_entran'],
                orientation='h',
                marker_color='#10b981',
            ))
            fig_flow.add_trace(go.Bar(
                name="Salen",
                y=df_flow['nombre_sucursal'],
                x=df_flow['personas_salen'],
                orientation='h',
                marker_color='#ef4444',
            ))
            fig_flow.update_layout(
                PLOT_LAYOUT,
                barmode='group',
                xaxis=dict(title=""),
                yaxis=dict(title=""),
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            )
            st.plotly_chart(fig_flow, width='stretch', config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="chart-wrap">
            <div class="chart-title">Historial de Lecturas</div>
            <div class="chart-subtitle">Últimos 50 eventos de sensores IoT</div>
        """, unsafe_allow_html=True)
        st.dataframe(
            df_aforo_log[['timestamp', 'id_sucursal', 'nombre_sucursal', 'aforo_actual', 'capacidad_maxima', 'porcentaje_ocupacion']],
            column_config={
                "timestamp": st.column_config.DatetimeColumn("Timestamp", format="YYYY-MM-DD HH:mm:ss"),
                "id_sucursal": st.column_config.NumberColumn("ID Sucursal"),
                "nombre_sucursal": st.column_config.TextColumn("Sucursal"),
                "aforo_actual": st.column_config.NumberColumn("Aforo Actual"),
                "capacidad_maxima": st.column_config.NumberColumn("Capacidad Máx"),
                "porcentaje_ocupacion": st.column_config.NumberColumn("Ocupación %", format="%.1f%%"),
            },
            hide_index=True,
            width='stretch',
            height=350,
        )
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No hay datos de sensores IoT aún. Inicie el pipeline de aforo con `python Unidad3/aforo/aforo_producer.py`")

# ==================== TAB 4: ML FORECAST ====================
with tab_ml:
    try:
        import requests
        resp = requests.get("http://localhost:8000/api/ml/predict", timeout=10)
        if resp.status_code == 200:
            ml_data = resp.json()
            if isinstance(ml_data, list) and len(ml_data) > 0 and "error" not in ml_data[0]:
                st.markdown("""
                <div class="chart-wrap">
                    <div class="chart-title">🤖 Pronóstico de Ventas LightGBM</div>
                    <div class="chart-subtitle">Predicción del próximo mes por sucursal vs. último mes real</div>
                """, unsafe_allow_html=True)
                for row in ml_data:
                    diff = row["prediccion"] - row["real_ultimo_mes"]
                    pct = f"{(diff / row['real_ultimo_mes'] * 100):.1f}%" if row["real_ultimo_mes"] > 0 else "—"
                    delta_class = "delta-up" if diff > 0 else "delta-down"
                    icon = "🛒" if row["id_sucursal"] == 0 else "🏪"
                    st.markdown(f"""
                    <div class="metric-card" style="margin-bottom: 0.5rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-weight: 600; font-size: 0.85rem;">{icon} {row.get('nombre_sucursal', f'Sucursal {row["id_sucursal"]}')}</span>
                            <span class="metric-delta {delta_class}">{'↑' if diff > 0 else '↓'} {pct}</span>
                        </div>
                        <div style="display: flex; gap: 2rem; margin-top: 0.4rem; font-size: 0.8rem;">
                            <span style="color: var(--text-muted);">Predicción: <strong style="color: var(--text);">${row['prediccion']:,.0f}</strong></span>
                            <span style="color: var(--text-muted);">Real último mes: <strong style="color: var(--text);">${row['real_ultimo_mes']:,.0f}</strong></span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("El endpoint ML no tiene predicciones disponibles.")
        else:
            st.info("FastAPI no está corriendo. Ejecute `uvicorn Unidad3.api.main:app --reload --port 8000`")
    except Exception as e:
        st.info(f"No se pudo conectar al endpoint ML. Asegúrese de que FastAPI esté corriendo en el puerto 8000.")

# 10. Auto-refresh execution trigger
if auto_refresh:
    countdown = st.empty()
    for remaining in range(60, 0, -1):
        countdown.markdown(
            f'<div style="text-align: center; font-size: 0.72rem; '
            f'color: var(--text-dim); padding: 1rem 0 0.25rem; '
            f'border-top: 1px solid var(--border-subtle); margin-top: 1rem;">'
            f'🔄 Próxima actualización en {remaining}s</div>',
            unsafe_allow_html=True
        )
        time.sleep(1)
    st.rerun()
