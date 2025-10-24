# app_dashboard.py

# Aquí solo se importan las librerías y módulos
import streamlit as st
from streamlit_folium import st_folium
from data_loader import load_data
from map_utils import load_geojson, render_folium_map

# Se configura título y layout
st.set_page_config(page_title="Dashboard CDMX", layout="wide")
st.title("🚨 Dashboard de Incidentes Delictivos – CDMX")

# === 1. Carga de datos y GeoJSON (local) ===
# Usamos el GeoJSON válido descargado del portal: "catalogo-de-colonias.json"
delegaciones = load_geojson("catalogo-de-colonias.json")
df = load_data("df_streamlit.csv")

# === 2. Controles de interfaz ===
st.sidebar.header("⚙️ Configuración del mapa")

# Selectbox para elegir alcaldía:
# - Opción "TODAS" no filtra; cualquier otra filtra por 'alcaldia_hecho'.
opcion = st.sidebar.selectbox(
    "Selecciona alcaldía (opcional):",
    ["TODAS"] + sorted(df["alcaldia_hecho"].dropna().unique())
)

# Multiselect para activar/desactivar las capas del mapa:
# - "Puntos": marcadores individuales
# - "Heatmap": mapa de calor
# Puedes elegir una o ambas. Por defecto se activa "Heatmap".
tipo_capa = st.sidebar.multiselect(
    "Capas a mostrar:",
    ["Puntos", "Heatmap"],
    default=["Heatmap"]
)

# Slider para limitar cuántos puntos se dibujan (muestreo aleatorio).
# Esto mantiene el mapa fluido cuando hay muchos registros.
num_points = st.sidebar.slider(
    "Número de puntos (muestreo)", 100, 2000, 500, step=100
)

# === 3. Filtrado ===
# Si el usuario eligió una alcaldía específica, filtramos el DataFrame
# para que solo contenga incidentes de esa alcaldía.
if opcion != "TODAS":
    df = df[df["alcaldia_hecho"] == opcion]

# Si el número de registros supera el límite seleccionado,
# tomamos una muestra aleatoria reproducible (random_state=42).
if len(df) > num_points:
    df = df.sample(num_points, random_state=42)

# === 4. Render del mapa ===
# Construimos el mapa Folium con las capas seleccionadas sobre el GeoJSON.
m = render_folium_map(
    df,
    delegaciones,
    show_points=("Puntos" in tipo_capa),
    show_heatmap=("Heatmap" in tipo_capa)
)

# Incrustamos el mapa en Streamlit
st_folium(m, width=800, height=600)
