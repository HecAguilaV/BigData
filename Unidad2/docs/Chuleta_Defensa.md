# GUÍA DE ESTUDIO Y PREPARACIÓN DE DEFENSA TÉCNICA

Esta guía de estudio resume de forma estructurada y accesible los fundamentos del pipeline de Big Data para el caso de estudio **Grupo Cordillera**. Su propósito es facilitar la comprensión de los conceptos clave y la preparación para la defensa de la evaluación ante la comisión.

---

## 1. Resumen Estructurado del Pipeline Analítico

El pipeline se compone de las siguientes fases secuenciales:

1. **Origen de los Datos:**
   * `ventas_historicas.csv` (Datos estructurados): Registro de transacciones de ventas físicas.
   * `sesiones_web.json` (Datos semi-estructurados en formato NDJSON): Logs de navegación en el e-commerce.
2. **Data Lake (Almacenamiento Crudo):** Implementado en **Google Cloud Storage (GCS)** en la región `us-central1`. Almacena los archivos en su formato nativo sin transformaciones previas.
3. **Capa RAW (Acceso SQL):** Definición de tablas externas en **BigQuery** bajo el dataset `grupo_cordillera_raw`, permitiendo la consulta de los archivos en GCS mediante sentencias DDL SQL sin duplicar el almacenamiento físico.
4. **Capa de Transformación (ETL):** Implementada en **Cloud Dataprep (Trifacta)**. Procesa los datos crudos aplicando reglas de limpieza (eliminación de caracteres sucios en `monto_clp`), enriquecimiento temporal, y seudonimización.
5. **Data Warehouse (Capa Analítica):** Almacenamiento físico definitivo en tablas de BigQuery (`grupo_cordillera_dw`) bajo un esquema relacional optimizado para consultas analíticas de alta velocidad.
6. **Visualización (Dashboard):** Conexión directa del Data Warehouse a **Looker Studio** para la construcción de indicadores clave (KPI) interactivos.

---

## 2. Balotario de Preguntas Técnicas y Respuestas Clave

A continuación se presentan las preguntas conceptuales más recurrentes por parte de los evaluadores y sus respuestas justificadas técnicamente:

### 🙋‍♂️ Pregunta 1: ¿Por qué se prefiere Cloud Dataprep en lugar de realizar la limpieza directo con SQL en BigQuery?
* **Respuesta:** "Cloud Dataprep proporciona una interfaz de perfilado visual interactivo que permite detectar anomalías e inconsistencias en la distribución de los datos de manera inmediata. Además, Dataprep escala de manera serverless compilando las recetas de transformación en jobs de **Google Cloud Dataflow** (Apache Beam), ejecutando el procesamiento distribuido de millones de registros de forma eficiente sin necesidad de administrar servidores."

### 🙋‍♂️ Pregunta 2: ¿Cuál es la diferencia de rol entre el Data Lake y el Data Warehouse?
* **Respuesta:** "El **Data Lake** (Cloud Storage) almacena datos crudos e inmutables, en múltiples formatos (estructurados y semi-estructurados) y sin esquema rígido. El **Data Warehouse** (BigQuery) almacena únicamente datos limpios, transformados y estructurados bajo un modelo de datos optimizado para consultas analíticas de negocio."

### 🙋‍♂️ Pregunta 3: ¿A qué se debió el error de regiones en BigQuery y cómo se solucionó?
* **Respuesta:** "El error ocurrió porque BigQuery prohíbe realizar operaciones de lectura y escritura cruzadas entre distintas regiones. Los datos crudos en Cloud Storage y las tablas RAW estaban en `us-central1`, pero el dataset de destino `grupo_cordillera_dw` se había creado en la multirregión `US`. Se solucionó recreando el dataset de destino explícitamente en la región `us-central1` mediante `bq mk --location=us-central1`."

### 🙋‍♂️ Pregunta 4: ¿Cómo garantiza el diseño el cumplimiento de la Ley N° 21.719 de protección de datos personales?
* **Respuesta:** "Se implementa la Privacidad por Diseño (Privacy by Design). Durante el proceso ETL en Dataprep, los datos sensibles identificatorios (`rut_cliente` y `customer_id`) se someten a **seudonimización** mediante una fórmula de enmascaramiento que oculta los caracteres centrales y conserva prefijos e identificador verificador. Las columnas crudas con información sensible se eliminan (`drop`) antes de guardar los datos en el Data Warehouse."

### 🙋‍♂️ Pregunta 5: ¿Cuál es la justificación de usar enmascaramiento parcial en lugar de aplicar Hash SHA-256?
* **Respuesta:** "El enmascaramiento parcial conserva utilidad analítica para agrupaciones de negocio (por ejemplo, analizar patrones agregados por rangos de RUT o comportamiento por tramos) mientras que resguarda el secreto de la identidad. Las funciones Hash SHA-256, aunque seguras, impiden cualquier tipo de análisis de patrones parciales en los textos originales."

### 🙋‍♂️ Pregunta 6: ¿Cómo se optimizan los costos de almacenamiento del Data Lake?
* **Respuesta:** "Se definieron políticas de Object Lifecycle Management en Cloud Storage. Los archivos crudos de ingesta se mueven automáticamente de la clase Standard a **Coldline** después de 90 días, y a la clase **Archive** a los 365 días, reduciendo los costos de almacenamiento para datos de retención regulatoria histórica obligatoria."

### 🙋‍♂️ Pregunta 7: ¿Por qué en Cloud Dataprep a veces desaparecen temporalmente las columnas al escribir una fórmula?
* **Respuesta:** "Es un comportamiento visual de la interfaz. Al previsualizar una fórmula de derivación (como `Derive`), Dataprep enfoca la pantalla únicamente en la nueva columna calculada para facilitar la revisión del resultado. Una vez que se hace clic en 'Add' para agregar el paso a la receta, todas las columnas de la tabla vuelven a visualizarse normalmente."

### 🙋‍♂️ Pregunta 8: ¿Por qué arroja un error de esquema al usar el término `null` en una fórmula de Dataprep y cómo se corrige?
* **Respuesta:** "En el lenguaje Wrangle de Dataprep, escribir `null` sin paréntesis hace que el compilador lo interprete como una referencia a una columna con ese nombre. Para inyectar un valor nulo real, se debe invocar como una función utilizando paréntesis: `null()` o `NULL()`."

### 🙋‍♂️ Pregunta 9: ¿Por qué el dataset final en BigQuery se llama `grupo_cordillera_dw`? ¿Qué significa "dw"?
* **Respuesta:** "`dw` son las siglas de **Data Warehouse** (Almacén de Datos). Representa la capa analítica final de la arquitectura. A diferencia de la zona `raw` (Data Lake) que tiene datos crudos, el Data Warehouse almacena la versión limpia, estructurada y de alta calidad de la información, lista para ser consumida directamente por los analistas y por Looker Studio."

### 🙋‍♂️ Pregunta 10: ¿Qué función exacta cumplen las recetas `ventas_historicas_recipe` y `sesiones_web_recipe`?
* **Respuesta:** "Son el núcleo del proceso ETL (Extraer, Transformar y Cargar) de la Capa Batch. `ventas_historicas_recipe` limpia anomalías numéricas en los montos y extrae el año/mes/día. `sesiones_web_recipe` estandariza el tiempo (timestamp) y enmascara las direcciones IP a nivel de subred. Ambas recetas tienen la misión crítica de **seudonimizar** los datos personales (RUT/Customer ID) para cumplir con la Ley N° 21.719 antes de inyectar los registros al Data Warehouse."

### 🙋‍♂️ Pregunta 11: ¿Por qué en la vista de BigQuery los números aparecen como `INTEGER` en lugar de `INT64`?
* **Respuesta:** "Es exactamente lo mismo. `INT64` es el nombre técnico formal del tipo de dato en el motor SQL de BigQuery, mientras que `INTEGER` es un alias visual que usa la interfaz gráfica de GCP para facilitar la lectura. Ambos representan números enteros de 64 bits. Lo mismo ocurre con el tipo `DATETIME`."

---

## 3. Glosario de Conceptos Clave

* **Esquema RAW:** Estructura de datos inicial o en bruto directamente vinculada a las fuentes de ingesta sin procesamiento.
* **Tabla Externa:** Tabla de BigQuery que no almacena los datos de forma nativa, sino que consulta directamente archivos almacenados en Cloud Storage.
* **Seudonimización:** Tratamiento de datos personales de manera que no puedan atribuirse a un interesado sin utilizar información adicional guardada por separado.
* **MLOps (Vertex AI):** Operaciones de Machine Learning. Conjunto de prácticas que estandarizan y automatizan el ciclo de vida de los modelos predictivos en la nube.

---

## 4. Estructura Sugerida para la Defensa (Presentación de 10 Minutos)

Para la presentación gerencial de 10 minutos, se sugiere estructurar las láminas de la siguiente manera:

* **Lámina 1: Introducción y Caso de Negocio (0:30 min):** Planteamiento del escenario comercial de Grupo Cordillera y objetivos de omnicanalidad.
* **Lámina 2: Justificación de Arquitectura - 5Vs (1:30 min):** Exposición de cómo el volumen, variedad, veracidad, velocidad y valor definieron el uso de Cloud Storage y BigQuery.
* **Lámina 3: Arquitectura Híbrida y Capas (2:00 min):**
  * **Capa Batch:** Flujo de procesamiento de transacciones históricas y logs mediante Dataprep a BigQuery DW.
  * **Capa Speed:** Procesamiento en tiempo real de interacciones web con Pub/Sub.
  * **Vertex AI MLOps:** Especificación de la capa operativa de aprendizaje automático:
    1. *Vertex AI Pipelines* (automatización de entrenamientos).
    2. *Vertex AI Model Registry* (control de versiones).
    3. *Vertex AI Feature Store* (servidor de atributos de baja latencia).
    4. *Vertex AI Prediction* (endpoints online y batch).
* **Lámina 4: Implementación de Ingesta y RAW (1:30 min):** Demostración de la ingesta estructurada mediante scripts en Bash y la definición de tablas SQL externas.
* **Lámina 5: Transformación y Calidad (Dataprep) (2:00 min):** Explicación de las reglas de limpieza, normalización temporal y la política de seudonimización.
* **Lámina 6: Visualización y Dashboard (1:30 min):** Mapeo de los 4 gráficos en Looker Studio (evolución temporal, desempeño comercial, canal de venta e inferencia predictiva).
* **Lámina 7: Gobierno de Datos y Seguridad (Ley N° 21.719) (1:00 min):** Mecanismos de protección, IP masking, y archivado en clases Coldline/Archive.
* **Lámina 8: Conclusiones y Preguntas (0:30 min):** Cierre y síntesis de los logros del proyecto.
