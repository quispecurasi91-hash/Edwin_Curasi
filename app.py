import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Panel de Control Docente", layout="wide")

# Título principal
st.title("📊 Registro Auxiliar Inteligente")

# 1. Conexión
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Cargar datos al inicio para las métricas
try:
    df_base = conn.read(worksheet="DATOS", ttl=0)
    df_base = df_base.dropna(how="all")
except:
    df_base = pd.DataFrame()

# --- BARRA LATERAL (SIDEBAR) PARA ENTRADA DE DATOS ---
with st.sidebar:
    st.header("📝 Nuevo Registro")
    with st.form(key="form_registro", clear_on_submit=True):
        nombre = st.text_input("Estudiante:")
        comp = st.selectbox("Competencia:", [
            "Lee diversos tipos de textos escritos",
            "Escribe diversos tipos de textos",
            "Se comunica oralmente"
        ])
        act = st.text_input("Actividad/Sesión:")
        nota = st.number_input("Nota (0-20):", min_value=0, max_value=20, step=1)
        
        submit = st.form_submit_button("💾 Guardar en Registro")

    st.divider()
    st.info("Consejo: Usa nombres completos para evitar confusiones en el buscador.")

# --- LÓGICA DE GUARDADO ---
if submit:
    if nombre:
        nueva_fila = pd.DataFrame([{
            "Fecha_Reg": datetime.now().strftime("%d/%m/%Y"),
            "Alumno_Nombre": nombre,
            "Competencia_Area": comp,
            "Actividad_Sesion": act,
            "Nota_Final": nota
        }])
        
        df_final = pd.concat([df_base, nueva_fila], ignore_index=True)
        conn.update(worksheet="DATOS", data=df_final)
        st.sidebar.success(f"✅ ¡{nombre} registrado!")
        st.rerun() # Recarga la app para actualizar métricas y tabla

# --- PANEL PRINCIPAL (MÉTRICAS Y TABLA) ---
if not df_base.empty:
    # 1. Métricas rápidas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Registros", len(df_base))
    with col2:
        promedio = df_base["Nota_Final"].mean()
        st.metric("Promedio Grupal", f"{promedio:.1f}")
    with col3:
        aprobados = len(df_base[df_base["Nota_Final"] >= 11])
        st.metric("Aprobados", aprobados)

    st.divider()

    # 2. Buscador y Filtros
    st.subheader("🔍 Consulta de Datos")
    busqueda = st.text_input("Buscar por nombre del estudiante:")
    
    # Aplicar filtro
    df_filtrado = df_base[df_base["Alumno_Nombre"].str.contains(busqueda, case=False, na=False)]
    
    # 3. Mostrar Tabla
    st.dataframe(df_filtrado, use_container_width=True)

    # 4. Botón de Descarga
    csv = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar esta vista en CSV",
        data=csv,
        file_name=f"registro_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )
else:
    st.warning("Aún no hay datos registrados. Usa el panel de la izquierda para empezar.")
