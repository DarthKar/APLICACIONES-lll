import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import folium_static
import matplotlib.pyplot as plt
import seaborn as sns

# Configuración de la aplicación
st.title("Análisis de Madera Movilizada en Colombia")

# Cargar el dataset desde GitHub
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/DarthKar/APLICACIONES-lll/refs/heads/main/Base_de_datos_relacionada_con_madera_movilizada_proveniente_de_Plantaciones_Forestales_Comerciales_20250217.csv"
    return pd.read_csv(url)

df = load_data()

# Cargar el archivo GeoJSON de los departamentos de Colombia
@st.cache_data
def load_geojson():
    url = "https://gist.githubusercontent.com/john-guerra/43c7656821069d00dcbc/raw/be6a6e239cd5b5b803c6e7c2ec405b793a9064dd/Colombia.geo.json"
    return gpd.read_file(url)

gdf = load_geojson()

# Definición de columnas
columnas = {
    "AÑO": "AÑO",
    "SEMESTRE": "SEMESTRE",
    "TRIMESTRE": "TRIMESTRE",
    "DPTO": "DPTO",
    "MUNICIPIO": "MUNICIPIO",
    "ESPECIE": "ESPECIE",
    "TIPO PRODUCTO": "TIPO PRODUCTO",
    "FUENTE": "FUENTE",
    "VOLUMEN M3": "VOLUMEN M3"
}

# Funciones para el análisis
def analisis_especies_frecuencia(df, col_especie):
    return df[col_especie].value_counts()

def grafico_barras(data, xlabel, ylabel):
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x=data.values, y=data.index, ax=ax, palette="viridis")
    ax.set(xlabel=xlabel, ylabel=ylabel)
    ax.set_title(f'Top 10 {ylabel}', fontsize=16)
    st.pyplot(fig)

def mapa_calor(data, xlabel, ylabel):
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.heatmap(data, cmap="YlGnBu", ax=ax, annot=True, fmt=".1f", linewidths=.5, cbar_kws={'label': 'Volumen (m³)'})
    ax.set(xlabel=xlabel, ylabel=ylabel)
    ax.set_title(f'Mapa de Calor: Distribución de Volúmenes por {ylabel}', fontsize=16)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    st.pyplot(fig)

def mapa_departamentos(gdf, df, col_departamento, col_volumen):
    # Obtener los 10 departamentos con mayor volumen
    top_departamentos = df.groupby(col_departamento)[col_volumen].sum().sort_values(ascending=False).head(10)

    # Filtrar el GeoDataFrame para obtener solo los departamentos en la lista top
    gdf_top_departamentos = gdf[gdf['NOMBRE_DPT'].isin(top_departamentos.index)]

    # Crear el mapa con folium
    m = folium.Map(location=[4.570868, -74.297333], zoom_start=5)

    # Añadir los departamentos al mapa
    for _, departamento in gdf_top_departamentos.iterrows():
        folium.GeoJson(
            departamento.geometry,
            name=departamento['NOMBRE_DPT'],
            style_function=lambda x: {'fillColor': 'blue', 'color': 'black', 'weight': 2, 'fillOpacity': 0.5}
        ).add_to(m)

    folium_static(m)

# Ejecución de análisis
try:
    # Análisis de frecuencia de especies
    especies_frecuencia = analisis_especies_frecuencia(df, columnas["ESPECIE"])
    st.subheader("Especies más comunes a nivel nacional (por frecuencia)")
    st.write(especies_frecuencia.head(10))
    grafico_barras(especies_frecuencia.head(10), 'Frecuencia', 'Especie')

    # Mapa de calor por departamento
    pivot_table = df.pivot_table(values=columnas["VOLUMEN M3"], index=columnas["DPTO"], aggfunc='sum', fill_value=0)
    st.subheader("Mapa de calor: Distribución de volúmenes por departamento")
    mapa_calor(pivot_table, 'Departamento', 'Volumen (m³)')

    # Mapa de departamentos con mayor movilización de madera
    st.subheader("Mapa de departamentos con mayor movilización de madera")
    mapa_departamentos(gdf, df, columnas["DPTO"], columnas["VOLUMEN M3"])

except KeyError as e:
    st.error(f"Columna no encontrada: {e}. Verifique los nombres de las columnas.")
except Exception as e:
    st.error(f"Error inesperado: {e}")
