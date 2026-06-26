# Propuesta de Migración a Arquitectura Big Data - Grupo Cordillera

Este repositorio contiene los recursos estratégicos y de arquitectura presentados para la **Evaluación Parcial N° 1** de la asignatura **Big Data (AVY1101)** en Duoc UC. El proyecto detalla el diseño de migración digital del **Grupo Cordillera** a un ecosistema de Big Data en la nube.

---

## Contexto Estratégico y Problemática

**Grupo Cordillera**, un gigante del retail chileno con más de 30 sucursales y 650 empleados, ha llegado al límite lógico de su infraestructura tradicional:
* **Fricción Operativa:** El 65% de los reportes gerenciales se consolidan de forma manual en hojas de cálculo, generando retrasos de información semanales o mensuales.
* **Silos de Información:** Las bases de datos de Finanzas, Operaciones y Recursos Humanos se encuentran totalmente desconectadas.
* **Falta de Inmediatez:** Los motores SQL clásicos no soportan la integración en tiempo real entre el tráfico del e-commerce y las tiendas físicas.
* **Cumplimiento Legal:** Necesidad inminente de adaptarse a la **Ley N° 21.719** de Protección de Datos Personales en Chile.

---

## Justificación del Proyecto (Las 5Vs de Big Data)

1. **Volumen:** Historial de ventas físicas de una década sumado a las sesiones de navegación online diarias que saturan los discos locales.
2. **Velocidad:** Necesidad de procesar el comportamiento web en menos de 5 segundos para reaccionar ante quiebres de stock o sugerir promociones.
3. **Variedad:** Fusión de datos altamente estructurados (ventas SQL) con semi-estructurados (logs de navegación JSON).
4. **Veracidad:** Reducción de la tasa de error manual (65% actual) mediante filtros de ingesta automatizados sin intervención humana.
5. **Valor:** Predicción del agotamiento de stock mediante analítica avanzada para evitar pérdidas comerciales mensuales.

---

## Arquitectura de Referencia Propuesta (Ecosistema GCP)

Se propone la adopción de una **Arquitectura Lambda** híbrida montada sobre Google Cloud Platform:
* **Capa Batch (Histórico):** Carga masiva de transacciones históricas hacia **Google Cloud Storage** (Data Lake) y procesamiento mediante **Cloud Dataproc** (Apache Spark/Hadoop).
* **Capa Speed (Tiempo Real):** Captura continua de eventos web usando **Google Cloud Pub/Sub** y transformación con **Google Cloud Dataflow** (Apache Beam).
* **Capa de Servicio:** Almacenamiento unificado en **Google BigQuery** (Data Warehouse) y visualización ejecutiva en **Looker Studio**.

---

## Gobierno de Datos, Seguridad y Cumplimiento

* **Seudonimización:** Enmascaramiento irreversible y consistente de RUTs y direcciones IP en el pipeline de ingesta para cumplir rigurosamente con la **Ley N° 21.719**.
* **Ciclo de Vida de los Datos:** Políticas de retención regulatoria de bajo costo moviendo datos históricos inactivos automáticamente a las clases **Coldline** y **Archive** de Cloud Storage.

---

## Recursos Disponibles en esta Rama (Ev1)

* [Informe Propuesta Big Data.pdf](file:///Users/user/Desktop/BigData/Unidad1/Informe%20Propuesta%20Big%20Data.pdf): Documento formal detallado de la propuesta de migración y gobierno de datos.
* [Transformación Digital_ Migración a Big Data en GCP para Grupo Cordillera.pptx](file:///Users/user/Desktop/BigData/Unidad1/Transformaci%C3%B3n%20Digital_%20Migraci%C3%B3n%20a%20Big%20Data%20en%20GCP%20para%20Grupo%20Cordillera.pptx): Presentación ejecutiva orientada a la alta gerencia (CEO/CFO).

---
**Integrantes:** Héctor Águila V.  
**Asignatura:** Big Data (AVY1101) - Duoc UC
