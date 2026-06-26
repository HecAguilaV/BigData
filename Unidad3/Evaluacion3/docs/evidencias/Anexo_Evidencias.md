# Anexo Técnico: Evidencias de Implementación — Grupo Cordillera (Ev3)

Este anexo documenta los comandos, configuraciones y validaciones utilizados durante la implementación de la Capa Speed, IoT Aforo y ML Forecasting. Sirve como respaldo técnico del informe principal.

---

## 1. Configuración del Entorno GCP

### 1.1 Autenticación y Proyecto

```bash
gcloud auth login
gcloud config set project cordillerabi
gcloud auth application-default login
```

### 1.2 Creación de Infraestructura Pub/Sub

```bash
# Tópico y suscripción para streaming web
gcloud pubsub topics create streaming-topic
gcloud pubsub subscriptions create streaming-subscription --topic=streaming-topic

# Tópico y suscripción para IoT Aforo
gcloud pubsub topics create aforo-topic
gcloud pubsub subscriptions create aforo-subscription --topic=aforo-topic
```

### 1.3 Validación

```bash
gcloud pubsub topics list
gcloud pubsub subscriptions list
```

---

## 2. Preparación de BigQuery (DDL)

### 2.1 Tablas del Data Warehouse

```sql
-- Respaldar tabla histórica de sesiones
CREATE OR REPLACE TABLE `cordillerabi.grupo_cordillera_dw.fact_sesiones_web_batch` AS 
SELECT * FROM `cordillerabi.grupo_cordillera_dw.fact_sesiones_web`;

-- Tabla para ingesta streaming web
CREATE TABLE IF NOT EXISTS `cordillerabi.grupo_cordillera_dw.fact_sesiones_web_streaming`
(
  session_id STRING,
  timestamp TIMESTAMP,
  ip_anonima STRING,
  id_anonimo_cliente STRING,
  event_type STRING,
  sku_product STRING,
  device STRING
);

-- Tabla para sensores IoT Aforo (con zona y región)
CREATE TABLE IF NOT EXISTS `cordillerabi.grupo_cordillera_dw.fact_aforo_streaming`
(
  timestamp TIMESTAMP,
  id_sucursal INTEGER,
  nombre_sucursal STRING,
  zona STRING,
  region STRING,
  lat FLOAT,
  lng FLOAT,
  capacidad_maxima INTEGER,
  aforo_actual INTEGER,
  personas_entran INTEGER,
  personas_salen INTEGER,
  porcentaje_ocupacion FLOAT
)
PARTITION BY DATE(timestamp)
CLUSTER BY id_sucursal;
```

### 2.2 Vista SQL Unificada (Deduplicación)

```sql
CREATE OR REPLACE VIEW `cordillerabi.grupo_cordillera_dw.fact_sesiones_web` AS
WITH union_data AS (
  SELECT session_id, timestamp, ip_anonima, id_anonimo_cliente, event_type, sku_product, device, 'BATCH' as origen
  FROM `cordillerabi.grupo_cordillera_dw.fact_sesiones_web_batch`
  UNION ALL
  SELECT session_id, timestamp, ip_anonima, id_anonimo_cliente, event_type, sku_product, device, 'STREAMING' as origen
  FROM `cordillerabi.grupo_cordillera_dw.fact_sesiones_web_streaming`
)
SELECT * EXCEPT(row_num, origen)
FROM (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY session_id ORDER BY CASE WHEN origen = 'BATCH' THEN 1 ELSE 2 END, timestamp DESC) as row_num
  FROM union_data
)
WHERE row_num = 1;
```

---

## 3. Ejecución del Pipeline Streaming

### 3.1 Productor Web (eventos desde JSON a Pub/Sub)

```bash
python Unidad3/scripts/streaming_producer.py \
  --project_id cordillerabi \
  --topic_id streaming-topic \
  --file data/sesiones_web.json \
  --delay 1.0
```

### 3.2 Consumidor Web (Pub/Sub a BigQuery con micro-batching)

```bash
python Unidad3/scripts/streaming_consumer.py \
  --project_id cordillerabi \
  --subscription_id streaming-subscription \
  --output_table grupo_cordillera_dw.fact_sesiones_web_streaming \
  --batch_size 15 --batch_interval 5
```

### 3.3 Productor IoT Aforo (sensores simulados)

```bash
python Unidad3/aforo/aforo_producer.py \
  --project_id cordillerabi \
  --topic_id aforo-topic \
  --delay 5
```

### 3.4 Consumidor IoT Aforo

```bash
python Unidad3/aforo/aforo_consumer.py \
  --project_id cordillerabi \
  --subscription_id aforo-subscription \
  --output_table cordillerabi.grupo_cordillera_dw.fact_aforo_streaming \
  --batch_size 20 --batch_interval 10
```

### 3.5 Orquestador Completo (4 procesos)

```bash
python Unidad3/scripts/run_simulation.py
```

---

## 4. Consultas de Validación en BigQuery

### 4.1 Monitorear ingesta streaming web

```sql
SELECT COUNT(*) as registros,
       MIN(timestamp) as primer_evento,
       MAX(timestamp) as ultimo_evento
FROM `cordillerabi.grupo_cordillera_dw.fact_sesiones_web_streaming`;
```

### 4.2 Monitorear ingesta IoT Aforo

```sql
SELECT id_sucursal, nombre_sucursal, zona, aforo_actual, porcentaje_ocupacion
FROM `cordillerabi.grupo_cordillera_dw.fact_aforo_streaming`
QUALIFY ROW_NUMBER() OVER (PARTITION BY id_sucursal ORDER BY timestamp DESC) = 1
ORDER BY id_sucursal;
```

### 4.3 Validar deduplicación de vista unificada

```sql
SELECT COUNT(*) as total_sesiones_sin_duplicados
FROM `cordillerabi.grupo_cordillera_dw.fact_sesiones_web`;
```

### 4.4 Verificar predicciones ML

```bash
curl -s http://localhost:8000/api/ml/predict | python3 -m json.tool
```

---

## 5. Arranque Rápido (Scripts Shell)

```bash
# Streamlit (web streaming + dashboard)
./start_streamlit.sh

# React completo (web + IoT + FastAPI + frontend)
./start_react.sh
```

---

## 6. Estructura de Sucursales

| ID | Ciudad | Zona | Región |
| :-- | :----- | :--- | :----- |
| 0 | E-Commerce | — | — |
| 1 | Arica | Norte | XV - Arica y Parinacota |
| 2 | Iquique | Norte | I - Tarapacá |
| 3 | Antofagasta | Norte | II - Antofagasta |
| 4 | Copiapó | Norte | III - Atacama |
| 5 | La Serena | Norte | IV - Coquimbo |
| 6 | Valparaíso | Centro | V - Valparaíso |
| 7 | Viña del Mar | Centro | V - Valparaíso |
| 8 | Santiago Centro | Centro | RM - Metropolitana |
| 9 | Providencia | Centro | RM - Metropolitana |
| 10 | Las Condes | Centro | RM - Metropolitana |
| 11 | Rancagua | Centro | VI - O'Higgins |
| 12 | Talca | Centro | VII - Maule |
| 13 | Curicó | Centro | VII - Maule |
| 14 | Chillán | Sur | XVI - Ñuble |
| 15 | Concepción | Sur | VIII - Biobío |
| 16 | Los Ángeles | Sur | VIII - Biobío |
| 17 | Temuco | Sur | IX - La Araucanía |
| 18 | Valdivia | Sur | XIV - Los Ríos |
| 19 | Osorno | Sur | X - Los Lagos |
| 20 | Puerto Montt | Sur | X - Los Lagos |
| 21 | Castro | Sur | X - Los Lagos |
| 22 | Coyhaique | Austral | XI - Aysén |
| 23 | Punta Arenas | Austral | XII - Magallanes |
| 24 | Calama | Norte | II - Antofagasta |
| 25 | San Antonio | Centro | V - Valparaíso |
| 26 | Quilpué | Centro | V - Valparaíso |
| 27 | San Bernardo | Centro | RM - Metropolitana |
| 28 | Maipú | Centro | RM - Metropolitana |
| 29 | La Florida | Centro | RM - Metropolitana |
| 30 | Puerto Varas | Sur | X - Los Lagos |

---

*Documento generado como anexo técnico del Informe de Evaluación Parcial N° 3 — Big Data (AVY1101), Duoc UC.*
