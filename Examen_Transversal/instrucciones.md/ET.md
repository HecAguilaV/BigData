<div align="justify">

# EXAMEN TRANSVERSAL — TALLER DE ALTO CÓMPUTO

## PROYECTO INTEGRAL DE BIG DATA (EXAMEN FINAL)

La evaluación consiste en el trabajo en un encargo con presentación que se realiza en el Taller de Alto Cómputo. A partir del caso semestral y las evaluaciones parciales, los/las estudiantes deben presentar el proyecto completo de encargo, enfatizando aspectos de un proyecto de Big Data como arquitectura propuesta, ingesta de datos de diversas fuentes, procesamiento batch, procesamiento streaming, carga en una base de datos y generación de un panel de control.

Esta evaluación consiste en una situación evaluativa de entrega de encargo con presentación que medirá los siguientes **Indicadores de Logro**:

* **IL1.1:** Reconoce qué es Big Data y el contexto de las organizaciones donde se aplica.
* **IL1.2:** Identifica herramientas dentro del ámbito de Big Data y su contexto de aplicación.
* **IL1.3:** Identifica principales prácticas de gobierno de datos y ciclo de vida del dato, de acuerdo con requerimientos.
* **IL1.4:** Analiza arquitecturas disponibles de Big Data para resolver los requerimientos de la industria.
* **IL2.1:** Construye procesos de carga de datos Batch en diferentes formatos y desde diversas fuentes.
* **IL2.3:** Construye procesos de limpieza, transformación y almacenamiento de grandes volúmenes de datos.
* **IL3.2:** Construye procesos, con el fin de realizar limpieza, transformación y almacenamiento de grandes volúmenes de datos en tiempo real/streaming.
* **IL3.3:** Sintetiza la información en un panel de control usado como insumo para tomar decisiones.

---

## INSTRUCCIONES ESPECÍFICAS DE LA EVALUACIÓN

### A) PROCESO BATCH: Datos de Taxis de New York

El transporte público es esencial para la movilidad urbana. Por ello, es crucial conocer los trayectos, paradas, horarios y duración de los viajes para planificar adecuadamente los desplazamientos.

Este examen busca generar una plataforma de datos que contenga la información histórica de los viajes de los taxis de New York, de tal forma de identificar los taxis disponibles, ver qué horarios tienen mayor disponibilidad en una zona determinada, y las tarifas cobradas entre un punto y otro de la ciudad.

* **Sitio Oficial:** https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page
* **Sitio Alternativo:** El primer parámetro de la dirección corresponde al mes, luego al año. Existe información para descargar desde enero de 2022 hasta abril de 2024: https://bdbatchescuelait.duoc.cl/01/2022
* *Además, el/la docente puede entregar un repositorio de datos diferente, según su criterio.*

### B) PROCESO STREAMING: Fluctuación de Precios de Componentes Electrónicos

Para este proceso se simula la subasta de distintos componentes electrónicos, cuyo precio varía constantemente. Para esta instancia, estos datos deben utilizarse para simular las fluctuaciones de precios de dichos componentes.

Al ingresar, si no tienes un correo registrado puedes solicitar un acceso en "Obtener Contraseña", te llegará un correo con una clave de acceso. Al ingresar, te permite registrar una URL de destino para la simulación: https://bdrealtimeescuelait.duoc.cl

* *Además, el/la docente puede entregar un repositorio de datos diferente, según su criterio.*

---

## ESTRUCTURA DEL ENCARGO (INFORME)

El informe (encargo) debe incluir los siguientes apartados:

1. **Justificación de la solución Big Data** aplicada al problema planteado, destacando cuáles son las características del problema por lo cual es apropiado usar una solución de Big Data y no otro tipo de solución.
2. **Selección y justificación de la arquitectura**, desde el punto de vista técnico y funcional, incorporando prácticas de gobierno de datos y ciclo de vida del dato, de acuerdo con los requerimientos.
3. **Definir los procesos, flujos de información y orquestación de datos** para dar inicio a la construcción de la solución, tanto batch como streaming.
4. **Conexiones con las fuentes de datos**, tanto para procesos batch como streaming.
5. **Generación de archivos en el data lake** según corresponda.
6. **Procesos de limpieza, transformación y carga** al modelo de datos final según corresponda.
7. **Reportes y/o visualizaciones** correspondientes en un panel o dashboard interactivo (del cual debe incluir imágenes en el informe respectivo).

---

## REQUISITOS TÉCNICOS ADICIONALES (ANEXO)

La construcción del proyecto total debe considerar los siguientes aspectos, los cuales deben incluirse en un anexo del informe:

* **a. Control de errores:** Todos los procesos pueden tener puntos de fallo. De acuerdo con lo identificado en la Etapa 1 (diseño), debe implementar los controles de errores correspondientes.
* **b. Control de duplicidad de datos:** Considerar que los procesos se pueden ejecutar múltiples veces, y que los datos desde el origen pueden cambiar. Por tanto, sus procesos deben determinar qué hacer si una ejecución devuelve datos que ya existen.
* **c. Registro de actividad:** Los procesos se podrían ejecutar varias veces, por lo que debe incorporar el control de ejecución y el ciclo de vida de los datos.
* **d. Validación de Datos y Procesos:** Según corresponda, debe considerar en su construcción la validación de los procesos y la validación de los datos a trabajar, incluyendo procesos de transformación, manteniendo la trazabilidad de los datos desde el origen. Debe considerar métricas de calidad adecuadas a completar en el informe (por ejemplo: cantidad de registros leídos vs cargados, cantidad de nulos, etc.).

---

## DEFENSA (PRESENTACIÓN ORAL)

La defensa (presentación) debe incluir los siguientes apartados:

1. Contexto
2. Arquitectura (diagrama)
3. Herramientas utilizadas
4. Descripción de procesos batch y streaming
5. Descripción de la estructura del repositorio final
6. Demostración de reportes / panel de control orientado al usuario final

*Aunque esta evaluación se desarrolla en duplas, la calificación es de carácter individual y responde al desempeño particular de cada integrante.*

---

## ASPECTOS FORMALES

### Aspectos formales del informe escrito:

* **Entrega:** Subir informe escrito a la plataforma AVA.
* **Formato:** Archivo `.pdf` con un máximo de 10 páginas, utilizando fuentes Arial o Calibri, tamaño de 10 a 12.
* **Estructura básica obligatoria:**
  * Portada con detalle de sección, nombre y RUT de los integrantes.
  * Introducción.
  * Índice.
  * Desarrollo (todos los apartados del encargo descritos arriba).
* *Los trabajos entregados fuera de plazo serán calificados con nota 1.0.*

### Aspectos formales de la presentación / defensa:

* Se recomienda la utilización de plantillas interactivas, en las cuales se priorice la organización de la información en diagramas, flujos de procesos y tablas consolidadas.
* **Entregables:** La PPT o recursos visuales no deben exceder las 10 láminas y deben entregarse con 48 horas de anticipación a la fecha de la presentación.
* **Tiempos:** Los/las estudiantes tienen un tiempo máximo de 15 minutos para presentar sus resultados (10 minutos de presentación de la dupla y 5 minutos de consultas del docente).
* **Diapositivas:** Las láminas deben ser formales (se recomienda seguir el formato PowerPoint institucional, con correcta ortografía, colores adecuados y contenido sintetizado).
* **Distribución de roles:** El tiempo de habla y el trabajo debe distribuirse de manera equivalente entre los integrantes del equipo.
* **Consultas:** Las preguntas de la defensa pueden ser dirigidas de manera individual a cualquier integrante del equipo.

</div>
