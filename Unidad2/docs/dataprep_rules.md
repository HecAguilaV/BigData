# Especificación de Transformación y Calidad de Datos en Cloud Dataprep (Trifacta)

Este documento detalla la receta de transformación y las reglas de calidad que se deben implementar en **Cloud Dataprep** para procesar los datos crudos de **Grupo Cordillera** y cargarlos de forma limpia en el Data Warehouse de **BigQuery**.

## Justificación de Tecnologías (Las 5Vs)

La implementación de **Cloud Dataprep (Trifacta)** y **BigQuery** se justifica bajo los siguientes pilares de las 5Vs de Big Data:
*   **Veracidad:** Cloud Dataprep permite perfilado de datos interactivo y la aplicación de reglas de calidad automatizadas para corregir formatos inconsistentes (por ejemplo, en `monto_clp`) y eliminar registros nulos o erróneos en las transacciones antes de cargarlas.
*   **Variedad:** La combinación de orígenes de datos de transacciones de ventas estructuradas (`ventas_historicas`) y registros de comportamiento de navegación web semi-estructurados en JSON (`sesiones_web`) es gestionada eficientemente por Cloud Dataprep mediante normalización y parseo de tipos de datos.
*   **Volumen:** BigQuery proporciona almacenamiento masivo elástico y capacidad de cómputo a gran escala capaz de responder consultas complejas sobre millones de filas sin degradación de rendimiento.
*   **Velocidad:** El procesamiento batch y la orquestación en la nube garantizan la disponibilidad de los datos en BigQuery de forma oportuna para la toma de decisiones estratégicas.
*   **Valor:** La limpieza y transformación de los datos crudos genera datos confiables (*trusted data*) que permiten calcular el ticket promedio y proyectar la conversión web real.

---

## 1. Pipeline de Ventas Históricas (`ventas_historicas_recipe`)

Esta receta toma la tabla externa cruda `grupo_cordillera_raw.ventas_historicas` en BigQuery, aplica las reglas de limpieza y seudonimización, y escribe el resultado en `grupo_cordillera_dw.fact_ventas`.

### Paso 1.1: Limpieza del Formato de Moneda (`monto_clp`)
*   **Problema:** Un 1% de las transacciones tiene el monto en formato sucio (ej: `$450,000` en lugar de `450000`), lo que impide clasificarlo como tipo numérico.
*   **Regla Dataprep:**
    1.  Reemplazar el símbolo `$` por vacío: `replace text: '$' with: '' on: monto_clp`
    2.  Eliminar las comas del formato de miles: `replace text: ',' with: '' on: monto_clp`
    3.  Convertir a tipo de dato entero: `settype col: monto_clp type: Integer`

### Paso 1.2: Normalización del Formato de Fecha (`fecha`)
*   **Problema:** Los datos de fecha vienen como cadenas de texto en formato `YYYY-MM-DD HH:MM:SS`.
*   **Regla Dataprep:**
    1.  Convertir la columna `fecha` a tipo fecha y hora (Datetime) utilizando el formato ISO: `settype col: fecha type: Datetime format: 'yyyy-MM-dd HH:mm:ss'`

### Paso 1.3: Control de Calidad e Integridad de Datos (Manejo de Errores)
*   **Regla Dataprep:**
    1.  **Filtrar transacciones negativas:** Eliminar filas donde el monto sea menor o igual a cero: `delete row: monto_clp <= 0`
    2.  **Filtrar cantidades nulas o erróneas:** Eliminar filas donde `cantidad` sea menor o igual a cero o sea nula: `delete row: cantidad <= 0 or ismissing([cantidad])`
    3.  **Deduplicación:** Eliminar registros duplicados basados en el identificador único de transacción: `deduplicate` (basado en la columna `id_transaccion`).

### Paso 1.4: Seudonimización de Datos Personales (Cumplimiento Ley N° 21.719)
*   **Problema:** La presencia de `rut_cliente` y `nombre_cliente` expone datos personales sensibles a los analistas de negocio.
*   **Regla Dataprep (Seudonimización por Diseño):**
    1.  Aplicar un algoritmo hash criptográfico (SHA-256) sobre la columna `rut_cliente` para crear un identificador anónimo único pero consistente para comportamiento regional: `derive value: sha2(rut_cliente, 256) as: 'id_anonimo_cliente'`
    2.  Eliminar las columnas originales `rut_cliente` y `nombre_cliente` del dataset final para evitar re-identificación: `drop col: rut_cliente, nombre_cliente`
    *   *Nota:* Para las compras anónimas (donde el RUT es vacío), el valor del hash resultante se manejará como nulo o "INVITADO".

### Paso 1.5: Enriquecimiento de Datos
*   **Regla Dataprep:**
    1.  Extraer el año de la transacción: `derive value: year(fecha) as: 'anio'`
    2.  Extraer el mes de la transacción: `derive value: month(fecha) as: 'mes'`
    3.  Extraer el día de la semana: `derive value: dayofweek(fecha) as: 'dia_semana'`

---

## 2. Pipeline de Sesiones Web (`sesiones_web_recipe`)

Esta receta toma la tabla externa cruda `grupo_cordillera_raw.sesiones_web`, aplica las reglas de limpieza y seudonimización, y escribe el resultado en `grupo_cordillera_dw.fact_sesiones_web`.

### Paso 2.1: Normalización del Timestamp (`timestamp`)
*   **Regla Dataprep:**
    1.  Convertir la columna `timestamp` de formato ISO string a Datetime: `settype col: timestamp type: Datetime format: 'yyyy-MM-dd\'T\'HH:mm:ss\'Z\''`

### Paso 2.2: Seudonimización del ID de Cliente (`customer_id`)
*   **Regla Dataprep:**
    1.  Para mantener la coherencia y permitir el cruce de datos omnicanal de forma segura, el `customer_id` (que contiene el RUT) debe hash-earse usando el mismo algoritmo SHA-256: `derive value: if(ismissing([customer_id]), null, sha2(customer_id, 256)) as: 'id_anonimo_cliente'`
    2.  Eliminar la columna original: `drop col: customer_id`

### Paso 2.3: Validación y Normalización de IPs (`ip_address`)
*   **Regla Dataprep:**
    1.  Validar formato de IP v4 y extraer la subred (anonimización parcial de IP para cumplimiento de privacidad): `derive value: textformat(ip_address, '###.###.###.0') as: 'ip_anonima'`
    2.  Eliminar la columna original: `drop col: ip_address`

---

## 3. Destino de los Datos (BigQuery Data Warehouse)

Una vez ejecutados los flujos de Dataprep de forma automática, los resultados se guardarán en BigQuery en el dataset `grupo_cordillera_dw` bajo el siguiente esquema relacional optimizado para analítica:

*   **Tabla `grupo_cordillera_dw.fact_ventas`:**
    *   `id_transaccion` (STRING - PK)
    *   `fecha` (TIMESTAMP)
    *   `id_sucursal` (INT64)
    *   `id_anonimo_cliente` (STRING - FK)
    *   `sku` (STRING)
    *   `cantidad` (INT64)
    *   `monto_clp` (INT64)
    *   `metodo_pago` (STRING)
    *   `anio` (INT64)
    *   `mes` (INT64)
    *   `dia_semana` (INT64)
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
*   **Cumplimiento Normativo:** Todas las operaciones de procesamiento se alinean estrictamente con la **Ley N° 21.719** de Protección de Datos de Chile.
*   **Seudonimización en la Transformación:** Se aplica seudonimización mediante funciones hash criptográficas SHA-256 no reversibles a datos personales identificables como `rut_cliente` y `customer_id`. Las direcciones IP se anonimizan parcialmente a nivel de subred (máscara de red `255.255.255.0` o reemplazando el último octeto por `.0`). Los datos identificatorios crudos son descartados (`drop`) y nunca ingresan al Data Warehouse final.
*   **Política de Archivado Automático de Bajo Costo:** Los datos de origen crudos almacenados en los buckets de Cloud Storage (`grupo_cordillera_raw`) están sujetos a una política de ciclo de vida de objetos (Object Lifecycle Management). Los archivos de ingesta diaria con más de 90 días de antigüedad son migrados automáticamente a la clase de almacenamiento **Coldline**, y aquellos con más de 365 días son transferidos a la clase **Archive** para retención histórica regulatoria obligatoria al menor costo posible.
