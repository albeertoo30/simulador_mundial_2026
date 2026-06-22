"""
Genera el fichero de Elo INICIAL para cada selección, anclado a valores
reales históricos (eloratings.net) justo antes del comienzo del ciclo
mundialista (29/12/2022).

POR QUÉ HACE FALTA ESTO:
El script de Elo original hacía arrancar a TODAS las selecciones desde
1500 puntos ("cold start"). Esto provoca un sesgo grave: una selección
que juega muchos partidos contra rivales débiles de su propia confederación
(que también arrancan en 1500, sin estar calibrados) gana esos partidos
con un "resultado esperado" de ~50%, llevándose la máxima cantidad de
puntos posibles, como si jugara contra un igual. El sistema nunca llega a
"enterarse" de que esos rivales son mucho más débiles si no hay suficientes
partidos que conecten esa confederación con el resto del mundo.

La solución estándar (la que usa eloratings.net) es que el rating de cada
equipo siempre parte de su nivel real conocido, no de un valor neutro.
Aquí usamos el dataset histórico de Elo (saifalnimri/international-football
-elo-ratings en Kaggle, basado en eloratings.net) para anclar cada
selección a su Elo real al cierre de 2022, justo antes del Mundial 2022 ya
disputado / inicio de tu ciclo de datos.

Uso:
    python3 generar_elo_inicial.py
Genera: elo_inicial_anclado.csv  (columnas: team, rating)
"""
import pandas as pd

RUTA_HISTORICO_ELO = 'eloratings.csv'   # Descargado de Kaggle (saifalnimri)
FECHA_CORTE = pd.Timestamp('2022-12-29')  # Justo antes del 1er partido del ciclo
RUTA_SALIDA = 'elo_inicial_anclado.csv'

# Selecciones "fantasma" / inactivas que aparecen en el histórico con un Elo
# desactualizado y artificialmente alto (no han jugado en décadas). Se
# excluyen para que no contaminen ningún cruce de nombres.
EXCLUIR_DEL_HISTORICO = {'West Germany', 'Czechoslovakia', 'Yugoslavia',
                          'Soviet Union', 'East Germany'}

# Mapa de equivalencias: nombre en TU dataset -> nombre en el histórico Elo
MAPA_EQUIVALENCIAS = {
    'Czech Republic': 'Czechia',
    'DR Congo': 'Democratic Republic of Congo',
    'Republic of Ireland': 'Ireland',
    'São Tomé and Príncipe': 'Sao Tome and Principe',
}

# Selecciones sin histórico en eloratings.net (regionales no-FIFA o con
# muy poca actividad). Se les asigna un Elo inicial conservador (no 1500)
# acorde a su nivel real conocido: claramente por debajo de la media de
# selecciones FIFA activas.
ELO_INICIAL_SIN_HISTORICO = {
    'Basque Country': 1350.0,  # Selección no-FIFA, nivel amateur/regional
    'Galicia': 1300.0,          # Selección no-FIFA, nivel amateur/regional
    'Samoa': 1200.0,            # Selección FIFA de nivel muy bajo (Oceanía)
}


def generar_elo_inicial(equipos_objetivo):
    """
    equipos_objetivo: lista/set de nombres de selección tal como aparecen
    en TU dataset (home_team / away_team), para las que se necesita un
    Elo inicial.
    """
    print("1. Cargando histórico de Elo real (eloratings.net)...")
    df = pd.read_csv(RUTA_HISTORICO_ELO)

    # Fix: los nombres del histórico traen espacios Unicode \xa0 en vez de
    # espacios normales -> rompen cualquier comparación de texto si no se
    # corrige primero.
    df['team'] = df['team'].astype(str).str.replace('\xa0', ' ', regex=False)

    df['date'] = pd.to_datetime(df['date'], format='mixed')
    df = df[~df['team'].isin(EXCLUIR_DEL_HISTORICO)]

    print("2. Filtrando al último rating conocido antes de {}...".format(FECHA_CORTE.date()))
    df_hasta_corte = df[df['date'] <= FECHA_CORTE]
    # FIX: algunas filas de la fuente traen el rating vacío (NaN) por huecos
    # de scraping en el dataset original (detectado en Moldova: 31 de 32
    # filas con rating=NaN). Se descartan ANTES de tomar "el último valor",
    # para no terminar anclando una selección a NaN sin enterarnos.
    df_hasta_corte = df_hasta_corte.dropna(subset=['rating'])
    ultimo_rating = (
        df_hasta_corte.sort_values('date')
        .groupby('team')['rating']
        .last()
    )

    print("3. Resolviendo equivalencias de nombres y construyendo el mapa final...")
    resultado = {}
    sin_match = []
    for equipo in equipos_objetivo:
        nombre_en_historico = MAPA_EQUIVALENCIAS.get(equipo, equipo)
        if nombre_en_historico in ultimo_rating.index:
            resultado[equipo] = float(ultimo_rating[nombre_en_historico])
        elif equipo in ELO_INICIAL_SIN_HISTORICO:
            resultado[equipo] = ELO_INICIAL_SIN_HISTORICO[equipo]
        else:
            # Última red de seguridad: si apareciera alguna selección nueva
            # no contemplada, se usa 1500 como neutro y se avisa para que
            # se pueda revisar a mano.
            resultado[equipo] = 1500.0
            sin_match.append(equipo)

    if sin_match:
        print(f"\n[AVISO] Selecciones SIN histórico encontrado, usando 1500 por defecto: {sin_match}")
        print("   Revisa si necesitan una entrada manual en ELO_INICIAL_SIN_HISTORICO o MAPA_EQUIVALENCIAS.")

    df_resultado = pd.DataFrame(list(resultado.items()), columns=['team', 'rating'])

    # Red de seguridad final: si por cualquier motivo quedara un NaN (p.ej.
    # un hueco de datos en la fuente, como pasó con Moldova), se sustituye
    # por un valor neutro 1500 en vez de dejarlo pasar y contaminar todo el
    # cálculo de Elo posterior (un solo NaN en este fichero deja TODO el
    # ranking final en NaN, porque se propaga partido a partido).
    filas_con_nan = df_resultado['rating'].isna()
    if filas_con_nan.any():
        equipos_afectados = df_resultado.loc[filas_con_nan, 'team'].tolist()
        print(f"\n[AVISO] Rating NaN detectado para {equipos_afectados} (hueco de datos en la fuente). "
              f"Se sustituye por 1500 de forma segura.")
        df_resultado.loc[filas_con_nan, 'rating'] = 1500.0

    df_resultado = df_resultado.sort_values('rating', ascending=False).reset_index(drop=True)
    df_resultado.to_csv(RUTA_SALIDA, index=False)

    print(f"\n4. Elo inicial anclado guardado en: {RUTA_SALIDA}")
    print("-" * 40)
    print("TOP 10 Elo inicial (29/12/2022):")
    print(df_resultado.head(10).to_string(index=False))
    print("-" * 40)
    return df_resultado


if __name__ == "__main__":
    # Cuando se ejecuta como script independiente, lee los equipos
    # directamente del dataset original del usuario.
    dataset_usuario = pd.read_csv('dataset_simulador_2026.csv')
    equipos = sorted(set(dataset_usuario['home_team']) | set(dataset_usuario['away_team']))
    generar_elo_inicial(equipos)