import pandas as pd

def preparar_datos_simulador(ruta_csv_entrada, ruta_csv_salida):
    # 1. Cargar el dataset original
    print("Cargando el dataset...")
    df = pd.read_csv(ruta_csv_entrada)
    
    # 2. Convertir la columna de fecha a un objeto datetime real
    df['date'] = pd.to_datetime(df['date'])
    
    # 3. Filtrar por el ciclo mundialista actual (Post Qatar 2022)
    fecha_inicio_ciclo = '2022-12-19'
    df_ciclo = df[df['date'] >= fecha_inicio_ciclo]
    
    # 4. Lista de los 48 equipos clasificados al Mundial 2026
    # Nota: Asegúrate de que los nombres coincidan EXACTAMENTE con cómo están escritos en el CSV 
    # (por lo general están en inglés en ese dataset de Kaggle, ej: 'United States', 'Spain', etc.)
    equipos_2026 = ["United States", "Mexico", "Canada",
    "Argentina", "Brazil", "Colombia", "Ecuador", "Paraguay", "Uruguay",
    "Australia", "Iran", "Japan", "South Korea", "Jordan", "Qatar",
    "Saudi Arabia", "Uzbekistan", "Iraq",
    "Algeria", "Cape Verde", "Ivory Coast", "Egypt", "Ghana",
    "Morocco", "Senegal", "South Africa", "Tunisia", "DR Congo",
    "Curacao", "Haiti", "Panama",
    "New Zealand",
    "Austria", "Belgium", "Bosnia and Herzegovina", "Croatia",
    "Czechia", "England", "France", "Germany", "Netherlands",
    "Norway", "Portugal", "Scotland", "Spain", "Sweden",
    "Switzerland", "Turkey"]
    
    # 5. Filtrar los partidos
    # OPCIÓN A: Partidos donde AL MENOS UN equipo es mundialista (recomendado para tener más datos de evaluación)
    df_filtrado = df_ciclo[
        df_ciclo['home_team'].isin(equipos_2026) | 
        df_ciclo['away_team'].isin(equipos_2026)
    ]
    
    # OPCIÓN B: Si quieres un modelo MÁS ESTRICTO, descomenta la siguiente línea y borra la anterior.
    # Esto dejará solo partidos donde AMBOS equipos son mundialistas.
    # df_filtrado = df_ciclo[df_ciclo['home_team'].isin(equipos_2026) & df_ciclo['away_team'].isin(equipos_2026)]
    
    # 6. Guardar el nuevo dataset listo para el modelo
    df_filtrado.to_csv(ruta_csv_salida, index=False)
    
    # Imprimir un resumen
    print("-" * 30)
    print(f"Total de partidos en la historia: {len(df)}")
    print(f"Total de partidos desde dic 2022: {len(df_ciclo)}")
    print(f"Total de partidos filtrados (para el simulador): {len(df_filtrado)}")
    print("-" * 30)
    print(f"Archivo guardado exitosamente en: {ruta_csv_salida}")

# Ejecución del script
if __name__ == "__main__":
    # Sustituye 'results.csv' por el nombre de tu archivo descargado
    preparar_datos_simulador('results.csv', 'dataset_simulador_2026.csv')