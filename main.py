import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import folium_static
import matplotlib.pyplot as plt
import seaborn as sns

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
    url = "https://gist.githubusercontent.com/john-guerra/43c7656821069d00dcbc/raw/3aadedf47badbdac823b00dbe259f6bc6d9e1899/colombia.geo.json"
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

def mapa_calor_departamentos(gdf, df, col_departamento, col_volumen):
    # Calcular el volumen total por departamento
    volumen_por_departamento = df.groupby(col_departamento)[col_volumen].sum()

    # Unir el GeoDataFrame con los datos de volumen
    gdf = gdf.set_index('DPTO')  # Asegúrate de que 'DPTO' es la columna correcta en tu GeoDataFrame
    gdf['VOLUMEN M3'] = volumen_por_departamento
    gdf['VOLUMEN M3'] = gdf['VOLUMEN M3'].fillna(0)

    # Crear el mapa con folium
    m = folium.Map(location=[4.570868, -74.297333], zoom_start=5)

    # Añadir los departamentos al mapa con un mapa de calor
    folium.Choropleth(
        geo_data=gdf,
        name="choropleth",
        data=gdf,
        columns=["DPTO", "VOLUMEN M3"],
        key_on="feature.properties.DPTO",
        fill_color="YlGnBu",
        fill_opacity=0.7,
        line_opacity=0.5,
        legend_name="Volumen (m³)"
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
    st.subheader("Mapa de calor: Distribución de volúmenes por departamento")
    mapa_calor_departamentos(gdf, df, columnas["DPTO"], columnas["VOLUMEN M3"])

except KeyError as e:
    st.error(f"Columna no encontrada: {e}. Verifique los nombres de las columnas.")
except Exception as e:
    st.error(f"Error inesperado: {e}")
