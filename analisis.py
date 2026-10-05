from pathlib import Path
import pandas as pd

base = Path(__file__).parent
ruta = base / "data" / "sensores_industriales.csv"

df = pd.read_csv(ruta)
df["fecha_hora"] = pd.to_datetime(df["fecha_hora"], format="%d/%m/%y %H:%M")

print("=== Resumen general ===")
print("Registros:", len(df))
print("Sensores distintos:", df["id_sensor"].nunique())
print("Rango de fechas:", df["fecha_hora"].min(), "a", df["fecha_hora"].max())
print()
print("Valores nulos por columna:")
print(df.isna().sum())