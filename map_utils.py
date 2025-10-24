# map_utils.py (versión mínima, 100% local)
import folium
from folium.plugins import HeatMap
import geopandas as gpd
import streamlit as st

def load_geojson(path: str):
    """Carga un GeoJSON local y lo regresa como GeoDataFrame (sin usar red)."""
    try:
        gdf = gpd.read_file(path)
        # Asegurar WGS84 para folium si viene con otro CRS
        if gdf.crs is not None and gdf.crs.to_epsg() != 4326:
            gdf = gdf.to_crs(epsg=4326)
        st.success(f"✅ GeoJSON cargado: {path}")
        return gdf
    except Exception as e:
        st.error(f"❌ Error al leer el GeoJSON local: {e}")
        st.stop()

def render_folium_map(df, delegaciones, show_points=True, show_heatmap=True):
    """Construye un mapa Folium con límites y capas."""
    m = folium.Map(location=[19.4326, -99.1332], zoom_start=11, tiles="Cartodb positron")

    # Tooltip mínimo: intentamos 'colonia', si no existe usamos 'alc'; si no, sin tooltip
    tooltip = None
    try:
        if "colonia" in delegaciones.columns:
            tooltip = folium.GeoJsonTooltip(fields=["colonia"], aliases=["Colonia:"])
        elif "alc" in delegaciones.columns:
            tooltip = folium.GeoJsonTooltip(fields=["alc"], aliases=["Alcaldía:"])
    except Exception:
        tooltip = None

    folium.GeoJson(
        delegaciones,
        name="Límites CDMX",
        style_function=lambda x: {"color": "gray", "weight": 1, "fillOpacity": 0.05},
        tooltip=tooltip,
    ).add_to(m)

    if show_points:
        for _, row in df.iterrows():
            folium.CircleMarker(
                location=[row["latitud"], row["longitud"]],
                radius=2, color="red", fill=True, fill_opacity=0.6
            ).add_to(m)

    if show_heatmap:
        heat_data = df[["latitud", "longitud"]].values.tolist()
        HeatMap(heat_data, radius=10, blur=15, min_opacity=0.3).add_to(m)

    folium.LayerControl().add_to(m)
    return m
