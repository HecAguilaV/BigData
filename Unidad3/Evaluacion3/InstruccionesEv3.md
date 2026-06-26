# Evaluación Parcial N° 3: Gestión de Grandes Volúmenes de Datos (Real-Time / Streaming)

## 1. Descripción General de la Evaluación
La evaluación consiste en realizar y presentar un informe de gestión de grandes volúmenes de Datos, mediante la carga histórica de todos los archivos disponibles, junto con información capturada en forma streaming / Real Time, la cual permita a los usuarios responder diversas preguntas de negocio relacionadas con la disponibilidad de servicios en ciertas zonas, horarios y frecuencia.

Adicionalmente, deberá diseñar y crear dos reportes que muestren información agregada.

### Indicadores de Logro (IL) a Evaluar
*   **IL 3.1:** Crea proceso de ingesta utilizando variedad de APIs disponibles en la industria para implementar procesos de ingesta de datos en línea.
*   **IL 3.2:** Construye proceso, con el fin de realizar limpieza, transformación y almacenamiento de grandes volúmenes de datos en tiempo real/streaming.
*   **IL 3.3:** Sintetiza la información en un panel de control para demostrar el potencial de la herramienta utilizada.

---

## 2. Instrucciones Específicas: Dimensión Encargo

Deberán construir procesos de carga, considerando disponibilidad de la información desde fuente de origen, en caso de errores. Construir procesos de transformación y limpieza de datos, dejando los datos en formatos para capa de consumo, evitando duplicidad de datos real-time/Streaming para detección oportuna de errores.

### Pasos de Ejecución
*   **Paso 1:** Realizar las conexiones con la fuente de origen de datos.
*   **Paso 2:** Descargar y/o generar los archivos al data lake o fuente de destino, utilizando las APIs disponibles o construidas por usted.
*   **Paso 3:** Construir los procesos de limpieza, transformación y carga al modelo de datos final, considerando la trazabilidad de información y ciclo de vida del dato.
*   **Paso 4:** Mejorar los reportes y/o visualizaciones correspondientes construidos previamente en la etapa 2 (debe considerar reportes y/o visualizaciones correspondientes en un panel o dashboard interactivo, del cual debe incluir imágenes en el informe).

### Requerimientos para la Construcción
Para lo anterior, deberá realizar lo siguiente:
*   Construir procesos de carga, considerando disponibilidad de la información desde fuente de origen, en caso de errores.
*   Construir procesos de transformación y limpieza de datos, dejando los datos en formatos para capa de consumo, evitando duplicidad de datos tiempo real/Streaming para detección oportuna de errores.

### Aspectos a Considerar en Cada Paso (si aplica)
*   **Control de errores:** Todos los procesos pueden tener puntos de fallo. De acuerdo con lo identificado en la etapa 1 (diseño), debe implementar los controles de errores correspondientes.
*   **Control de duplicidad de datos:** Considerar que los procesos se pueden ejecutar múltiples veces, y que los datos desde el origen pueden cambiar. Por lo tanto, sus procesos deben determinar qué hacer si una ejecución devuelve datos que ya existen (tome la decisión de acuerdo con lo visto durante el semestre). También debe considerar que parte de estos datos pueden haber sido cargados desde la etapa 2 de datos Batch.
*   **Registro de actividad:** Como los procesos se podrían ejecutar varias veces, debe incorporar el control de ejecución (ej.: ¿Si el proceso ya se ejecutó lo debo volver a ejecutar, lo debo bloquear o debo pedir autorización para volver a ejecutar?).
*   **Validación de Datos y Procesos:** Según corresponda, debe considerar en su construcción la validación de los procesos y la validación de los datos a trabajar, incluyendo procesos de transformación, manteniendo la trazabilidad de los datos desde el origen.

---

## 3. Instrucciones Específicas: Dimensión Presentación
*   Para la presentación, deberán simular una entrega gerencial, evaluada individualmente.
*   Presenta el proceso de ingesta de datos utilizando variedad de APIs disponibles en la industria para implementar procesos de ingesta de datos en línea.
*   Presenta la construcción del proceso, con el fin de realizar limpieza, transformación y almacenamiento de grandes volúmenes de datos en formato real-time/streaming.
*   Presenta la síntesis de la información en un panel de control para demostrar el potencial de la herramienta utilizada.
*   Presenta los resultados siguiendo una estructura lógica, considerando la información del informe.
*   Deberá utilizar un lenguaje técnico propio de la disciplina, además de justificar y responder preguntas sobre cualquier aspecto trabajado.

---

## 4. Detalles Administrativos y Ponderación

### Distribución de Tiempos
*   **Ponderación total:** 35% de la nota final de la asignatura.
*   **Tiempo asignado:** Tres semanas (entrega de instrucciones en la semana 14).
*   **Entrega:** Se entrega el informe el mismo día de la presentación (semana 17).
*   **Defensa / Presentación:** Exposición de 10 minutos, en parejas, realizada en el taller de alto cómputo.

### Tabla de Distribución de Porcentajes
| Evaluación | Porcentaje en la Asignatura | Tipo de Situación Evaluativa | Distribución Interna |
| :--- | :---: | :---: | :---: |
| **Evaluación Parcial N° 3** | **35%** | **Encargo (A)** | **30%** |
| | | **Presentación (B)** | **70%** |
