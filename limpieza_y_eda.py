import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import unicodedata

def cargar_configuracion(ruta_config='config.json'):
    with open(ruta_config, 'r', encoding='utf-8') as f:
        return json.load(f)

def limpieza_y_eda(ruta_entrada, ruta_salida, config):
    print("1. Cargando el dataset filtrado...")
    df = pd.read_csv(ruta_entrada)
    
    # --- A. LIMPIEZA DE DATOS ---
    print("\n--- LIMPIEZA ---")
    filas_originales = len(df)
    
    # Eliminar filas donde falten los goles
    df = df.dropna(subset=['home_score', 'away_score'])
    
    # Convertir goles a enteros
    df['home_score'] = df['home_score'].astype(int)
    df['away_score'] = df['away_score'].astype(int)
    
    filas_limpias = len(df)
    print(f"Se eliminaron {filas_originales - filas_limpias} partidos por datos incompletos.")

    # --- B. PONDERACIÓN DE TORNEOS ---
    print("\n--- PONDERACIÓN ---")

    def quitar_acentos(texto):
        texto = unicodedata.normalize('NFKD', texto)
        return ''.join(c for c in texto if not unicodedata.combining(c))

    def asignar_peso_torneo(torneo):
        torneo_normalizado = quitar_acentos(str(torneo).strip().lower())

        # 1) Coincidencia exacta desde el JSON
        pesos_especificos = config['pesos_torneos']['especificos']
        if torneo_normalizado in pesos_especificos:
            return pesos_especificos[torneo_normalizado]

        # 2) Reglas por patrón desde el JSON
        pesos_patrones = config['pesos_torneos']['patrones']
        for patron, peso in pesos_patrones.items():
            if patron in torneo_normalizado:
                return peso

        # 3) Cualquier otro torneo no identificado -> peso por defecto del JSON
        return config['pesos_torneos']['default']

    df['tournament_weight'] = df['tournament'].apply(asignar_peso_torneo)
    
    print("Pesos asignados correctamente. Distribución de torneos y su peso:")
    resumen_pesos = (
        df.groupby('tournament')['tournament_weight']
        .agg(['first', 'count'])
        .rename(columns={'first': 'peso', 'count': 'nº_partidos'})
        .sort_values('nº_partidos', ascending=False)
    )
    print(resumen_pesos.to_string())

    # Aviso de control
    pesos_especificos_keys = config['pesos_torneos']['especificos'].keys()
    torneos_no_reconocidos = sorted(
        t for t in df['tournament'].unique()
        if quitar_acentos(str(t).strip().lower()) not in pesos_especificos_keys
        and 'qualification' not in quitar_acentos(str(t).lower())
        and 'friendly' not in quitar_acentos(str(t).lower())
    )
    if torneos_no_reconocidos:
        print(f"\n⚠️  Torneos NO reconocidos explícitamente (peso por defecto {config['pesos_torneos']['default']}): {torneos_no_reconocidos}")

    # Guardar el dataset ya limpio y ponderado
    df.to_csv(ruta_salida, index=False)
    print(f"\nDataset limpio y ponderado guardado en: {ruta_salida}")

    # --- C. EDA: DISTRIBUCIÓN DE GOLES ---
    print("\n--- EDA (Análisis Exploratorio) ---")
    print("Generando gráficos de distribución de goles...")
    
    todos_los_goles = pd.concat([df['home_score'], df['away_score']])
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(10, 6))
    ax = sns.countplot(x=todos_los_goles, palette="viridis", hue=todos_los_goles, legend=False)
    
    plt.title("Distribución de Goles por Equipo y Partido (Ciclo 2022-2026)", fontsize=14)
    plt.xlabel("Goles Marcados", fontsize=12)
    plt.ylabel("Frecuencia (Nº de veces que ocurrió)", fontsize=12)
    
    for p in ax.patches:
        ax.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    configuracion = cargar_configuracion()
    limpieza_y_eda('dataset_simulador_2026.csv', 'dataset_simulador_limpio.csv', configuracion)