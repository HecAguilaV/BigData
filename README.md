# Proyecto Integral de Big Data — Grupo Cordillera

Este repositorio contiene el desarrollo completo del proyecto de Big Data para la empresa **Grupo Cordillera**, realizado para la asignatura de Big Data (AVY1101) en Duoc UC.

El proyecto implementa una **Arquitectura Lambda** híbrida sobre Google Cloud Platform (GCP) para el procesamiento, limpieza, almacenamiento y visualización de datos de ventas (Capa Batch), telemetría web en tiempo real (Capa Speed) y sensores de ocupación de locales físicos (Capa IoT), complementado con analítica avanzada mediante Machine Learning (LightGBM).

---

## Estructura del Repositorio y Ramas

El repositorio está organizado por ramas para separar cada una de las evaluaciones del semestre, manteniendo la rama principal (`main`) como el centro del informe consolidado final.

### [Rama Principal (`main`)](https://github.com/HecAguilaV/BigData/tree/main)

Contiene la consolidación final del proyecto (Examen Transversal). Es la rama de entrega formal del Examen Final.

* **Directorio principal:** `Examen_Transversal/`
  * [Informe Final Consolidado (Markdown)](Examen_Transversal/Informe_Examen_Transversal.md)
  * [Informe Final Consolidado (PDF)](Examen_Transversal/Informe_Examen_Transversal.pdf)
  * [Guía Técnica de Evidencias (Markdown)](Examen_Transversal/evidencias/documentos/Evidencias.md)
  * Directorio de imágenes y capturas de pantalla de infraestructura en GCP y dashboards: `Examen_Transversal/evidencias/img/`

### [Rama Evaluación 1 (`Ev1_PropuestaBigData`)](https://github.com/HecAguilaV/BigData/tree/Ev1_PropuestaBigData)

Contiene el diseño inicial, la propuesta de negocio y la justificación tecnológica de la migración analítica a la nube.

* **Directorio principal:** `Unidad1/`
  * Propuesta de arquitectura y justificación de las 5Vs.
  * Presentación ejecutiva del proyecto.

### [Rama Evaluación 2 (`Ev2_Pipeline_Batch`)](https://github.com/HecAguilaV/BigData/tree/Ev2_Pipeline_Batch)

Contiene la construcción del pipeline Batch para el procesamiento de 1.2 millones de ventas históricas.

* **Directorio principal:** `Unidad2/`
  * Script de ingesta batch a Cloud Storage (`ingest_data.sh`).
  * Reglas de calidad y recetas en Cloud Dataprep.
  * Modelo lógico de base de datos en BigQuery.

### [Rama Evaluación 3 (`Ev3_Streaming`)](https://github.com/HecAguilaV/BigData/tree/Ev3_Streaming)

Contiene el desarrollo de la Capa Speed (Streaming en tiempo real) y el sensorizado IoT de aforo.

* **Directorio principal:** `Unidad3/`
  * Simuladores de eventos en Python (Producers de navegación y aforo).
  * Consumidores Pub/Sub asíncronos con micro-batching.
  * Cuaderno de entrenamiento de Machine Learning (LightGBM) para pronóstico de ventas.
  * Código fuente del frontend en React + Vite y backend en FastAPI.

---

## Resumen de Tecnologías Utilizadas

* **Cloud Ingest & Messaging:** Google Cloud Storage (Data Lake), Google Cloud Pub/Sub.
* **Data Processing & ETL:** Cloud Dataprep (Apache Beam en Cloud Dataflow).
* **Data Warehouse:** Google Cloud BigQuery.
* **Machine Learning & MLOps:** LightGBM, Vertex AI (Model Registry, Pipelines).
* **Servicios de Visualización:** Streamlit, FastAPI, React + Vite + TypeScript (Tailwind CSS, Leaflet Maps, Recharts).
