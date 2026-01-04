import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Registro Secuencial", layout="centered")

st.title("📝 Registro de Estudiantes en Serie")
st.info("Introduce los datos y presiona 'Guardar'. El sistema quedará listo para el siguiente alumno.")

# 1. Conexión
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Formulario de entrada
# Usamos 'clear_on_submit=True' para que el nombre se borre al terminar y puedas escribir el siguiente rápido
with st.form(key="registro_form", clear_on_submit=True):
    nombre = st.text_input("Nombre completo del Estudiante:")
    comp = st.selectbox("Competencia:", [
        "Lee diversos tipos de textos escritos", 
        "Escribe diversos tipos de textos", 
        "Se comunica oralmente"
    ])
    actividad = st.text_input("Sesión / Actividad:")
    nota = st.number_input("Calificación:", min_value=0, max_value=20, step=1)
    
    submit = st.form_submit_button("Guardar y Continuar con otro")

# 3. Lógica de Guardado Secuencial
if submit:
    if nombre.strip() != "":
        try:
            # LEER: Traemos lo que ya existe en la pestaña DATOS
            df_actual = conn.read(worksheet="DATOS", ttl=0)
            df_actual = df_actual.dropna(how="all")

            # CREAR: La nueva fila
            nueva_fila = pd.DataFrame([{
                "Fecha": datetime.now().strftime("%d/%m/%Y"),
                "Estudiante": nombre,
                "Competencia": comp,
                "Actividad": actividad,
                "Puntaje": nota
            }])
            
            # UNIR: Ponemos el nuevo debajo de los anteriores
            df_final = pd.concat([df_actual, nueva_fila], ignore_index=True)
            
            # ACTUALIZAR: Subimos todo al Excel
            conn.update(worksheet="DATOS", data=df_final)
            
            st.success(f"✅ {nombre} guardado. ¡Puedes ingresar al siguiente!")
            
        except Exception as e:
            st.error(f"Error al guardar: {e}")
    else:
        st.warning("⚠️ El nombre no puede estar vacío.")

# 4. Tabla en tiempo real (Para que veas la secuencia)
st.divider()
st.subheader("📋 Lista de alumnos registrados hoy")
try:
    # Mostramos la tabla actualizada para confirmar que se están acumulando
    df_visualizacion = conn.read(worksheet="DATOS", ttl=0)
    if not df_visualizacion.empty:
        st.table(df_visualizacion.tail(10)) # Muestra los últimos 10 registrados
    else:
        st.write("Aún no hay alumnos en la lista.")
except:
    st.write("Conectando con la base de datos...")
