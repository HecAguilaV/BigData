# Guion de Presentación: Migración Big Data - Grupo Cordillera

Este guion está diseñado para 10 minutos (aprox. 1 minuto por slide). Habla con seguridad, no leas textualmente la presentación, úsala solo como apoyo visual.

---

## Slide 1: Portada
**Guion:** "Buenos días profesor. Hoy presentaré el análisis y la propuesta de transformación digital para Grupo Cordillera, enfocado en resolver sus dolores técnicos y operativos mediante la migración de un BI tradicional hacia una arquitectura de Big Data en Google Cloud."

## Slide 2: El Dolor de Cordillera
**Guion:** "Cordillera ha alcanzado el límite de su infraestructura actual. Con más de 30 sucursales, el 65% de los reportes se consolida manualmente en hojas de cálculo. Tienen silos de información desconectados entre Finanzas y Ventas, lo que genera un desfase de 48 horas en la toma de decisiones gerenciales. Esta propuesta busca resolver dicha brecha de integración y latencia."

## Slide 3: La Oportunidad de las 5V (Justificación)
**Guion:** "¿Por qué Big Data y no simplemente comprar un servidor más grande? Por las 5V. El **Volumen** de 10 años de ventas supera los discos locales. La **Velocidad** que exige el e-commerce hoy requiere respuestas en segundos. Tenemos **Variedad** de datos (SQL y JSON). Al migrar, garantizamos la **Veracidad** de los reportes y entregamos **Valor** al negocio con logística predictiva."

## Slide 4: Alternativas On-Premise
**Guion:** "Evaluamos construir la infraestructura nosotros mismos usando herramientas como Hadoop, Spark o Cassandra. La conclusión fue descartarlo. El CAPEX (costo inicial de servidores) y la falta de equipo técnico hiper-especializado lo hacían inviable y riesgoso."

## Slide 5: La Solución (GCP)
**Guion:** "Por ello, proponemos migrar al ecosistema de Google Cloud Platform (GCP). Operamos 100% con servicios administrados (Serverless). Usaremos Cloud Storage como Data Lake, Pub/Sub para ingestar eventos en vivo, Dataflow para procesarlos y BigQuery como nuestro gran Data Warehouse."

## Slide 6: Gobierno de Datos y Ley
**Guion:** "No podemos llenar un lago de datos sin reglas. Implementamos validaciones automáticas de calidad. Pero lo más importante: alineamos la arquitectura a la Ley 21.719 de Chile. Aplicamos seudonimización para que los analistas vean comportamientos y métricas, pero nunca expongamos directamente los datos personales del cliente, cumpliendo por diseño."

## Slide 7: Ciclo de Vida del Dato
**Guion:** "El viaje del dato será continuo. Desde la **captura** en las cajas y celulares, el **almacenamiento** en bruto en Cloud Storage, su **procesamiento** inteligente en Dataflow, hasta la **explotación** en BigQuery y Looker Studio para los ejecutivos."

## Slide 8: Arquitectura de Referencia (Lambda)
**Guion:** "Para cumplir con los requerimientos, implementamos una Arquitectura Lambda. Esta se divide en dos flujos independientes que luego se unifican en la capa de servicio:
1. La **Capa Speed (Tiempo Real)**: Captura eventos del e-commerce y sucursales en Pub/Sub, los procesa en streaming mediante Dataflow y consume características desde el *Feature Store* de Vertex AI para servir **predicciones online** en tiempo real.
2. La **Capa Batch (Lote)**: Ejecuta flujos nocturnos en Dataflow para consolidar el historial transaccional en BigQuery. El reentrenamiento de modelos se orquesta mediante *Vertex AI Pipelines*, registrando versiones en el *Model Registry*, y ejecutando **predicciones batch** de demanda de stock de forma periódica.
Ambos flujos se unifican en BigQuery para entregar reportes consolidados consistentes."

## Slide 9: Beneficios
**Guion:** "Cordillera gana escabilidad elástica. Si es el CyberDay, los recursos crecen automáticamente, y luego bajan para no pagar de más. Además, se segmenta la seguridad aislando lo contable de lo operativo."

## Slide 10: Conclusión
**Guion:** "En conclusión, este proyecto representa una evolución fundamental para Grupo Cordillera. Proporcionará la infraestructura analítica y la gobernabilidad de datos necesarias para sustentar la toma de decisiones estratégicas en tiempo real y asegurar la competitividad en el sector retail. Muchas gracias, quedo atento a sus preguntas."

---
---

## 🛑 Posibles Preguntas del Profesor y Cómo Responderlas

**1. Profesor: "Mencionas una Arquitectura Lambda, ¿por qué no utilizar una Arquitectura Kappa?"**
*   **Respuesta Ideal:** "La arquitectura Kappa procesa todo como si fuera un streaming en tiempo real. En Cordillera todavía tenemos terminales físicas y 10 años de datos históricos en bases relacionales que se suben de noche (procesos Batch). Lambda nos permite respetar esos procesos nocturnos históricos pesados (Capa Batch) y SUMARLE la capa rápida para el e-commerce (Capa Speed), siendo menos disruptiva para la empresa hoy."

**2. Profesor: "Descartaste Hadoop alegando que es On-Premise, pero ¿no puedo instalar Hadoop en máquinas virtuales en la nube?"**
*   **Respuesta Ideal:** "Sí, es correcto, se puede correr en IaaS (Infraestructura como Servicio) usando VMs en Cloud. Sin embargo, el problema del mantenimiento se mantiene: habría que actualizar nodos, lidiar con caídas del NameNode, etc. Al irnos directo por servicios tipo 'SaaS/PaaS' como BigQuery o Cloud Storage, Google nos administra todo eso y el equipo de Cordillera solo se preocupa de meter y sacar datos."

**3. Profesor: "¿Cómo vas a optimizar costos para 10 años de historial que ya no se consulta todos los días?"**
*   **Respuesta Ideal:** "Para eso dentro del ciclo de vida del dato aplicamos políticas de **Archivado**. En Google Cloud Storage configuraremos reglas para que todo historial mayor a 6 meses o 1 año sea movido automáticamente a las clases **Coldline** o **Archive**. Esto reduce drásticamente el costo por gigabyte, y los datos siguen estando disponibles por si hay alguna auditoría legal."

**4. Profesor: "Hablas de la Ley 21.719 en tu Gobierno de Datos, ¿qué técnica en específico usas en tu arquitectura para cumplirla?"**
*   **Respuesta Ideal:** "Usamos **seudonimización** en la etapa de transformación. Cuando *Dataflow* lee el evento de Pub/Sub, toma el Rut y el nombre del cliente y los enmascara o les asigna un ID único. Así, la información que se guarda en *BigQuery* permite saber que 'el Usuario HZ-99 compró 3 camisas', perfilando ventas regionales, sin necesidad de exponer su identidad real a los analistas."

**5. Profesor: "¿Por qué no incluiste herramientas de linaje de datos avanzado como Apache Atlas que vimos en clase?"**
*   **Respuesta Ideal:** "Principalmente para evitar el sobrediseño en esta etapa inicial. Antes de levantar un motor complejo de metadatos externo, queremos estabilizar el flujo básico. Durante esta fase 1, la trazabilidad la cubriremos directamente con los logs nativos de Google Cloud, y Apache Atlas quedaría como una mejora propuesta para una fase 2."

**6. Profesor: "¿Cómo encaja Vertex AI y su capa operativa en la arquitectura Lambda propuesta?"**
*   **Respuesta Ideal:** "Vertex AI opera de forma híbrida e integrada en nuestra arquitectura Lambda. Su **capa operativa (MLOps)** gestiona todo el ciclo de vida: los flujos de reentrenamiento y evaluación automática se orquestan con *Vertex AI Pipelines*, los artefactos se versionan en *Model Registry*, y el *Feature Store* sirve características unificadas con baja latencia. Para la *Capa Speed*, consumimos características del Feature Store para servir **predicciones online** en tiempo real mediante endpoints en línea. Para la *Capa Batch*, ejecutamos **predicciones batch** nocturnas de demanda de stock para actualizar los reportes de inventario de forma consistente."
