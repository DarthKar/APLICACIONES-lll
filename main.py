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
    Genera un gráfico de la evolución temporal del volumen de madera por especie y tipo de producto.
    """
    try:
        # Obtener la lista de especies disponibles
        especies = df['ESPECIE'].unique()

        # Crear un selector para elegir la especie
        especie_seleccionada = st.selectbox('Selecciona la especie para analizar su evolución temporal', especies)

        # Filtrar los tipos de producto disponibles para la especie seleccionada
        tipos_producto_disponibles = df[df['ESPECIE'] == especie_seleccionada]['TIPO PRODUCTO'].unique()

        # Crear un selector para elegir el tipo de producto, basado en los tipos de producto disponibles para la especie
        tipo_producto_seleccionado = st.selectbox('Selecciona el tipo de producto', tipos_producto_disponibles)

        # Filtrar el DataFrame por la especie y tipo de producto seleccionados
        df_filtrado = df[(df['ESPECIE'] == especie_seleccionada) & (df['TIPO PRODUCTO'] == tipo_producto_seleccionado)]

        # Agrupar y calcular el volumen por año, especie y tipo de producto
        evolucion = df_filtrado.groupby(['AÑO', 'ESPECIE', 'TIPO PRODUCTO'])['VOLUMEN M3'].sum().unstack()

        # Crear el gráfico
        fig, ax = plt.subplots(figsize=(12, 8))
        evolucion.plot(ax=ax)
        ax.set(xlabel='Año', ylabel='Volumen (m³)')
        ax.set_title(f'Evolución Temporal del Volumen de Madera para la Especie {especie_seleccionada} y Tipo de Producto {tipo_producto_seleccionado}', fontsize=16)

        # Mostrar el gráfico en Streamlit
        st.pyplot(fig)

    except Exception as e:
        st.error(f"Error al generar el gráfico de evolución temporal: {e}")

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
def generar_mapa_top_10_municipios(df):
    """
    Genera un mapa de Colombia con los diez municipios con mayor movilización de madera.
    """
    try:
        # Cargar el dataset de coordenadas de los municipios
        url_coordenadas = "https://github.com/Darkblack595/Apps_streamlit/raw/main/DIVIPOLA-_C_digos_municipios_geolocalizados_20250217.csv"
        df_coordenadas = pd.read_csv(url_coordenadas)

        # Convertir los nombres de los municipios a minúsculas en ambos datasets
        df['MUNICIPIO'] = df['MUNICIPIO'].str.lower()
        df_coordenadas['NOM_MPIO'] = df_coordenadas['NOM_MPIO'].str.lower()

        # Agrupar los volúmenes de madera por municipio
        vol_por_municipio = df.groupby('MUNICIPIO')['VOLUMEN M3'].sum().reset_index()

        # Ordenar y seleccionar los 10 municipios con mayor volumen
        top_10_municipios = vol_por_municipio.sort_values(by='VOLUMEN M3', ascending=False).head(10)

        # Unir los datos de los municipios con mayor volumen con las coordenadas
        top_10_municipios = top_10_municipios.merge(
            df_coordenadas,
            left_on='MUNICIPIO',
            right_on='NOM_MPIO',
            how='left'
        )

        # Crear un GeoDataFrame de los municipios top 10
        top_10_geo = gpd.GeoDataFrame(top_10_municipios, geometry=gpd.GeoSeries.from_wkt(top_10_municipios['Geo Municipio']))

        # Mostrar el mapa
        fig, ax = plt.subplots(figsize=(10, 8))
        colombia.plot(ax=ax, color='lightgrey')
        top_10_geo.plot(ax=ax, color='red', markersize=50)
        ax.set_title("Top 10 Municipios con Mayor Movilización de Madera", fontsize=16)
        st.pyplot(fig)

    except Exception as e:
        st.error(f"Error al generar el mapa: {e}")

# Interfaz en Streamlit
pagina = st.sidebar.selectbox("Selecciona una opción", ["Mapa de calor", "Análisis por especie", "Volumen por municipio", "Especies con menor volumen", "Municipios con mayor volumen"])

if pagina == "Mapa de calor":
    generar_mapa_calor(df)
elif pagina == "Análisis por especie":
    grafico_especies(df)
elif pagina == "Volumen por municipio":
    volumen_por_municipio(df)
elif pagina == "Especies con menor volumen":
    especies_menor_volumen(df)
elif pagina == "Municipios con mayor volumen":
    generar_mapa_top_10_municipios(df)
