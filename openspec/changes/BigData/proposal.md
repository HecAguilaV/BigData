# Plan de Implementación: Ingesta, Transformación y Visualización de Datos (Evaluación 2)

Este plan detalla los pasos para realizar la ingesta de datos en modalidad Batch, el proceso de limpieza y transformación en la nube (GCP) y el diseño de la visualización final para cumplir con los requerimientos de la **Evaluación Parcial N° 2** del proyecto **Grupo Cordillera**.

---

## Justificación de Tecnologías (Las 5Vs)

La arquitectura y tecnologías propuestas se justifican bajo los pilares de las 5Vs:
*   **Volumen:** Google Cloud Storage y BigQuery actúan como repositorios elásticos capaces de almacenar y consultar de forma instantánea el historial acumulado de 10 años de transacciones.
*   **Velocidad:** Se divide el flujo en procesamiento batch (Dataflow/Dataprep) y analítica predictiva en tiempo real (Capa Speed), garantizando respuestas sub-segundo.
*   **Variedad:** Cloud Dataprep maneja fuentes heterogéneas, integrando archivos estructurados CSV (`ventas_historicas`) y logs semi-estructurados JSON (`sesiones_web`).
*   **Veracidad:** Las recetas de Dataprep y reglas de calidad limpian montos, estandarizan fechas y filtran anomalías, garantizando la integridad.
*   **Valor:** Looker Studio expone métricas y embudos interactivos integrando proyecciones de compra para toma de decisiones ejecutivas.

---

## Arquitectura Híbrida y MLOps (Capa Batch y Capa Speed)

Para garantizar la escalabilidad e integración predictiva, la arquitectura se divide en:
*   **Capa Batch:** Carga periódica de logs históricos a BigQuery mediante Cloud Dataprep. Procesa las transacciones de ventas y sesiones web para reportes semanales e históricos.
*   **Capa Speed:** Canalización de eventos web en tiempo real (clics, carritos) mediante Pub/Sub para la toma de decisiones instantáneas en la web (ofertas personalizadas).
*   **Capa operativa de Vertex AI (MLOps):**
    1.  *Vertex AI Pipelines:* Automatiza el reentrenamiento y validación de los modelos predictivos de conversión de clientes.
    2.  *Vertex AI Model Registry:* Registra y gestiona el versionado de los modelos entrenados.
    3.  *Vertex AI Feature Store:* Centraliza los atributos analíticos (features) del comportamiento de clientes.
    4.  *Vertex AI Prediction:* Sirve predicciones online (Capa Speed) y predicciones batch (Capa Batch) para las visualizaciones.

---

## Gobierno de Datos, Privacidad y Archivado (Cumplimiento Ley N° 21.719)

*   **Cumplimiento Normativo:** Alineado con la **Ley N° 21.719** de Protección de Datos de Chile.
*   **Seudonimización:** Se aplica SHA-256 no reversible para `rut_cliente` y `customer_id`, y enmascaramiento de IP a nivel de subred. Los datos identificatorios crudos se descartan antes de cargar en BigQuery.
*   **Archivado de Bajo Costo:** Los archivos crudos de Cloud Storage se gestionan con Object Lifecycle Management, migrando a **Coldline** a los 90 días, y a **Archive** a los 365 días para conservación histórica obligatoria a costo mínimo.

---

## Proposed Changes

### Componente 1: Generación y Estructura de Datos Locales

#### [NEW] [generate_dataset.py](file:///home/hector/Escritorio/BigData/Unidad2/scripts/generate_dataset.py)
*   Script en Python para generar de manera pseudoaleatoria los registros transaccionales y de logs de Grupo Cordillera (1.5 millones de registros en total).
*   Estructura de salida en una nueva carpeta `data/`:
    *   `data/ventas_historicas.csv` (Campos: `id_transaccion`, `fecha`, `id_sucursal`, `rut_cliente`, `nombre_cliente`, `sku`, `cantidad`, `monto_clp`, `metodo_pago`).
    *   `data/sesiones_web.json` (Campos: `session_id`, `timestamp`, `ip_address`, `customer_id`, `event_type`, `sku_product`, `device`).

---

### Componente 2: Ingesta y Data Lake en GCP (Cloud Storage)

#### [NEW] [ingest_data.sh](file:///home/hector/Escritorio/BigData/Unidad2/scripts/ingest_data.sh)
*   Script en bash con comandos `gcloud storage cp` (o `gsutil`) para automatizar la subida de los archivos locales a los buckets correspondientes del Data Lake en GCP:
    *   `gs://grupo-cordillera-datalake/raw/ventas_historicas.csv`
    *   `gs://grupo-cordillera-datalake/raw/sesiones_web.json`

---

### Componente 3: Almacén de Datos (BigQuery RAW)

#### [NEW] [create_raw_tables.sql](file:///home/hector/Escritorio/BigData/Unidad2/sql/create_raw_tables.sql)
*   Sentencias DDL para inicializar el dataset `grupo_cordillera_raw` en BigQuery y crear las tablas RAW externas o nativas a partir del almacenamiento de Cloud Storage, preparándolas para su ingesta y procesamiento en Dataprep.

---

### Componente 4: Transformación y Calidad de Datos (Cloud Dataprep)

#### [NEW] [dataprep_rules.md](file:///home/hector/Escritorio/BigData/Unidad2/docs/dataprep_rules.md)
*   Documento de diseño que detalla la lógica de limpieza y transformación que se debe implementar en la interfaz de Cloud Dataprep (Trifacta) con el soporte de 5Vs, seudonimización y archivado de bajo costo.

---

### Componente 5: Visualización y Reportes (Looker Studio)

#### [NEW] [dashboard_design.md](file:///home/hector/Escritorio/BigData/Unidad2/docs/dashboard_design.md)
*   Documento con el boceto y especificación del dashboard de 4 gráficos exigido por la pauta de evaluación, integrando justificación 5Vs, Vertex AI MLOps y políticas de archivado del Data Warehouse.

---

## Verification Plan

### Automated Tests
*   Ejecutar el script generador de datos localmente para verificar que se generen los archivos en la estructura y formatos correctos (`csv` y `json`), validando los recuentos de filas mediante un script de verificación.

### Manual Verification
*   Validar la creación de buckets de Cloud Storage y datasets de BigQuery en la consola de GCP.
*   Validar el flujo de transformación de Dataprep y asegurar que la exportación termine exitosamente cargando los datos refinados en BigQuery.
*   Verificar que el informe final de la Evaluación 2 contenga todas las capturas y explicaciones técnicas de los procesos de ingesta, transformación y visualización.
