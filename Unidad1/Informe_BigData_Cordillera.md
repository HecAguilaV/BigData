# Informe de Evaluación Parcial 1: Migración a Arquitectura Big Data

**Empresa:** Grupo Cordillera
**Asignatura:** Big Data (AVY1101)
**Estudiante:** [Tu Nombre]
**Fecha:** 10 de Abril de 2026

---

## 1. Contexto Estratégico y Problemática Actual

Grupo Cordillera, empresa de retail nacional con 650 empleados y más de 30 sucursales, alcanzó el límite técnico y operativo de su infraestructura tradicional. Actualmente, la organización presenta una ineficiencia en sus procesos operativos: un 65% de los reportes gerenciales se consolidan manualmente mediante hojas de cálculo, generando un desfase de información semanal.

A nivel de entorno, la empresa enfrenta un mercado omnicanal competitivo y la inminente exigencia de la **Ley N° 21.719** de Protección de Datos en Chile. El sistema actual opera en silos (bases de datos relacionales inconexas entre Finanzas y Ventas). Intentar resolver esto con herramientas de Business Intelligence (BI) clásico ya falló; los sistemas de bases de datos relacionales tradicionales carecen de la arquitectura de procesamiento distribuido y la capacidad de ingesta continua necesarias para integrar en tiempo real los eventos de las sucursales físicas con el tráfico del e-commerce. La necesidad de contar con datos consolidados orienta el proyecto hacia una infraestructura de Big Data basada en servicios administrados.

### 1.1 Objetivos Técnicos a Cumplir

Para resolver esta fricción operativa, el proyecto define los siguientes objetivos técnicos:

1. **Desacoplar la infraestructura:** Separar la lectura analítica de la carga transaccional para evitar caídas en el e-commerce y cajas físicas.
2. **Procesamiento de baja latencia:** Analizar el comportamiento del usuario web en tiempo real (bajo 5 segundos) para ejecutar acciones logísticas y de marketing en el momento.
3. **Unificación de silos (Single Source of Truth):** Centralizar la información estructurada (bases SQL) y semi-estructurada (JSON web) en un único Data Warehouse corporativo.
4. **Cumplimiento y retención de bajo costo:** Implementar políticas de archivado automático que cumplan con los requerimientos legales sin inflar el presupuesto de infraestructura.

---

## 2. Parte 1: Justificación del paso a Big Data (Aplicación de las 5V)

Instalar Big Data es una inversión mayor, pero en el Grupo Cordillera, retener la infraestructura actual es matemáticamente inviable para la continuidad comercial. La urgencia se sostiene técnicamente bajo los parámetros de las 5V:

1. **Volumen:** Cordillera almacena el historial de ventas físicas a lo largo de una década. Sumado a miles de sesiones de usuarios online diarias, el total de la información satura invariablemente discos y memorias locales.
2. **Velocidad:** En fechas críticas, ventas requiere detectar comportamientos por debajo de los 5 segundos para sugerir promociones mientras el usuario todavía navega. Los procesos ETL de carga nocturna son irrelevantes en este escenario.
3. **Variedad:** Históricamente la empresa cruzaba filas y columnas estructurales. Hoy, Operaciones exige asimilar el comportamiento web (archivos JSON semi-estructurados) que las bases SQL rechazan.
4. **Veracidad:** El reporte humano es fuente fundamental de errores operativos en Cordillera (afectando al 65% de la carga actual). Centralizar la ingesta en Big Data garantiza un filtro sin intervención, limpiando registros corruptos de inmediato.
5. **Valor:** El resultado tangible no es poseer mucha información, sino la ejecución logística. Predecir que el volumen web agota el stock de una categoría y mover camionetas durante esa misma jornada detiene la pérdida financiera mensual.

---

## 3. Parte 2: Selección de Herramientas Analíticas

El diseño de la solución contrasta el costo de adquirir infraestructura física tradicional contra ecosistemas en la nube.

### 3.1. Evaluación del Ecosistema On-Premise (Descartado)

Si el Grupo Cordillera desarrollara un centro de datos propio, la pila requerida sería operativa pero rígida económicamente:

* **Hadoop (HDFS):** Actúa como disco duro distribuido. Soluciona el almacenamiento masivo económico inicial.
* **Apache Spark:** Analizador en memoria que podría calcular las ventas de las 30 sucursales nacionales en segundos de procesamiento sin acceder permanentemente a discos.
* **Apache Cassandra:** Base NoSQL columnar de alta disponibilidad que operaría ininterrumpidamente para sostener las peticiones del sitio e-commerce.
* **MongoDB:** Útil para mantener catálogos flexibles y semi estructurados con diversas cantidades asimétricas de atributos para diferentes artículos.

**Justificación del Descarte:** Levantar los cuartos físicos, la mantenibilidad técnica y las licencias anulan el presupuesto operativo. Es un proyecto de altísima fricción estructural.

### 3.2. Selección Oficial: Ecosistema Google Cloud Platform (GCP)

Alineado con el crecimiento sostenible de la industria, Cordillera migrará su carga a los servicios administrados de **Google Cloud Platform (GCP)**.

* Utilizaremos **Google Cloud Storage (GCS)** como repositorio central del Data Lake. Funciona como un almacenamiento de objetos distribuido, altamente escalable y de menor costo operativo en comparación con la administración de nodos locales de HDFS.
* La latencia en la ingesta se reduce al conectar los flujos de eventos directamente a **Google Cloud Pub/Sub**, el cual actúa como un bus de mensajería asíncrono y escalable para la distribución de mensajes en tiempo real.
* El procesamiento a gran escala será ejecutado por **Google Cloud Dataflow**, estructurando y unificando los datos para su carga en **BigQuery**, el almacén de datos analítico que servirá de soporte para los reportes gerenciales.
* La analítica avanzada e inteligencia artificial se implementarán con **Vertex AI**. Su **capa operativa (MLOps)** automatizará el ciclo de vida de los modelos de Machine Learning. Esto incluye la orquestación de flujos de entrenamiento mediante *Vertex AI Pipelines*, el control de versiones a través de *Model Registry*, el almacenamiento y servicio de características de baja latencia con *Feature Store*, y la ejecución de **predicciones en tiempo real (online)** para la personalización de ofertas y **predicciones por lotes (batch)** para la planificación logística de inventarios.

---

## 4. Parte 3: Normativa, Gobierno y Ciclo de Vida del Dato

Para asegurar la gobernabilidad del Data Lake, se implementará un marco estructurado de gobierno de datos:

### 4.1. Prácticas Estratégicas de Gobierno de Datos

* **Gestión de Calidad del Dato:** Todo ingreso es evaluado preventivamente. Si una carga desde los terminales remotos arroja fechas inconsistentes o monedas distintas al peso chileno, el orquestador detiene esa ingesta individual, evitando que corrompa la estadística gerencial, subsanando la falta de confianza mostrada por los mandos directivos previos.
* **Privacidad Institucional y Legal:** Respondiendo incondicionalmente a la **Ley 21.719** de Chile enfocada a las bases e-commerce, todo historial es procesado mediante técnicas de seudonimato automático en los conductos de Google Cloud. El ejecutivo visualiza el comportamiento regional anónimo protegiendo los datos originarios completos al extremo.

### 4.2. Ciclo de Vida Analítico (Trazabilidad End-to-End)

Se estandarizó el pipeline de datos corporativo mediante un flujo de procesamiento end-to-end:

1. **Ingesta (Captura):** Extracción programada desde sistemas legados mediante cargas por lotes (Batch), y captura en tiempo real del flujo de datos del comercio electrónico a través de Pub/Sub.
2. **Almacenamiento Segmentado:** El *Data Lake* almacena los datos en su formato original (raw data) dentro de zonas de acceso restringido para garantizar su integridad.
3. **Procesamiento:** El motor de procesamiento distribuido *Google Cloud Dataflow* normaliza los datos, aplicando las transformaciones necesarias y cruzando las métricas operativas antes de cargarlos en el almacén de datos analítico BigQuery.
4. **Archivado (Ciclo de Vida):** Los datos históricos con baja frecuencia de consulta son transferidos automáticamente a clases de almacenamiento de menor costo (Coldline o Archive en Cloud Storage) mediante políticas de ciclo de vida del dato, optimizando costos y asegurando el cumplimiento regulatorio de retención histórica.

---

## 5. Parte 4: Análisis Funcional de Arquitectura de Referencia (Lambda)

El CEO exigía visión transversal: una analista necesita historial del año anterior absolutamente corroborable y el gerente de turno exige alertas instantáneas ante los quiebres del e-commerce. La solución lógica es adoptar un patrón matriz de **Arquitectura Lambda** construida de cara a este ecosistema dual:

![alt text](Arquitectura BigData.png)

### Análisis Crítico:

1. **Escalabilidad nativa:** La implementación de la arquitectura Lambda mediante servicios administrados en GCP permite el aprovisionamiento dinámico y el autoescalado de recursos. Durante eventos de alta demanda, los servicios escalan automáticamente para absorber la carga y se contraen posteriormente, optimizando el costo operativo.
2. **Seguridad Diferenciada:** La separación de capas en la arquitectura Lambda permite implementar políticas de control de acceso (IAM) diferenciadas. El pipeline de procesamiento Batch opera de forma aislada de la capa de velocidad, limitando la superficie de exposición y garantizando que un incidente de seguridad en el canal web no comprometa la integridad de los datos históricos.
3. **Garantía de Consistencia (Calidad):** Las posibles inconsistencias de datos que puedan surgir en el procesamiento de flujo rápido (Capa Speed) son corregidas y consolidadas periódicamente por el pipeline Batch nocturno, asegurando la consistencia final de los datos históricos de Grupo Cordillera.
4. **Eficiencia y Optimización:** La separación de las rutas de procesamiento reduce el tiempo de respuesta analítico. Los usuarios de negocio pueden consultar vistas unificadas que combinan datos históricos y en tiempo real en milisegundos, eliminando los retrasos asociados a la extracción manual de múltiples sistemas.
5. **Operacionalización de Modelos Inteligentes (MLOps):** La integración de la capa operativa de **Vertex AI** se acopla a la arquitectura Lambda: la *Capa Speed* consume predicciones inmediatas de baja latencia mediante endpoints en línea (ej. predicciones online de recomendaciones personalizadas en segundos), mientras que la *Capa Batch* ejecuta predicciones masivas diferidas (predicciones batch de stock) para planificar la distribución logística del día siguiente.

### 5.1 Elementos No Requeridos en esta Fase Inicial

Para mantener la eficiencia y evitar el **sobrediseño**, esta arquitectura se depuró de los siguientes elementos:

* **Orquestadores externos pesados (ej. Apache Airflow / Cloud Composer):** No son requeridos aún, ya que los procesos actuales pueden ser gatillados directamente por las funciones integradas de GCP (Pub/Sub hacia Dataflow).
* **Capas de Caché en memoria (ej. Redis / Memorystore):** BigQuery cuenta con su propia caché interna administrada, por lo que agregar una capa de Redis exclusiva para servir tableros de BI resulta redundante y costoso para la carga actual de ejecutivos.
* **Herramientas complejas de Linaje (ej. Apache Atlas):** Por ahora, la trazabilidad se manejará nativamente con los logs de auditoría de Google Cloud en lugar de levantar un motor de metadatos externo.

---

## 6. Conclusión

La migración de Grupo Cordillera hacia una arquitectura Big Data en la nube (GCP) no es una simple actualización tecnológica, sino una necesidad de supervivencia comercial. Las herramientas tradicionales *on-premise* demostraron ser insuficientes para manejar el **Volumen** y la **Velocidad** requeridos por las operaciones modernas, como el comercio electrónico y eventos de alta demanda.

Adoptar una **Arquitectura Lambda** permite satisfacer dos necesidades que antes parecían incompatibles: la inmediatez operativa (Capa Speed) y la certeza matemática del reporte histórico (Capa Batch). Sumado a una estrategia de **Gobierno de Datos** respetuosa de la Ley 21.719, la empresa no solo resolverá su dolor gerencial actual, sino que establecerá una base escalable, segura y financieramente optimizada para el futuro.
