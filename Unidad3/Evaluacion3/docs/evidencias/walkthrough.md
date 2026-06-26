# Guía de Implementación y Evidencias: Capa Speed & Dashboard Profesional — CordilleraBI

Esta guía documenta el desarrollo técnico y las evidencias de visualización del dashboard interactivo consolidado en Streamlit (Capa Batch histórica + Capa Speed en tiempo real) tras resolver todos los problemas de diseño y UX detectados.

---

## 1. Diseño y Flujo del Dashboard Omnicanal

El dashboard unifica la información de dos capas analíticas:
*   **Capa Batch (Histórica):** Conectada a `grupo_cordillera_dw.fact_ventas`. Se recargó la tabla con una distribución de Pareto realista (~22% de ingresos en E-Commerce / Sucursal 0) y Zipf en la popularidad de productos.
*   **Capa Speed (Tiempo Real):** Conectada a la vista unificada `grupo_cordillera_dw.fact_sesiones_web`, que combina datos históricos de sesiones con telemetría en tiempo real recibida a través de Cloud Pub/Sub (`streaming-subscription`) y procesada por `streaming_consumer.py`.

---

## 2. Refinamientos de Diseño y UX Aplicados

Para lograr una interfaz de nivel profesional y resolver las observaciones del usuario:

1.  **Agregación en una Única Llamada a Markdown**: Se corrigió el error del espacio vacío en las tablas de auditoría. Anteriormente, la cabecera y el cuerpo del HTML se renderizaban en llamadas `st.markdown` distintas, lo que hacía que el navegador las cerrara por separado y Streamlit añadiera márgenes innecesarios. Ahora todo se renderiza como un único bloque HTML unificado.
2.  **Sincronización Inteligente de Temas (Sistema + Manual)**:
    *   Al ingresar por primera vez (sin parámetro en la URL), un script cliente de JavaScript detecta la preferencia de tema del sistema operativo (`prefers-color-scheme`) y redirecciona con el parámetro correspondiente (`?theme=dark` o `?theme=light`).
    *   Si el usuario hace clic en el botón de alternancia, la URL y el estado se actualizan de forma manual de manera persistente.
3.  **Contraste de Fuentes en Modo Claro**: Se actualizó la configuración de `PLOT_LAYOUT` para utilizar colores de fuente reactivos al tema seleccionado: `#fafafa` en modo oscuro y `#09090b` en modo claro para textos, títulos y leyendas de Plotly, evitando que las etiquetas queden invisibles.
4.  **Distribución Realista de Métodos de Pago**:
    *   Se actualizó el script `clean_and_load_ventas.py` para aplicar una distribución probabilística realista. Por ejemplo, en **E-Commerce (Sucursal 0) no se admiten transacciones en Efectivo**.
    *   Se modificó el flujo del dashboard para que el gráfico de Métodos de Pago ignore el autofiltrado de pago lateral (usando `where_clause_pago`), permitiendo analizar la distribución de métodos de pago completa incluso al filtrar un método específico.
5.  **Indicador LIVE y Embudo Profesional**:
    *   Se añadió un indicador **LIVE** con una animación de pulsación en CSS rojo en la pestaña de streaming.
    *   Se estilizó el gráfico de embudo utilizando la tipografía `DM Sans` y suavizando la opacidad de los conectores.

---

## 3. Evidencias del Dashboard Profesional

### Pestaña 1: Capa Batch - Modo Oscuro
Muestra la facturación histórica, el gráfico de líneas con la evolución mensual real agrupada, y el desglose de sucursales con el canal digital destacado en verde esmeralda.

![Capa Batch: Ventas Transaccionales (Oscuro)](/Users/user/.gemini/antigravity-ide/brain/8767dc13-7818-43f3-ae75-d1b56c414952/batch_tab_loaded_dark_1782477442694.png)

### Pestaña 1: Capa Batch - Modo Claro
La misma vista con un contraste de tipografías impecable y alta legibilidad para reportes ejecutivos diurnos.

![Capa Batch: Ventas Transaccionales (Claro)](/Users/user/.gemini/antigravity-ide/brain/8767dc13-7818-43f3-ae75-d1b56c414952/batch_tab_light_1782477638004.png)

### Pestaña 2: Capa Speed - Monitoreo en Tiempo Real (Claro)
El embudo de conversión web y la auditoría de ingesta con IP enmascaradas en modo claro. El indicador de transmisión en vivo parpadea activamente.

![Capa Speed: Monitoreo Streaming (Claro)](/Users/user/.gemini/antigravity-ide/brain/8767dc13-7818-43f3-ae75-d1b56c414952/speed_tab_light_1782477680978.png)

### Pestaña 2: Capa Speed - Monitoreo en Tiempo Real (Oscuro)
La misma vista de ingesta Pub/Sub en tiempo real en modo oscuro.

![Capa Speed: Monitoreo Streaming (Oscuro)](/Users/user/.gemini/antigravity-ide/brain/8767dc13-7818-43f3-ae75-d1b56c414952/speed_tab_dark_1782477722360.png)

---

## 4. Ejecución de la Simulación e Ingesta

La actualización de datos en el dashboard es interactiva y automática:
1.  **Autorefresh**: El checkbox lateral viene activado por defecto (`value=True`), lo que causa que Streamlit actualice los datos de BigQuery cada 5 segundos de forma autónoma.
2.  **Procesos Activos**:
    *   **Productor**: Inyectando telemetría web continua a Pub/Sub.
    *   **Consumidor**: Escribiendo micro-lotes de forma controlada a BigQuery.
