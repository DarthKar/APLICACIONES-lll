import streamlit as st
import pandas as pd

# Configuración de la aplicación
st.title("Análisis de Madera Movilizada en Colombia")

# Cargar el dataset desde GitHub
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/DarthKar/APLICACIONES-lll/refs/heads/main/Base_de_datos_relacionada_con_madera_movilizada_proveniente_de_Plantaciones_Forestales_Comerciales_20250217.csv"
    df = pd.read_csv(url)
    return df

df = load_data()

# Mostrar información general del dataset
st.subheader("Vista previa del dataset")
st.write(df.head())

st.subheader("Información del dataset")
st.write(df.info())

# Análisis de valores nulos
st.subheader("Valores nulos en el dataset")
missing_values = df.isnull().sum()
st.write(missing_values[missing_values > 0])

# Identificación de especies más comunes y volúmenes movilizados
col_especie = "Nombre_Columna_Especie"  # Reemplazar con el nombre real de la columna de especies
col_volumen = "Nombre_Columna_Volumen"  # Reemplazar con el nombre real de la columna de volumen
col_departamento = "Nombre_Columna_Departamento"  # Reemplazar con el nombre real de la columna de departamento

if col_especie in df.columns and col_volumen in df.columns:
    especies_nacionales = df.groupby(col_especie)[col_volumen].sum().sort_values(ascending=False)
    st.subheader("Especies más comunes a nivel nacional")
    st.write(especies_nacionales.head(10))

    if col_departamento in df.columns:
        especies_por_departamento = df.groupby([col_departamento, col_especie])[col_volumen].sum().reset_index()
        st.subheader("Especies más comunes por departamento")
        st.write(especies_por_departamento.head(10))
else:
    st.error("Las columnas necesarias no se encuentran en el dataset. Verifique los nombres de las columnas.")

# Determinación de interpolación
st.subheader("¿Es necesario interpolar?")
if missing_values.sum() > 0:
    st.write("Se encontraron valores nulos en el dataset. Puede ser necesario interpolar.")
else:
    st.write("No hay valores nulos en el dataset. No es necesario interpolar.")


st.subheader("Nombres de las columnas en el dataset")
st.write(df.columns)

