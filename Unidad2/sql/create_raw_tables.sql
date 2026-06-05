-- ==============================================================================
-- Creación de Tablas RAW en BigQuery: Grupo Cordillera (Evaluación Parcial N° 2)
-- ==============================================================================

-- 1. Crear el dataset principal para datos crudos (RAW Zone)
-- Nota: Reemplazar la región si se requiere (por defecto: us-central1)
CREATE SCHEMA IF NOT EXISTS `grupo_cordillera_raw`
OPTIONS(
  location="us-central1",
  description="Zona cruda del Data Lake de Grupo Cordillera que contiene tablas externas referenciando a GCS"
);

-- 2. Crear la Tabla Externa para Ventas Históricas (formato CSV)
-- Esta tabla lee en tiempo real el archivo cargado en GCS sin duplicar almacenamiento.
-- Nota: Reemplazar 'grupo-cordillera-datalake-ID_PROYECTO' por tu nombre real de bucket.
CREATE OR REPLACE EXTERNAL TABLE `grupo_cordillera_raw.ventas_historicas`
(
  id_transaccion STRING,
  fecha STRING, -- Se define como STRING temporalmente para limpiar inconsistencias en Dataprep
  id_sucursal INT64,
  rut_cliente STRING,
  nombre_cliente STRING,
  sku STRING,
  cantidad INT64,
  monto_clp STRING, -- Se define como STRING porque contiene anomalías de formato (símbolos $, comas)
  metodo_pago STRING
)
OPTIONS (
  format = 'CSV',
  uris = ['gs://grupo-cordillera-datalake-cordillerabi/raw/ventas_historicas.csv'],
  skip_leading_rows = 1,
  field_delimiter = ',',
  ignore_unknown_values = true,
  description = "Tabla externa conectada al CSV de ventas históricas en GCS"
);

-- 3. Crear la Tabla Externa para Sesiones Web (formato NDJSON / JSON Line-Delimited)
-- Esta tabla lee en vivo los registros de navegación estructurados en JSON.
CREATE OR REPLACE EXTERNAL TABLE `grupo_cordillera_raw.sesiones_web`
(
  session_id STRING,
  timestamp STRING,
  ip_address STRING,
  customer_id STRING,
  event_type STRING,
  sku_product STRING,
  device STRING
)
OPTIONS (
  format = 'NEWLINE_DELIMITED_JSON',
  uris = ['gs://grupo-cordillera-datalake-cordillerabi/raw/sesiones_web.json'],
  ignore_unknown_values = true,
  description = "Tabla externa conectada a los logs de sesiones web en formato JSON en GCS"
);
