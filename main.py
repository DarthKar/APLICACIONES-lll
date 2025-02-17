import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
from shapely.geometry import Point

# Configuración de la aplicación
st.title("Análisis de Madera Movilizada en Colombia")

# Cargar el dataset principal desde GitHub
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

colombia = load_geojson()

# Cargar el archivo CSV con las coordenadas de los municipios
@st.cache_data
def load_municipios_data():
    url = "https://raw.githubusercontent.com/DarthKar/APLICACIONES-lll/refs/heads/main/DIVIPOLA-_C_digos_municipios_geolocalizados_20250217.csv"
    municipios = pd.read_csv(url)
    # Convertir la columna 'Geo Municipio' a geometrías
    municipios['geometry'] = gpd.GeoSeries.from_wkt(municipios['Geo Municipio'])
    # Convertir los nombres de los municipios a mayúsculas
    municipios['NOM_MPIO'] = municipios['NOM_MPIO'].str.upper()
    return gpd.GeoDataFrame(municipios, geometry='geometry')

municipios = load_municipios_data()

# Verificar que el GeoDataFrame no esté vacío
st.write("Municipios GeoDataFrame:", municipios.head())

# Función para generar el mapa de calor
def generar_mapa_calor(df):
    """
    Genera un mapa de calor de volúmenes de madera por departamento.
    """
    try:
        df['DPTO'] = df['DPTO'].str.upper()

        # Agrupar los volúmenes de madera por departamento
        vol_por_dpto = df.groupby('DPTO')['VOLUMEN M3'].sum().reset_index()

        # Unir los datos de volumen con el GeoDataFrame
        df_geo = colombia.merge(vol_por_dpto, left_on='NOMBRE_DPT', right_on='DPTO')

        # Crear la figura y el eje
        fig, ax = plt.subplots(figsize=(10, 8))

        # Graficar el mapa de calor
        df_geo.plot(column='VOLUMEN M3', cmap='OrRd', linewidth=0.8, edgecolor='k', legend=True, ax=ax)

        # Establecer el título
        ax.set_title("Distribución de volúmenes de madera por departamento", fontsize=16)

        # Mostrar el mapa en Streamlit
        st.pyplot(fig)

    except Exception as e:
        st.error(f"Error al generar el mapa de calor: {e}")

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
# Función para visualizar los municipios con mayor movilización de madera
def mapa_municipios_mayor_movilizacion(df, municipios):
    """
    Visualiza en un mapa los diez municipios con mayor movilización de madera, usando solo puntos.
    """
    try:
        # Calcular el volumen total por municipio
        volumen_municipio = df.groupby('MUNICIPIO')['VOLUMEN M3'].sum().reset_index()

        # Convertir los nombres de los municipios a mayúsculas
        volumen_municipio['MUNICIPIO'] = volumen_municipio['MUNICIPIO'].str.upper()

        # Identificar los 10 municipios con mayor volumen
        top_municipios = volumen_municipio.nlargest(10, 'VOLUMEN M3')

        # Unir con las coordenadas de los municipios
        top_municipios_coords = top_municipios.merge(municipios, left_on='MUNICIPIO', right_on='NOM_MPIO')

        # Crear la figura y el eje
        fig, ax = plt.subplots(figsize=(10, 8))

        # Graficar el mapa de Colombia (solo los límites del país)
        colombia.boundary.plot(ax=ax, linewidth=1, edgecolor='black')

        # Graficar los puntos de los municipios con mayor movilización
        top_municipios_coords.plot(ax=ax, color='red', markersize=50, alpha=0.7, marker='o', legend=True)

        # Añadir etiquetas a los municipios
        for _, row in top_municipios_coords.iterrows():
            ax.text(row['geometry'].x + 0.1, row['geometry'].y + 0.1, row['NOM_MPIO'], fontsize=9, ha='right', color='black')

        # Establecer el título y las etiquetas
        ax.set_title("Municipios con Mayor Movilización de Madera", fontsize=16)
        ax.set_xlabel("Longitud")
        ax.set_ylabel("Latitud")

        # Mostrar el mapa en Streamlit
        st.pyplot(fig)

    except Exception as e:
        st.error(f"Error al generar el mapa de municipios: {e}")



# Ejecución de análisis
try:
    # Mapa de calor por departamento
    st.subheader("Mapa de Calor: Distribución de Volúmenes por Departamento")
    generar_mapa_calor(df)

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
    mapa_municipios_mayor_movilizacion(df, municipios)

except KeyError as e:
    st.error(f"Columna no encontrada: {e}. Verifique los nombres de las columnas.")
except Exception as e:
    st.error(f"Error inesperado: {e}")
