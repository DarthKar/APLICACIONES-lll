import streamlit as st
import pandas as pd
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

# Mostrar información general del dataset
st.subheader("Vista previa del dataset")
st.write(df.head())

st.subheader("Información del dataset")
buffer = df.info(memory_usage='deep')
st.text(buffer)

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

def grafico_lineas(data, x, y, hue, xlabel, ylabel):
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=data, x=x, y=y, hue=hue, ax=ax, palette="husl")
    ax.set(xlabel=xlabel, ylabel=ylabel)
    ax.set_title(f'Evolución Temporal del Volumen Movilizado por {hue}', fontsize=16)
    st.pyplot(fig)

# Ejecución de análisis
try:
    especies_frecuencia = analisis_especies_frecuencia(df, columnas["ESPECIE"])
    st.subheader("Especies más comunes a nivel nacional (por frecuencia)")
    st.write(especies_frecuencia.head(10))
    grafico_barras(especies_frecuencia.head(10), 'Frecuencia', 'Especie')

    # Mapa de calor
    pivot_table = df.pivot_table(values=columnas["VOLUMEN M3"], index=columnas["DPTO"], aggfunc='sum', fill_value=0)
    st.subheader("Mapa de calor: Distribución de volúmenes por departamento")
    mapa_calor(pivot_table, 'Departamento', 'Volumen (m³)')

except KeyError as e:
    st.error(f"Columna no encontrada: {e}. Verifique los nombres de las columnas.")
except Exception as e:
    st.error(f"Error inesperado: {e}")
