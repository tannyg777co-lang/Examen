# Análisis de sensores industriales

## Objetivo
Analizar con Python las mediciones de temperatura y vibración de sensores instalados en cuatro plantas industriales: calcular promedios por planta, identificar la temperatura máxima y detectar alertas de temperatura (lecturas mayores que 85 °C).

## Datos
> **Los datos son simulados.** No provienen de sensores reales; el umbral de 85 °C es una regla didáctica del ejercicio.

Archivo: `data/sensores_industriales.csv` (100,000 mediciones, una por minuto por sensor).

| Columna | Significado |
|---------|-------------|
| id_registro | Identificador de la medición |
| fecha_hora | Fecha y hora de la lectura |
| id_sensor | Identificador del sensor |
| planta | Planta donde está instalado |
| temperatura_c | Temperatura en grados Celsius |
| vibracion_mm_s | Vibración en milímetros por segundo |

## Instalación y ejecución

Requiere Python 3.

```bash
git clone https://github.com/tannyg777co-lang/Examen.git
cd Examen
python -m venv .venv
```

Activar el entorno virtual:

```powershell
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

```bash
# Mac / Linux
source .venv/bin/activate
```

Instalar dependencias y ejecutar:

```bash
pip install -r requirements.txt
python analisis.py
```

## Resultados
El programa imprime en consola el resumen del análisis y exporta las lecturas con alerta a `resultados/alertas.csv`, conservando las columnas originales.

## Estructura
```
data/            CSV original
resultados/      alertas.csv generado por el programa
evidencias/      captura de la ejecución reproducible
analisis.py      programa de análisis
informe.md       respuestas de la Parte II
requirements.txt dependencias
```
