import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

# Forzar UTF-8 para la consola en Windows
sys.stdout.reconfigure(encoding='utf-8')

def generar_grafico_favoritos(ruta_csv_entrada, directorio_salida, top_n=15):
    """
    Lee el CSV de probabilidades y genera un gráfico de barras horizontal
    con el Top N de selecciones favoritas.
    """
    print(f"Leyendo los datos desde: {ruta_csv_entrada}...")
    
    try:
        df = pd.read_csv(ruta_csv_entrada)
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo {ruta_csv_entrada}.")
        return

    # Quedarnos solo con el Top N
    df_top = df.head(top_n).copy()

    # Configurar el estilo visual (Seaborn hace que se vea mucho más profesional)
    sns.set_theme(style="whitegrid")
    
    # Crear la figura
    plt.figure(figsize=(12, 8))
    
    # Crear el gráfico de barras horizontal (barplot)
    # Usamos una paleta de colores secuencial para destacar al primero
    ax = sns.barplot(
        x='Probabilidad_%', 
        y='Equipo', 
        data=df_top, 
        palette="crest" # Paleta elegante en tonos azules/verdes
    )
    
    # Títulos y etiquetas
    plt.title(f"Top {top_n} Favoritos para ganar el Mundial 2026", fontsize=16, fontweight='bold', pad=20)
    plt.xlabel("Probabilidad de ser Campeón (%)", fontsize=12)
    plt.ylabel("", fontsize=12) # Ocultamos el título del eje Y porque los nombres ya son evidentes
    
    # Añadir los porcentajes exactos al final de cada barra para facilitar la lectura
    for i, p in enumerate(ax.patches):
        probabilidad = df_top.iloc[i]['Probabilidad_%']
        ax.annotate(f'{probabilidad}%', 
                    (p.get_width() + 0.5, p.get_y() + p.get_height() / 2.), 
                    ha='left', va='center', 
                    fontsize=11, color='black', fontweight='bold')

    # Ajustar márgenes para que todo quepa bien
    plt.tight_layout()
    
    # Crear la carpeta de salida si no existe
    if not os.path.exists(directorio_salida):
        os.makedirs(directorio_salida)
        print(f"Carpeta '{directorio_salida}' creada.")
        
    # Guardar el gráfico en alta resolución
    ruta_imagen = os.path.join(directorio_salida, 'probabilidades_mundial.png')
    plt.savefig(ruta_imagen, dpi=300, bbox_inches='tight')
    
    print(f"✅ Gráfico generado y guardado con éxito en: {ruta_imagen}")
    
    # Mostrar el gráfico en pantalla
    plt.show()

if __name__ == "__main__":
    # Nombres de archivos y carpetas
    ARCHIVO_ENTRADA = 'probabilidades_campeon_2026.csv'
    CARPETA_SALIDA = 'graficos'
    
    # Ejecutar la función (puedes cambiar el Top 15 a Top 10 o Top 20)
    generar_grafico_favoritos(ARCHIVO_ENTRADA, CARPETA_SALIDA, top_n=15)