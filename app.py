import streamlit as st
from supabase import create_client, Client
import main
import os
import zipfile
from io import BytesIO
import time
import extra_streamlit_components as stx

# ============================================================
# 1. CONFIGURACIÓN Y TEMA VISUAL (DEBE IR PRIMERO)
# ============================================================
st.set_page_config(
    page_title="Fire Form Pro", 
    layout="wide", 
    page_icon="app_icon.png",
    initial_sidebar_state="collapsed"
)

# ============================================================
# 2. INICIALIZACIÓN DE COOKIES Y "EL FRENO"
# ============================================================
cookie_manager = stx.CookieManager()

# --- EL FRENO OBLIGATORIO ---
# Si get_all() devuelve None, significa que Chrome aún no le manda los datos a Python.
# Forzamos una recarga rápida antes de intentar leer o guardar nada.
if cookie_manager.get_all() is None:
    time.sleep(0.5)
    st.rerun()
# ----------------------------

# --- LA SOLUCIÓN: GUARDAR COOKIES EN EL FLUJO PRINCIPAL ---
if st.session_state.get("guardar_cookies"):
    cookie_manager.set("sb_access", st.session_state.temp_access, max_age=2592000, key="set_access_cookie")
    cookie_manager.set("sb_refresh", st.session_state.temp_refresh, max_age=2592000, key="set_refresh_cookie")
    st.session_state.guardar_cookies = False
# ----------------------------------------------------------

# Estilo CSS Moderno (Light Theme + Naranja Fire Alarm)
modern_styles = """
<style>
/* Ocultar elementos por defecto de Streamlit */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Fondo general de la aplicación (Gris muy claro para resaltar las tarjetas blancas) */
.stApp {
    background-color: #F4F7F9;
}

/* Forzar colores de texto oscuros para evitar que se pierdan en Modo Oscuro */
h1, h2, h3, h4, h5, h6, p, span, div {
    color: #2D3748;
}

/* Etiquetas de los inputs (Labels) */
.stTextInput label, .stNumberInput label, .stSelectbox label, .stCheckbox label, .stTextArea label {
    color: #2D3748 !important;
    font-weight: 600 !important;
}

/* Controlar el ancho de la app y centrar el contenedor principal */
.block-container {
    padding-top: 1rem !important; /* Lo bajamos a 1rem o 0.5rem para quitar espacio arriba */
    max-width: 1200px !important; 
    margin: 0 auto !important; 
}

/* Jalar las pestañas (Tabs) hacia arriba para reducir el hueco blanco */
div[data-testid="stTabs"] {
    margin-top: -30px !important; /* Ajusta este número si quieres que suba más o menos */
}

/* Ocultar la línea de decoración superior por defecto de Streamlit */
[data-testid="stDecoration"] {
    display: none;
}

/* Contenedor interno para el contenido */
.main-content {
    max-width: 1400px;
    margin: 0 auto;
    padding: 0 2rem;
}

/* Estilo para los botones principales (Naranja) */
.stButton > button[kind="primary"], .stDownloadButton > button {
    background: linear-gradient(135deg, #FF6B00 0%, #E65100 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 0.6rem 1.5rem !important;
    box-shadow: 0 4px 10px rgba(255, 107, 0, 0.25) !important;
    transition: all 0.3s ease !important;
}

.stButton > button[kind="primary"]:hover, .stDownloadButton > button:hover {
    box-shadow: 0 6px 15px rgba(255, 107, 0, 0.4) !important;
    transform: translateY(-2px) !important;
    color: white !important;
}

/* Estilo para botones secundarios */
.stButton > button[kind="secondary"] {
    background-color: white !important;
    color: #4A5568 !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
}

.stButton > button[kind="secondary"]:hover {
    border-color: #FF6B00 !important;
    color: #FF6B00 !important;
}

/* Botón de logout blanco */
.stButton > button[key="logout_btn"] {
    background: rgba(255,255,255,0.25) !important;
    backdrop-filter: blur(10px) !important;
    border: 1px solid rgba(255,255,255,0.4) !important;
    color: white !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 0.5rem 1rem !important;
    transition: all 0.3s ease !important;
}

.stButton > button[key="logout_btn"]:hover {
    background: rgba(255,255,255,0.35) !important;
    transform: translateY(-1px) !important;
}

/* Tarjetas (Expanders y Data Editor) */
[data-testid="stExpander"], [data-testid="stDataEditor"] {
    background-color: white !important;
    border-radius: 12px !important;
    border: 1px solid #E2E8F0 !important;
    box-shadow: 0 4px 6px rgba(0,0,0,0.02) !important;
}

[data-testid="stExpander"] summary {
    font-weight: 600 !important;
    color: #2D3748 !important;
}

/* Inputs de texto y selects */
.stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"], .stTextArea textarea {
    background-color: white !important;
    border-radius: 8px !important;
    border: 1px solid #E2E8F0 !important;
    color: #1A202C !important;
}

/* Efecto focus en inputs */
.stTextInput input:focus, .stTextArea textarea:focus, .stSelectbox div[data-baseweb="select"]:focus-within {
    border-color: #FF6B00 !important;
    box-shadow: 0 0 0 1px #FF6B00 !important;
}

/* Títulos de pestañas (Tabs) */
.stTabs [data-baseweb="tab"] {
    color: #718096 !important;
    font-weight: 600 !important;
    font-size: 1.1rem !important;
}
.stTabs [aria-selected="true"] {
    color: #FF6B00 !important;
    border-bottom-color: #FF6B00 !important;
}

/* Mensajes de éxito/error */
.stAlert {
    border-radius: 10px !important;
}

/* Forzar el fondo blanco y texto oscuro en el menú desplegable de los Selectbox */
div[data-baseweb="popover"] div, 
ul[role="listbox"], 
ul[role="listbox"] li {
    background-color: white !important;
    color: #2D3748 !important;
}

/* Efecto hover (gris claro) al pasar el mouse por las opciones del menú */
ul[role="listbox"] li:hover {
    background-color: #F4F7F9 !important;
    color: #FF6B00 !important;
}
</style>
"""
st.markdown(modern_styles, unsafe_allow_html=True)

# ============================================================
# INICIALIZACIÓN Y VARIABLES
# ============================================================
 
main.API_KEY_NYC = st.secrets.get("NYC_API_KEY", "")
main.APP_TOKEN_SOCRATA = st.secrets.get("SOCRATA_TOKEN", "")

SUPABASE_URL = st.secrets.get("SUPABASE_URL", "https://uhhiqkymipbcepqzwtvg.supabase.co")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "sb_publishable_mvqOWXc5s4b3_IMe4gGexw_sU3B2DRL")

if "supabase" not in st.session_state:
    try:
        st.session_state.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"❌ Failed to connect to Supabase: {e}")
        st.stop()

supabase = st.session_state.supabase

# --- LÓGICA DE SESIÓN PERSISTENTE (COOKIES) ---
if "user" not in st.session_state:
    st.session_state.user = None
    
    access_token = cookie_manager.get(cookie="sb_access")
    refresh_token = cookie_manager.get(cookie="sb_refresh")
    
    if access_token and refresh_token:
        try:
            session_data = supabase.auth.set_session(access_token, refresh_token)
            if session_data and session_data.user:
                st.session_state.user = session_data.user
        except Exception:
            pass
    else:
        try:
            session = supabase.auth.get_session()
            if session and session.user:
                st.session_state.user = session.user
        except Exception:
            pass

if "device_list" not in st.session_state:
    st.session_state.device_list = []

if "generated_data" not in st.session_state:
    st.session_state.generated_data = None

# ============================================================
# FUNCIONES DE APOYO
# ============================================================
def logout():
    try:
        supabase.auth.sign_out()
    except Exception:
        pass
        
    cookie_manager.delete("sb_access", key="del_access_cookie")
    cookie_manager.delete("sb_refresh", key="del_refresh_cookie")
    
    st.session_state.user = None
    st.session_state.device_list = []
    st.session_state.generated_data = None
    st.session_state.guardar_cookies = False # Limpieza por seguridad
    time.sleep(0.5) # Le damos medio segundo a JS para borrar la cookie
    st.rerun()

def fetch_user_profile(user_id):
    try:
        response = supabase.table("profiles").select("*").eq("id", user_id).execute()
        return response.data[0] if response.data else {}
    except Exception as e:
        return {}

def sync_profile_to_main(profile):
    main.COMPANY.update({
        "Company Name": profile.get("company_name", ""),
        "Address":      profile.get("company_address", ""),
        "City":         profile.get("company_city", ""),
        "State":        profile.get("company_state", "NY"),
        "Zip":          profile.get("company_zip", ""),
        "Phone":        profile.get("company_phone", ""),
        "Email":        profile.get("company_email", ""),
        "First Name":   profile.get("company_first_name", ""),
        "Last Name":    profile.get("company_last_name", ""),
        "COF S97":      profile.get("company_cof_s97", ""),
        "Expiration":   profile.get("company_expiration", ""),
    })
    
    # --- NUEVO BLOQUE PARA EL EXPEDITOR ---
    if not hasattr(main, 'EXPEDITOR'):
        main.EXPEDITOR = {}
        
    main.EXPEDITOR.update({
        "Company Name": profile.get("exp_name", ""),
        "Address":      profile.get("exp_address", ""),
        "City":         profile.get("exp_city", ""),
        "State":        profile.get("exp_state", "NY"),
        "Zip":          profile.get("exp_zip", ""),
        "Phone":        profile.get("exp_phone", ""),
        "Email":        profile.get("exp_email", ""),
        "First Name":   profile.get("exp_first_name", ""),
        "Last Name":    profile.get("exp_last_name", ""),
        "Reg No":       profile.get("exp_reg_no", ""),
    })
    main.ARCHITECT.update({
        "Company Name": profile.get("arch_name", ""),
        "Address":      profile.get("arch_address", ""),
        "City":         profile.get("arch_city", ""),
        "State":        profile.get("arch_state", ""),
        "Zip":          profile.get("arch_zip", ""),
        "Phone":        profile.get("arch_phone", ""),
        "Email":        profile.get("arch_email", ""),
        "First Name":   profile.get("arch_first_name", ""),
        "Last Name":    profile.get("arch_last_name", ""),
        "License No":   profile.get("arch_license", ""),
        "Role":         profile.get("arch_role", "PE"),
    })
    main.ELECTRICIAN.update({
        "Company Name": profile.get("elec_name", ""),
        "Address":      profile.get("elec_address", ""),
        "City":         profile.get("elec_city", ""),
        "State":        profile.get("elec_state", ""),
        "Zip":          profile.get("elec_zip", ""),
        "Phone":        profile.get("elec_phone", ""),
        "Email":        profile.get("elec_email", ""),
        "First Name":   profile.get("elec_first_name", ""),
        "Last Name":    profile.get("elec_last_name", ""),
        "License No":   profile.get("elec_license", ""),
        "Expiration":   profile.get("elec_expiration", ""),
    })
    main.TECH_DEFAULTS.update({
        "Manufacturer": profile.get("tech_manufacturer", ""),
        "Approval":     profile.get("tech_approval", ""),
        "WireGauge":    profile.get("tech_wire_gauge", ""),
        "WireType":     profile.get("tech_wire_type", ""),
    })
    main.CENTRAL_STATION.update({
        "Company Name": profile.get("cs_name", ""),
        "CS Code":      profile.get("cs_code", ""),
        "Address":      profile.get("cs_address", ""),
        "City":         profile.get("cs_city", ""),
        "State":        profile.get("cs_state", ""),
        "Zip":          profile.get("cs_zip", ""),
        "Phone":        profile.get("cs_phone", ""),
    })

def save_project(user_id, bin_val, address, devices, job_desc):
    project_data = {
        "user_id": user_id,
        "bin": bin_val,
        "address": address,
        "device_list": devices,
        "job_description": job_desc
    }
    # Usamos upsert basado en el BIN y user_id para actualizar si ya existe
    try:
        supabase.table("projects").upsert(
            project_data, on_conflict="user_id, bin" 
        ).execute()
    except Exception as e:
        st.error(f"Error saving project: {e}")

def fetch_projects(user_id):
    try:
        res = supabase.table("projects").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        return res.data
    except:
        return []

def delete_project(project_id):
    try:
        supabase.table("projects").delete().eq("id", project_id).execute()
        st.rerun()
    except:
        pass

# --- NUEVAS FUNCIONES PARA PAYPAL Y SUSCRIPCIONES ---
import streamlit.components.v1 as components
from datetime import datetime

def check_subscription(user_id):
    """Verifica el estado del plan del usuario en Supabase."""
    try:
        # Intenta obtener la suscripción de la tabla (asume que la tabla existe en Supabase)
        response = supabase.table("user_subscriptions").select("*").eq("user_id", user_id).execute()
        
        # Si el usuario tiene un registro
        if response.data:
            sub_data = response.data[0]
            
            # Lógica simple para resetear el contador si cambió de mes (opcional, pero buena práctica)
            # Por ahora confiaremos en la base de datos.
            return sub_data
            
    except Exception as e:
        # st.error(f"Error reading subscription: {e}") # Descomentar para depurar
        pass
        
    # Si no existe registro o hay error, asume que es un usuario 'free' nuevo con 0 usos
    return {"plan_type": "free", "forms_generated_this_month": 0}

def increment_free_usage(user_id, current_usage):
    """Suma 1 al contador de usos del mes para usuarios free."""
    try:
        nuevo_uso = current_usage + 1
        # Usamos upsert por si el registro no existía
        supabase.table("user_subscriptions").upsert({
            "user_id": user_id,
            "plan_type": "free",
            "forms_generated_this_month": nuevo_uso,
            "last_reset_date": "now()"
        }).execute()
    except Exception as e:
        pass


# ============================================================
# PANTALLA DE LOGIN (TARJETA MODERNA)
# ============================================================
def login_ui_centered():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Tarjeta blanca central
        st.markdown("""
        """, unsafe_allow_html=True)
        
        if os.path.exists("logo.png"):
            st.image("logo.png", width=250)
            st.markdown("<p style='color: #718096 !important; font-size: 15px; margin-top: -90px; margin-bottom: 1rem;'>Automated form generation for the NYC Fire Alarm Industry</p>", unsafe_allow_html=True)
        else:
            st.markdown("<h1 style='color: #FF6B00; margin-bottom: 0;'>🔥 Fire Form Pro</h1>", unsafe_allow_html=True)
            st.markdown("<p style='color: #718096; font-size: 15px; margin-bottom: 1rem;'>Automated form generation for the NYC Fire Alarm Industry</p>", unsafe_allow_html=True)
            
        # --- NUEVO: BLOQUE DE VALOR (HOOK) ---
        hook_html = """
        <div style="background-color: #FFFaf0; border-left: 4px solid #FF6B00; padding: 12px 16px; border-radius: 4px; margin-bottom: 55px;">
            <p style="color: #4A5568; font-size: 14.5px; margin: 0; font-style: italic;">
                "Your NYC property research and automation tool. Get the intel you need and generate forms in <b>20 seconds</b>."
            </p>
        </div>
        """
        st.markdown(hook_html, unsafe_allow_html=True)
        # -------------------------------------
        
        tab1, tab2 = st.tabs(["🔑 Sign In", "📝 Create Account"])
        
        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            email = st.text_input("Email Address", key="login_email", placeholder="you@company.com")
            password = st.text_input("Password", type="password", key="login_password", placeholder="••••••••")
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("Sign In →", use_container_width=True, type="primary"):
                if not email or not password:
                    st.error("Please enter both email and password")
                else:
                    with st.spinner("Authenticating..."):
                        try:
                            # 1. Intentamos el login
                            response = supabase.auth.sign_in_with_password({"email": email.strip(), "password": password})
                            
                            if response.user:
                                st.session_state.user = response.user
                                
                                # 2. Preparamos las cookies para que se guarden en el recargo
                                if response.session:
                                    st.session_state.temp_access = response.session.access_token
                                    st.session_state.temp_refresh = response.session.refresh_token
                                    st.session_state.guardar_cookies = True
                                
                                # 3. Recargamos la app
                                st.rerun()
                        except Exception as e:
                            # Imprimimos el error REAL por si algo más falla (y no un mensaje ciego)
                            st.error(f"⚠️ Invalid email or password: {e}")
                          
        
        with tab2:
            st.markdown("<br>", unsafe_allow_html=True)
            email = st.text_input("Email Address", key="signup_email", placeholder="you@company.com")
            password = st.text_input("Password", type="password", key="signup_password", placeholder="Min. 6 characters")
            password_confirm = st.text_input("Confirm Password", type="password", key="signup_password_confirm", placeholder="Repeat password")
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("Create Account →", use_container_width=True, type="primary"):
                if password != password_confirm:
                    st.error("❌ Passwords do not match.")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    with st.spinner("Creating account..."):
                        try:
                            response = supabase.auth.sign_up({"email": email.strip(), "password": password})
                            if response.user:
                                st.success("✅ Account created! Please check your email.")
                                try:
                                    supabase.table("profiles").insert({"id": response.user.id, "email": email}).execute()
                                except Exception: pass
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")

        st.markdown("</div>", unsafe_allow_html=True)

if not st.session_state.user:
    login_ui_centered()
    st.stop()

# ============================================================
# ENCABEZADO SUPERIOR (LIMPIO)
# ============================================================
col_logo, col_logout = st.columns([3, 1])

with col_logo:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=280)
        # Eslogan principal (cuando hay logo)
        st.markdown("<p style='color: #2D3748; font-size: 16px; margin-top: -90px; margin-bottom: 20px; font-weight: 500;'>Automated form generation for the NYC Fire Alarm Industry</p>", unsafe_allow_html=True)
    else:
        # PLAN DE RESPALDO (si no encuentra el logo, SOLO muestra el eslogan, ya no el título)
        st.markdown("<p style='color: #2D3748; font-size: 16px; margin-top: 5px; margin-bottom: 20px; font-weight: 500;'>Automated form generation for the NYC Fire Alarm Industry</p>", unsafe_allow_html=True)

with col_logout:
    st.markdown(f"<div style='text-align: right; margin-top: 25px; margin-bottom: 10px;'><span style='color: #4A5568; font-weight: 600;'>👤 {st.session_state.user.email}</span></div>", unsafe_allow_html=True)
    if st.button("🚪 Logout", use_container_width=True, type="secondary"):
        logout()

st.markdown("</div></div>", unsafe_allow_html=True)

# Contenedor para el contenido principal
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# ============================================================
# APP PRINCIPAL (PESTAÑAS)
# ============================================================
profile = fetch_user_profile(st.session_state.user.id)
tabs = st.tabs(["🏗️ Project Builder", "🏢 Property Lookup", "👤 Profile Settings"])

# ------------------------------------------------------------
# TAB 1: PROPERTY INTELLIGENCE (NUEVO MÓDULO)
# ------------------------------------------------------------
with tabs[1]:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #2D3748;'>🔍 Property Lookup</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #718096;'>Scan NYC databases to uncover property details.</p>", unsafe_allow_html=True)
    
    with st.container(border=True):
        
        # 1. Buscador Dual (Radio Buttons)
        search_type = st.radio("Search Method", ["By BIN", "By Address"], horizontal=True)
        
        bin_to_search = ""
        
        if search_type == "By BIN":
            bin_input = st.text_input("Property BIN Number", placeholder="e.g. 3335982", key="intel_bin")
            bin_to_search = bin_input.strip()
        else:
            col_a1, col_a2, col_a3 = st.columns([1, 2, 1])
            with col_a1:
                house = st.text_input("House No.", placeholder="e.g. 164", key="intel_house")
            with col_a2:
                street = st.text_input("Street Name", placeholder="e.g. Atlantic Avenue", key="intel_street")
            with col_a3:
                borough = st.selectbox("Borough", ["Manhattan", "Bronx", "Brooklyn", "Queens", "Staten Island"], key="intel_boro")
            

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # 2. Botón de Acción y Lógica de Búsqueda
        if st.button("Run Property Lookup", type="primary", use_container_width=True):
            final_bin = ""
            
            # --- FASE 1: RESOLVER EL BIN ---
            if search_type == "By BIN":
                final_bin = bin_input.strip()
                if not final_bin:
                    st.error("⚠️ Please enter a valid BIN.")
            else:
                if not house or not street or not borough:
                    st.error("⚠️ Please fill in House No., Street, and Borough.")
                else:
                    with st.spinner("🌍 Translating Address to BIN using NYC Geoclient..."):
                        # Llamamos a la nueva función de main.py
                        final_bin = main.obtener_bin_por_direccion(house, street, borough)
                        if not final_bin:
                            st.error("❌ Could not find a valid BIN for this exact address. Please check spelling or use 'By BIN'.")
            
            # --- FASE 2: CORRER EL ESCÁNER SI TENEMOS BIN ---
            if final_bin:
                with st.status(f"🕵️‍♂️ Scanning City Databases for BIN: {final_bin}...", expanded=True) as status:
                    st.write("⏳ Fetching DOB, PLUTO & Geoclient data...")
                    info = main.obtener_datos_completos(final_bin)
                    
                    status.update(label="✅ Scan Complete!", state="complete", expanded=False)
                
                # 3. Mostrar Resultados (Dashboard)
                if info:
                    st.markdown("<hr style='border-color: #E2E8F0; margin: 1.5rem 0;'>", unsafe_allow_html=True)
                    st.markdown("<h4 style='color: #2D3748;'>🏢 Property Overview</h4>", unsafe_allow_html=True)
                    
                    # --- Fila 1: Dirección, BIN y DCP ---
                    address_str = f"{info.get('house', '')} {info.get('street', '')}, {info.get('borough', '')}, NY {info.get('zip', '')}"
                    st.markdown(f"<p style='font-size: 1.1rem; margin-bottom: 0;'><b>Address:</b> {address_str}</p>", unsafe_allow_html=True)
                    
                    col_top1, col_top2 = st.columns(2)
                    col_top1.markdown(f"<p style='font-size: 1.1rem; margin-bottom: 0;'><b>BIN:</b> {final_bin}</p>", unsafe_allow_html=True)
                    col_top2.markdown(f"<p style='font-size: 1rem; margin-bottom: 1.5rem; color: #718096;'><b>DCP Address Range:</b> {info.get('dcp_address', 'N/A')}</p>", unsafe_allow_html=True)
                    
                    # --- Fila 2: Métricas Principales ---
                    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                    col_m1.metric("Block / Lot", f"{info.get('block', 'N/A')} / {info.get('lot', 'N/A')}")
                    col_m2.metric("Height", f"{info.get('height', '0')} ft")
                    col_m3.metric("Stories", info.get('stories', '0'))
                    col_m4.metric("Const. Class", info.get('construction_class', 'N/A'))
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # --- Fila 3: Landmark, Flood, Occupancy, Owner ---
                    col_m5, col_m6, col_m7, col_m8 = st.columns([1, 1, 1, 2])
                    col_m5.metric("Landmark", info.get('landmarked', 'No'))
                    col_m6.metric("Flood Zone", info.get('flood_zone', 'No'))
                    col_m7.metric("Occupancy", info.get('occupancy_group', 'N/A'))
                    
                    owner_name = info.get('owner_business') or f"{info.get('owner_first', '')} {info.get('owner_last', '')}".strip() or "N/A"
                    col_m8.metric("Property Owner", owner_name)
                    
                    st.markdown("<br>", unsafe_allow_html=True)

                    # --- Fila 4: Sprinklers, Elevators, Coordinates ---
                    col_m9, col_m10, col_m11 = st.columns([1, 1, 2])
                    col_m9.metric("Sprinklers (History)", info.get('has_sprinklers', 'Unknown'))
                    col_m10.metric("Elevators (History)", info.get('has_elevators', 'Unknown'))
                    
                    x_c = info.get('x_coord') or 'N/A'
                    y_c = info.get('y_coord') or 'N/A'
                    col_m11.metric("X / Y Coordinates", f"{x_c} / {y_c}")

                    # --- SECCIÓN CONDICIONAL: TRABAJOS DE FIRE ALARM ---
                    if info.get("fire_alarm_jobs"):
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.markdown("""
                        <div style='background-color: #FFF5F5; border-left: 4px solid #E53E3E; padding: 10px 15px; margin-bottom: 15px;'>
                            <h5 style='color: #C53030; margin:0;'>🚨 Historical Fire Alarm Jobs Detected</h5>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # --- NUEVO: TABLA CON LINKS CLICABLES ---
                        st.dataframe(
                            info["fire_alarm_jobs"],
                            use_container_width=True,
                            hide_index=True,
                            column_config={
                                "DOB Link": st.column_config.LinkColumn("Action", display_text="View in BIS 🔗")
                            }
                        )
                    
                    # --- DISCLAIMER ---
                    st.markdown("""
                    <div style='background-color: #F7FAFC; padding: 12px; border-radius: 6px; border-left: 4px solid #A0AEC0; margin-top: 25px; margin-bottom: 20px;'>
                        <p style='font-size: 12px; color: #4A5568; margin: 0; line-height: 1.4;'>
                        <b>* Accuracy Disclaimer:</b> Property ownership, structural data, and historical jobs are retrieved in real-time from public NYC APIs (DOB NOW, BIS, PLUTO). Due to filing delays or database inconsistencies, this information is provided "AS IS". Always verify critical details.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("<h4 style='color: #2D3748;'>⚡ Quick Actions (Smart Links)</h4>", unsafe_allow_html=True)
                    
                    col_link1, col_link2, col_link3 = st.columns(3)
                    
                    with col_link1:
                        dob_url = f"https://a810-bisweb.nyc.gov/bisweb/COsByLocationServlet?requestid=1&allbin={final_bin}"
                        st.link_button("🏛️ View C of O (DOB)", dob_url, use_container_width=True)
                    with col_link2:
                        fdny_url = "https://fires.fdnycloud.org/CitizenAccess/Report/ReportParameter.aspx?module=&reportID=1423&reportType=LINK_REPORT_LIST"
                        st.link_button("📄 Full FDNY Profile", fdny_url, use_container_width=True)
                    with col_link3:
                        # --- NUEVO: LÓGICA PARA ZOLA MAP ---
                        bbl = info.get('bbl_full', '')
                        if bbl and len(bbl) == 10:
                            # BBL = 1 dígito de borough + 5 de block + 4 de lot
                            boro = bbl[0]
                            block = str(int(bbl[1:6])) # int() remueve los ceros a la izquierda
                            lot = str(int(bbl[6:10]))
                            zola_url = f"https://zola.planning.nyc.gov/lot/{boro}/{block}/{lot}"
                        else:
                            zola_url = "https://zola.planning.nyc.gov/"
                            
                        st.link_button("🗺️ NYC ZOLA Map", zola_url, use_container_width=True)

                    # Botón extra abajo para CapHome
                    caphome_url = "https://fires.fdnycloud.org/CitizenAccess/Cap/CapHome.aspx?module=BFP&TabName=BFP"
                    st.link_button("🔥 FDNY CapHome Portal (LOA Search)", caphome_url, use_container_width=True)
                    
                    try:
                        supabase.table("property_searches").insert({
                            "user_id": st.session_state.user.id,
                            "bin": final_bin,
                            "loa_account_found": "Manual Search" 
                        }).execute()
                    except Exception: pass


# ------------------------------------------------------------
# TAB 2: PROFILE SETTINGS
# ------------------------------------------------------------
with tabs[2]:
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("💾 Data saved here is stored securely in the cloud and auto-fills your FDNY forms on every project.")

    with st.expander("🏢 Fire Alarm Vendor Information", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            c_name  = st.text_input("Company Name",   value=profile.get("company_name", ""),       key="c_name")
            c_addr  = st.text_input("Address",        value=profile.get("company_address", ""),    key="c_addr")
            c_city  = st.text_input("City",           value=profile.get("company_city", ""),       key="c_city")
            c_state = st.text_input("State",          value=profile.get("company_state", "NY"),    key="c_state")
            c_zip   = st.text_input("Zip Code",       value=profile.get("company_zip", ""),        key="c_zip")
            c_phone = st.text_input("Phone",          value=profile.get("company_phone", ""),      key="c_phone")
        with col2:
            c_email = st.text_input("Email",          value=profile.get("company_email", ""),      key="c_email")
            c_first = st.text_input("First Name",     value=profile.get("company_first_name", ""), key="c_first")
            c_last  = st.text_input("Last Name",      value=profile.get("company_last_name", ""),  key="c_last")
            c_cof   = st.text_input("COF S97",        value=profile.get("company_cof_s97", ""),    key="c_cof")
            c_exp   = st.text_input("Exp. Date",      value=profile.get("company_expiration", ""), key="c_exp")

    with st.expander("📑 Filing Representative / Expeditor"):
        col1, col2 = st.columns(2)
        with col1:
            x_name  = st.text_input("Company Name",   value=profile.get("exp_name", ""),       key="x_name")
            x_addr  = st.text_input("Address",        value=profile.get("exp_address", ""),    key="x_addr")
            x_city  = st.text_input("City",           value=profile.get("exp_city", ""),       key="x_city")
            x_state = st.text_input("State",          value=profile.get("exp_state", "NY"),    key="x_state")
            x_zip   = st.text_input("Zip Code",       value=profile.get("exp_zip", ""),        key="x_zip")
            x_phone = st.text_input("Phone",          value=profile.get("exp_phone", ""),      key="x_phone")
        with col2:
            x_email = st.text_input("Email",          value=profile.get("exp_email", ""),      key="x_email")
            x_first = st.text_input("First Name",     value=profile.get("exp_first_name", ""), key="x_first")
            x_last  = st.text_input("Last Name",      value=profile.get("exp_last_name", ""),  key="x_last")
            x_reg   = st.text_input("FDNY Reg No.",   value=profile.get("exp_reg_no", ""),     key="x_reg")

    with st.expander("📐 Architect / Engineer Information"):
        col1, col2 = st.columns(2)
        with col1:
            a_name    = st.text_input("Company Name",   value=profile.get("arch_name", ""),        key="a_name")
            a_addr    = st.text_input("Address",         value=profile.get("arch_address", ""),     key="a_addr")
            a_city    = st.text_input("City",            value=profile.get("arch_city", ""),        key="a_city")
            a_state   = st.text_input("State",           value=profile.get("arch_state", ""),       key="a_state")
            a_zip     = st.text_input("Zip Code",        value=profile.get("arch_zip", ""),         key="a_zip")
            a_phone   = st.text_input("Phone",           value=profile.get("arch_phone", ""),       key="a_phone")
        with col2:
            a_email   = st.text_input("Email",           value=profile.get("arch_email", ""),       key="a_email")
            a_first   = st.text_input("First Name",      value=profile.get("arch_first_name", ""),  key="a_first")
            a_last    = st.text_input("Last Name",       value=profile.get("arch_last_name", ""),   key="a_last")
            a_license = st.text_input("License No",      value=profile.get("arch_license", ""),     key="a_license")
            a_role    = st.selectbox("Role", ["PE", "RA"], index=0 if profile.get("arch_role") == "PE" else 1, key="a_role")

    with st.expander("⚡ Electrical Contractor Information"):
        col1, col2 = st.columns(2)
        with col1:
            e_name    = st.text_input("Company Name",   value=profile.get("elec_name", ""),        key="e_name")
            e_addr    = st.text_input("Address",         value=profile.get("elec_address", ""),     key="e_addr")
            e_city    = st.text_input("City",            value=profile.get("elec_city", ""),        key="e_city")
            e_state   = st.text_input("State",           value=profile.get("elec_state", ""),       key="e_state")
            e_zip     = st.text_input("Zip Code",        value=profile.get("elec_zip", ""),         key="e_zip")
            e_phone   = st.text_input("Phone",           value=profile.get("elec_phone", ""),       key="e_phone")
        with col2:
            e_email   = st.text_input("Email",           value=profile.get("elec_email", ""),       key="e_email")
            e_first   = st.text_input("First Name",      value=profile.get("elec_first_name", ""),  key="e_first")
            e_last    = st.text_input("Last Name",       value=profile.get("elec_last_name", ""),   key="e_last")
            e_license = st.text_input("License No",      value=profile.get("elec_license", ""),     key="e_license")
            e_exp     = st.text_input("Expiration",      value=profile.get("elec_expiration", ""),  key="e_exp")

    col1, col2 = st.columns(2)
    with col1:
        with st.expander("🛠️ A-433 Defaults"):
            t_man   = st.text_input("Default Manufacturer",  value=profile.get("tech_manufacturer", ""), key="t_man")
            t_appr  = st.text_input("BSA/MEA/COA Approval",  value=profile.get("tech_approval", ""),     key="t_appr")
            t_gauge = st.text_input("Wire Gauge",            value=profile.get("tech_wire_gauge", ""),   key="t_gauge")
            t_wire  = st.text_input("Wire Type",             value=profile.get("tech_wire_type", ""),    key="t_wire")
    with col2:
        with st.expander("📡 Central Station Information"):
            cs_name  = st.text_input("CS Name",    value=profile.get("cs_name", ""),    key="cs_name")
            cs_code  = st.text_input("CS Code",    value=profile.get("cs_code", ""),    key="cs_code")
            cs_addr  = st.text_input("CS Address", value=profile.get("cs_address", ""), key="cs_addr")
            cs_city  = st.text_input("CS City",    value=profile.get("cs_city", ""),    key="cs_city")
            cs_state = st.text_input("CS State",   value=profile.get("cs_state", ""),   key="cs_state")
            cs_zip   = st.text_input("CS Zip",     value=profile.get("cs_zip", ""),     key="cs_zip")
            cs_phone = st.text_input("CS Phone",   value=profile.get("cs_phone", ""),   key="cs_phone")
            
    st.markdown("<br>", unsafe_allow_html=True)
    col_save1, col_save2, col_save3 = st.columns([1, 1, 1])
    with col_save2:
        if st.button("💾 Save Profile", use_container_width=True, type="primary"):
            full_update = {
                "id": st.session_state.user.id,
                "updated_at": "now()",
                # Fire Alarm Vendor
                "company_name": c_name, "company_address": c_addr, "company_city": c_city,
                "company_state": c_state, "company_zip": c_zip, "company_phone": c_phone,
                "company_email": c_email, "company_first_name": c_first, "company_last_name": c_last,
                "company_cof_s97": c_cof, "company_expiration": c_exp,
                
                # Expeditor (Nuevos campos)
                "exp_name": x_name, "exp_address": x_addr, "exp_city": x_city,
                "exp_state": x_state, "exp_zip": x_zip, "exp_phone": x_phone,
                "exp_email": x_email, "exp_first_name": x_first, "exp_last_name": x_last,
                "exp_reg_no": x_reg,
                
                # Resto de los campos
                "arch_name": a_name, "arch_address": a_addr, "arch_city": a_city,
                "arch_state": a_state, "arch_zip": a_zip, "arch_phone": a_phone,
                "arch_email": a_email, "arch_first_name": a_first, "arch_last_name": a_last,
                "arch_license": a_license, "arch_role": a_role,
                "elec_name": e_name, "elec_address": e_addr, "elec_city": e_city,
                "elec_state": e_state, "elec_zip": e_zip, "elec_phone": e_phone,
                "elec_email": e_email, "elec_first_name": e_first, "elec_last_name": e_last,
                "elec_license": e_license, "elec_expiration": e_exp,
                "tech_manufacturer": t_man, "tech_approval": t_appr,
                "tech_wire_gauge": t_gauge, "tech_wire_type": t_wire,
                "cs_name": cs_name, "cs_code": cs_code, "cs_address": cs_addr,
                "cs_city": cs_city, "cs_state": cs_state, "cs_zip": cs_zip, "cs_phone": cs_phone,
            }
            try:
                supabase.table("profiles").upsert(full_update).execute()
                profile.update(full_update)
                sync_profile_to_main(profile)
                st.success("✅ Profile saved successfully!")
            except Exception as e:
                st.error(f"Error saving: {e}")

# ------------------------------------------------------------
# TAB 0: PROJECT BUILDER
# ------------------------------------------------------------
with tabs[0]:
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- NUEVA SECCIÓN: HISTORIAL (Ahora correctamente dentro del tab) ---
    with st.expander("📂 Recent Projects / History", expanded=False):
        projects = fetch_projects(st.session_state.user.id)
        if not projects:
            st.info("No saved projects yet.")
        else:
            for p in projects:
                col_p1, col_p2, col_p3 = st.columns([3, 1, 1])
                with col_p1:
                    st.markdown(f"**{p['address']}** (BIN: {p['bin']})")
                with col_p2:
                    if st.button(f"🔄 Load", key=f"load_{p['id']}", use_container_width=True):
                        st.session_state.bin_input = p['bin']
                        st.session_state.device_list = p['device_list']
                        st.session_state.job_desc_input = p['job_description']
                        st.rerun()
                with col_p3:
                    if st.button(f"🗑️", key=f"del_{p['id']}", use_container_width=True):
                        delete_project(p['id'])

    # --- ONBOARDING: AVISO INTELIGENTE SI EL PERFIL ESTÁ VACÍO ---
    if not profile.get("company_name"):
        aviso_urgente = """
        <div style="background-color: #FFF5F5; border: 2px solid #FC8181; border-left: 8px solid #E53E3E; padding: 16px; border-radius: 8px; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(229, 62, 62, 0.1);">
            <h4 style="color: #E53E3E; margin-top: 0; margin-bottom: 8px; font-size: 18px;">🚨 Action Required: Complete Your Profile First</h4>
            <p style="color: #2D3748; margin-bottom: 0; font-size: 15px;">
                <b>Welcome to Fire Form Pro!</b> Before generating your first PDF, please go to the <b>Profile Settings</b> tab to enter your company details and license numbers. <br><i>If you skip this step, your forms will be generated with blank company fields.</i>
            </p>
        </div>
        """
        st.markdown(aviso_urgente, unsafe_allow_html=True)

    # SECCIÓN 1 (CORREGIDA - SIN ERRORES DE SESIÓN)
    st.markdown("<h4 style='color: #2D3748;'>1️⃣ Project Information</h4>", unsafe_allow_html=True)
    col_info1, col_info2 = st.columns([1, 2])

    with col_info1:
        # Eliminamos 'st.session_state.bin_input = bin_number'
        # El widget ya guarda el valor en session_state['bin_input'] por su 'key'
        bin_number = st.text_input(
            "Property BIN Number", 
            value=st.session_state.get('bin_input', ''), 
            placeholder="e.g. 1012345",
            key="bin_input" 
        )

    with col_info2:
        # Eliminamos 'st.session_state.job_desc_input = job_desc'
        job_desc = st.text_area(
            "TM-1 Job Description", 
            value=st.session_state.get('job_desc_input', "Installation of Fire Alarm System."), 
            height=68,
            key="job_desc_input"
        )        
    
    
    # SECCIÓN 2
    st.markdown("<h4 style='color: #2D3748;'>2️⃣ Device Schedule <span style='font-size:14px; color:#A0AEC0;'>(A-433 Optional)</span></h4>", unsafe_allow_html=True)
    col_dev_left, col_dev_right = st.columns([1, 2])
    
    with col_dev_left:
        with st.container():
            floor    = st.selectbox("Floor Location", main.FULL_FLOOR_LIST)
            category = st.selectbox("Category", list(main.MASTER_DEVICE_LIST.keys()))
            device   = st.selectbox("Device Type", main.MASTER_DEVICE_LIST.get(category, []))
            qty      = st.number_input("Quantity", min_value=1, value=1)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("➕ Add to Schedule", use_container_width=True, type="secondary"):
                st.session_state.device_list.append({
                    "device": device,
                    "floor": floor,
                    "qty": qty,
                })
                st.success(f"Added: {device}")

    with col_dev_right:
        if st.session_state.device_list:
            edited_list = st.data_editor(
                st.session_state.device_list,
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    "qty": st.column_config.NumberColumn("Qty", min_value=1, max_value=999, step=1, required=True),
                    "device": st.column_config.TextColumn("Device Type", disabled=True),
                    "floor":  st.column_config.TextColumn("Floor Location", disabled=True),
                },
                key="device_editor",
            )
            if edited_list != st.session_state.device_list:
                st.session_state.device_list = edited_list
                st.rerun()
                
            if st.button("🗑️ Clear List", use_container_width=False, type="secondary"):
                st.session_state.device_list = []
                st.rerun()
        else:
            st.markdown("""
            <div style='background-color: white; border: 1px dashed #CBD5E0; border-radius: 12px; padding: 3rem; text-align: center; color: #A0AEC0;'>
                <h3 style='color: #A0AEC0; margin-bottom: 0.5rem;'>📋</h3>
                <p style='margin: 0;'>No devices added yet</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color: #E2E8F0; margin: 2rem 0;'>", unsafe_allow_html=True)

    # SECCIÓN 3
    st.markdown("<h4 style='color: #2D3748; text-align: center;'>3️⃣ Document Generation</h4>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_chk0, col_chk1, col_chk2, col_chk3, col_chk4, col_chk5 = st.columns([1, 2, 2, 2, 2, 1])
    with col_chk1:
        gen_tm1 = st.checkbox("📄 TM-1", value=True, key="chk_gen_tm1")
    with col_chk2:
        gen_a433 = st.checkbox("📋 A-433", value=True, key="chk_gen_a433")
    with col_chk3:
        gen_b45 = st.checkbox("🔍 B-45", value=True, key="chk_gen_b45")
    with col_chk4:
        gen_report = st.checkbox("📊 Report", value=True, key="chk_gen_report")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- LÓGICA DE SUSCRIPCIÓN ANTES DE GENERAR ---
    sub_data = check_subscription(st.session_state.user.id)
    is_pro = sub_data.get("plan_type") == "pro"
    usos_mes = sub_data.get("forms_generated_this_month", 0)
    
    col_gen1, col_gen2, col_gen3 = st.columns([1, 2, 1])
    with col_gen2:
        # Si es free y ya usó sus 2 oportunidades, BLOQUEAR
        if not is_pro and usos_mes >= 2:
            st.warning("⚠️ You have reached your free limit (2 forms/month).")
            st.markdown("### Upgrade to Pro for unlimited forms ($349/year)")
            
            # Inyectamos el botón de PayPal
            usuario_actual_id = st.session_state.user.id
            paypal_html = f"""
            <div id="paypal-button-container-P-73L06517ME334400KNGY24TI" style="text-align: center;"></div>
            <script src="https://www.paypal.com/sdk/js?client-id=AeCRCUKXnF3G_15llpYzaFzgqbaOeay3eWcO6fXMcaoRA6Cy7v2iXO5FOQPaqenMndAzHRR_YArdquue&vault=true&intent=subscription" data-sdk-integration-source="button-factory"></script>
            <script>
              paypal.Buttons({{
                  style: {{
                      shape: 'rect',
                      color: 'gold',
                      layout: 'vertical',
                      label: 'subscribe'
                  }},
                  createSubscription: function(data, actions) {{
                    return actions.subscription.create({{
                      plan_id: 'P-73L06517ME334400KNGY24TI',
                      custom_id: '{usuario_actual_id}' 
                    }});
                  }},
                  onApprove: function(data, actions) {{
                    // Muestra un mensaje y recarga la app para que detecte la cuenta Pro
                    alert("Thank you for upgrading! Your Pro account is now active.");
                    window.parent.location.reload();
                  }}
              }}).render('#paypal-button-container-P-73L06517ME334400KNGY24TI');
            </script>
            """
            components.html(paypal_html, height=150)
            
        else:
            # Mostrar indicador de usos si es free
            if not is_pro:
                st.info(f"💡 Free Account: You have used {usos_mes} out of 2 forms this month.")
                
            if st.button("GENERATE DOCUMENTS", type="primary", use_container_width=True):
                if not bin_number:
                    st.error("⚠️ Please enter a BIN number.")
                elif not (gen_tm1 or gen_a433 or gen_b45 or gen_report):
                    st.warning("⚠️ Select at least one form.")
                else:
                    with st.spinner("Fetching property data & generating..."):
                        try:
                            sync_profile_to_main(profile)
                            info = main.obtener_datos_completos(bin_number)
                            
                            if info:
                                # Si es cuenta Free, sumar 1 al uso ANTES de generar
                                if not is_pro:
                                    increment_free_usage(st.session_state.user.id, usos_mes)
                                    
                                address_full = f"{info.get('house')} {info.get('street')}, {info.get('borough')}"
                                
                                # --- NUEVO: Crear nombre seguro para los archivos ---
                                safe_address = f"{info.get('house')} {info.get('street')}".replace("/", "-").replace("\\", "-").strip()
                                if not safe_address:
                                    safe_address = bin_number # Respaldo por si no hay dirección
                                # ----------------------------------------------------

                                save_project(
                                    st.session_state.user.id, 
                                    bin_number, 
                                    address_full, 
                                    st.session_state.device_list, 
                                    job_desc
                                )
                            
                                job_specs = {"job_desc": job_desc, "devices": st.session_state.device_list}
                                full_data = {**info, **job_specs}
                                generated_files = []

                                if gen_tm1:
                                    fname = f"TM-1 - {safe_address}.pdf"
                                    main.generar_tm1(full_data, "tm-1-application-for-plan-examination-doc-review.pdf", fname)
                                    generated_files.append(fname)
                                if gen_a433:
                                    fname = f"A-433 - {safe_address}.pdf"
                                    main.generar_a433(full_data, "application-a-433-c.pdf", fname)
                                    generated_files.append(fname)
                                if gen_b45:
                                    fname = f"B-45 - {safe_address}.pdf"
                                    main.generar_b45(full_data, "b45-inspection-request.pdf", fname)
                                    generated_files.append(fname)
                                if gen_report:
                                    fname = f"REPORT - {safe_address}.txt"
                                    main.generar_reporte_auditoria(full_data, fname)
                                    generated_files.append(fname)

                                file_data_dict = {}
                                zip_buffer = BytesIO()
                                
                                with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                                    for file_name in generated_files:
                                        if os.path.exists(file_name):
                                            with open(file_name, "rb") as f:
                                                file_bytes = f.read()
                                                file_data_dict[file_name] = file_bytes
                                            zip_file.writestr(file_name, file_bytes)
                                            os.remove(file_name)

                                st.session_state.generated_data = {
                                    "archivos": file_data_dict,
                                    "zip_buffer": zip_buffer.getvalue(),
                                    "bin": bin_number,
                                    "address": safe_address
                                }
                                
                                # Si generó exitosamente, forzamos un rerun para actualizar el contador en pantalla
                                st.rerun() 
                                
                            else:
                                st.error("❌ Could not retrieve data for this BIN.")
                        except Exception as e:
                            st.error(f"❌ Error: {e}")

        # Bloque de descargas
        if "generated_data" in st.session_state and st.session_state.generated_data:
            st.markdown("<hr style='margin: 2rem 0;'>", unsafe_allow_html=True)
            datos = st.session_state.generated_data
            
            dir_lista = datos.get('address', datos['bin'])
            st.success(f"✅ {len(datos['archivos'])} documents ready for {dir_lista}!")
            
            st.download_button(
                label="📦 Download All as ZIP",
                data=datos["zip_buffer"],
                file_name=f"FDNY_Forms - {dir_lista}.zip",
                mime="application/zip",
                use_container_width=True,
                type="primary"
            )

            st.markdown("<p style='text-align: center; color: #A0AEC0; font-size: 14px; margin: 15px 0;'>Or download individually</p>", unsafe_allow_html=True)

            archivos_lista = list(datos['archivos'].items())
            for i in range(0, len(archivos_lista), 2):
                cols = st.columns(2)
                for j in range(2):
                    if i + j < len(archivos_lista):
                        f_name, f_bytes = archivos_lista[i + j]
                        with cols[j]:
                            mime_type = "text/plain" if f_name.endswith(".txt") else "application/pdf"
                            icon = "📊" if f_name.endswith(".txt") else "📄"
                            short_name = f_name.split(' - ')[0]
                            
                            st.download_button(
                                label=f"{icon} {short_name}",
                                data=f_bytes,
                                file_name=f_name,
                                mime=mime_type,
                                use_container_width=True
                            )

st.markdown('</div>', unsafe_allow_html=True)
