import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Registro Auxiliar", layout="wide")

st.title("📝 Registro Auxiliar de Notas")

# 1. Conexión
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Formulario de entrada
with st.form(key="formulario_registro"):
    col1, col2 = st.columns(2)
    
    with col1:
        nombre = st.text_input("Nombre del Estudiante:")
        competencia = st.selectbox("Competencia:", [
            "Lee diversos tipos de textos escritos",
            "Escribe diversos tipos de textos",
            "Se comunica oralmente"
        ])
    
    with col2:
        sesion = st.text_input("Sesión / Actividad:")
        nota = st.number_input("Calificación (0-20):", min_value=0, max_value=20, step=1)
    
    boton_guardar = st.form_submit_button("Registrar en Excel")

# 3. Lógica para GUARDAR (Append)
if boton_guardar:
    if nombre.strip() != "" and sesion.strip() != "":
        try:
            # LEER lo que ya existe
            df_existente = conn.read(worksheet="Sheet1", ttl=0)
            
            # Limpiar filas vacías que Google Sheets a veces añade
            df_existente = df_existente.dropna(how="all")

            # CREAR la nueva fila (Asegúrate de que los nombres coincidan con el Excel)
            nueva_fila = pd.DataFrame([{
                "Fecha": datetime.now().strftime("%d/%m/%Y"),
                "Estudiante": nombre,
                "Competencia": competencia,
                "Sesion": sesion,
                "Calificacion": nota
            }])
            
            # CONCATENAR (Unir viejo + nuevo)
            df_final = pd.concat([df_existente, nueva_fila], ignore_index=True)
            
            # SUBIR al Excel
            conn.update(worksheet="Sheet1", data=df_final)
            
            st.success(f"✅ ¡Registrado con éxito! {nombre} ha sido añadido.")
            st.balloons()
            
        except Exception as e:
            st.error(f"Error crítico: {e}")
    else:
        st.warning("⚠️ Por favor, completa el nombre y la sesión.")

# 4. Visualización
st.divider()
if st.button("🔄 Actualizar y Ver Tabla"):
    df_ver = conn.read(worksheet="Sheet1", ttl=0)
    st.dataframe(df_ver, use_container_width=True)
