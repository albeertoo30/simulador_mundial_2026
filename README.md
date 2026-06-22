# 🏆 Simulador Mundial 2026 | Monte Carlo & Rating Elo

Un modelo estadístico y estocástico desarrollado en Python para predecir las probabilidades de ganar la Copa del Mundo de la FIFA 2026.

El motor de simulación se basa en un sistema de **Rating Elo** dinámico calculado a partir de todos los partidos del ciclo mundialista (2022-2026), combinado con una **Distribución de Poisson** y simulaciones de **Monte Carlo** para generar las predicciones del torneo replicando el formato oficial de 48 equipos.

## Características Principales

* **Motor Elo Personalizado:** Ajusta el nivel de cada selección basándose en un registro histórico limpio, ponderando la importancia de los torneos (Mundiales, Copas Continentales, Amistosos) y la diferencia de goles.
* **Simulación Estocástica:** Utiliza la probabilidad esperada de victoria para calcular la tasa de goles esperados ($\lambda$) y muestrear resultados realistas mediante distribuciones de Poisson.
* **Formato Real 2026:** Implementa el fixture oficial de la FIFA de 12 grupos, incluyendo la clasificación de los mejores terceros y todas las rondas eliminatorias con prórrogas y penaltis.
* **Arquitectura Modular:** Diseñado con separación de responsabilidades. La lógica matemática está aislada de los parámetros de configuración (pesos, variables) centralizados en un `config.json`.
* **Pipeline Automatizado:** Un orquestador central ejecuta el proceso End-to-End (desde la limpieza de datos hasta la generación de gráficas).

## Instalación y Ejecución

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/TU_USUARIO/simulador-mundial-2026.git
   cd simulador-mundial-2026
   ```

2. **Instalar dependencias:** Asegúrate de tener Python instalado y ejecuta:
   ```bash
   pip install pandas numpy matplotlib seaborn
   ```

3. **Ejecutar la simulación:** El proyecto cuenta con un orquestador que automatiza todo el flujo. Simplemente ejecuta:
   ```bash
   python pipeline_sensibilidad.py
   ```

   Esto generará una nueva carpeta en `/experimentos/` con los rankings Elo actualizados, el CSV con las probabilidades de cada selección y un gráfico de barras `.png` con los favoritos.

## Estructura del Proyecto

```
├── config.json                 # Hiperparámetros, pesos de torneos y configuración
├── limpieza_y_eda.py           # Limpieza de datos y asignación de pesos
├── rating_elo.py               # Algoritmo de cálculo del Rating Elo
├── simulador_torneo.py         # Lógica del torneo y simulación Monte Carlo
├── visualizador.py             # Generación de gráficos (Seaborn/Matplotlib)
├── pipeline_sensibilidad.py    # Orquestador maestro del pipeline
└── README.md
```

## Stack Tecnológico

* **Lenguaje:** Python 3
* **Análisis de Datos:** Pandas, NumPy
* **Visualización:** Matplotlib, Seaborn
