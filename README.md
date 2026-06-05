# Pipeline de Procesamiento Batch — Grupo Cordillera

Este repositorio contiene los recursos, scripts y especificaciones técnicas para la **Evaluación N° 2** de la asignatura **Big Data (AVY1101)** de Duoc UC. El objetivo principal es implementar un pipeline de procesamiento Batch robusto utilizando Google Cloud Platform (GCP) para el caso de estudio **Grupo Cordillera**.

---

## Arquitectura Híbrida de Solución (Las 5Vs)

La solución implementa una arquitectura que separa claramente el procesamiento histórico y en tiempo real:

* **Volumen:** Procesamiento elástico de más de 1.5 millones de registros utilizando **Google Cloud Storage** y **Google BigQuery** en la **Capa Batch**.
* **Variedad:** Ingesta de datos de transacciones de ventas estructuradas (CSV) y logs de navegación semi-estructurados (JSON).
* **Veracidad:** Calidad de datos por perfilado interactivo en **Cloud Dataprep (Trifacta)** para corregir anomalías monetarias y eliminar registros inválidos.
* **Velocidad:** Pipeline Batch programado para consistencia semanal en el Data Warehouse, integrado con una **Capa Speed** para habilitar procesamiento de baja latencia en predicciones online.
* **Valor:** Generación de un modelo analítico limpio en BigQuery para alimentar un dashboard en **Looker Studio** y soportar la capa operativa de **Vertex AI (MLOps)** (incluyendo pipelines de entrenamiento, registro de modelos, almacén de características o Feature Store y predicciones online/batch).

---

## Estructura del Proyecto

* **`Unidad2/docs/`**: Especificaciones y manuales técnicos.
  * [gsp823_guide.md](file:///home/hector/Escritorio/BigData/Unidad2/docs/gsp823_guide.md): Guía detallada paso a paso para la ejecución del pipeline en GCP y resolución de problemas.
  * [dataprep_rules.md](file:///home/hector/Escritorio/BigData/Unidad2/docs/dataprep_rules.md): Reglas de transformación, calidad de datos, enmascaramiento y esquema final del Data Warehouse.
  * [dashboard_design.md](file:///home/hector/Escritorio/BigData/Unidad2/docs/dashboard_design.md): Guía de diseño del dashboard ejecutivo en Looker Studio.
* **`Unidad2/scripts/`**: Scripts automáticos del pipeline.
  * `generate_dataset.py`: Generador local de datos de prueba sintéticos.
  * `ingest_data.sh`: Script en Bash para la automatización de la carga al Data Lake en GCS.
* **`Unidad2/sql/`**: Sentencias DDL y consultas analíticas.
  * `create_raw_tables.sql`: Script SQL para definir el esquema externo RAW en BigQuery.

---

## Justificación Analítica de Visualizaciones (Looker Studio)

Los 4 gráficos elegidos para el dashboard ejecutivo responden directamente a los objetivos comerciales estratégicos de **Grupo Cordillera**:
1. **Evolución Temporal de Ingresos (Líneas):** Permite a la gerencia identificar tendencias estacionales, el impacto de campañas a lo largo del tiempo y el crecimiento general del negocio de forma intuitiva.
2. **Desempeño por Sucursal (Barras Horizontales):** Visibiliza instantáneamente el ranking comercial (tiendas estrella vs. tiendas con bajo rendimiento) para la toma de decisiones operativas locales.
3. **Participación Omnicanal (Anillo):** Mide la tasa de penetración del canal digital (E-commerce) frente al canal tradicional (Tienda Física), un KPI crítico para validar la estrategia de transformación digital.
4. **Embudo Predictivo Web (Funnel):** Identifica el punto exacto de fuga de los clientes durante la navegación online (desde la vista de producto hasta la compra), permitiendo calcular la tasa de conversión y anticipar la demanda de stock logístico mediante modelos de Vertex AI.

---

## Resumen del Flujo de Ejecución

1. **Generación de Datos:** Ejecución de `generate_dataset.py` para crear los archivos CSV y JSON locales.
2. **Ingesta a GCS:** Ejecución de `ingest_data.sh` para crear el bucket y cargar los archivos a `/raw/` en la región `us-central1`.
3. **Tablas RAW en BigQuery:** Ejecución del DDL para crear las tablas externas en el dataset `grupo_cordillera_raw` apuntando a GCS.
4. **Transformación con Cloud Dataprep:**
   * Limpieza de caracteres sucios en `monto_clp` e imputación de tipos numéricos.
   * Seudonimización consistente de RUTs e IP addresses para cumplir con la **Ley N° 21.719**.
   * Enriquecimiento de fechas (`anio`, `mes`, `dia_semana`).
5. **Carga al DW:** Escritura de los resultados en `grupo_cordillera_dw.fact_ventas` y `grupo_cordillera_dw.fact_sesiones_web` en la región `us-central1`.
6. **Visualización:** Consumo del DW en Looker Studio estructurando un panel de 4 gráficos interactivos y predictivos.
   * **[Dashboard en Producción](https://datastudio.google.com/reporting/0c780fc8-88a6-43a4-8f62-55b5461f6177)**

---

## Gobierno de Datos y Seguridad

* **Seudonimización:** Enmascaramiento irreversible y consistente (`rut_cliente` -> `id_anonimo_cliente`) asegurando que ningún dato personal sensible llegue al Data Warehouse o al Dashboard.
* **Ciclo de Vida en Storage:** Regla de ciclo de vida configurada para migrar automáticamente de clase *Standard* a *Coldline* a los 90 días, y a *Archive* a los 365 días para la retención regulatoria de bajo costo.
---

**Héctor Aguila**

