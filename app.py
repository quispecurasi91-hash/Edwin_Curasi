import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Plataforma de Comunicación", layout="wide")

# --- CONEXIÓN ---
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    try: return conn.read(worksheet="DATOS", ttl=0).dropna(how="all")
    except: return pd.DataFrame(columns=["Fecha", "Estudiante", "Sesion", "Tema", "Nota", "Aciertos", "Desaciertos"])

def cargar_config():
    try: return conn.read(worksheet="CONFIG", ttl=0).dropna(how="all")
    except: return pd.DataFrame({"Sesion": [f"SESIÓN {i}" for i in range(1,9)], "Estado": ["Cerrado"]*8})

# --- LÓGICA DE COLOR (TERMÓMETRO) ---
def obtener_color(nota):
    if nota >= 14: return "green", "Logrado", "🟢"
    if nota >= 11: return "orange", "En Proceso", "🟡"
    return "red", "En Inicio", "🔴"

# --- NAVEGACIÓN ---
rol = st.sidebar.radio("Selecciona Rol:", ["👨‍🏫 Panel Docente", "🎓 Panel Estudiante"])

# ==========================================
# PANEL DOCENTE
# ==========================================
if rol == "👨‍🏫 Panel Docente":
    st.title("👨‍🏫 Gestión del Aula")
    tab_control, tab_retro, tab_reg = st.tabs(["🎮 Control de Sesiones", "🔍 Retroalimentación", "📋 Registro General"])
    
    with tab_control:
        st.subheader("Activar/Desactivar Actividades")
        df_conf = cargar_config()
        for i, row in df_conf.iterrows():
            col_s, col_e = st.columns([3, 1])
            nuevo_estado = col_e.selectbox(f"Estado {row['Sesion']}", ["Cerrado", "Activo"], 
                                         index=0 if row['Estado']=="Cerrado" else 1, key=f"conf_{i}")
            df_conf.at[i, "Estado"] = nuevo_estado
        
        if st.button("Guardar Configuración de Sesiones"):
            conn.update(worksheet="CONFIG", data=df_conf)
            st.success("¡Configuración actualizada! Los estudiantes ya pueden ver las sesiones activas.")

    with tab_retro:
        df_datos = cargar_datos()
        if not df_datos.empty:
            sesion_f = st.selectbox("Analizar Sesión:", df_datos["Sesion"].unique())
            est_f = df_datos[df_datos["Sesion"] == sesion_f]
            for _, r in est_f.iterrows():
                with st.expander(f"👤 {r['Estudiante']} - Nota: {r['Nota']}"):
                    st.write(f"✅ **Aciertos:** {r['Aciertos']}")
                    st.write(f"❌ **Desaciertos:** {r['Desaciertos']}")
        else: st.info("No hay datos aún.")

    with tab_reg:
        st.dataframe(cargar_datos(), use_container_width=True)

# ==========================================
# PANEL ESTUDIANTE
# ==========================================
else:
    st.title("🎓 Mi Progreso de Aprendizaje")
    nombre = st.text_input("Escribe tu nombre completo:").strip()
    
    if nombre:
        # --- TERMÓMETRO DE APRENDIZAJE ---
        df_datos = cargar_datos()
        mis_datos = df_datos[df_datos["Estudiante"] == nombre]
        
        if not mis_datos.empty:
            promedio = mis_datos["Nota"].mean()
            color, estado, emoji = obtener_color(promedio)
            st.markdown(f"### Mi Termómetro de Aprendizaje: {emoji} {estado}")
            st.progress(promedio / 20)
        
        # --- SELECCIÓN DE SESIÓN ACTIVA ---
        df_conf = cargar_config()
        sesiones_activas = df_conf[df_conf["Estado"] == "Activo"]["Sesion"].tolist()
        
        if sesiones_activas:
            sesion_actual = st.selectbox("Selecciona la sesión que trabajaste hoy:", sesiones_activas)
            
            # --- MOTOR DE ACTIVIDADES ---
            st.divider()
            aciertos, desaciertos, puntos = [], [], 0
            
            if "SESIÓN 1" in sesion_actual:
                st.header("📖 Exploramos la Anécdota")
                p1 = st.radio("1. ¿Qué tipo de texto es la anécdota?", ["Informativo", "Narrativo", "Instructivo"])
                p2 = st.multiselect("2. ¿Qué elementos no pueden faltar?", ["Inicio", "Nudo", "Desenlace", "Receta"])
                p3 = st.selectbox("3. El propósito es contar un hecho...", ["Ficticio", "Curioso/Real", "Científico"])
                
                if st.button("Finalizar Sesión 1"):
                    if p1 == "Narrativo": puntos += 7; aciertos.append("Tipo de texto")
                    else: desaciertos.append("Tipo de texto")
                    if set(p2) == {"Inicio", "Nudo", "Desenlace"}: puntos += 7; aciertos.append("Estructura")
                    else: desaciertos.append("Estructura")
                    if p3 == "Curioso/Real": puntos += 6; aciertos.append("Propósito")
                    else: desaciertos.append("Propósito")
                    
            elif "SESIÓN 2" in sesion_actual:
                st.header("🔗 Los Conectores")
                p1 = st.selectbox("Conector de contraste:", ["Pero", "Luego", "Primero"])
                p2 = st.selectbox("Conector de secuencia:", ["Sin embargo", "Después", "Porque"])
                p3 = st.text_input("Completa: 'Estudié mucho, _____ no aprobé'").lower()
                
                if st.button("Finalizar Sesión 2"):
                    if p1 == "Pero": puntos += 7; aciertos.append("Contraste")
                    if p2 == "Después": puntos += 7; aciertos.append("Secuencia")
                    if "pero" in p3 or "mas" in p3: puntos += 6; aciertos.append("Uso práctico")
                    else: desaciertos.append("Uso práctico")

            elif "SESIÓN 5" in sesion_actual:
                st.header("🔠 Uso de la Mayúscula")
                p1 = st.checkbox("¿Se usa mayúscula después de un punto?")
                p2 = st.text_input("Escribe correctamente: 'lima es la capital de peru'")
                
                if st.button("Finalizar Sesión 5"):
                    if p1: puntos += 10; aciertos.append("Regla del punto")
                    if p2.strip() == "Lima es la capital de Perú": puntos += 10; aciertos.append("Nombres propios")
                    else: desaciertos.append("Ortografía de nombres propios")

            # --- GUARDADO AUTOMÁTICO ---
            if puntos > 0 or len(desaciertos) > 0:
                nueva_fila = pd.DataFrame([{
                    "Fecha": datetime.now().strftime("%d/%m/%Y"), "Estudiante": nombre,
                    "Sesion": sesion_actual, "Tema": "Actividad Práctica", "Nota": puntos,
                    "Aciertos": ", ".join(aciertos), "Desaciertos": ", ".join(desaciertos)
                }])
                conn.update(worksheet="DATOS", data=pd.concat([df_datos, nueva_fila], ignore_index=True))
                st.success(f"¡Actividad enviada! Tu nota es {puntos}")
                st.rerun()

        else:
            st.warning("El docente aún no ha activado actividades para hoy. ¡Atento a la clase!")
