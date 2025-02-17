import streamlit as st
import pandas as pd
import geopandas as gpd
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
    url = "https://raw.githubusercontent.com/Ritz38/Analisis_maderas/refs/heads/main/Colombia.geo.json"
    return gpd.read_file(url)

gdf = load_geojson()

# Función para generar el mapa de calor
def generar_mapa_calor(df):
    """Genera un mapa de calor de volúmenes de madera por departamento."""
    df['DPTO'] = df['DPTO'].str.upper()
    # Cargar el archivo GeoJSON de Colombia
    colombia = gpd.read_file('https://raw.githubusercontent.com/Ritz38/Analisis_maderas/refs/heads/main/Colombia.geo.json')

# Crear la figura y el eje
    fig, ax = plt.subplots()

# Agrupar los volúmenes de madera por departamento
    vol_por_dpto = df.groupby('DPTO')['VOLUMEN M3'].sum().reset_index()

# Unir los datos de volumen con el GeoDataFrame
    df_geo = colombia.merge(vol_por_dpto, left_on='NOMBRE_DPT', right_on='DPTO')

# Función para graficar las especies más comunes
def grafico_especies(df):
    """
    Genera un gráfico de barras de las especies más comunes.
    """
    try:
        especies_frecuencia = df['ESPECIE'].value_counts().nlargest(10)
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x=especies_frecuencia.values, y=especies_frecuencia.index, ax=ax, palette="viridis")
        ax.set(xlabel='Frecuencia', ylabel='Especie')
        ax.set_title('Top 10 Especies por Frecuencia', fontsize=16)
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Error al generar el gráfico de especies: {e}")

# Función para graficar los volúmenes más altos por especie
def grafico_volumen_especies(df):
    """
    Genera un gráfico de barras de las especies con mayor volumen movilizado.
    """
    try:
        volumen_por_especie = df.groupby('ESPECIE')['VOLUMEN M3'].sum().nlargest(10)
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x=volumen_por_especie.values, y=volumen_por_especie.index, ax=ax, palette="viridis")
        ax.set(xlabel='Volumen (m³)', ylabel='Especie')
        ax.set_title('Top 10 Especies por Volumen Movilizado', fontsize=16)
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Error al generar el gráfico de volúmenes por especie: {e}")

# Función para analizar la evolución temporal
def evolucion_temporal(df):
    """
    Genera un gráfico de la evolución temporal del volumen de madera por especie.
    """
    try:
        evolucion = df.groupby(['AÑO', 'ESPECIE'])['VOLUMEN M3'].sum().unstack()
        fig, ax = plt.subplots(figsize=(12, 8))
        evolucion.plot(ax=ax)
        ax.set(xlabel='Año', ylabel='Volumen (m³)')
        ax.set_title('Evolución Temporal del Volumen de Madera por Especie', fontsize=16)
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Error al generar el gráfico de evolución temporal: {e}")

# Función para identificar outliers
def analisis_outliers(df):
    """
    Genera un boxplot para identificar outliers en los volúmenes de madera.
    """
    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.boxplot(x=df['VOLUMEN M3'], ax=ax)
        ax.set_title('Distribución de Volúmenes de Madera', fontsize=16)
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Error al generar el análisis de outliers: {e}")

# Función para calcular el volumen por municipio
def volumen_por_municipio(df):
    """
    Calcula y muestra el volumen total de madera por municipio.
    """
    try:
        volumen_municipio = df.groupby('MUNICIPIO')['VOLUMEN M3'].sum().reset_index()
        st.subheader("Volumen Total de Madera por Municipio")
        st.write(volumen_municipio.sort_values(by='VOLUMEN M3', ascending=False))
    except Exception as e:
        st.error(f"Error al calcular el volumen por municipio: {e}")

# Función para identificar especies con menor volumen
def especies_menor_volumen(df):
    """
    Identifica y muestra las especies con menor volumen movilizado.
    """
    try:
        especies_menor_volumen = df.groupby('ESPECIE')['VOLUMEN M3'].sum().nsmallest(10).reset_index()
        st.subheader("Especies con Menor Volumen Movilizado")
        st.write(especies_menor_volumen)
    except Exception as e:
        st.error(f"Error al identificar especies con menor volumen: {e}")

# Función para visualizar los municipios con mayor movilización de madera
def mapa_municipios_mayor_movilizacion(df):
    """
    Visualiza en un mapa los diez municipios con mayor movilización de madera.
    """
    try:
        top_municipios = df.groupby('MUNICIPIO')['VOLUMEN M3'].sum().nlargest(10).reset_index()
        top_municipios_geo = gdf.merge(top_municipios, left_on='NOMBRE_MPI', right_on='MUNICIPIO')

        fig, ax = plt.subplots(figsize=(10, 8))
        top_municipios_geo.plot(column='VOLUMEN M3', cmap='OrRd', linewidth=0.8, edgecolor='k', legend=True, ax=ax)
        ax.set_title("Municipios con Mayor Movilización de Madera", fontsize=16)
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Error al generar el mapa de municipios: {e}")

# Ejecución de análisis
try:
    # Mapa de calor por departamento
    st.subheader("Mapa de Calor: Distribución de Volúmenes por Departamento")
    mapa_calor(df)

    # Gráfico de especies más comunes
    st.subheader("Especies más comunes a nivel nacional (por frecuencia)")
    grafico_especies(df)

    # Gráfico de especies con mayor volumen movilizado
    st.subheader("Especies con Mayor Volumen Movilizado")
    grafico_volumen_especies(df)

    # Evolución temporal del volumen de madera
    st.subheader("Evolución Temporal del Volumen de Madera por Especie")
    evolucion_temporal(df)

    # Análisis de outliers
    st.subheader("Análisis de Outliers en Volúmenes de Madera")
    analisis_outliers(df)

    # Volumen total por municipio
    volumen_por_municipio(df)

    # Especies con menor volumen movilizado
    especies_menor_volumen(df)

    # Mapa de municipios con mayor movilización de madera
    st.subheader("Municipios con Mayor Movilización de Madera")
    mapa_municipios_mayor_movilizacion(df)

except KeyError as e:
    st.error(f"Columna no encontrada: {e}. Verifique los nombres de las columnas.")
except Exception as e:
    st.error(f"Error inesperado: {e}")
