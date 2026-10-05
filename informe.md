# Informe: aplicación al caso de Big Data

## Resultados base del análisis

Calculados con `analisis.py` sobre `data/sensores_industriales.csv` (datos simulados):

- 100,000 registros, 40 sensores distintos, 4 plantas, del 01/09/2026 00:00 al 02/09/2026 17:39.
- Temperatura promedio: Planta_1 66.62 °C, Planta_2 66.53 °C, Planta_3 66.77 °C, Planta_4 66.67 °C.
- Temperatura máxima: 104.99 °C, repetida en 4 lecturas (S023 en Planta_3, S019 en Planta_2, S014 en Planta_2 y S030 en Planta_3).
- Alertas (temperatura > 85 °C): 6,954 lecturas. Por planta: Planta_1 1,737; Planta_2 1,708; Planta_3 1,777; Planta_4 1,732.
- Planta con más alertas: Planta_3 (1,777).

---

## 5. Las 5 V aplicadas al proyecto

| V | Relación con el sistema de sensores | Ejemplo concreto | ¿CSV actual o ampliación? |
|---|---|---|---|
| **Volumen** | Cantidad de datos que generan los sensores. | El CSV tiene 100,000 registros (40 sensores x 1 lectura por minuto, unas 57,600 lecturas al día). Con 5,000 sensores leyendo cada segundo (cifra hipotética) serían unos 432 millones de lecturas al día. | El CSV actual es un volumen pequeño; el ejemplo de 432 millones corresponde a la **ampliación**. |
| **Velocidad** | Rapidez con la que llegan los datos y con la que se necesita reaccionar. | Cada sensor registra una lectura por minuto. En la ampliación habría una por segundo (60 veces más por sensor) y una alerta debería emitirse en pocos segundos. | El CSV tiene la frecuencia de un minuto, pero se analiza ya guardado, sin llegada continua. La lectura cada segundo es **ampliación**. |
| **Variedad** | Diferentes formatos y fuentes de datos. | Mensajes JSON de sensores, fotografías de máquinas y reportes de mantenimiento en texto libre. | El CSV contiene un solo formato (tabla estructurada). Todo lo demás es **ampliación**. |
| **Veracidad** | Confiabilidad y calidad de los datos. | En el CSV no hay valores nulos en ninguna de las 6 columnas, pero la temperatura de 104.99 °C aparece idéntica en 4 lecturas de 4 sensores distintos, algo que habría que validar (no se determinó la causa). Con sensores reales podrían aparecer fallas de calibración, lecturas duplicadas o desconexiones. | La ausencia de nulos y la repetición del máximo están en el **CSV actual** (y los datos son simulados). Las fallas de sensores reales son **ampliación**. |
| **Valor** | Utilidad de los datos para tomar decisiones. | Identificar 6,954 alertas y que Planta_3 concentra la mayor cantidad (1,777) permite priorizar qué planta revisar primero. | Este ejemplo sale del **CSV actual**. Predecir fallas combinando temperatura, vibración, fotos y reportes sería **ampliación**. |

---

## 6. Tipos de datos y procesamiento tradicional

| Elemento | Clasificación | Justificación |
|---|---|---|
| CSV de sensores | **Estructurado** | Filas y columnas fijas con tipos definidos (fecha, texto, número). |
| Mensaje JSON de un sensor | **Semiestructurado** | Tiene etiquetas y campos, pero no un esquema rígido; los campos pueden variar entre mensajes. |
| Fotografía de una máquina | **No estructurado** | Es una imagen sin campos tabulares; requiere técnicas de visión para extraer información. |
| Texto libre de un reporte de mantenimiento | **No estructurado** | Lenguaje natural sin formato fijo. |

**Por qué 100,000 registros no convierten el archivo en Big Data.** Big Data no depende solo de la cantidad de filas, sino de que los datos superen lo que las herramientas tradicionales pueden manejar, considerando también velocidad, variedad, veracidad y valor. Este archivo cabe en la memoria de una computadora personal y `analisis.py` lo procesa con pandas en segundos, en una sola máquina. Es un conjunto de datos grande para una hoja de cálculo, pero no es Big Data.

**Limitaciones al aumentar la escala:**

- **Memoria:** `pandas.read_csv` carga todo el archivo en RAM; con cientos de millones de filas dejaría de caber.
- **Una sola máquina:** el tiempo de procesamiento y el almacenamiento tendrían un límite.
- **Formato CSV:** no es adecuado para escrituras continuas ni concurrentes, ni para consultas rápidas sin índices.
- **Procesamiento por lotes:** analizar un archivo guardado no permite reaccionar en segundos.
- **Variedad:** fotos, JSON y texto libre no se analizan con una tabla de pandas; necesitarían otras herramientas y otros tipos de almacenamiento.

---

## 7. Batch y Streaming

**Tipo de procesamiento realizado: batch (por lotes).** El programa lee un archivo completo que ya estaba guardado y calcula todos los resultados de una vez. No procesa cada lectura al llegar, y el resultado se obtiene hasta que termina de ejecutarse.

**Alerta pocos segundos después de una lectura > 85 °C: streaming.** Cada lectura se evaluaría como evento en cuanto llega, con una regla simple (`temperatura_c > 85`) que dispare la notificación. Por ejemplo, los sensores publicarían sus mensajes en un sistema de mensajería (como Kafka) y un procesador de flujos (como Spark Structured Streaming o Flink) aplicaría la regla. Se justifica porque el resultado pierde utilidad si llega tarde: una alerta de temperatura sirve mientras la máquina aún puede revisarse.

**Resumen al terminar el día: batch.** Se necesita hasta el cierre del día y puede esperar, así que basta una tarea programada que procese todas las lecturas del día de una vez (promedios por planta, máximos y conteo de alertas), como hace `analisis.py`.

**Relación con el tiempo:** lo que debe actuarse en segundos (alertas) se resuelve con streaming; lo que puede esperar horas (resúmenes e historiales) se resuelve con batch, que es más simple y barato.

---

## 8. Lambda y Kappa

### Escenario A: Lambda

La empresa quiere combinar una ruta que recalcule el historial por lotes con otra que procese las mediciones recientes rápidamente. Eso es exactamente la arquitectura **Lambda**, que mantiene dos rutas paralelas y las combina para responder consultas.

```
                 +--> [ Capa batch: recalcula todo el historial ] --+
[ Sensores ] --> [ Almacén de   ]                                   +--> [ Capa de servicio ] --> [ Consultas / Dashboard ]
                 [ datos crudos ]                                   |
                 +--> [ Capa rápida: mediciones recientes ] --------+
```

Justificación: la capa batch da resultados completos y corregibles sobre el historial, y la capa rápida da resultados casi inmediatos sobre lo reciente; la capa de servicio los une. El costo es mantener dos rutas de procesamiento.

### Escenario B: Kappa

La empresa quiere una sola lógica de procesamiento de eventos y conservar las mediciones para volver a procesarlas cuando sea necesario. Eso es la arquitectura **Kappa**, que usa solo procesamiento de flujo sobre un registro de eventos que se conserva.

```
[ Sensores ] --> [ Registro de eventos (log) conservado ] --> [ Procesamiento de flujo (una sola lógica) ] --> [ Resultados / Alertas ]
                              ^                                                  |
                              +-------- reprocesar: se vuelve a leer el log -----+
```

Justificación: hay un solo código que mantener, y si la lógica cambia (por ejemplo, otro umbral) se reprocesa leyendo de nuevo el registro de eventos desde el inicio.

---

## 9. Analítica descriptiva, predictiva y prescriptiva

### Descriptiva

Dos hallazgos reales de mi análisis:

1. Las lecturas por encima de 85 °C son **6,954** de 100,000 (6.95 %), y **Planta_3** concentra la mayor cantidad con **1,777** alertas.
2. La temperatura promedio es casi igual en las cuatro plantas (de 66.53 °C en Planta_2 a 66.77 °C en Planta_3), y el máximo registrado fue **104.99 °C**, repetido en 4 lecturas.

### Predictiva

**Pregunta:** ¿qué máquinas tienen mayor probabilidad de tener un problema de sobrecalentamiento en las próximas horas?

**Datos adicionales necesarios:** un historial mucho más largo; registro de fallas reales de las máquinas; reportes y fechas de mantenimiento; tipo y antigüedad de cada máquina; carga de trabajo; temperatura ambiente; y análisis de la vibración junto con la temperatura. El CSV actual cubre solo unas 41 horas y no contiene fallas registradas, así que no permite estimar probabilidades.

### Prescriptiva

**Acción propuesta:** ante un riesgo previsto de sobrecalentamiento en una máquina, programar una inspección preventiva antes de que falle.

**Información que revisaría antes de decidir:** si las alertas son lecturas aisladas o sostenidas en el tiempo; si la vibración también está elevada; el historial de mantenimiento de esa máquina; si el sensor funciona bien (descartar un sensor defectuoso); y el costo de detener la máquina frente al costo de una falla.

> Una lectura por encima del umbral es una alerta del ejercicio; por sí sola no demuestra que una máquina vaya a fallar.
