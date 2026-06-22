import pandas as pd
import json

def cargar_configuracion(ruta_config='config.json'):
    with open(ruta_config, 'r', encoding='utf-8') as f:
        return json.load(f)

def calcular_rating_elo(ruta_entrada, ruta_salida_rankings, config, ruta_elo_inicial=None):
    print("1. Cargando el dataset limpio...")
    df = pd.read_csv(ruta_entrada)

    # Es VITAL ordenar los partidos cronológicamente para que el Elo funcione
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)

    # Cargar Elo inicial anclado a valores reales
    elo_inicial = {}
    if ruta_elo_inicial is not None:
        print(f"   Anclando Elo inicial desde: {ruta_elo_inicial}")
        df_inicial = pd.read_csv(ruta_elo_inicial)
        elo_inicial = dict(zip(df_inicial['team'], df_inicial['rating']))
    else:
        print("   ⚠️  Sin Elo inicial anclado: todas las selecciones arrancan en cold-start.")

    # Parámetros inyectados desde config.json
    K_BASE = config["parametros_elo"]["k_base"]
    BONUS_CAMPO_LOCAL = config["parametros_elo"]["bonus_campo"]
    ELO_POR_DEFECTO = config["parametros_elo"]["elo_nuevo"]

    def calcular_multiplicador_goles(goles_a, goles_b):
        diferencia = abs(goles_a - goles_b)
        if diferencia <= 1:
            return 1.0
        elif diferencia == 2:
            return 1.5
        else:
            return (11.0 + diferencia) / 8.0

    def ejecutar_una_pasada(df, ratings_iniciales):
        ratings_elo = dict(ratings_iniciales)

        def obtener_elo(equipo):
            if equipo not in ratings_elo:
                ratings_elo[equipo] = ELO_POR_DEFECTO
            return ratings_elo[equipo]

        for _, row in df.iterrows():
            equipo_local = row['home_team']
            equipo_visitante = row['away_team']
            goles_local = row['home_score']
            goles_visitante = row['away_score']
            peso_torneo = row['tournament_weight']

            elo_local = obtener_elo(equipo_local)
            elo_visitante = obtener_elo(equipo_visitante)

            es_neutral = bool(row.get('neutral', False))
            BONUS_CAMPO = 0.0 if es_neutral else BONUS_CAMPO_LOCAL

            esperado_local = 1 / (1 + 10 ** ((elo_visitante - (elo_local + BONUS_CAMPO)) / 400))
            esperado_visitante = 1 - esperado_local

            if goles_local > goles_visitante:
                resultado_local, resultado_visitante = 1.0, 0.0
            elif goles_local < goles_visitante:
                resultado_local, resultado_visitante = 0.0, 1.0
            else:
                resultado_local, resultado_visitante = 0.5, 0.5

            multiplicador_goles = calcular_multiplicador_goles(goles_local, goles_visitante)
            K_final = K_BASE * peso_torneo

            nuevo_elo_local = elo_local + K_final * multiplicador_goles * (resultado_local - esperado_local)
            nuevo_elo_visitante = elo_visitante + K_final * multiplicador_goles * (resultado_visitante - esperado_visitante)

            ratings_elo[equipo_local] = nuevo_elo_local
            ratings_elo[equipo_visitante] = nuevo_elo_visitante

        return ratings_elo

    print("2. Calculando la evolución del Rating Elo partido a partido...")
    ratings_elo = ejecutar_una_pasada(df, ratings_iniciales=elo_inicial)

    print("3. Generando el ranking final...")
    df_rankings = pd.DataFrame(list(ratings_elo.items()), columns=['Equipo', 'Elo'])
    df_rankings = df_rankings.sort_values(by='Elo', ascending=False).reset_index(drop=True)
    
    # Guardar el ranking
    df_rankings.to_csv(ruta_salida_rankings, index=False)
    
    print("-" * 40)
    print("TOP 10 SELECCIONES (CARA AL MUNDIAL 2026)")
    print("-" * 40)
    df_rankings_display = df_rankings.copy()
    df_rankings_display['Elo'] = df_rankings_display['Elo'].round(1)
    print(df_rankings_display.head(10).to_string(index=False))
    print("-" * 40)
    print(f"Ranking completo guardado en: {ruta_salida_rankings}")
    return df_rankings

if __name__ == "__main__":
    configuracion = cargar_configuracion()
    calcular_rating_elo(
        'dataset_simulador_limpio.csv',
        'rankings_elo_2026.csv',
        configuracion,
        ruta_elo_inicial='elo_inicial_anclado.csv'
    )