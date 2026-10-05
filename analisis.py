from pathlib import Path
import pandas as pd

base = Path(__file__).parent
ruta = base / "data" / "sensores_industriales.csv"

df = pd.read_csv(ruta)
columnas_originales = list(df.columns)
df["fecha_dt"] = pd.to_datetime(df["fecha_hora"], format="%d/%m/%y %H:%M")

# --- 1. Resumen general ---
print("=== Resumen general ===")
print("Registros:", len(df))
print("Sensores distintos:", df["id_sensor"].nunique())
print("Rango de fechas:", df["fecha_dt"].min(), "a", df["fecha_dt"].max())
print()

# --- 2. Temperatura promedio por planta ---
print("=== Temperatura promedio por planta (°C) ===")
promedios = df.groupby("planta")["temperatura_c"].mean().round(2)
print(promedios)
print()

# --- 3. Temperatura máxima (muestra todos los empates) ---
temp_max = df["temperatura_c"].max()
maximos = df[df["temperatura_c"] == temp_max]
print(f"=== Temperatura máxima: {temp_max} °C ===")
print(maximos[["id_sensor", "planta", "fecha_hora", "temperatura_c"]].to_string(index=False))


# --- 4. Alertas de temperatura (> 85 °C) ---
UMBRAL_C = 85
alertas = df[df["temperatura_c"] > UMBRAL_C]
print()
print(f"=== Lecturas con temperatura > {UMBRAL_C} °C ===")
print("Total de alertas:", len(alertas))

# --- 5. Planta con más alertas (muestra todos los empates) ---
alertas_por_planta = alertas.groupby("planta").size()
print()
print("=== Alertas por planta ===")
print(alertas_por_planta)

max_alertas = alertas_por_planta.max()
plantas_top = alertas_por_planta[alertas_por_planta == max_alertas]
print()
print(f"Planta(s) con más alertas ({max_alertas}):", ", ".join(plantas_top.index))

# --- 6. Exportar alertas con las columnas originales ---
DIR_RESULTADOS = base / "resultados"
DIR_RESULTADOS.mkdir(exist_ok=True)
ruta_alertas = DIR_RESULTADOS / "alertas.csv"
alertas[columnas_originales].to_csv(ruta_alertas, index=False)
print()
print("Alertas exportadas a:", ruta_alertas.relative_to(base))