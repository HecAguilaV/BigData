# Especificación de Transformación y Calidad de Datos en Cloud Dataprep (Trifacta)

Este documento detalla la receta de transformación y las reglas de calidad que se deben implementar en **Cloud Dataprep** para procesar los datos crudos de **Grupo Cordillera** y cargarlos de forma limpia en el Data Warehouse de **BigQuery**.

## Justificación de Tecnologías (Las 5Vs)

La implementación de **Cloud Dataprep (Trifacta)** y **BigQuery** se justifica bajo los siguientes pilares de las 5Vs de Big Data:

* **Veracidad:** Cloud Dataprep permite perfilado de datos interactivo y la aplicación de reglas de calidad automatizadas para corregir formatos inconsistentes (por ejemplo, en `monto_clp`) y eliminar registros nulos o erróneos en las transacciones antes de cargarlas.
* **Variedad:** La combinación de orígenes de datos de transacciones de ventas estructuradas (`ventas_historicas`) y registros de comportamiento de navegación web semi-estructurados en JSON (`sesiones_web`) es gestionada eficientemente por Cloud Dataprep mediante normalización y parseo de tipos de datos.
* **Volumen:** BigQuery proporciona almacenamiento masivo elástico y capacidad de cómputo a gran escala capaz de responder consultas complejas sobre millones de filas sin degradación de rendimiento.
* **Velocidad:** El procesamiento batch y la orquestación en la nube garantizan la disponibilidad de los datos en BigQuery de forma oportuna para la toma de decisiones estratégicas.
* **Valor:** La limpieza y transformación de los datos crudos genera datos confiables (*trusted data*) que alimentan las capas analítica y predictiva del pipeline.

## Arquitectura Híbrida (Capa Batch y Capa Speed)

Las recetas de transformación documentadas en este archivo corresponden a la **Capa Batch** de la arquitectura híbrida:

* **Capa Batch:** Procesamiento periódico de datos históricos de ventas y sesiones web mediante Cloud Dataprep, con destino al Data Warehouse en BigQuery (`grupo_cordillera_dw`) para reportes ejecutivos semanales.
* **Capa Speed:** Procesamiento en tiempo real de eventos de navegación web mediante Pub/Sub y Cloud Dataflow para decisiones operativas instantáneas (ofertas personalizadas, detección de abandono).

### Capa Operativa de Vertex AI (MLOps)

Para operacionalizar la analítica predictiva sobre los datos transformados por estas recetas, se define la siguiente capa MLOps:

1. *Vertex AI Pipelines:* Automatiza el reentrenamiento de modelos predictivos de conversión a partir de los datos limpios en `grupo_cordillera_dw`.
2. *Vertex AI Model Registry:* Registra y versiona los modelos entrenados para control de producción.
3. *Vertex AI Feature Store:* Centraliza atributos de comportamiento de clientes con latencia sub-segundo.
4. *Vertex AI Prediction:* Sirve predicciones online (Capa Speed) y batch (reportes semanales) para las visualizaciones en Looker Studio.

---

## 1. Pipeline de Ventas Históricas (`ventas_historicas_recipe`)

Esta receta toma la tabla externa cruda `grupo_cordillera_raw.ventas_historicas` en BigQuery, aplica las reglas de limpieza y seudonimización, y escribe el resultado en `grupo_cordillera_dw.fact_ventas`.

### Paso 1.1: Limpieza del Formato de Moneda (`monto_clp`)

* **Problema:** Un 1% de las transacciones tiene el monto en formato sucio (ej: `$450,000` en lugar de `450000`), lo que impide clasificarlo como tipo numérico.
* **Regla Dataprep:**
  1. Reemplazar el símbolo `$` por vacío: `replace text: '$' with: '' on: monto_clp`
  2. Eliminar las comas del formato de miles: `replace text: ',' with: '' on: monto_clp`
  3. Convertir a tipo de dato entero: `settype col: monto_clp type: Integer`

### Paso 1.2: Normalización del Formato de Fecha (`fecha`)

* **Problema:** Los datos de fecha vienen como cadenas de texto en formato `YYYY-MM-DD HH:MM:SS`.
* **Regla Dataprep:**
  1. Convertir la columna `fecha` a tipo fecha y hora (Datetime) utilizando el formato ISO: `settype col: fecha type: Datetime format: 'yyyy-MM-dd HH:mm:ss'`

### Paso 1.3: Control de Calidad e Integridad de Datos (Manejo de Errores)

* **Regla Dataprep:**
  1. **Filtrar transacciones negativas:** Eliminar filas donde el monto sea menor o igual a cero: `delete row: monto_clp <= 0`
  2. **Filtrar cantidades nulas o erróneas:** Eliminar filas donde `cantidad` sea menor o igual a cero o sea nula: `delete row: cantidad <= 0 or ismissing([cantidad])`
  3. **Deduplicación:** Eliminar registros duplicados basados en el identificador único de transacción: `deduplicate` (basado en la columna `id_transaccion`).

### Paso 1.4: Seudonimización de Datos Personales (Cumplimiento Ley N° 21.719)

* **Problema:** La presencia de `rut_cliente` y `nombre_cliente` expone datos personales sensibles a los analistas de negocio.
* **Regla Dataprep (Seudonimización por Diseño):**

  1. Aplicar enmascaramiento sobre la columna `rut_cliente` para crear un identificador anónimo único pero consistente para comportamiento regional, ocultando los dígitos centrales y dejando solo los primeros 3 caracteres y el dígito verificador: `derive value: merge([substring(rut_cliente, 0, 3), 'XXXXXX-', right(rut_cliente, 1)], '') as: 'id_anonimo_cliente'`
  2. Eliminar las columnas originales `rut_cliente` y `nombre_cliente` del dataset final para evitar re-identificación: `drop col: rut_cliente, nombre_cliente`

  * *Nota:* Para las compras anónimas (donde el RUT es vacío), el valor resultante se manejará como nulo o "INVITADO".

### Paso 1.5: Enriquecimiento de Datos

* **Regla Dataprep:**
  1. Extraer el año de la transacción: `derive value: year(fecha) as: 'anio'`
  2. Extraer el mes de la transacción: `derive value: month(fecha) as: 'mes'`
  3. Extraer el día de la semana: `derive value: dayofweek(fecha) as: 'dia_semana'`

---

## 2. Pipeline de Sesiones Web (`sesiones_web_recipe`)

Esta receta toma la tabla externa cruda `grupo_cordillera_raw.sesiones_web`, aplica las reglas de limpieza y seudonimización, y escribe el resultado en `grupo_cordillera_dw.fact_sesiones_web`.

### Paso 2.1: Normalización del Timestamp (`timestamp`)

* **Problema:** Los datos del timestamp vienen como cadenas de texto en formato ISO (`2024-06-01T14:30:00Z`).
* **Implementación en Dataprep:**
  1. Al importar la tabla de origen, Cloud Dataprep detecta automáticamente la columna `timestamp` y la convierte al tipo **Date/Time** con el formato `yyyy*mm*dd*HH:MM:SSX` (detección automática).
  2. No es necesario agregar un paso manual; basta con verificar que el ícono de calendario aparezca en el encabezado de la columna confirmando la conversión.

### Paso 2.2: Seudonimización del ID de Cliente (`customer_id`)

* **Problema:** La presencia de `customer_id` (que contiene el RUT del cliente) expone datos personales sensibles.
* **Implementación en Dataprep:**

  1. Hacer clic en **Add Step** (`+`) y buscar la transformación **Derive** (seleccionar explícitamente "Derive column - Custom formula" o "New formula"). Es importante elegir primero el tipo de transformación Derive antes de ingresar la fórmula; de lo contrario, Dataprep puede interpretar la operación como un `keep` y eliminar todas las demás columnas.
  2. En el campo **Formula** ingresar: `IF(ISMISSING([customer_id]), NULL(), MERGE([SUBSTRING(customer_id, 0, 3), 'XXXXXX-', RIGHT(customer_id, 1)], ''))`
  3. En **New column name** escribir: `id_anonimo_cliente`
  4. Hacer clic en **Add**.

  * *Nota importante:* Se debe usar `NULL()` con paréntesis. Escribir `null` sin paréntesis genera el error `Column null does not exist in schema` porque Dataprep lo interpreta como referencia a una columna inexistente.

  5. Eliminar la columna original `customer_id`: clic en el encabezado de la columna → menú → **Drop**.

### Paso 2.3: Anonimización de IPs a Nivel de Subred (`ip_address`)

* **Problema:** La dirección IP completa permite identificar al usuario específico. Se anonimiza a nivel de subred para conservar utilidad geográfica sin exponer identidad individual.
* **Implementación en Dataprep:**
  1. **Crear columna derivada:** Add Step → buscar **Derive** (Custom formula) → en Formula escribir: `ip_address` → en New column name: `ip_anonima` → Add.
  2. **Anonimizar el último octeto:** Add Step → buscar **Replace** → seleccionar la opción **"text or pattern"** → en Column seleccionar `ip_anonima` → en Find ingresar la expresión regular `/\.\d+$/` → en Replace with escribir `.0` → Add. Esto transforma IPs del tipo `192.168.1.55` a `192.168.1.0`.
  3. **Eliminar columna original:** Clic en el encabezado de `ip_address` → menú → **Drop**.

---

## 3. Destino de los Datos (BigQuery Data Warehouse)

Una vez ejecutados los flujos de Dataprep de forma automática, los resultados se guardarán en BigQuery en el dataset `grupo_cordillera_dw` (que debe crearse en la región `us-central1` para coincidir con el origen) bajo el siguiente esquema relacional optimizado para analítica:

*   **Tabla `grupo_cordillera_dw.fact_ventas`:**
    *   `id_transaccion` (STRING - PK)
    *   `fecha` (DATETIME)
    *   `dia_semana` (INTEGER)
    *   `mes` (INTEGER)
    *   `anio` (DATETIME)
    *   `id_sucursal` (INTEGER)
    *   `id_anonimo_cliente` (STRING - FK)
    *   `sku` (STRING)
    *   `cantidad` (INTEGER)
    *   `monto_clp` (INTEGER)
    *   `metodo_pago` (STRING)
*   **Tabla `grupo_cordillera_dw.fact_sesiones_web`:**
    *   `session_id` (STRING - PK)
    *   `timestamp` (TIMESTAMP)
    *   `ip_anonima` (STRING)
    *   `id_anonimo_cliente` (STRING - FK)
    *   `event_type` (STRING)
    *   `sku_product` (STRING)
    *   `device` (STRING)

---

## 4. Gobierno de Datos, Privacidad y Archivado (Cumplimiento Ley N° 21.719)

Para garantizar la seguridad, el cumplimiento regulatorio y la eficiencia en costos, se establecen las siguientes directrices de gobierno:

**Cumplimiento Normativo:** Todas las operaciones de procesamiento se alinean estrictamente con la **Ley N° 21.719** de Protección de Datos de Chile.

**Seudonimización en la Transformación:** Se aplica seudonimización por enmascaramiento de texto (masking) a datos personales identificables como `rut_cliente` y `customer_id` ocultando los dígitos centrales y preservando solo el prefijo y el dígito verificador. Las direcciones IP se anonimizan parcialmente a nivel de subred reemplazando el último octeto por `.0` usando expresiones regulares. Los datos identificatorios crudos son descartados (`drop`) y nunca ingresan al Data Warehouse final.

* [ ] **Política de Archivado Automático de Bajo Costo:** Los datos de origen crudos almacenados en los buckets de Cloud Storage (`grupo_cordillera_raw`) están sujetos a una política de ciclo de vida de objetos (Object Lifecycle Management). Los archivos de ingesta diaria con más de 90 días de antigüedad son migrados automáticamente a la clase de almacenamiento **Coldline**, y aquellos con más de 365 días son transferidos a la clase **Archive** para retención histórica regulatoria obligatoria al menor costo posible.
