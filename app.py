import streamlit as st
import pandas as pd
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# --- Configuración de la página ---
st.set_page_config(
    page_title="Consulta de Calificaciones",
    page_icon="🎓",
    layout="wide"
)

# --- Cargar imágenes ---
portada_path = "assets/cabecera_marco_legal.png"
logo_path = "assets/logo-utn.png"

# --- Estilos CSS personalizados ---
st.markdown(
    """
    <style>
    body {
        background-color: #ffffff;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Tipografía ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

    body, h1, h2, h3, h4, h5, h6, p, span, div, a, button {
        font-family: 'Poppins', sans-serif !important;
    }
    .big-font {
        font-size: 2.5rem !important;
        font-weight: bold;
        color: #005873;
        margin-bottom: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Encabezado ---
st.image(portada_path, use_container_width=True)
st.markdown("<p class='big-font'>Consulta de Calificaciones - Marco legal de los Negocios Digitales</p>", unsafe_allow_html=True)
st.markdown("---")

# --- Cargar variables de entorno ---
load_dotenv()
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")

# --- Inicializar Supabase ---
try:
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error(f"Error al inicializar Supabase. Verifica las variables de entorno. Error: {e}")
    st.stop()

# --- Función optimizada para buscar en Supabase ---
def buscar_estudiante(search_term: str):
    """
    Búsqueda exacta por ID o email.
    Email: case-insensitive, ignora espacios.
    No permite coincidencias parciales.
    """
    try:
        # Limpia espacios
        search_term_clean = search_term.strip()

        # Email: comparar siempre en minúsculas
        email_clean = search_term_clean.lower()

        query = supabase.table('calificaciones_marco_legal_utn').select("*")

        # Si es número, buscar por ID
        if search_term_clean.isdigit():
            query = query.eq("Número de ID", search_term_clean)

        # Si contiene @, buscar por email exacto (case-insensitive)
        elif "@" in search_term_clean:
            query = query.ilike("Dirección de correo", email_clean)

        # Ejecutamos
        response = query.execute()
        return pd.DataFrame(response.data)

    except Exception as e:
        st.error(f"Error al consultar Supabase: {e}")
        return pd.DataFrame()

# --- Interfaz de búsqueda ---
search_term = st.text_input(
    "Ingresa tu **número de ID** o **correo electrónico** para consultar tu calificación:",
    placeholder="Ej: 123456 o perez@gmail",
).strip()

# --- Lógica de búsqueda ---
if search_term:
    search_results = buscar_estudiante(search_term)

    if not search_results.empty:
        st.subheader("Tu calificación:")

        # Seleccionamos las columnas necesarias
        result_to_show = search_results[[
            "Nombre", "Número de ID", "Dirección de correo",
            "Cantidad de actividades aprobadas", "Nota de concepto (40% promedio de actividades)", 
            "Nota de parciales (60% promedio de parciales)", "Nota final", "Condición"
        ]].copy()

        nombres_cortos = {
                    "Dirección de correo": "Email",
                    "Nota de concepto (40% promedio de actividades)": "Nota Concepto (40%)",
                    "Nota de parciales (60% promedio de parciales)": "Nota Parciales (60%)"
                }

        result_to_show = result_to_show.rename(columns=nombres_cortos)

        # Mostrar resultado
        st.dataframe(result_to_show, use_container_width=True, hide_index=True)

        # --- Mensajes personalizados ---
        estudiante = search_results.iloc[0]
        condicion = estudiante["Condición"]
        nombre = estudiante["Nombre"]

        if condicion == "Promoción":
            st.balloons()
            st.success(f"¡Felicitaciones, {nombre}! ¡Has promocionado la materia! 🎉")

        elif condicion == "Regular - A examen final":
            st.info(
                f"¡Hola, {nombre}! Te esperamos en la instancia de examen final 💪. "
                "Hacenos todas las consultas que necesites 🤗"
            )
        elif condicion == "Desaprobado":
            st.error(
                f"¡Hola, {nombre}! Lamentablemente no alcanzaste los objetivos mínimos para regularizar. "
                "¡No te desanimes! Te esperamos el próximo cuatrimestre para volver a intentarlo con todo 💪."
            )

    else:
        st.warning("No se encontraron resultados para el ID o email ingresado.")

else:
    st.info("Ingresa tu número de ID o email para ver tu calificación.")

st.markdown("---")

st.image(logo_path, width=250)
st.markdown("Aplicación desarrollada para la cátedra de Marco legal de los Negocios Digitales")
