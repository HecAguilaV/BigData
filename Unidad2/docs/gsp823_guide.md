# Guía de Paso a Paso: Laboratorio GSP823 - Cloud Dataprep

Esta guía está diseñada para que completes de forma eficiente y rápida el laboratorio **GSP823: Preparing and Aggregating Data for Visualizations using Cloud Dataprep** en Qwiklabs / Google Cloud Skills Boost, permitiéndote además entender el flujo para replicarlo en el proyecto de Grupo Cordillera.

## Justificación de Arquitectura (Las 5Vs)

El diseño de la arquitectura analítica de procesamiento por lotes (Batch) utilizada en este laboratorio se justifica bajo los siguientes pilares de las 5Vs:
*   **Volumen:** Trifacta/Dataprep compila recetas visuales en jobs de Cloud Dataflow (Apache Beam), permitiendo el procesamiento masivo y escalado horizontal de millones de filas de datos históricos sobre clima y éxito de escaladas.
*   **Variedad:** Permite integrar formatos tabulares heterogéneos y datasets de diferentes estructuras sin necesidad de codificar complejos scripts ETL manuales.
*   **Veracidad:** Las herramientas de análisis de calidad de Dataprep identifican de forma inmediata campos nulos, formatos de fechas inconsistentes y datos atípicos, asegurando la confiabilidad e integridad de los datos finales antes de su consumo.
*   **Valor:** La agregación temporal (año, mes) y el cálculo de métricas sumadas de éxito permiten descubrir correlaciones operacionales de gran valor estratégico que son expuestas en dashboards interactivos.

---

## 🏁 Preparación Inicial
1.  Inicia el laboratorio en Qwiklabs haciendo clic en **Start Lab**.
2.  Abre la consola de Google Cloud en una **ventana de incógnito** utilizando las credenciales temporales provistas por la plataforma (Usuario y Contraseña del lab).
3.  Acepta los términos y condiciones iniciales.

---

## 🛠️ Paso 1: Inicializar Cloud Dataprep
1.  En el menú de navegación de GCP, busca y haz clic en **Dataprep**.
2.  Marca la casilla para aceptar los Términos de Servicio de Google Dataprep y haz clic en **Agree and Continue**.
3.  A continuación, marca la casilla para autorizar a **Alteryx Designer Cloud (Trifacta)** a acceder a los datos de tu proyecto y haz clic en **Allow**.
4.  En la pantalla de configuración de almacenamiento de Trifacta, haz clic en **Use default storage project** y luego en **Continue**.
5.  Una vez cargada la interfaz de Dataprep, ya estás listo para crear tu flujo de trabajo.

---

## 📁 Paso 2: Crear el Flujo e Importar Datos
1.  En la interfaz de Dataprep, haz clic en **Flows** en el menú de la izquierda y luego en **Create Flow** (arriba a la derecha).
2.  Nombra el flujo como `Rainier Climb Data Flow` y haz clic en **Create**.
3.  Haz clic en el botón **Connect to Data** (o **Add Datasets**).
4.  En el menú de la izquierda, selecciona **Import Datasets**.
5.  Elige **Cloud Storage** y haz clic en el icono del lápiz para buscar la ruta del bucket.
6.  Busca el bucket que contiene el archivo de origen (generalmente inicia con el ID de tu proyecto o tiene un nombre predefinido en las instrucciones del lab).
7.  Selecciona el archivo `rainier_climb_data.csv` y haz clic en el botón de **+** al lado del archivo para agregarlo.
8.  Haz clic en **Import & Add to Flow** en la esquina inferior derecha.

---

## ✏️ Paso 3: Crear la Receta y Editar en la Cuadrícula
1.  En la pantalla del flujo, haz clic en el icono de **+** en el dataset importado y selecciona **Add new Recipe**.
2.  Haz clic en **Edit Recipe** para abrir la cuadrícula de Trifacta con la vista previa de las columnas del archivo.
3.  **Limpieza de Datos:**
    *   **Normalización de Fechas:** Selecciona la columna `Date`. En la barra de sugerencias, busca la opción para cambiar el formato de fecha (o haz clic derecho en la cabecera de la columna, selecciona **Change Type** -> **Datetime**).
    *   **Filtrar registros nulos/vacíos:** Si la columna `Date` tiene barras rojas indicando valores erróneos o nulos, haz clic en la sección roja de la barra de calidad sobre la cabecera y selecciona **Delete rows with missing values**.
    *   **Extracción de Atributos:** Selecciona la columna `Date`. Haz clic en **Extract** en la barra de herramientas superior y elige **Year** para crear una nueva columna con el año. Haz lo mismo para extraer el **Month**.

---

## 📊 Paso 4: Agregación de Datos
1.  Haz clic en el botón **Pivot/Group** (o la herramienta **Aggregate** en el menú superior).
2.  En el panel de configuración de la agregación:
    *   En **Group by**, selecciona las columnas recién creadas: `year` y `month`.
    *   En **Values**, selecciona la columna `Climbers` y elige la función **SUM**.
    *   También selecciona `Successes` y aplica la función **SUM**.
3.  Haz clic en **Add to Recipe** para aplicar los cambios. La vista previa ahora mostrará los datos agregados y resumidos por año y mes.

---

## 🚀 Paso 5: Configurar Salida y Ejecutar el Job
1.  Haz clic en **Run Job** en la esquina superior derecha.
2.  En la configuración de ejecución del trabajo (Publishing Actions):
    *   Por defecto, la salida estará configurada como un archivo CSV en GCS. Haz clic en **Edit** (icono de lápiz) al lado de las acciones de publicación.
    *   Cambia el destino a **BigQuery**.
    *   Selecciona tu base de datos (dataset del proyecto del lab, ej. `clean_climb_data` o similar).
    *   Configura la acción como **Create a new table** (o **Truncate table** si ya existe) y nombra la tabla de salida como `rainier_summary`.
    *   Haz clic en **Update**.
3.  Haz clic en **Run** para iniciar el procesamiento en Dataflow en segundo plano.
4.  Espera de 3 a 5 minutos a que el estado del Job cambie a **Green (Success)**.
5.  *Verificación:* Ve a la consola de BigQuery y ejecuta un `SELECT * FROM clean_climb_data.rainier_summary` para verificar que la tabla contiene los datos correctos y agregados. ¡Haz clic en **Check my progress** en Qwiklabs para ganar los puntos!

---

## 💾 Paso 6: Exportar tu Flujo (Evidencia para el Encargo)
Dado que el entorno de Qwiklabs es temporal, debes exportar tu diseño para documentarlo en tu informe final:
1.  En la pantalla del flujo (`Rainier Climb Data Flow`), haz clic en los tres puntos **(...)** en la esquina superior derecha.
2.  Selecciona **Export Flow**.
3.  Esto descargará un archivo comprimido `.zip` con la receta y configuraciones. Guárdalo y tómale captura al diagrama del flujo en pantalla para incluirlo como anexo en el informe de la Evaluación 2.

---

## 🛡️ Gobierno de Datos, Privacidad y Archivado (Cumplimiento Ley N° 21.719)

Aunque este es un laboratorio práctico de preparación de datos genéricos, la replicación de este flujo en el entorno de producción de Grupo Cordillera debe cumplir con los estándares de gobierno del proyecto:
*   **Cumplimiento Normativo:** Los flujos y visualizaciones se estructuran bajo los lineamientos de la **Ley N° 21.719** de Protección de Datos de Chile.
*   **Seudonimización:** En la receta de Dataprep se omiten o enmascaran campos identificatorios directos de los escaladores/clientes (por ejemplo, mediante SHA-256 no reversibles) antes de cargarlos en BigQuery.
*   **Archivado de Bajo Costo:** Los datos de origen en Cloud Storage se gestionan mediante políticas de ciclo de vida de objetos (Object Lifecycle Management), migrando de la clase Standard a **Coldline** después de 90 días, y a **Archive** a los 365 días, reduciendo costos de retención de cumplimiento histórico.

