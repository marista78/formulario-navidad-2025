import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import plotly.express as px
import plotly.graph_objects as go

# Configuración de Google Sheets
SHEET_ID = "1qRSogtdIlpjupoTVwTd-MqUkXXjwnomdDuP9qwWLEbg"
PASSWORD_ADMIN = "navidad2025"

# Función para hacer scroll al inicio
def scroll_to_top():
    st.markdown("""
        <script>
        window.parent.document.querySelector('section.main').scrollTo({
            top: 0,
            behavior: 'smooth'
        });
        </script>
    """, unsafe_allow_html=True)

# Función para obtener credenciales
def obtener_credenciales():
    try:
        # PRIMERO: Intentar leer desde secrets (Streamlit Cloud)
        if hasattr(st, 'secrets') and 'gcp_service_account' in st.secrets:
            return dict(st.secrets['gcp_service_account'])
        
        # SEGUNDO: Si no hay secrets, intentar archivo local (solo para desarrollo)
        else:
            import json
            import os
            
            if os.path.exists('credenciales.json'):
                with open('credenciales.json') as f:
                    return json.load(f)
            else:
                st.error("❌ No se encontraron credenciales. Por favor configura los secrets en Streamlit Cloud.")
                return None
                
    except Exception as e:
        st.error(f"Error al cargar credenciales: {e}")
        return None

# Función para conectar a Google Sheets
@st.cache_resource
def conectar_google_sheets():
    try:
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        
        creds_dict = obtener_credenciales()
        if creds_dict is None:
            return None
            
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SHEET_ID).sheet1
        return sheet
    except Exception as e:
        st.error(f"❌ Error al conectar: {e}")
        return None

# Función para guardar en Google Sheets
def guardar_respuestas_sheets():
    try:
        sheet = conectar_google_sheets()
        if sheet is None:
            return False
        
        # Crear encabezados si la hoja está vacía
        try:
            primera_celda = sheet.cell(1, 1).value
        except:
            primera_celda = None
            
        if primera_celda is None or primera_celda == "":
            headers = ["Fecha y Hora", "Nombre Alumno", "Participa", "Tipo Regalo", 
                      "Juguete Preferido", "Otro Juguete", "Precio", "Comisión", "Comentarios"]
            sheet.append_row(headers)
        
        # Agregar datos
        st.session_state.respuestas['fecha_hora'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        row = [
            st.session_state.respuestas.get('fecha_hora', ''),
            st.session_state.respuestas.get('nombre_alumno', ''),
            st.session_state.respuestas.get('participa', ''),
            st.session_state.respuestas.get('tipo_regalo_opcion', ''),
            st.session_state.respuestas.get('juguete_preferido', ''),
            st.session_state.respuestas.get('otro_juguete', ''),
            st.session_state.respuestas.get('precio', ''),
            st.session_state.respuestas.get('comision', ''),
            st.session_state.respuestas.get('comentarios', '')
        ]
        sheet.append_row(row)
        return True
    except Exception as e:
        st.error(f"Error al guardar: {e}")
        return False

# Función para leer datos
def leer_datos_sheets():
    try:
        sheet = conectar_google_sheets()
        if sheet is None:
            return pd.DataFrame()
        data = sheet.get_all_records()
        if not data:
            return pd.DataFrame()
        return pd.DataFrame(data)
    except Exception as e:
        return pd.DataFrame()

# Función para contar comisiones desde Google Sheets
def contar_comisiones():
    df = leer_datos_sheets()
    if df.empty or 'Comisión' not in df.columns:
        return {}
    return df['Comisión'].value_counts().to_dict()

# Configuración de la página
st.set_page_config(
    page_title="Fiesta Navideña 2025",
    page_icon="🎄",
    layout="wide"
)

# CSS personalizado
st.markdown("""
    <style>
    /* Fondo navideño con gradiente */
    .main {
        background: linear-gradient(135deg, #1a472a 0%, #2d5a3d 50%, #1a472a 100%);
        background-attachment: fixed;
    }
    
    /* Animación de nieve */
    @keyframes snowfall {
        0% {
            transform: translateY(-10vh) translateX(0);
            opacity: 1;
        }
        100% {
            transform: translateY(100vh) translateX(100px);
            opacity: 0.3;
        }
    }
    
    .snowflake {
        position: fixed;
        top: -10vh;
        z-index: 9999;
        color: white;
        font-size: 1em;
        pointer-events: none;
        animation: snowfall linear infinite;
    }
    
    /* Contenedor principal con efecto cristal */
    [data-testid="stAppViewContainer"] > .main > div {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
    }
    
    /* Título principal animado */
    h1 {
        color: #C41E3A !important;
        text-align: center !important;
        font-size: 48px !important;
        font-weight: 800 !important;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.2);
        animation: titlePulse 2s ease-in-out infinite;
        margin-bottom: 30px !important;
    }
    
    @keyframes titlePulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }
    
    /* Subtítulos */
    h2 {
        color: #0F5132 !important;
        font-size: 36px !important;
        font-weight: 700 !important;
        border-bottom: 3px solid #FFD700;
        padding-bottom: 10px;
        margin-top: 30px !important;
    }
    
    h3 {
        color: #C41E3A !important;
        font-size: 28px !important;
        font-weight: 600 !important;
    }
    
    /* Caja de información mejorada */
    .info-box {
        background: linear-gradient(135deg, #fffbea 0%, #fff9e6 100%);
        padding: 25px;
        border-radius: 15px;
        border-left: 6px solid #FFD700;
        margin: 20px 0;
        font-size: 18px;
        box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
        animation: slideIn 0.5s ease-out;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* Botones mejorados con animación */
    .stButton>button {
        background: linear-gradient(135deg, #C41E3A 0%, #8B0000 100%) !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 15px !important;
        padding: 15px 35px !important;
        font-size: 20px !important;
        border: none !important;
        box-shadow: 0 6px 20px rgba(196, 30, 58, 0.4) !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #8B0000 0%, #C41E3A 100%) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(196, 30, 58, 0.6) !important;
    }
    
    .stButton>button:active {
        transform: translateY(0) !important;
    }
    
    /* Labels más visibles */
    .stTextInput label, .stTextArea label, .stRadio label, .stSelectbox label {
        font-size: 22px !important;
        font-weight: 700 !important;
        color: #0F5132 !important;
        text-shadow: 1px 1px 2px rgba(255,255,255,0.8);
    }
    
    /* Inputs mejorados */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        font-size: 18px !important;
        border: 2px solid #0F5132 !important;
        border-radius: 10px !important;
        padding: 12px !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #FFD700 !important;
        box-shadow: 0 0 15px rgba(255, 215, 0, 0.5) !important;
    }
    
    /* Radio buttons mejorados */
    .stRadio > div {
        font-size: 19px !important;
        background: rgba(15, 81, 50, 0.05);
        padding: 15px;
        border-radius: 10px;
    }
    
    /* Imágenes con efecto navideño */
    [data-testid="stImage"] img {
        height: 220px !important;
        width: 220px !important;
        object-fit: cover !important;
        border-radius: 15px !important;
        border: 4px solid #C41E3A !important;
        margin: 0 auto !important;
        display: block !important;
        box-shadow: 0 6px 20px rgba(196, 30, 58, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    
    [data-testid="stImage"] img:hover {
        transform: scale(1.05) rotate(2deg);
        box-shadow: 0 8px 30px rgba(196, 30, 58, 0.6) !important;
        border-color: #FFD700 !important;
    }
    
    [data-testid="stImage"] + div {
        text-align: center;
        font-weight: 700;
        color: #0F5132;
        margin-top: 12px;
        font-size: 16px;
        text-shadow: 1px 1px 2px rgba(255,255,255,0.8);
    }
    
    /* Divisores decorativos */
    hr {
        border: none;
        height: 3px;
        background: linear-gradient(90deg, 
            transparent 0%, 
            #FFD700 25%, 
            #C41E3A 50%, 
            #FFD700 75%, 
            transparent 100%);
        margin: 30px 0;
    }
    
    /* Botón flotante mejorado */
    .floating-container button {
        background: linear-gradient(135deg, #0F5132 0%, #1a472a 100%) !important;
        color: white !important;
        border-radius: 50% !important;
        width: 70px !important;
        height: 70px !important;
        font-size: 28px !important;
        border: 4px solid #FFD700 !important;
        box-shadow: 0 6px 20px rgba(255, 215, 0, 0.6) !important;
        padding: 0 !important;
        min-height: 70px !important;
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    .floating-container button:hover {
        background: linear-gradient(135deg, #1a472a 0%, #0F5132 100%) !important;
        transform: scale(1.15) !important;
        box-shadow: 0 8px 30px rgba(255, 215, 0, 0.8) !important;
    }
    
    /* Mensajes de éxito y error mejorados */
    .stSuccess {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border-left: 6px solid #28a745;
        border-radius: 10px;
        padding: 15px;
        font-size: 18px;
    }
    
    .stError {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        border-left: 6px solid #dc3545;
        border-radius: 10px;
        padding: 15px;
        font-size: 18px;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        border-left: 6px solid #17a2b8;
        border-radius: 10px;
        padding: 15px;
        font-size: 18px;
    }
    
    /* Indicador de progreso */
    .progress-bar {
        width: 100%;
        height: 8px;
        background: rgba(15, 81, 50, 0.2);
        border-radius: 10px;
        overflow: hidden;
        margin: 20px 0;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #FFD700 0%, #C41E3A 100%);
        transition: width 0.5s ease;
        animation: shimmer 2s infinite;
    }
    
    @keyframes shimmer {
        0% { background-position: -100% 0; }
        100% { background-position: 200% 0; }
    }
    
    /* Efectos de carga */
    .stSpinner > div {
        border-top-color: #C41E3A !important;
    }
    
    /* Selectbox mejorado */
    .stSelectbox select {
        background: white;
        border: 2px solid #0F5132 !important;
    }
    
    /* Number input mejorado */
    .stNumberInput input {
        border: 2px solid #0F5132 !important;
        border-radius: 10px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Agregar nieve animada
st.markdown("""
    <script>
    function createSnowflake() {
        const snowflake = document.createElement('div');
        snowflake.classList.add('snowflake');
        snowflake.innerHTML = '❄';
        snowflake.style.left = Math.random() * 100 + 'vw';
        snowflake.style.animationDuration = Math.random() * 3 + 5 + 's';
        snowflake.style.fontSize = Math.random() * 1 + 0.5 + 'em';
        document.body.appendChild(snowflake);
        
        setTimeout(() => {
            snowflake.remove();
        }, 8000);
    }
    
    setInterval(createSnowflake, 300);
    </script>
""", unsafe_allow_html=True)

# Inicializar session state
if 'seccion' not in st.session_state:
    st.session_state.seccion = 1
if 'respuestas' not in st.session_state:
    st.session_state.respuestas = {}
if 'pagina' not in st.session_state:
    st.session_state.pagina = 'formulario'
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

# Título principal
st.title("🎄 FIESTA NAVIDEÑA 2025! 🎁")

# Barra de progreso (solo si no se ha enviado el formulario)
if st.session_state.pagina == 'formulario' and not st.session_state.get('formulario_enviado', False):
    progreso = (st.session_state.seccion / 4) * 100
    st.markdown(f"""
        <div class="progress-bar">
            <div class="progress-fill" style="width: {progreso}%"></div>
        </div>
        <p style="text-align: center; color: #0F5132; font-weight: 600; font-size: 16px;">
            Sección {st.session_state.seccion} de 4 • {progreso:.0f}% completado
        </p>
    """, unsafe_allow_html=True)

# Botón flotante para admin (solo en página de formulario)
if st.session_state.pagina == 'formulario':
    # Crear contenedor flotante
    st.markdown("""
        <style>
        .floating-container {
            position: fixed;
            bottom: 30px;
            right: 30px;
            z-index: 999;
        }
        .floating-container button {
            background-color: #165b33 !important;
            color: white !important;
            border-radius: 50% !important;
            width: 60px !important;
            height: 60px !important;
            font-size: 24px !important;
            border: none !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3) !important;
            padding: 0 !important;
            min-height: 60px !important;
        }
        .floating-container button:hover {
            background-color: #0f4025 !important;
            transform: scale(1.1);
            box-shadow: 0 6px 16px rgba(0,0,0,0.4) !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Usar columnas para posicionar el botón
    col1, col2, col3 = st.columns([10, 1, 1])
    with col3:
        st.markdown('<div class="floating-container">', unsafe_allow_html=True)
        if st.button("📊", key="admin-btn-float", help="Panel de Administración"):
            st.session_state.pagina = 'admin'
            scroll_to_top()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ============== PANEL DE ADMINISTRACIÓN ==============
if st.session_state.pagina == 'admin':
    # Botón para volver al formulario
    col1, col2, col3 = st.columns([1, 5, 1])
    with col1:
        if st.button("⬅️ Volver", key="volver_form"):
            st.session_state.pagina = 'formulario'
            st.session_state.autenticado = False
            scroll_to_top()
            st.rerun()
    
    st.title("📊 Panel de Administración")
    
    if not st.session_state.autenticado:
        st.subheader("🔐 Acceso al Panel de Administración")
        password = st.text_input("Contraseña:", type="password", key="password_input")
        if st.button("Ingresar"):
            if password == PASSWORD_ADMIN:
                st.session_state.autenticado = True
                scroll_to_top()
                st.rerun()
            else:
                st.error("❌ Contraseña incorrecta")
    else:
        st.success("✅ Acceso autorizado")
        df = leer_datos_sheets()
        
        if df.empty:
            st.warning("⚠️ No hay respuestas registradas aún.")
        else:
            # Estadísticas
            st.header("📊 Estadísticas Generales")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Respuestas", len(df))
            with col2:
                participan = len(df[df['Participa'] == 'Sí'])
                st.metric("Participan", participan)
            with col3:
                no_participan = len(df[df['Participa'] == 'No'])
                st.metric("No Participan", no_participan)
            with col4:
                precio_promedio = df['Precio'].astype(str).str.extract('(\d+)').astype(float).mean()[0]
                st.metric("Precio Promedio", f"S/ {precio_promedio:.0f}")
            
            st.divider()
            
            # Gráficos
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📈 Participación")
                participa_counts = df['Participa'].value_counts()
                fig1 = px.pie(values=participa_counts.values, 
                             names=participa_counts.index,
                             title="Confirmación de Participación",
                             color_discrete_sequence=['#2ecc71', '#e74c3c'])
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                st.subheader("🎁 Juguetes Preferidos")
                juguetes = df['Juguete Preferido'].value_counts().head(5)
                fig2 = px.bar(x=juguetes.index, 
                             y=juguetes.values,
                             title="Top 5 Juguetes",
                             labels={'x': 'Juguete', 'y': 'Votos'},
                             color=juguetes.values,
                             color_continuous_scale='Viridis')
                st.plotly_chart(fig2, use_container_width=True)
            
            # Tipo de regalo
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("🎁 Tipo de Regalo")
                tipo_counts = df['Tipo Regalo'].value_counts()
                fig3 = px.pie(values=tipo_counts.values, 
                             names=tipo_counts.index,
                             title="Preferencia de Tipo de Regalo")
                st.plotly_chart(fig3, use_container_width=True)
            
            with col2:
                st.subheader("💰 Distribución de Precios")
                precio_counts = df['Precio'].value_counts().sort_index()
                fig4 = px.bar(x=precio_counts.index, 
                             y=precio_counts.values,
                             title="Votos por Precio",
                             labels={'x': 'Precio (S/)', 'y': 'Votos'})
                st.plotly_chart(fig4, use_container_width=True)
            
            st.divider()
            
            # Comisiones
            st.subheader("👥 Estado de Comisiones")
            limites_comisiones = {
                "Forrado de regalos (2 personas)": 2,
                "Limpieza del lugar (antes del show) (3 personas)": 3,
                "Decoración del lugar (4 personas)": 4,
                "Limpieza del lugar (después del show) (3 personas)": 3
            }
            
            conteo = contar_comisiones()
            for comision, limite in limites_comisiones.items():
                actual = conteo.get(comision, 0)
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"**{comision}**")
                with col2:
                    st.write(f"{actual}/{limite}")
                with col3:
                    if actual < limite:
                        st.success("✅ Disponible")
                    else:
                        st.error("❌ Completa")
            
            st.divider()
            
            # Tabla completa
            st.subheader("📋 Todas las Respuestas")
            sheet_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"
            st.markdown(f"[🔗 Abrir en Google Sheets]({sheet_url})")
            st.dataframe(df, use_container_width=True, height=400)
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar CSV",
                data=csv,
                file_name=f"respuestas_navidad_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

# ============== FORMULARIO ==============
else:
    # Verificar si se acaba de enviar
    if 'formulario_enviado' in st.session_state and st.session_state.formulario_enviado:
        st.success("🎉 ¡Formulario enviado exitosamente!")
        st.balloons()
        
        # Confeti adicional con HTML/CSS
        st.markdown("""
            <style>
            @keyframes confetti-fall {
                0% { transform: translateY(-100vh) rotate(0deg); }
                100% { transform: translateY(100vh) rotate(720deg); }
            }
            .confetti {
                position: fixed;
                width: 10px;
                height: 10px;
                background: #FFD700;
                animation: confetti-fall 3s linear;
                z-index: 9999;
            }
            </style>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-box" style="text-align: center; padding: 40px;">
            <h2 style='color: #C41E3A; margin-bottom: 20px;'>✨ ¡Gracias por su participación! ✨</h2>
            <p style='font-size: 20px; line-height: 1.8;'>Sus respuestas han sido registradas exitosamente en Google Sheets.</p>
            <p style='font-size: 20px; line-height: 1.8;'>Nos vemos en la fiesta navideña el <strong>19 de diciembre</strong>.</p>
            <p style='font-size: 32px; margin-top: 30px;'><b>¡Feliz Navidad! 🎄🎁✨</b></p>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    st.markdown("""
    <div class="info-box">
        <h3 style='color: #C41E3A; margin-bottom: 15px;'>🎅 ¡Hola papitos! 🎄✨</h3>
        <p style='line-height: 1.8;'>
            Los invitamos a completar este formulario para organizar juntos nuestra fiesta navideña 2025. 
            Sus respuestas nos ayudarán a planificar un evento especial para todos.
        </p>
        <p style='margin-top: 15px; font-weight: 600; color: #0F5132;'>
            ¡Gracias por su participación! 🎁
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # SECCIÓN 1: DATOS DEL ALUMNO
    if st.session_state.seccion == 1:
        st.markdown("<br>", unsafe_allow_html=True)
        st.header("📋 Sección 1 de 4")
        st.subheader("🎓 DATOS DEL ALUMNO")
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 2])
        
        with col1:
            nombre_alumno = st.text_input(
                "Escribir el nombre del Alumno *", 
                key="nombre_alumno",
                placeholder="Ej: Juan Pérez"
            )
        
        st.write("")
        
        if st.button("➡️ Continuar a Sección 2", key="btn_sec1"):
            if nombre_alumno:
                st.session_state.respuestas.update({
                    'nombre_alumno': nombre_alumno
                })
                st.session_state.seccion = 2
                st.rerun()
            else:
                st.error("⚠️ Por favor completa el nombre del alumno")

    # SECCIÓN 2: PARTICIPACIÓN
    if st.session_state.seccion == 2:
        st.markdown("---")
        st.markdown('<div id="seccion2"></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.header("🎉 Sección 2 de 4")
        st.subheader("📅 DATOS PARA EL COMPARTIR")
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.info("📅 La fecha tentativa en la cual se realizará la reunión será el **19 de diciembre**")
        
        participa = st.radio("¿Vas a participar? *", ["Sí", "No"], key="participa")
        
        if participa == "No":
            st.success("✨ ¡Gracias por tu respuesta! ¡Feliz Navidad! 🎄🎁")
            st.balloons()
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("📤 Enviar respuesta", key="btn_enviar_no"):
                st.session_state.respuestas['participa'] = "No"
                if guardar_respuestas_sheets():
                    st.session_state.seccion = 1
                    st.session_state.respuestas = {}
                    st.session_state.formulario_enviado = True
                    scroll_to_top()
                    st.rerun()
                else:
                    st.error("❌ Hubo un error al guardar la respuesta")
            st.stop()
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➡️ Continuar a Sección 3", key="btn_sec2"):
            if participa:
                st.session_state.respuestas['participa'] = participa
                st.session_state.seccion = 3
                st.rerun()
            else:
                st.error("⚠️ Por favor selecciona una opción")

    # SECCIÓN 3: REGALO
    if st.session_state.seccion == 3:
        st.markdown("---")
        st.markdown('<div id="seccion3"></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.header("🎁 Sección 3 de 4")
        st.subheader("🎀 DATOS PARA EL REGALO")
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-box">
            <h3 style='color: #C41E3A; margin-bottom: 15px;'>📌 Estimados padres:</h3>
            <p style='line-height: 1.8;'>
                Las fotografías mostradas son <strong>referenciales</strong>. El regalo se elegirá según la opción con más votos.
            </p>
            <h4 style='color: #0F5132; margin-top: 20px; margin-bottom: 10px;'>⚠️ Importante:</h4>
            <ul style='line-height: 1.8;'>
                <li>Marcar solo <strong>UNA opción</strong> por pregunta</li>
                <li>Una vez que elijan el tipo de regalo, seleccionen un precio acorde</li>
                <li>El monto seleccionado será el <strong>aporte individual por familia</strong></li>
                <li>Se elegirá el monto que tenga más votos</li>
            </ul>
            <p style='margin-top: 20px; font-weight: 600; color: #0F5132;'>
                ¡Gracias por su participación! 🎄
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        
        tipo_regalo_opcion = st.radio(
            "El regalo debería ser? *",
            ["Igual para todos", "Diferente para niños y niñas"],
            key="tipo_regalo_opcion"
        )
        
        st.write("")
        st.write("")
        
        st.write("**¿Qué tipo de juguete prefiere su hijo(a)? ***")
        st.write("")
        
        st.write("**Opciones disponibles:**")
        st.write("")
        
        # Fila 1
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.image("imagenes/juego_mesa.jpg", caption="Juegos de Mesa")
        with col2:
            st.image("imagenes/munecas_barbie.jpg", caption="Muñecas")
        with col3:
            st.image("imagenes/juego_cocina.jpg", caption="Juegos de Cocina")
        with col4:
            st.image("imagenes/lego.jpg", caption="Lego")
        
        st.write("")
        
        # Fila 2
        col5, col6, col7, col8 = st.columns(4)
        with col5:
            st.image("imagenes/transformers.jpg", caption="Carritos/Transformers")
        with col6:
            st.image("imagenes/quimica.jpg", caption="Kit de Química")
        with col7:
            st.image("imagenes/pista.jpg", caption="Pistas de Carreras")
        with col8:
            st.image("imagenes/reloj.jpg", caption="Reloj Smartwatch")
        
        st.write("")
        
        # Fila 3
        col9, col10, col11, col12 = st.columns(4)
        with col9:
            st.image("imagenes/consola.jpg", caption="Consola Videojuegos")
        with col10:
            st.image("imagenes/camara.jpg", caption="Cámara Digital")
        with col11:
            st.write("")
        with col12:
            st.write("")
        
        st.write("")
        st.write("---")
        st.write("")
        
        opciones_juguetes = [
            "-- Seleccione una opción --",
            "Juegos de Mesa (Monopoly, Jenga, Uno, etc.)",
            "Muñecas (Barbie, Frozen, etc.)",
            "Juegos de Cocina",
            "Lego",
            "Carritos/Transformers",
            "Kit de Química",
            "Pistas de carreras",
            "Reloj Inteligente Smartwatch (S/30 - S/40)",
            "Consola de Videojuegos (S/50 - S/60)",
            "Cámara Digital Infantil (S/40 - S/50)",
            "Otro"
        ]
        
        juguete_preferido = st.selectbox(
            "**Seleccione su opción de la lista:**",
            options=opciones_juguetes,
            index=0,
            key="juguete"
        )
        
        if juguete_preferido == "-- Seleccione una opción --":
            juguete_preferido = None
        
        otro_juguete = ""
        if juguete_preferido == "Otro":
            otro_juguete = st.text_input("Por favor especifica qué otro juguete:", key="otro_juguete", placeholder="Ej: Rompecabezas, Instrumentos musicales, etc.")
        
        st.write("")
        st.write("")
        
        precio = st.radio(
            "¿Cuánto debería costar el regalo? (Soles) *",
            ["20", "25", "30", "35", "40", "50"],
            key="precio"
        )
        
        if st.button("➡️ Continuar a Sección 4", key="btn_sec3"):
            if tipo_regalo_opcion and juguete_preferido and precio:
                st.session_state.respuestas.update({
                    'tipo_regalo_opcion': tipo_regalo_opcion,
                    'juguete_preferido': juguete_preferido,
                    'otro_juguete': otro_juguete if juguete_preferido == "Otro" else "",
                    'precio': precio
                })
                st.session_state.seccion = 4
                st.rerun()
            else:
                st.error("⚠️ Por favor completa todos los campos obligatorios (*)")

    # SECCIÓN 4: COMISIONES
    if st.session_state.seccion == 4:
        st.markdown("---")
        st.markdown('<div id="seccion4"></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.header("👥 Sección 4 de 4")
        st.subheader("🤝 PARTICIPACIÓN EN COMISIONES")
        st.markdown("<br>", unsafe_allow_html=True)
        
        limites_comisiones = {
            "Forrado de regalos (2 personas)": 2,
            "Limpieza del lugar (antes del show) (3 personas)": 3,
            "Decoración del lugar (4 personas)": 4,
            "Limpieza del lugar (después del show) (3 personas)": 3
        }
        
        conteo = contar_comisiones()
        
        opciones_disponibles = []
        opciones_completas = []
        
        st.write("**Disponibilidad de comisiones:**")
        st.write("")
        
        for comision, limite in limites_comisiones.items():
            actual = conteo.get(comision, 0)
            disponibles = limite - actual
            
            if disponibles > 0:
                st.markdown(f"✅ **{comision}** - Disponibles: {disponibles}/{limite}")
                opciones_disponibles.append(comision)
            else:
                st.markdown(f"❌ **{comision}** - COMPLETA ({limite}/{limite})")
                opciones_completas.append(comision)
        
        st.write("")
        st.write("---")
        st.write("")
        
        if opciones_disponibles:
            comision = st.radio(
                "¿En qué comisión le gustaría participar? *",
                opciones_disponibles,
                key="comision"
            )
        else:
            st.error("⚠️ Lo sentimos, todas las comisiones están completas.")
            comision = None
        
        st.write("")
        
        comentarios = st.text_area(
            "Comentarios adicionales (opcional)",
            placeholder="Si tiene algún comentario o sugerencia, por favor escríbalo aquí...",
            key="comentarios"
        )
        
        st.write("")
        
        if st.button("✅ ENVIAR FORMULARIO", key="btn_final", type="primary"):
            if comision:
                st.session_state.respuestas.update({
                    'comision': comision,
                    'comentarios': comentarios
                })
                
                if guardar_respuestas_sheets():
                    st.session_state.seccion = 1
                    st.session_state.respuestas = {}
                    st.session_state.formulario_enviado = True
                    scroll_to_top()
                    st.rerun()
                else:
                    st.error("❌ Hubo un error al enviar el formulario. Por favor intenta nuevamente.")
            else:
                st.error("⚠️ Por favor selecciona una comisión")
