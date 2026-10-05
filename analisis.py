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