import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="Registro Auxiliar de Comunicación",
    page_icon="📝",
    layout="centered"
)

# 2. TÍTULO Y DESCRIPCIÓN
st.title("📝 Registro de Progreso - Comunicación")
st.markdown("""
Bienvenido a la plataforma de evaluación. Al finalizar tu sesión, 
completa los datos para registrar tu progreso de aprendizaje.
""")

# 3. ENLACE A TU HOJA DE CÁLCULO
# REEMPLAZA EL ENLACE DE ABAJO POR EL DE TU PROPIA HOJA DE GOOGLE
URL_HOJA = "https://docs.google.com/spreadsheets/d/11sselcGsX_76mlaL6nK5VpJQyxXVmT9xXyMo_3IHBj0/edit?usp=sharing"

# Establecer la conexión
conn = st.connection("gsheets", type=GSheetsConnection)

# Intentar leer los datos actuales de la hoja
try:
    df_existente = conn.read(spreadsheet=URL_HOJA, usecols=[0, 1, 2, 3, 4])
    df_existente = df_existente.dropna(how="all")
except Exception:
    # Si la hoja está vacía, creamos la estructura básica
    df_existente = pd.DataFrame(columns=["Fecha", "Estudiante", "Sesión", "Competencia", "Nota"])

# --- SECCIÓN A: FORMULARIO PARA EL ESTUDIANTE ---
st.subheader("👨‍🎓 Formulario de Salida")

with st.form("registro_notas"):
    nombre = st.text_input("Nombre y Apellido del Estudiante:")
    
    sesion = st.selectbox("Selecciona la Sesión de hoy:", [
        "Sesión 1: Comprensión de textos argumentativos",
        "Sesión 2: Elaboración de ensayos",
        "Sesión 3: El debate y la expresión oral"
    ])
    
    competencia = st.selectbox("Competencia trabajada:", [
        "Lee diversos tipos de textos escritos",
        "Escribe diversos tipos de textos",
        "Se comunica oralmente en su lengua materna"
    ])
    
    # Aquí el estudiante pone su nota o el resultado de su práctica
    nota = st.number_input("Calificación obtenida (0-20):", min_value=0, max_value=20, step=1)
    
    boton_enviar = st.form_submit_button("Registrar mi nota")

    if boton_enviar:
        if nombre.strip() == "":
            st.error("Por favor, escribe tu nombre antes de enviar.")
        else:
            # Crear la nueva fila con los datos
            nueva_fila = pd.DataFrame([{
                "Fecha": datetime.date.today().strftime("%d/%m/%Y"),
                "Estudiante": nombre,
                "Sesión": sesion,
                "Competencia": competencia,
                "Nota": nota
            }])
            
            # Unir los datos nuevos con los que ya existían
            df_final = pd.concat([df_existente, nueva_fila], ignore_index=True)
            
            # Actualizar la hoja de Google Sheets
            conn.update(spreadsheet=URL_HOJA, data=df_final)
            
            st.success(f"¡Excelente trabajo, {nombre}! Tu nota ha sido registrada.")
            st.balloons()

# --- SECCIÓN B: VISTA DEL DOCENTE (OPCIONAL) ---
st.divider()
with st.expander("📊 Ver Registro Auxiliar (Solo Docente)"):
    if not df_existente.empty:
        st.write("Aquí puedes ver el progreso acumulado de todos los estudiantes:")
        st.dataframe(df_existente)
        
        # Un pequeño gráfico para ver promedios
        st.subheader("Promedio por Competencia")
        promedios = df_existente.groupby("Competencia")["Nota"].mean()
        st.bar_chart(promedios)
    else:
        st.info("Aún no hay datos registrados en la hoja de cálculo.")
