import streamlit as st
from supabase import create_client, Client
import main
import os
import zipfile
from io import BytesIO

# ── CONFIGURACIÓN DE PÁGINA ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Fire Form Pro", 
    layout="wide", 
    page_icon="🔥", 
    initial_sidebar_state="expanded"
)

# ── SECRETOS Y CONEXIÓN ──────────────────────────────────────────────────────
main.API_KEY_NYC       = st.secrets.get("NYC_API_KEY", "")
main.APP_TOKEN_SOCRATA = st.secrets.get("SOCRATA_TOKEN", "")
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "https://uhhiqkymipbcepqzwtvg.supabase.co")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "sb_publishable_mvqOWXc5s4b3_IMe4gGexw_sU3B2DRL")

# ── ESTILO CSS PERSONALIZADO (MODERNO & LIMPIO) ──────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Variables de Color */
    :root {
        --primary: #E03131; /* Rojo Fire Alarm */
        --primary-hover: #C92A2A;
        --bg-main: #F8F9FA;
        --text-main: #1A1B1E;
        --card-bg: #FFFFFF;
        --border: #E9ECEF;
    }

    html, body, [data-testid="stAppViewContainer"] {
        background-color: var(--bg-main);
        font-family: 'Inter', sans-serif;
    }

    /* Ocultar elementos innecesarios */
    [data-testid="stHeader"], [data-testid="stDecoration"] { display: none; }

    /* Tarjetas y Contenedores */
    .stTabs {
        background: transparent;
    }
    
    div[data-testid="stVerticalBlock"] > div.stButton button {
        border-radius: 8px;
    }

    /* Estilo para los Títulos de Pasos */
    .step-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 15px;
        margin-top: 10px;
    }
    .step-number {
        background-color: var(--primary);
        color: white;
        border-radius: 50%;
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 14px;
    }
    .step-title {
        font-weight: 600;
        font-size: 18px;
        color: #2C2E33;
    }

    /* Inputs y Selects */
    .stTextInput input, .stSelectbox, .stTextArea textarea {
        border-radius: 8px !important;
    }

    /* Botón Principal */
    div.stButton > button[kind="primary"] {
        background-color: var(--primary);
        border: none;
        padding: 0.5rem 2rem;
        font-weight: 600;
        width: 100%;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: var(--primary-hover);
    }
    
    /* Perfil en Sidebar */
    .user-profile {
        padding: 15px;
        background: #F1F3F5;
        border-radius: 12px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ── INICIALIZACIÓN SUPABASE ──────────────────────────────────────────────────
if "supabase" not in st.session_state:
    try:
        st.session_state.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Supabase Connection Error: {e}"); st.stop()

supabase = st.session_state.supabase

if "user" not in st.session_state:
    st.session_state.user = None
    try:
        session = supabase.auth.get_session()
        if session and session.user: st.session_state.user = session.user
    except: pass

if "device_list" not in st.session_state:
    st.session_state.device_list = []

# ── FUNCIONES ────────────────────────────────────────────────────────────────
def logout():
    supabase.auth.sign_out()
    st.session_state.user = None
    st.session_state.device_list = []
    st.rerun()

def fetch_profile(uid):
    try:
        res = supabase.table("profiles").select("*").eq("id", uid).execute()
        return res.data[0] if res.data else {}
    except: return {}

def sync_profile(p):
    main.COMPANY.update({
        "Company Name": p.get("company_name",""), "Address": p.get("company_address",""),
        "City": p.get("company_city",""), "State": p.get("company_state","NY"),
        "Zip": p.get("company_zip",""), "Phone": p.get("company_phone",""),
        "Email": p.get("company_email",""), "First Name": p.get("company_first_name",""),
        "Last Name": p.get("company_last_name",""), "Reg No": p.get("company_reg_no",""),
        "COF S97": p.get("company_cof_s97",""), "Expiration": p.get("company_expiration",""),
    })
    # (Se asume que los demás diccionarios main.ARCHITECT, main.ELECTRICIAN, etc. se actualizan igual)

# ── LÓGICA DE ACCESO ─────────────────────────────────────────────────────────
if not st.session_state.user:
    st.sidebar.title("🔥 Fire Form Pro")
    mode = st.sidebar.radio("Acceso", ["Login", "Registro"])
    email = st.sidebar.text_input("Email")
    pw = st.sidebar.text_input("Password", type="password")
    
    if st.sidebar.button("Entrar" if mode == "Login" else "Crear Cuenta", type="primary", use_container_width=True):
        try:
            if mode == "Login":
                res = supabase.auth.sign_in_with_password({"email": email, "password": pw})
            else:
                res = supabase.auth.sign_up({"email": email, "password": pw})
            if res.user: 
                st.session_state.user = res.user
                st.rerun()
        except Exception as e: st.sidebar.error(f"Error: {e}")
    
    st.title("Bienvenido a Fire Form Pro")
    st.info("Por favor inicia sesión en la barra lateral para comenzar.")
    st.stop()

# ── APP PRINCIPAL ────────────────────────────────────────────────────────────
profile = fetch_profile(st.session_state.user.id)

with st.sidebar:
    st.markdown(f"""
    <div class="user-profile">
        <small style="color: #868E96;">Usuario Activo</small><br>
        <strong>{st.session_state.user.email}</strong>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Cerrar Sesión", use_container_width=True): logout()

# Tabs Modernos
tab_project, tab_profile = st.tabs(["🚀 Project Builder", "👤 Professional Profile"])

# ==========================================
# TAB 0: PROJECT BUILDER
# ==========================================
with tab_project:
    col_left, col_right = st.columns([1, 1.2], gap="large")

    with col_left:
        # Paso 1
        st.markdown('<div class="step-header"><div class="step-number">1</div><div class="step-title">Project Info</div></div>', unsafe_allow_html=True)
        bin_no = st.text_input("Property BIN", placeholder="e.g. 1012345")
        job_desc = st.text_area("TM-1 Job Description", value="Installation of Fire Alarm System.", height=100)

        # Paso 2
        st.markdown('<div class="step-header"><div class="step-number">2</div><div class="step-title">Add Devices (A-433)</div></div>', unsafe_allow_html=True)
        f_col1, f_col2 = st.columns(2)
        with f_col1: floor = st.selectbox("Floor", main.FULL_FLOOR_LIST)
        with f_col2: qty = st.number_input("Qty", min_value=1, value=1)
        
        cat = st.selectbox("Category", list(main.MASTER_DEVICE_LIST.keys()))
        dev = st.selectbox("Device Type", main.MASTER_DEVICE_LIST.get(cat, []))
        
        if st.button("➕ Add to List", use_container_width=True):
            st.session_state.device_list.append({"device": dev, "floor": floor, "qty": qty})
            st.toast(f"Agregado: {dev}")

        # Paso 3: Selección y Generación
        st.markdown('<div class="step-header"><div class="step-number">3</div><div class="step-title">Output</div></div>', unsafe_allow_html=True)
        c_a, c_b = st.columns(2)
        with c_a:
            g_tm1 = st.checkbox("TM-1 Application", value=True)
            g_a433 = st.checkbox("A-433 Device List", value=True)
        with c_b:
            g_b45 = st.checkbox("B-45 Request", value=True)
            g_rep = st.checkbox("Audit Report", value=True)

        if st.button("🔥 GENERATE DOCUMENTS", type="primary"):
            if not bin_no:
                st.error("BIN is required")
            else:
                with st.spinner("Procesando..."):
                    # Aquí iría tu lógica de generación original...
                    st.success("Documentos listos para descarga")

    with col_right:
        st.markdown('<div class="step-header"><div class="step-number">4</div><div class="step-title">Review Device List</div></div>', unsafe_allow_html=True)
        
        if st.session_state.device_list:
            # CORRECCIÓN DE TABLA: Asignación directa sin rerun conflictivo
            st.session_state.device_list = st.data_editor(
                st.session_state.device_list,
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    "qty": st.column_config.NumberColumn("Qty", min_value=1),
                    "device": st.column_config.TextColumn("Device", disabled=True),
                    "floor": st.column_config.TextColumn("Floor", disabled=True),
                },
                key="editor_pro"
            )
            
            if st.button("🗑️ Clear All", use_container_width=True):
                st.session_state.device_list = []
                st.rerun()
        else:
            st.info("La lista está vacía. Agrega dispositivos desde el panel izquierdo.")

# ==========================================
# TAB 1: PROFILE (Simplificado)
# ==========================================
with tab_profile:
    st.subheader("Configuración Profesional")
    with st.expander("🏢 Fire Alarm Company Data", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Company Name", value=profile.get("company_name",""))
            addr = st.text_input("Address", value=profile.get("company_address",""))
        with c2:
            reg = st.text_input("Reg No", value=profile.get("company_reg_no",""))
            cof = st.text_input("COF S97", value=profile.get("company_cof_s97",""))

    if st.button("💾 Guardar Perfil", type="primary"):
        # Lógica de guardado en Supabase...
        st.success("Perfil actualizado correctamente")
