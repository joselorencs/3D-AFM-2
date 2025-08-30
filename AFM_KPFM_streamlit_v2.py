import streamlit as st
import numpy as np
import plotly.graph_objects as go
import base64

# --- Fondo con imagen ---
def set_background(png_file):
    with open(png_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# --- Función para leer los archivos ---
def read_txt_as_matrix(file_path):
    lines = file_path.read().decode("utf-8").splitlines()
    width = height = None
    data_lines = []
    for line in lines:
        if line.startswith("# Anchura:") or line.startswith("# Width:"):
            width = float(line.split()[2])
        elif line.startswith("# Altura:") or line.startswith("# Height:"):
            height = float(line.split()[2])
        elif not line.startswith("#") and line.strip():
            data_lines.append(line.strip())
    matrix = np.array([list(map(float, l.split())) for l in data_lines])
    return matrix, width, height

# --- Funciones de gráficos ---
def plot_3d_surface_topography(data, scale_x, scale_y, colorscale="Hot"):
    x = np.linspace(0, scale_x, data.shape[1])
    y = np.linspace(0, scale_y, data.shape[0])
    z = data * 1e9

    fig = go.Figure(data=[
        go.Surface(x=x, y=y, z=z, colorscale=colorscale,
                   colorbar=dict(title="Height (nm)"))
    ])
    fig.update_layout(
                      scene=dict(xaxis_title="X (µm)", yaxis_title="Y (µm)", zaxis_title="Z (nm)"),
                      margin=dict(l=0, r=0, b=0, t=40))
    return fig

def plot_3d_surface_with_overlay(topography, potential, colorscale, scale_x, scale_y, cmin=0.0, cmax=1.0):
    x = np.linspace(0, scale_x, topography.shape[1])
    y = np.linspace(0, scale_y, topography.shape[0])
    z = topography * 1e9
    surface_color = np.clip(potential, cmin, cmax)

    fig = go.Figure(data=[
        go.Surface(x=x, y=y, z=z, surfacecolor=surface_color,
                   colorscale=colorscale, cmin=cmin, cmax=cmax,
                   colorbar=dict(title="Surface Potential (V)"))
    ])
    fig.update_layout(
                      scene=dict(xaxis_title="X (µm)", yaxis_title="Y (µm)", zaxis_title="Z (nm)"),
                      margin=dict(l=0, r=0, b=0, t=40))
    return fig

def plot_3d_surface_with_overlay_CAFM(topography, current, colorscale, scale_x, scale_y, cmin=0.0, cmax=0.7):
    x = np.linspace(0, scale_x, topography.shape[1])
    y = np.linspace(0, scale_y, topography.shape[0])
    z = topography * 1e9
    surface_color = np.clip(current * 1e9, cmin, cmax)

    fig = go.Figure(data=[
        go.Surface(x=x, y=y, z=z, surfacecolor=surface_color,
                   colorscale=colorscale, cmin=cmin, cmax=cmax,
                   colorbar=dict(title="Electric Current (nA)"))
    ])
    fig.update_layout(
                      scene=dict(xaxis_title="X (µm)", yaxis_title="Y (µm)", zaxis_title="Height (nm)"),
                      margin=dict(l=0, r=0, b=0, t=40))
    return fig

def plot_3d_surface_with_overlay_MFM(topography, phase, colorscale, scale_x, scale_y, cmin=0.0, cmax=15):
    x = np.linspace(0, scale_x, topography.shape[1])
    y = np.linspace(0, scale_y, topography.shape[0])
    z = topography * 1e9
    surface_color = np.clip(phase, cmin, cmax)

    fig = go.Figure(data=[
        go.Surface(x=x, y=y, z=z, surfacecolor=surface_color,
                   colorscale=colorscale, cmin=cmin, cmax=cmax,
                   colorbar=dict(title="Phase (deg)"))
    ])
    fig.update_layout(
                      scene=dict(xaxis_title="X (µm)", yaxis_title="Y (µm)", zaxis_title="Height (nm)"),
                      margin=dict(l=0, r=0, b=0, t=40))
    return fig

# --- Interfaz con Streamlit ---
set_background("streamlit_background.png")  # Fondo aplicado a TODAS las secciones

st.title("Immersive 3D visualization tool for Atomic Force Microscopy (AFM)")
st.sidebar.title("Menu")
mode = st.sidebar.radio("Select mode:", ["Main Page", "AFM Topography", 
                                         "Kelvin Probe Force Microscopy (KPFM)", 
                                         "Conductive Atomic Force Microscopy (C-AFM)", "Magnetic Force Microscopy (MFM)", "PeakForce Tapping"])

if mode == "Main Page":
    st.image("main_image.png", use_container_width=True)
    st.image("streamlit_examples.png", use_container_width=True)
    st.image("streamlit_examples2.png", use_container_width=True)
    st.image("instructions_streamlit.png", use_container_width=True)
    st.markdown("### Developed by José Lorenzo Calderón Solís")
    st.markdown('[📧 Contact: joselorencs@gmail.com](mailto:joselorencs@gmail.com)')
    st.markdown('[💼 LinkedIn](https://www.linkedin.com/in/jos%C3%A9-lorenzo-calder%C3%B3n-sol%C3%ADs-44b086341/)')

elif mode == "AFM Topography":
    colorscale = st.selectbox("Select colorscale", ["Viridis", "Plasma", "Inferno", "Magma", "Cividis",
                                                    "Greens", "Blues", "Reds", "Greys", "Turbo", "Picnic", "Jet", "Hot"])
    uploaded = st.file_uploader("Upload Topography .txt", type="txt")
    
    if uploaded:
        matrix, sx, sy = read_txt_as_matrix(uploaded)
        fig = plot_3d_surface_topography(matrix, sx, sy, colorscale)
        st.plotly_chart(fig, use_container_width=True)

elif mode == "Kelvin Probe Force Microscopy (KPFM)":
    colorscale = st.selectbox("Select colorscale", ["Viridis","Plasma","Inferno","Magma","Cividis",
                                                    "Greens","Blues","Reds","Greys","Turbo","Picnic","Jet","Hot"])
    cmin, cmax = st.slider("False color scale (V)", 0.0, 10.0, (0.0, 1.0))
    topo_file = st.file_uploader("Upload Topography .txt", type="txt")
    pot_file = st.file_uploader("Upload Surface Potential .txt", type="txt")
    
    if topo_file and pot_file:
        topo, sx, sy = read_txt_as_matrix(topo_file)
        pot, _, _ = read_txt_as_matrix(pot_file)
        fig = plot_3d_surface_with_overlay(topo, pot, colorscale, sx, sy, cmin, cmax)
        st.plotly_chart(fig, use_container_width=True)

elif mode == "Conductive Atomic Force Microscopy (C-AFM)":
    colorscale = st.selectbox("Select colorscale", ["Viridis","Plasma","Inferno","Magma","Cividis",
                                                    "Greens","Blues","Reds","Greys","Turbo","Picnic","Jet","Hot"])
    cmin, cmax = st.slider("False color scale (nA)", 0.0, 10.0, (0.0, 0.7))
    topo_file = st.file_uploader("Upload Topography .txt", type="txt")
    cur_file = st.file_uploader("Upload Electric Current .txt", type="txt")
    
    if topo_file and cur_file:
        topo, sx, sy = read_txt_as_matrix(topo_file)
        cur, _, _ = read_txt_as_matrix(cur_file)
        fig = plot_3d_surface_with_overlay_CAFM(topo, cur, colorscale, sx, sy, cmin, cmax)
        st.plotly_chart(fig, use_container_width=True)

elif mode == "Magnetic Force Microscopy (MFM)":
    colorscale = st.selectbox("Select colorscale", ["Viridis","Plasma","Inferno","Magma","Cividis",
                                                    "Greens","Blues","Reds","Greys","Turbo","Picnic","Jet","Hot"])
    cmin, cmax = st.slider("False color scale (deg)", -30.0, 30.0, (0.0, 15.0))
    topo_file = st.file_uploader("Upload Topography .txt", type="txt")
    ph_file = st.file_uploader("Upload Phase .txt", type="txt")
    
    if topo_file and ph_file:
        topo, sx, sy = read_txt_as_matrix(topo_file)
        ph, _, _ = read_txt_as_matrix(ph_file)
        fig = plot_3d_surface_with_overlay_MFM(topo, ph, colorscale, sx, sy, cmin, cmax)
        st.plotly_chart(fig, use_container_width=True)

elif mode == "PeakForce Tapping":
    pfm_mode = st.selectbox("Select property:", 
                            ["Stiffness", "Adhesion", "Indentation", "Dissipation", "Deformation"])

    # Diccionario con conversiones y rangos
    properties = {
        "Stiffness": {"units": "GPa", "factor": 1e-9, "range": (0, 50)},
        "Adhesion": {"units": "nN", "factor": 1e9, "range": (0, 500)},
        "Indentation": {"units": "nm", "factor": 1e9, "range": (0, 500)},
        "Dissipation": {"units": "keV", "factor": 1e-3, "range": (0, 100)},
        "Deformation": {"units": "nm", "factor": 1e9, "range": (0, 100)},
    }

    prop_info = properties[pfm_mode]

    colorscale = st.selectbox("Select colorscale", 
                              ["Viridis","Plasma","Inferno","Magma","Cividis",
                               "Greens","Blues","Reds","Greys","Turbo","Picnic","Jet","Hot"])
    cmin, cmax = st.slider(f"False color scale ({prop_info['units']})", 
                           float(prop_info["range"][0]), float(prop_info["range"][1]), 
                           (float(prop_info["range"][0]), float(prop_info["range"][1])))

    topo_file = st.file_uploader("Upload Topography .txt", type="txt")
    prop_file = st.file_uploader(f"Upload {pfm_mode} .txt", type="txt")

    if topo_file and prop_file:
        topo, sx, sy = read_txt_as_matrix(topo_file)
        prop, _, _ = read_txt_as_matrix(prop_file)

        # Aplicar factor de conversión
        prop = prop * prop_info["factor"]

        fig = plot_3d_surface_with_overlay(topo, prop, colorscale, sx, sy, cmin, cmax)

        # Cambiar dinámicamente el título de la barra de color
        fig.data[0].colorbar.title = f"{pfm_mode} ({prop_info['units']})"

        st.plotly_chart(fig, use_container_width=True)
