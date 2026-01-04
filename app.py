import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Registro de Notas", page_icon="📝")

st.title("📝 Sistema de Registro de Notas")
st.markdown("Introduce los datos del estudiante a continuación:")

# 1. Conexión con Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Formulario de entrada
with st.form(key="formulario_notas"):
    nombre = st.text_input("Nombre del Estudiante:")
    nota = st.number_input("Nota Final:", min_value=0.0, max_value=20.0, step=0.1)
    submit_button = st.form_submit_button(label="Registrar Nota")

# 3. Lógica al presionar el botón
if submit_button:
    if nombre.strip() != "":
        try:
            # LEER: Traemos lo que ya existe (ttl=0 para que sea en tiempo real)
            df_existente = conn.read(worksheet="Sheet1", ttl=0)
            
            # CREAR: Nueva fila con los datos
            nuevo_dato = pd.DataFrame([{"Estudiante": nombre, "Nota": nota}])
            
            # UNIR: Ponemos el nuevo dato debajo de los anteriores
            df_final = pd.concat([df_existente, nuevo_dato], ignore_index=True)
            
            # ACTUALIZAR: Subimos la lista completa al Excel
            conn.update(worksheet="Sheet1", data=df_final)
            
            st.success(f"✅ ¡{nombre} registrado con éxito!")
        except Exception as e:
            st.error(f"Error al conectar con Google Sheets: {e}")
    else:
        st.warning("⚠️ Por favor, escribe un nombre antes de registrar.")

# 4. Visualización de los datos registrados
st.divider()
if st.button("🔄 Ver / Actualizar Registro Auxiliar"):
    try:
        datos = conn.read(worksheet="Sheet1", ttl=0)
        if not datos.empty:
            st.subheader("Lista de Estudiantes Registrados")
            st.dataframe(datos, use_container_width=True)
        else:
            st.info("Aún no hay datos en la hoja.")
    except:
        st.error("No se pudo leer la hoja. Asegúrate de que la pestaña se llame 'Sheet1'.")
