import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Configuración
st.set_page_config(page_title="Registro Auxiliar", layout="centered")
st.title("📝 Registro de Notas")

# 1. Conexión
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Formulario
with st.form(key="form_registro"):
    nombre = st.text_input("Nombre del Estudiante:")
    comp = st.selectbox("Competencia:", ["Lee diversos textos", "Escribe diversos textos", "Se comunica oralmente"])
    sesion_nombre = st.text_input("Nombre de la Sesión:")
    calificacion = st.number_input("Nota (0-20):", min_value=0, max_value=20, step=1)
    
    boton_enviar = st.form_submit_button("Guardar Registro")

# 3. Lógica para añadir datos
if boton_enviar:
    if nombre.strip() != "" and sesion_nombre.strip() != "":
        try:
            # LEER: Obtenemos lo que ya hay en el Excel
            # ttl=0 es obligatorio para que no use datos viejos de la memoria
            df_existente = conn.read(worksheet="Sheet1", ttl=0)
            
            # Limpiar el Excel de filas vacías
            df_existente = df_existente.dropna(how="all")

            # CREAR: La nueva fila con los nombres EXACTOS de tus encabezados
            nueva_fila = pd.DataFrame([{
                "Fecha": datetime.now().strftime("%d/%m/%Y"),
                "Estudiante": nombre,
                "Competencia": comp,
                "Sesion": sesion_nombre,
                "Nota": calificacion
            }])
            
            # UNIR: Si está vacío, el nuevo es el primero. Si no, se pega abajo.
            if df_existente.empty:
                df_final = nueva_fila
            else:
                df_final = pd.concat([df_existente, nueva_fila], ignore_index=True)
            
            # ACTUALIZAR: Se envía la lista completa al Excel
            conn.update(worksheet="Sheet1", data=df_final)
            
            st.success(f"✅ ¡Registrado! {nombre} se añadió a la lista.")
            st.balloons()
            
        except Exception as e:
            st.error(f"Hubo un problema: {e}")
    else:
        st.warning("⚠️ Completa el nombre y la sesión.")

# 4. Ver registros
st.divider()
if st.button("🔄 Ver Registro Auxiliar"):
    # Volvemos a leer para mostrar lo último
    df_ver = conn.read(worksheet="Sheet1", ttl=0)
    if not df_ver.empty:
        st.dataframe(df_ver, use_container_width=True)
    else:
        st.info("La hoja está vacía.")
