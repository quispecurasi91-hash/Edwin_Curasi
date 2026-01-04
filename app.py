import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Registro de Notas", page_icon="📝")
st.title("📝 Registro de Notas")

# Conexión
conn = st.connection("gsheets", type=GSheetsConnection)

# Formulario
with st.form(key="my_form"):
    nombre = st.text_input("Nombre del Estudiante")
    nota = st.number_input("Nota", min_value=0, max_value=20)
    boton_enviar = st.form_submit_button("Registrar")

if boton_enviar:
    if nombre:
        try:
            # 1. LEER DATOS ACTUALES (ttl=0 es vital para no leer datos viejos)
            df_previo = conn.read(worksheet="Sheet1", ttl=0)
            
            # Limpiar datos vacíos si los hay
            df_previo = df_previo.dropna(how="all")

            # 2. CREAR NUEVO REGISTRO
            nuevo_registro = pd.DataFrame([{"Estudiante": nombre, "Nota": nota}])
            
            # 3. UNIR (Si la hoja estaba vacía, solo usa el nuevo)
            if df_previo.empty:
                df_final = nuevo_registro
            else:
                df_final = pd.concat([df_previo, nuevo_registro], ignore_index=True)
            
            # 4. ACTUALIZAR LA HOJA
            conn.update(worksheet="Sheet1", data=df_final)
            
            st.success(f"✅ ¡Registrado! Ahora hay {len(df_final)} alumnos en la lista.")
            st.balloons() # Animación para confirmar
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Escribe un nombre.")

# Visualización
st.divider()
if st.button("Ver lista completa"):
    df_ver = conn.read(worksheet="Sheet1", ttl=0)
    st.dataframe(df_ver)
