import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Configuración de página
st.set_page_config(page_title="Plataforma Educativa - Comunicación", layout="wide")

# Conexión
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    try:
        df = conn.read(worksheet="DATOS", ttl=0)
        return df.dropna(how="all")
    except:
        return pd.DataFrame(columns=["Fecha", "Estudiante", "Sesion", "Tema", "Nota", "Aciertos", "Desaciertos"])

# --- ESTILOS DE SEMÁFORO ---
def mostrar_semaforo(nota):
    if nota >= 14:
        st.success(f"🟢 LOGRADO ({nota}) - ¡Excelente trabajo, dominas el tema!")
    elif 11 <= nota <= 13:
        st.warning(f"🟡 EN PROCESO ({nota}) - Vas por buen camino, revisa los aciertos.")
    else:
        st.error(f"🔴 EN INICIO ({nota}) - Necesitas reforzar este tema con tu profesor.")

# --- NAVEGACIÓN ---
rol = st.sidebar.radio("Ir a:", ["🎓 Panel del Estudiante", "👨‍🏫 Panel del Docente"])

# ==========================================
# PANEL DEL ESTUDIANTE
# ==========================================
if rol == "🎓 Panel del Estudiante":
    st.title("🚀 Mi Espacio de Aprendizaje")
    
    nombre = st.text_input("Ingresa tu nombre completo para comenzar:").strip()
    
    if nombre:
        sesion_selec = st.selectbox("Selecciona la Sesión de hoy:", [
            "SESIÓN 1 - La anécdota y su estructura",
            "SESIÓN 2 - Conectores de secuencia y contraste",
            "SESIÓN 5 - Uso de la mayúscula",
            "SESIÓN 6 - La sílaba"
        ])
        
        st.divider()
        
        # --- ACTIVIDAD SESIÓN 1 ---
        if "SESIÓN 1" in sesion_selec:
            st.header("📝 Actividad: Exploramos la Anécdota")
            st.info("Criterio: Reconoce la estructura y propósito de la anécdota.")
            
            p1 = st.radio("1. ¿Cuál es el propósito principal de una anécdota?", 
                         ["Informar sobre una noticia", "Contar un hecho curioso o divertido", "Dar instrucciones"])
            p2 = st.multiselect("2. Selecciona las partes de la estructura de la anécdota:", 
                               ["Inicio", "Nudo", "Ingredientes", "Desenlace", "Moraleja"])
            
            if st.button("Enviar Actividad S1"):
                aciertos = []
                desaciertos = []
                puntos = 0
                
                if p1 == "Contar un hecho curioso o divertido": 
                    puntos += 10
                    aciertos.append("Identifica el propósito")
                else: desaciertos.append("Confunde el propósito de la anécdota")
                
                if set(p2) == {"Inicio", "Nudo", "Desenlace"}: 
                    puntos += 10
                    aciertos.append("Reconoce la estructura")
                else: desaciertos.append("Error en identificar las partes (Inicio, Nudo, Desenlace)")
                
                # Guardar
                nueva_data = pd.DataFrame([{"Fecha": datetime.now().strftime("%d/%m/%Y"), "Estudiante": nombre, "Sesion": "Sesión 1", "Tema": "La Anécdota", "Nota": puntos, "Aciertos": ", ".join(aciertos), "Desaciertos": ", ".join(desaciertos)}])
                conn.update(worksheet="DATOS", data=pd.concat([cargar_datos(), nueva_data], ignore_index=True))
                st.balloons()
                mostrar_semaforo(puntos)

        # --- ACTIVIDAD SESIÓN 2 ---
        elif "SESIÓN 2" in sesion_selec:
            st.header("🔗 Actividad: Los Conectores")
            st.info("Criterio: Usa conectores de secuencia y contraste adecuadamente.")
            
            texto = "Salí de casa temprano, ________ llegué tarde porque el bus se malogró. ________, decidí tomar un taxi."
            st.code(texto)
            c1 = st.selectbox("Primer conector (Contraste):", ["y", "pero", "además"])
            c2 = st.selectbox("Segundo conector (Secuencia):", ["Luego", "Porque", "Finalmente"])
            
            if st.button("Enviar Actividad S2"):
                aciertos, desaciertos, puntos = [], [], 0
                if c1 == "pero": puntos += 10; aciertos.append("Usa bien contraste")
                else: desaciertos.append("Falla en conector de contraste")
                
                if c2 == "Luego": puntos += 10; aciertos.append("Usa bien secuencia")
                else: desaciertos.append("Falla en conector de secuencia")
                
                nueva_data = pd.DataFrame([{"Fecha": datetime.now().strftime("%d/%m/%Y"), "Estudiante": nombre, "Sesion": "Sesión 2", "Tema": "Conectores", "Nota": puntos, "Aciertos": ", ".join(aciertos), "Desaciertos": ", ".join(desaciertos)}])
                conn.update(worksheet="DATOS", data=pd.concat([cargar_datos(), nueva_data], ignore_index=True))
                mostrar_semaforo(puntos)

# ==========================================
# PANEL DEL DOCENTE
# ==========================================
else:
    st.title("👨‍🏫 Panel de Retroalimentación")
    df_docente = cargar_datos()
    
    if not df_docente.empty:
        st.subheader("Seguimiento de Logros y Dificultades")
        
        # Filtro por sesión
        filtro_sesion = st.selectbox("Filtrar por Sesión:", df_docente["Sesion"].unique())
        df_filtrado = df_docente[df_docente["Sesion"] == filtro_sesion]
        
        for index, row in df_filtrado.iterrows():
            with st.expander(f"👤 {row['Estudiante']} - Nota: {row['Nota']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.success(f"**Aciertos:**\n{row['Aciertos']}")
                with col2:
                    st.error(f"**Para mejorar:**\n{row['Desaciertos']}")
                st.info(f"📅 Fecha: {row['Fecha']} | 📚 Tema: {row['Tema']}")
        
        st.divider()
        st.subheader("Vista General del Registro")
        st.dataframe(df_docente)
    else:
        st.warning("Aún no hay actividades realizadas.")
