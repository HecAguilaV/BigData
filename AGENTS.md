# Reglas de Revisión de Documentación — BigData

Estas reglas definen los estándares de calidad y contenido para los informes técnicos del proyecto de Big Data de Grupo Cordillera.

## 1. Terminología Técnica y Formalidad
- Mantener un lenguaje formal, técnico y alineado con la disciplina de Big Data.
- Evitar generalidades o lenguaje promocional (seguir principios de objetividad).

## 2. Justificación de Tecnologías (Las 5Vs)
- Cualquier propuesta de almacenamiento o procesamiento masivo debe estar debidamente justificada mediante al menos uno de los pilares de las 5V (Volumen, Velocidad, Variedad, Veracidad, Valor).

## 3. Arquitectura y MLOps
- Toda arquitectura analítica híbrida o Lambda debe detallar la separación clara de la **Capa Batch** y la **Capa Speed**.
- Cuando se mencione Inteligencia Artificial o analítica avanzada, se debe especificar la **capa operativa de Vertex AI (MLOps)** (pipelines de entrenamiento, registro de modelos, almacén de características o Feature Store y predicciones online/batch).

## 4. Gobierno de Datos, Privacidad y Cumplimiento
- Las propuestas deben alinearse explícitamente con la **Ley N° 21.719** de Protección de Datos de Chile.
- Describir técnicas específicas de protección como la **seudonimización** en la etapa de transformación.
- Definir políticas de archivado automático a bajo costo (ej. clases Coldline o Archive en Cloud Storage) para datos de retención regulatoria histórica.
