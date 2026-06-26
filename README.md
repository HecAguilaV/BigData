# Procesamiento de Datos en Tiempo Real (Streaming) — Grupo Cordillera

Este repositorio y rama (`Ev3_Streaming`) contienen el diseño y los futuros desarrollos técnicos de la **Capa Speed** para la **Evaluación Parcial N° 3** de la asignatura **Big Data (AVY1101)** en Duoc UC.

---

## Adelanto del Proyecto: Arquitectura Streaming (Capa Speed)

Para solucionar el problema estratégico del **Grupo Cordillera** referente a la inmediatez de la información ("ver la venta y el comportamiento web mientras ocurre"), implementaremos un flujo de datos en tiempo real (Streaming) sobre **Google Cloud Platform (GCP)** que complementará el pipeline Batch de la Unidad 2 bajo un diseño de **Arquitectura Lambda**.

### Flujo Técnico Propuesto:
1. **Producer (Cliente Ingesta):** Script local en Python que leerá los logs históricos y simulará la generación de eventos en tiempo real enviándolos continuamente.
2. **Bus de Ingesta (Google Cloud Pub/Sub):** Captura masiva de eventos de navegación web (JSON) de forma segura y elástica.
3. **Pipeline de Procesamiento (Google Cloud Dataflow):** Ejecución de un pipeline serverless con **Apache Beam** para realizar la limpieza de datos, control de duplicados en caliente, validación lógica y seudonimización de datos sensibles en cumplimiento con la **Ley N° 21.719**.
4. **Capa de Destino (Google BigQuery):** Almacenamiento continuo en el Data Warehouse para disponibilidad inmediata de consultas analíticas.
5. **Visualización Unificada (Looker Studio):** Dashboard ejecutivo interactivo que combinará métricas históricas (Batch) con telemetría en tiempo real (Streaming).

---

## Estado de la Rama
> [!NOTE]
> **En Desarrollo:** Esta rama se encuentra en fase inicial de diseño. Actualmente, los componentes técnicos locales están configurados localmente y se irán confirmando a lo largo del sprint de desarrollo.

---
**Integrantes:** Héctor Águila V.  
**Asignatura:** Big Data (AVY1101) - Duoc UC
