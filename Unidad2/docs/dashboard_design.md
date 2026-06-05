# Diseño y Especificación de Dashboard en Looker Studio

Este documento detalla la estructura, métricas y configuración de los gráficos del Dashboard de control ejecutivo para **Grupo Cordillera**, conectándose directamente a las tablas refinadas del Data Warehouse en **BigQuery** (`grupo_cordillera_dw`).

## Justificación de Tecnologías (Las 5Vs)
La selección de **BigQuery** como motor del Data Warehouse se justifica bajo los pilares de **Volumen** (capacidad para almacenar y consultar de forma instantánea el historial acumulado de 10 años de transacciones sin degradación del rendimiento) y **Velocidad** (tiempos de respuesta sub-segundo en agregaciones analíticas complejas). La herramienta de visualización **Looker Studio** permite materializar el **Valor** del negocio mediante dashboards ejecutivos interactivos que exponen KPI operacionales y comerciales de forma inmediata.

---

## 1. Configuración General del Dashboard

*   **Herramienta:** Looker Studio (anteriormente Google Data Studio).
*   **URL del Dashboard:** [https://datastudio.google.com/s/rdobu0geO2M](https://datastudio.google.com/s/rdobu0geO2M)
*   **Fuentes de Datos (Data Sources):**
    1.  `grupo_cordillera_dw.fact_ventas` (Conector BigQuery nativo).
    2.  `grupo_cordillera_dw.fact_sesiones_web` (Conector BigQuery nativo).
*   **Controles de Filtro (Cabecera):**
    *   **Control de Periodo:** Filtro de rango de fechas para análisis histórico flexible.
    *   **Filtro por Sucursal:** Menú desplegable para seleccionar una o varias sucursales (`id_sucursal`).
    *   **Filtro por Dispositivo:** Menú desplegable para segmentar por tipo de dispositivo (`device` de sesiones web).

---

## 2. Especificación de los 4 Gráficos Requeridos

### Gráfico 1: Evolución Temporal de Ingresos (Capa Batch)
*   **Tipo de Gráfico:** Gráfico de Líneas (Time Series Chart).
*   **Origen de Datos:** `grupo_cordillera_dw.fact_ventas`
*   **Dimensión Temporal:** `fecha` (agrupada por Día o Mes).
*   **Métrica:** Suma de `monto_clp` (etiquetado como *Total de Ingresos*).
*   **Objetivo de Negocio:** Permite a la CFO y al CEO identificar tendencias de ventas a lo largo de los años, estacionalidad (ej: CyberDays, Navidad) y crecimiento histórico.

### Gráfico 2: Desempeño Comercial por Sucursal Física
*   **Tipo de Gráfico:** Gráfico de Barras Horizontales (Bar Chart).
*   **Origen de Datos:** `grupo_cordillera_dw.fact_ventas`
*   **Dimensión:** `id_sucursal` (Sucursales 1 a 30).
*   **Métrica:** Suma de `monto_clp` (ordenado de mayor a menor).
*   **Objetivo de Negocio:** Comparar visualmente el rendimiento de las sucursales físicas para identificar locales líderes y aquellos que requieren intervenciones o promociones locales.

### Gráfico 3: Participación Omnicanal (Físico vs. Digital)
*   **Tipo de Gráfico:** Gráfico de Anillo (Donut Chart).
*   **Origen de Datos:** `grupo_cordillera_dw.fact_ventas` (con campo calculado).
*   **Dimensión (Campo Calculado - `Canal de Venta`):**
    *   *Fórmula:* `CASE WHEN id_sucursal <= 5 THEN "E-Commerce" ELSE "Tienda Física" END`
    *   *(Nota: En datos sintéticos el generador no asignó `id_sucursal = 0` para ventas web. Se ajustó la fórmula para simular la distribución omnicanal. En producción se usaría un flag de canal real del sistema transaccional).*
*   **Métrica:** Recuento de transacciones (`id_transaccion`) o suma de `monto_clp`.
*   **Objetivo de Negocio:** Medir la tasa de penetración del e-commerce frente a las compras tradicionales en sucursal física.

### Gráfico 4: Embudo de Conversión Web y Proyección Predictiva (Capa Speed + BigQuery ML)
*   **Tipo de Gráfico:** Gráfico de Barras Apiladas / Embudo (Funnel Chart).
*   **Origen de Datos:** Combinación de `fact_sesiones_web` y consultas predictivas de BigQuery ML.
*   **Dimensión (Campo Calculado - `Etapa del Cliente`):**
    *   *Fórmula:* `CASE WHEN event_type = "view_product" THEN "1. Visita Producto" WHEN event_type = "add_to_cart" THEN "2. Añade al Carrito" WHEN event_type = "purchase" THEN "3. Compra" END`
    *   Etapas resultantes:
        1.  *1. Visita Producto* (equivalente a `view_product`)
        2.  *2. Añade al Carrito* (equivalente a `add_to_cart`)
        3.  *3. Compra* (equivalente a `purchase`)
*   **Métrica:** Cantidad de sesiones únicas (`session_id`).
*   **Línea de Proyección Predictiva:** Línea punteada que muestra la tasa de conversión esperada basada en el comportamiento del último trimestre (calculada mediante modelos de clasificación en BigQuery ML).
*   **Integración con MLOps (Vertex AI):** Para operacionalizar este modelo analítico, el pipeline se integra con la capa operativa de **Vertex AI (MLOps)**:
    1.  *Vertex AI Pipelines* orquesta los flujos de reentrenamiento continuo del modelo de conversión a partir de los datos en BigQuery.
    2.  *Vertex AI Model Registry* gestiona el versionado y aprobación de los modelos de clasificación entrenados.
    3.  El *Feature Store* de Vertex AI centraliza y sirve los atributos agregados en tiempo real.
    4.  *Vertex AI Prediction* sirve las **predicciones online** (en la Capa Speed para ofertas en tiempo real) y **predicciones batch** (en la Capa Batch para el cálculo de conversión histórico semanal).
*   **Objetivo de Negocio:** Visualizar la fuga de clientes en el embudo web en tiempo real y anticipar el volumen de conversión semanal para la planificación del stock en los centros de distribución.

---

## 3. Tarjetas de Resumen Rápido (Scorecards)

Para dar un contexto ejecutivo inmediato, se colocarán tres tarjetas de métricas clave en la parte superior:
1.  **Monto Facturado a la Fecha:** Suma acumulada de `monto_clp` (Métrica: SUM). Muestra el ingreso total global del grupo ($1.838.769.817.641 CLP).
2.  **Total Transacciones:** Recuento de `id_transaccion` (Métrica: CTD). Muestra la cantidad total de compras completadas (1.200.000 registros).

---

## 4. Gobierno de Datos, Privacidad y Archivado (Cumplimiento Ley N° 21.719)

Para cumplir con la legislación chilena y optimizar costos de almacenamiento en el Data Warehouse de BigQuery, se definen las siguientes políticas:
*   **Privacidad por Diseño (Ley N° 21.719):** Las fuentes de datos alimentadas a Looker Studio (`fact_ventas` y `fact_sesiones_web`) solo contienen datos previamente seudonimizados en la capa de transformación (IDs de clientes cifrados con hash SHA-256 no reversibles e IP con anonimización de subred). No hay exposición de RUTs o nombres de clientes en ninguna parte del modelo semántico de visualización.
*   **Política de Archivado a Bajo Costo:** Para minimizar costos de retención prolongada en BigQuery, se aplica una política de ciclo de vida del dato:
    1.  Las tablas calientes de BigQuery retienen datos operativos de los últimos 2 años de forma activa.
    2.  Las transacciones históricas de más de 2 años se exportan automáticamente a un bucket de **Cloud Storage** en formato comprimido (Parquet) y se eliminan de BigQuery.
    3.  A nivel de Cloud Storage, una política de ciclo de vida de objetos (Object Lifecycle Management) migra estos históricos a la clase **Coldline** a los 90 días, y a la clase **Archive** al cumplir 365 días, donde se conservan bajo retención de bajo costo durante el plazo legal requerido.
