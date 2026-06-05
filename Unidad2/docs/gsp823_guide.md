# Guía de Ejecución Técnica: Pipeline de Big Data - Grupo Cordillera (Evaluación N° 2)

Esta guía detalla el procedimiento paso a paso para desplegar, ejecutar y verificar el pipeline de procesamiento por lotes (Batch) de **Grupo Cordillera** en la nube de Google Cloud Platform (GCP), cumpliendo con los estándares de diseño, seguridad y gobierno exigidos para la evaluación.

---

## Justificación de Arquitectura (Las 5Vs)

El diseño de esta arquitectura analítica de procesamiento por lotes (Batch) se justifica bajo los siguientes pilares de las 5Vs:
*   **Volumen:** Google Cloud Storage y BigQuery permiten almacenar y procesar de manera elástica millones de transacciones de ventas históricas y logs de comportamiento web sin degradación de rendimiento.
*   **Variedad:** Integración fluida de datos tabulares estructurados (CSV) y datos de navegación semi-estructurados (JSON) en un flujo unificado.
*   **Veracidad:** Las herramientas de calidad y perfilado de Cloud Dataprep identifican y descartan registros nulos o inconsistencias en los montos de transacciones antes de cargarlos.
*   **Valor:** La agregación temporal y el cálculo de métricas clave (como ticket promedio y embudo de conversión predictiva) habilitan la toma de decisiones estratégicas.

---

## Arquitectura Híbrida y MLOps (Capa Batch / Capa Speed)

Para soportar las necesidades operativas de baja latencia y análisis predictivo, la arquitectura analítica del proyecto se compone de:
*   **Capa Batch:** El flujo principal de procesamiento de datos históricos de ventas y sesiones web se realiza por lotes. Los datos cargados en BigQuery son procesados semanalmente para alimentar reportes estratégicos y dashboards ejecutivos en Looker Studio.
*   **Capa Speed:** Procesamiento en tiempo real de eventos de interacción web mediante Pub/Sub para la toma de decisiones inmediatas, como ofertas personalizadas o detección de fraudes.
*   **Capa operativa de Vertex AI (MLOps):** Para operacionalizar e integrar la analítica avanzada y proyecciones predictivas en el Gráfico 4 del Dashboard, se define la siguiente arquitectura MLOps:
    1.  *Vertex AI Pipelines:* Automatiza la ejecución y el reentrenamiento programado de los modelos predictivos utilizando los datos limpios en BigQuery.
    2.  *Vertex AI Model Registry:* Centraliza y versiona los modelos de clasificación entrenados, facilitando el control y aprobación de versiones.
    3.  *Vertex AI Feature Store:* Almacena y sirve atributos de comportamiento de clientes consolidados con latencia sub-segundo.
    4.  *Vertex AI Prediction:* Expone endpoints para servir predicciones online (Capa Speed, en tiempo real) y ejecuciones de predicciones batch (Capa Batch, para reportes históricos semanales).

---

## 🛠️ Paso 1: Generación de Datos Sintéticos Locales
1. Asegúrate de tener Python instalado y ejecuta el script generador de datos [generate_dataset.py](file:///home/hector/Escritorio/BigData/Unidad2/scripts/generate_dataset.py):
   ```bash
   python3 Unidad2/scripts/generate_dataset.py
   ```
2. Esto creará el directorio `data/` con los archivos de prueba que simulan la operación comercial de Grupo Cordillera:
   * `data/ventas_historicas.csv` (1.2 millones de filas).
   * `data/sesiones_web.json` (300 mil filas en formato NDJSON).

---

## 🪣 Paso 2: Ingesta al Data Lake (Cloud Storage)

### 2.1 Preparación de la CLI en Ubuntu
Si estás en Ubuntu y no tienes instalada la herramienta de línea de comandos `gcloud`, instálala ejecutando:
```bash
sudo snap install google-cloud-cli --classic
```

### 2.2 Autenticación y Configuración de Proyecto
1. Autentícate en Google Cloud SDK con tu cuenta:
   ```bash
   gcloud auth login
   ```
2. Si tienes múltiples cuentas configuradas (ej. institucional y personal) y necesitas alternar a la cuenta con los créditos activos, lista las cuentas y selecciona tu correo personal:
   ```bash
   gcloud auth list
   gcloud config set account TU_CORREO@gmail.com
   ```
3. Lista los proyectos para verificar que tu proyecto `cordillerabi` está disponible en la lista:
   ```bash
   gcloud projects list
   ```
4. Configura el proyecto activo en tu terminal:
   ```bash
   gcloud config set project cordillerabi
   ```

### 2.3 Ejecución del Script de Ingesta
1. Asegúrate de dar permisos de ejecución al script [ingest_data.sh](file:///home/hector/Escritorio/BigData/Unidad2/scripts/ingest_data.sh) y córrelo desde el directorio raíz del proyecto:
   ```bash
   chmod +x Unidad2/scripts/ingest_data.sh
   ./Unidad2/scripts/ingest_data.sh
   ```
   *Nota:* Este script, desarrollado por el **Equipo Desarrollo CordilleraBI**, creará automáticamente el bucket `gs://grupo-cordillera-datalake-cordillerabi` en `us-central1` (vinculándolo a tu facturación activa) y subirá los archivos locales `ventas_historicas.csv` y `sesiones_web.json` a la ruta `/raw/`.


---

## 🗄️ Paso 3: Definición del Esquema RAW en BigQuery
1. Abre la consola de **Google BigQuery**.
2. Ejecuta las sentencias DDL del archivo [create_raw_tables.sql](file:///home/hector/Escritorio/BigData/Unidad2/sql/create_raw_tables.sql).
3. Esto inicializará el dataset `grupo_cordillera_raw` y creará las dos tablas externas (`ventas_historicas` y `sesiones_web`) conectadas a los archivos de Cloud Storage.

---

## 🧼 Paso 4: Configuración de Reglas de Transformación en Cloud Dataprep
1. Entra a **Cloud Dataprep** desde la consola de GCP.
2. Crea un flujo de datos llamado `Grupo Cordillera ETL Flow`.
3. Importa las tablas de origen desde el dataset `grupo_cordillera_raw` en BigQuery.
4. Implementa las recetas detalladas en el documento de especificación [dataprep_rules.md](file:///home/hector/Escritorio/BigData/Unidad2/docs/dataprep_rules.md):
   * **Limpieza:** Conversión de tipos de datos, corrección del formato en `monto_clp`, y filtrado de valores nulos o negativos.
   * **Seudonimización (Privacidad):** Seudonimización por enmascaramiento de texto (masking) para RUTs e IDs de cliente (`rut_cliente` y `customer_id`) para resguardar la identidad de los usuarios en cumplimiento de la Ley N° 21.719. Enmascaramiento parcial de direcciones IP.
5. Ejecuta el Job configurando la salida para escribir las tablas refinadas (`fact_ventas` y `fact_sesiones_web`) en el dataset final de BigQuery `grupo_cordillera_dw`.
   > [!IMPORTANT]
   > **Consistencia de Regiones:** El dataset de destino `grupo_cordillera_dw` debe crearse en la región específica `us-central1` (ej. `bq mk --location=us-central1 grupo_cordillera_dw`). Si se crea como multirregión `US`, Dataprep fallará al intentar cruzar o escribir datos debido a la restricción de BigQuery de no leer y escribir en distintas regiones.


---

## 📊 Paso 5: Construcción del Dashboard Ejecutivo en Looker Studio
1. Crea un nuevo reporte en **Looker Studio**.
2. Añade las tablas de BigQuery (`fact_ventas` y `fact_sesiones_web`) como orígenes de datos.
3. Agrega los 4 gráficos requeridos siguiendo las pautas de [dashboard_design.md](file:///home/hector/Escritorio/BigData/Unidad2/docs/dashboard_design.md):
   * **Gráfico 1 (Evolución Temporal):** Línea de tiempo de ingresos acumulados diarios/mensuales.
   * **Gráfico 2 (Desempeño Comercial):** Barras horizontales de ventas acumuladas por sucursal física.
   * **Gráfico 3 (Omnicanalidad):** Gráfico de anillo mostrando el canal de venta (Físico vs Digital).
   * **Gráfico 4 (Conversión Web Predictivo):** Embudo de sesiones y proyecciones basadas en modelos de Vertex AI.

---

## 🛡️ Gobierno de Datos, Privacidad y Archivado (Ley N° 21.719)

Para cumplir con la legislación chilena y optimizar costos de almacenamiento:
*   **Cumplimiento de la Ley N° 21.719:** Se aplica seudonimización por diseño en el paso 4. Ningún dato personal crudo (RUT o nombres) llega al Data Warehouse de BigQuery o a Looker Studio.
*   **Archivado de Bajo Costo:** Los datos de origen en Cloud Storage se gestionan mediante políticas de ciclo de vida de objetos (Object Lifecycle Management), migrando de la clase Standard a **Coldline** después de 90 días, y a la clase **Archive** a los 365 días para conservación histórica obligatoria a costo mínimo.
