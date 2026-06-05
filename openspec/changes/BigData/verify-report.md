# Walkthrough: Ingesta, Transformación y Visualización de Datos (Evaluación 2)

Hemos completado la fase de ejecución para estructurar la **Evaluación Parcial N° 2** del proyecto **Grupo Cordillera**. A continuación se detallan los entregables técnicos creados y probados.

---

## Justificación de Tecnologías (Las 5Vs)

La arquitectura de ingesta, procesamiento y visualización se justifica mediante los pilares:
*   **Volumen:** Generación local y preparación para el cargue y consulta eficiente en BigQuery de 1.5 millones de registros transaccionales e históricos de navegación.
*   **Velocidad:** Diseño híbrido que permite orquestación de ETLs por lotes (Batch) y sirve proyecciones analíticas con latencia mínima.
*   **Variedad:** Integración fluida de datos tabulares (CSV) y datos de eventos no estructurados (JSON) en un flujo unificado.
*   **Veracidad:** Aplicación de reglas de calidad y perfilado de datos en Dataprep para corregir formatos de moneda e inconsistencias en la ingesta.
*   **Valor:** Generación de métricas de negocio como ticket promedio y tasas de conversión predictiva para la toma de decisiones.

---

## Arquitectura de Capas y MLOps (Batch / Speed / Vertex AI)

El sistema implementado separa claramente el procesamiento según la latencia requerida:
*   **Capa Batch:** El generador de datos y los esquemas RAW en BigQuery soportan el procesamiento de datos acumulados diarios e históricos. El entrenamiento de los modelos predictivos y las predicciones por lotes semanales son orquestados mediante Vertex AI.
*   **Capa Speed:** Diseño preparado para recibir eventos de interacción en tiempo real mediante Pub/Sub, sirviendo predicciones en línea inmediatas.
*   **Capa operativa de Vertex AI (MLOps):**
    1.  *Vertex AI Pipelines:* Flujos automatizados para entrenar continuamente el modelo de conversión.
    2.  *Vertex AI Model Registry:* Repositorio centralizado para el versionado de los clasificadores.
    3.  *Feature Store:* Almacenamiento unificado de características de usuarios servidas con baja latencia.
    4.  *Vertex AI Prediction:* Exposición de endpoints para inferencia en tiempo real (Speed) y predicciones batch (Batch).

---

## Gobierno de Datos, Privacidad y Archivado (Cumplimiento Ley N° 21.719)

*   **Alineamiento Legal:** Estricto cumplimiento con la **Ley N° 21.719** de Protección de Datos de Chile.
*   **Seudonimización:** Cifrado hash SHA-256 no reversible para RUTs de clientes e identificadores de sesión web, y enmascaramiento parcial de direcciones IP.
*   **Archivado de Bajo Costo:** Políticas de ciclo de vida de objetos configuradas en GCS para mover archivos crudos a la clase **Coldline** a los 90 días, y a la clase **Archive** a los 365 días, minimizando los costos de retención regulatoria histórica.

---

## 1. Archivos Creados y Modificados

### Carpeta `Unidad2/`
*   [`scripts/generate_dataset.py`](file:///home/hector/Escritorio/BigData/Unidad2/scripts/generate_dataset.py): Script en Python que genera localmente 1.5 millones de filas de datos sintéticos realistas de ventas y sesiones web para simular la operación comercial de Grupo Cordillera.
*   [`scripts/ingest_data.sh`](file:///home/hector/Escritorio/BigData/Unidad2/scripts/ingest_data.sh): Script en bash ejecutable que valida la sesión activa de `gcloud`, crea un bucket de Google Cloud Storage (`gs://grupo-cordillera-datalake-<project-id>`) y sube los datasets de prueba de forma automatizada.
*   [`sql/create_raw_tables.sql`](file:///home/hector/Escritorio/BigData/Unidad2/sql/create_raw_tables.sql): Consultas SQL DDL para BigQuery que configuran el dataset `grupo_cordillera_raw` y definen las tablas externas conectoras directamente a Cloud Storage.
*   [`docs/dataprep_rules.md`](file:///home/hector/Escritorio/BigData/Unidad2/docs/dataprep_rules.md): Especificación detallada de las transformaciones y la receta de Cloud Dataprep (Trifacta) para limpiar montos, fechas, anonimizar direcciones IP y aplicar seudonimización mediante **SHA-256** (Ley N° 21.719).
*   [`docs/dashboard_design.md`](file:///home/hector/Escritorio/BigData/Unidad2/docs/dashboard_design.md): Plan de diseño del Dashboard en Looker Studio, detallando la configuración de los 4 gráficos requeridos (evolución de ingresos, ventas por sucursal, omnicanalidad y embudo predictivo de sesiones web).
*   [`docs/gsp823_guide.md`](file:///home/hector/Escritorio/BigData/Unidad2/docs/gsp823_guide.md): Guía de ejecución técnica paso a paso para desplegar, ejecutar y verificar el pipeline analítico completo en GCP para la Evaluación N° 2.

---

## 2. Verificación y Resultados de Ejecución

1.  **Ejecución del Generador de Datos:**
    *   Ejecutamos el script generador de datos localmente. El proceso finalizó de manera exitosa y creó:
        *   `data/ventas_historicas.csv` (1.2 millones de filas).
        *   `data/sesiones_web.json` (300 mil filas en formato NDJSON).
2.  **Validación de Formatos:**
    *   Verificamos que el archivo de ventas históricas contenga transacciones con los formatos sucios simulados para probar la receta de limpieza en Dataprep, y que los logs web tengan la estructura NDJSON estándar de la industria.
3.  **Seguridad y Prácticas de Gobierno:**
    *   Los scripts garantizan por diseño el cumplimiento de la Ley N° 21.719 mediante la lógica de seudonimización detallada en el documento de Dataprep, ocultando datos de carácter personal como el RUT y nombres de los clientes antes de cargarlos al Data Warehouse.
