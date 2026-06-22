"""
Simulador del Mundial 2026 (formato de 48 equipos) - VERSIÓN PURA DESDE CERO.

FORMATO REAL DEL TORNEO:
  - 12 grupos de 4 equipos (A-L), todos contra todos a 1 vuelta.
  - Clasifican a la fase eliminatoria: los 2 primeros de cada grupo (24) +
    los 8 MEJORES terceros de entre los 12 (8) = 32 equipos.
  - Fase eliminatoria de 32: dieciseisavos -> octavos -> cuartos -> semis -> final.
"""
import pandas as pd
import numpy as np
import sys
import json
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

# ============================================================
# 1. FIXTURE REAL: LOS 12 GRUPOS DEL MUNDIAL 2026
# ============================================================
GRUPOS_MUNDIAL_2026 = {
    'A': ['Mexico', 'South Africa', 'South Korea', 'Czech Republic'],
    'B': ['Canada', 'Bosnia and Herzegovina', 'Qatar', 'Switzerland'],
    'C': ['Brazil', 'Morocco', 'Haiti', 'Scotland'],
    'D': ['United States', 'Paraguay', 'Australia', 'Turkey'],
    'E': ['Germany', 'Curacao', 'Ivory Coast', 'Ecuador'],
    'F': ['Netherlands', 'Japan', 'Sweden', 'Tunisia'],
    'G': ['Belgium', 'Egypt', 'Iran', 'New Zealand'],
    'H': ['Spain', 'Cape Verde', 'Saudi Arabia', 'Uruguay'],
    'I': ['France', 'Senegal', 'Iraq', 'Norway'],
    'J': ['Argentina', 'Algeria', 'Austria', 'Jordan'],
    'K': ['Portugal', 'DR Congo', 'Uzbekistan', 'Colombia'],
    'L': ['England', 'Croatia', 'Ghana', 'Panama'],
}

MAPA_EQUIVALENCIAS_NOMBRES = {
    'Czech Republic': 'Czechia',
    'Curacao': 'Curaçao',
}

def normalizar_nombre(equipo, dict_elos):
    if equipo in dict_elos:
        return equipo
    alternativo = MAPA_EQUIVALENCIAS_NOMBRES.get(equipo)
    if alternativo and alternativo in dict_elos:
        return alternativo
    return equipo 

# ============================================================
# 2. CARGA DE DATOS
# ============================================================
def cargar_rankings(ruta_csv):
    df = pd.read_csv(ruta_csv)
    return dict(zip(df['Equipo'], df['Elo']))

# ============================================================
# 3. SIMULACIÓN DE UN PARTIDO (Elo + Poisson)
# ============================================================
def simular_partido(equipo_a, equipo_b, dict_elos, media_goles, es_eliminatoria=False):
    elo_a = dict_elos.get(equipo_a, 1500)
    elo_b = dict_elos.get(equipo_b, 1500)

    prob_a = 1 / (1 + 10 ** ((elo_b - elo_a) / 400))
    prob_b = 1 - prob_a

    lambda_a = media_goles * prob_a
    lambda_b = media_goles * prob_b

    goles_a = int(np.random.poisson(lambda_a))
    goles_b = int(np.random.poisson(lambda_b))

    goles_a_final, goles_b_final = goles_a, goles_b
    resultado_texto = f"{goles_a}-{goles_b}"

    if goles_a > goles_b:
        ganador = equipo_a
    elif goles_b > goles_a:
        ganador = equipo_b
    else:
        ganador = "Empate"

    if es_eliminatoria and ganador == "Empate":
        goles_a_pro = int(np.random.poisson(lambda_a / 3))
        goles_b_pro = int(np.random.poisson(lambda_b / 3))
        goles_a_final += goles_a_pro
        goles_b_final += goles_b_pro

        if goles_a_final > goles_b_final:
            ganador = equipo_a
            resultado_texto = f"{goles_a_final}-{goles_b_final} (prórroga)"
        elif goles_b_final > goles_a_final:
            ganador = equipo_b
            resultado_texto = f"{goles_a_final}-{goles_b_final} (prórroga)"
        else:
            prob_penaltis_a = prob_a * 0.15 + 0.425
            if np.random.random() < prob_penaltis_a:
                ganador = equipo_a
                resultado_texto = f"{goles_a_final}-{goles_b_final} (pen. {equipo_a})"
            else:
                ganador = equipo_b
                resultado_texto = f"{goles_a_final}-{goles_b_final} (pen. {equipo_b})"

    return {
        'equipo_a': equipo_a, 'equipo_b': equipo_b,
        'goles_a': goles_a_final, 'goles_b': goles_b_final,
        'ganador': ganador, 'resultado_texto': resultado_texto,
    }

# ============================================================
# 4. FASE DE GRUPOS
# ============================================================
def jugar_grupo(nombre_grupo, equipos, dict_elos, media_goles):
    tabla = {
        equipo: {'PJ': 0, 'PG': 0, 'PE': 0, 'PP': 0,
                 'GF': 0, 'GC': 0, 'DG': 0, 'Pts': 0}
        for equipo in equipos
    }
    enfrentamientos_directos = {}

    for i in range(len(equipos)):
        for j in range(i + 1, len(equipos)):
            eq_a, eq_b = equipos[i], equipos[j]
            # Pasamos media_goles a la simulación
            res = simular_partido(eq_a, eq_b, dict_elos, media_goles, es_eliminatoria=False)
            ga, gb = res['goles_a'], res['goles_b']

            tabla[eq_a]['PJ'] += 1
            tabla[eq_b]['PJ'] += 1
            tabla[eq_a]['GF'] += ga
            tabla[eq_a]['GC'] += gb
            tabla[eq_b]['GF'] += gb
            tabla[eq_b]['GC'] += ga

            if ga > gb:
                tabla[eq_a]['PG'] += 1
                tabla[eq_a]['Pts'] += 3
                tabla[eq_b]['PP'] += 1
                enfrentamientos_directos[(eq_a, eq_b)] = eq_a
                enfrentamientos_directos[(eq_b, eq_a)] = eq_a
            elif gb > ga:
                tabla[eq_b]['PG'] += 1
                tabla[eq_b]['Pts'] += 3
                tabla[eq_a]['PP'] += 1
                enfrentamientos_directos[(eq_a, eq_b)] = eq_b
                enfrentamientos_directos[(eq_b, eq_a)] = eq_b
            else:
                tabla[eq_a]['PE'] += 1
                tabla[eq_b]['PE'] += 1
                tabla[eq_a]['Pts'] += 1
                tabla[eq_b]['Pts'] += 1
                enfrentamientos_directos[(eq_a, eq_b)] = 'Empate'
                enfrentamientos_directos[(eq_b, eq_a)] = 'Empate'

    for equipo in tabla:
        tabla[equipo]['DG'] = tabla[equipo]['GF'] - tabla[equipo]['GC']

    def clave_orden(equipo):
        return (tabla[equipo]['Pts'], tabla[equipo]['DG'], tabla[equipo]['GF'])

    equipos_ordenados = sorted(equipos, key=clave_orden, reverse=True)

    for pos in range(len(equipos_ordenados) - 1):
        eq1, eq2 = equipos_ordenados[pos], equipos_ordenados[pos + 1]
        if clave_orden(eq1) == clave_orden(eq2):
            ganador_directo = enfrentamientos_directos.get((eq1, eq2))
            if ganador_directo == eq2:
                equipos_ordenados[pos], equipos_ordenados[pos + 1] = eq2, eq1
            elif ganador_directo == 'Empate':
                if np.random.random() < 0.5:
                    equipos_ordenados[pos], equipos_ordenados[pos + 1] = eq2, eq1

    tabla_final = pd.DataFrame(tabla).T.loc[equipos_ordenados]
    tabla_final.insert(0, 'Grupo', nombre_grupo)
    tabla_final.insert(1, 'Equipo', equipos_ordenados)
    tabla_final.insert(2, 'Posicion', range(1, len(equipos_ordenados) + 1))
    return tabla_final.reset_index(drop=True)

def jugar_fase_de_grupos(dict_elos, media_goles):
    tablas = []
    for nombre_grupo, equipos in GRUPOS_MUNDIAL_2026.items():
        equipos_normalizados = [normalizar_nombre(e, dict_elos) for e in equipos]
        tabla = jugar_grupo(nombre_grupo, equipos_normalizados, dict_elos, media_goles)
        tablas.append(tabla)
    return pd.concat(tablas, ignore_index=True)

# ============================================================
# 5. CLASIFICACIÓN: 2 PRIMEROS + 8 MEJORES TERCEROS
# ============================================================
def calcular_clasificados(tabla_grupos):
    primeros_segundos = {}
    terceros = []

    for grupo in tabla_grupos['Grupo'].unique():
        sub = tabla_grupos[tabla_grupos['Grupo'] == grupo].sort_values('Posicion')
        primeros_segundos[grupo] = [
            sub.iloc[0]['Equipo'], sub.iloc[1]['Equipo']
        ]
        fila_tercero = sub.iloc[2]
        terceros.append({
            'Grupo': grupo, 'Equipo': fila_tercero['Equipo'],
            'Pts': fila_tercero['Pts'], 'DG': fila_tercero['DG'],
            'GF': fila_tercero['GF'],
        })

    df_terceros = pd.DataFrame(terceros).sort_values(
        by=['Pts', 'DG', 'GF'], ascending=False
    ).reset_index(drop=True)

    mejores_8_terceros = df_terceros.head(8)['Equipo'].tolist()

    return primeros_segundos, mejores_8_terceros, df_terceros

# ============================================================
# 6. FASE ELIMINATORIA (dieciseisavos -> final)
# ============================================================
def construir_dieciseisavos(primeros_segundos, mejores_terceros):
    grupos_orden = list(GRUPOS_MUNDIAL_2026.keys()) 
    primeros = [primeros_segundos[g][0] for g in grupos_orden]
    segundos = [primeros_segundos[g][1] for g in grupos_orden]

    terceros_disponibles = list(mejores_terceros) 

    cruces = []
    idx_tercero = 0
    primeros_con_tercero = []
    primeros_sin_tercero = []
    for p in primeros:
        if idx_tercero < len(terceros_disponibles):
            primeros_con_tercero.append((p, terceros_disponibles[idx_tercero]))
            idx_tercero += 1
        else:
            primeros_sin_tercero.append(p)

    cruces.extend(primeros_con_tercero)

    resto = primeros_sin_tercero + segundos
    np.random.shuffle(resto) 
    for i in range(0, len(resto) - 1, 2):
        cruces.append((resto[i], resto[i + 1]))

    return cruces[:16] 

def jugar_ronda_eliminatoria(cruces, dict_elos, media_goles, nombre_ronda):
    ganadores = []
    detalle = []
    for eq_a, eq_b in cruces:
        res = simular_partido(eq_a, eq_b, dict_elos, media_goles, es_eliminatoria=True)
        ganadores.append(res['ganador'])
        detalle.append(f"{nombre_ronda}: {eq_a} {res['resultado_texto']} {eq_b}  ->  {res['ganador']}")
    return ganadores, detalle

def jugar_fase_eliminatoria(dieciseisavos, dict_elos, media_goles):
    historial = []

    ganadores_16, det = jugar_ronda_eliminatoria(dieciseisavos, dict_elos, media_goles, "Dieciseisavos")
    historial += det

    octavos = [(ganadores_16[i], ganadores_16[i + 1]) for i in range(0, len(ganadores_16), 2)]
    ganadores_8, det = jugar_ronda_eliminatoria(octavos, dict_elos, media_goles, "Octavos")
    historial += det

    cuartos = [(ganadores_8[i], ganadores_8[i + 1]) for i in range(0, len(ganadores_8), 2)]
    ganadores_4, det = jugar_ronda_eliminatoria(cuartos, dict_elos, media_goles, "Cuartos")
    historial += det

    semis = [(ganadores_4[i], ganadores_4[i + 1]) for i in range(0, len(ganadores_4), 2)]
    ganadores_2, det = jugar_ronda_eliminatoria(semis, dict_elos, media_goles, "Semifinal")
    historial += det

    final = [(ganadores_2[0], ganadores_2[1])]
    campeon, det = jugar_ronda_eliminatoria(final, dict_elos, media_goles, "FINAL")
    historial += det

    return campeon[0], historial

# ============================================================
# 7. SIMULACIÓN COMPLETA DE UN MUNDIAL (1 iteración)
# ============================================================
def simular_mundial_una_vez(dict_elos, media_goles, verbose=False):
    tabla_grupos = jugar_fase_de_grupos(dict_elos, media_goles)
    primeros_segundos, mejores_terceros, _ = calcular_clasificados(tabla_grupos)
    dieciseisavos = construir_dieciseisavos(primeros_segundos, mejores_terceros)
    campeon, historial = jugar_fase_eliminatoria(dieciseisavos, dict_elos, media_goles)

    if verbose:
        print("\n".join(historial))
        print(f"\n CAMPEÓN: {campeon}")

    return campeon, tabla_grupos

# ============================================================
# 8. SIMULACIÓN MONTE CARLO (N iteraciones -> probabilidades)
# ============================================================
def simular_mundial_completo(ruta_rankings_elo, config, n_simulaciones=10000):
    print("1. Cargando ratings Elo...")
    dict_elos = cargar_rankings(ruta_rankings_elo)
    
    # Extraemos la media de goles del JSON de configuración
    media_goles = config["parametros_simulacion"]["media_goles_partido"]

    print(f"2. Ejecutando {n_simulaciones} simulaciones del torneo completo desde cero...")
    conteo_campeon = defaultdict(int)

    for i in range(n_simulaciones):
        campeon, _ = simular_mundial_una_vez(dict_elos, media_goles, verbose=False)
        conteo_campeon[campeon] += 1
        if (i + 1) % max(1, n_simulaciones // 10) == 0:
            print(f"   ... {i + 1}/{n_simulaciones} simulaciones completadas")

    df_probabilidades = pd.DataFrame([
        {'Equipo': equipo, 'Veces_Campeon': veces,
         'Probabilidad_%': round(100 * veces / n_simulaciones, 2)}
        for equipo, veces in conteo_campeon.items()
    ]).sort_values('Probabilidad_%', ascending=False).reset_index(drop=True)

    return df_probabilidades

# ============================================================
# EJECUCIÓN AISLADA (Para testing directo del archivo)
# ============================================================
if __name__ == "__main__":
    # Función auxiliar para cargar el config si se ejecuta este archivo directamente
    def cargar_config_local():
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
            
    configuracion_local = cargar_config_local()
    
    df_resultado = simular_mundial_completo(
        ruta_rankings_elo='rankings_elo_2026.csv',
        config=configuracion_local,
        n_simulaciones=5000,   
    )

    print("\n" + "=" * 50)
    print("PROBABILIDAD DE SER CAMPEÓN DEL MUNDIAL 2026")
    print("=" * 50)
    print(df_resultado.head(20).to_string(index=False))

    df_resultado.to_csv('probabilidades_campeon_2026.csv', index=False)
    print("\nResultado completo guardado en: probabilidades_campeon_2026.csv")