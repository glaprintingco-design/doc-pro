import streamlit as st
from supabase import create_client, Client
import main
import os
import zipfile
from io import BytesIO

# ============================================================
# CONFIGURACIÓN PROFESIONAL (CORREGIDA)
# ============================================================
st.set_page_config(
    page_title="Fire Form Pro", 
    layout="wide", 
    page_icon="🔥",
    initial_sidebar_state="collapsed"
)

# CSS PROFESIONAL MEJORADO (FUNCIONAL)
pro_styles = """
<style>
/* Reset y tipografía */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
#MainMenu, footer, header {visibility: hidden;}
.stApp { 
    font-family: 'Inter', sans-serif; 
    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
}

/* Variables CSS */
:root {
    --primary-gradient: linear-gradient(135deg, #f97316 0%, #ea580c 50%, #c2410c 100%);
    --primary: #f97316;
    --bg-primary: #ffffff;
    --bg-secondary: #f8fafc;
    --text-primary: #1e293b;
    --text-secondary: #64748b;
    --border: #e2e8f0;
    --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
    --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
}

.stApp h1,h2,h3,h4,h5,h6 { color: var(--text-primary); font-weight: 600; }
.stApp p,span,div,label { color: var(--text-primary); }

/* Layout */
.block-container {
    padding-top: 1rem !important;
    max-width: 100% !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
}
.main-content {
    max-width: 1440px;
    margin: 0 auto;
    padding: 2rem 2rem 4rem;
}

/* Header Hero */
.header-hero {
    background: var(--primary-gradient);
    border-radius: 24px;
    margin: 0 0 2rem 0;
    box-shadow: var(--shadow-lg);
    overflow: hidden;
}

/* Botones */
.stButton > button {
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 12px 24px !important;
    border: none !important;
    transition: all 0.2s ease !important;
}
.stButton > button[kind="primary"] {
    background: var(--primary-gradient) !important;
    color: white !important;
    box-shadow: var(--shadow-md) !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 20px 25px -5px rgb(249 115 22 / 0.4) !important;
}
.stButton > button[kind="secondary"] {
    background: var(--bg-primary) !important;
    color: var(--text-primary) !important;
    border: 2px solid var(--border) !important;
}

/* Cards */
[data-testid="stExpander"] {
    background: var(--bg-primary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 20px !important;
    box-shadow: var(--shadow-md) !important;
    margin-bottom: 1.5rem !important;
}
[data-testid="stExpander"] summary {
    padding: 1.5rem 2rem !important;
    font-weight: 600 !important;
    font-size: 1.1rem !important;
}

/* Inputs */
.stTextInput input, .stNumberInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
    background: var(--bg-primary) !important;
    border: 2px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 14px 16px !important;
    transition: border-color 0.2s ease !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgb(249 115 22 / 0.1) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab"] {
    padding: 12px 24px !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
}
.stTabs [aria-selected="true"] {
    background: var(--primary-gradient) !important;
    color: white !important;
}

/* User card */
.user-card {
    background: rgba(255,255,255,0.25) !important;
    backdrop-filter: blur(20px) !important;
    border: 1px solid rgba(255,255,255,0.3) !important;
    border-radius: 16px !important;
    padding: 16px 24px !important;
}
</style>
"""
st.markdown(pro_styles, unsafe_allow_html=True)

# ============================================================
# INICIALIZACIÓN (FUNCIONAL)
# ============================================================
# ... [Mismo código de inicialización que tenías originalmente] ...
main.API_KEY_NYC = st.secrets.get("NYC_API_KEY", "")
main.APP_TOKEN_SOCRATA = st.secrets.get("SOCRATA_TOKEN", "")

SUPABASE_URL = st.secrets.get("SUPABASE_URL", "https://uhhiqkymipbcepqzwtvg.supabase.co")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "sb_publishable_mvqOWXc5s4b3_IMe4gGexw_sU3B2DRL")

if "supabase" not in st.session_state:
    try:
        st.session_state.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except:
        st.error("❌ Supabase connection failed")
        st.stop()

supabase = st.session_state.supabase

if "user" not in st.session_state:
    st.session_state.user = None
    try:
        session = supabase.auth.get_session()
        if session and session.user:
            st.session_state.user = session.user
    except:
        pass

if "device_list" not in st.session_state:
    st.session_state.device_list = []
if "generated_data" not in st.session_state:
    st.session_state.generated_data = None

# Funciones (iguales a las originales)
def logout():
    try: supabase.auth.sign_out()
    except: pass
    st.session_state.user = None
    st.session_state.device_list = []
    st.session_state.generated_data = None
    st.rerun()

def fetch_user_profile(user_id):
    try:
        response = supabase.table("profiles").select("*").eq("id", user_id).execute()
        return response.data[0] if response.data else {}
    except:
        return {}

def sync_profile_to_main(profile):
    # ... [Tu código original de sync_profile_to_main] ...
    pass

# ============================================================
# LOGIN CORREGIDO
# ============================================================
def login_ui_centered():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style='background: rgba(255,255,255,0.95); backdrop-filter: blur(30px); border-radius: 32px; padding: 4rem 3rem; 
                    box-shadow: var(--shadow-lg); border: 1px solid rgba(255,255,255,0.3); text-align: center; max-width: 480px; margin: 2rem auto;'>
        """, unsafe_allow_html=True)
        
        if os.path.exists("logo.png"):
            st.image("logo.png", width=220)
        else:
            st.markdown("<h1 style='color: var(--primary); font-size: 3rem; font-weight: 700; margin: 0 0 1rem 0;'>🔥 Fire Form Pro</h1>", unsafe_allow_html=True)
        
        st.markdown("<p style='color: var(--text-secondary); font-size: 16px; margin-bottom: 3rem;'>Automated form generation for NYC Fire Alarm Industry</p>", unsafe_allow_html=True)
            
        tab1, tab2 = st.tabs(["🔑 Sign In", "📝 Create Account"])
        
        with tab1:
            email = st.text_input("📧 Email", key="login_email", placeholder="you@company.com")
            password = st.text_input("🔒 Password", type="password", key="login_password")
            
            if st.button("Sign In →", type="primary", use_container_width=True):
                # Tu lógica de login original
                pass
        
        with tab2:
            email = st.text_input("📧 Email", key="signup_email")
            password = st.text_input("🔒 Password", type="password", key="signup_password")
            password_confirm = st.text_input("🔒 Confirm Password", type="password", key="signup_password_confirm")
            
            if st.button("Create Account →", type="primary", use_container_width=True):
                # Tu lógica de signup original
                pass

        st.markdown("</div>", unsafe_allow_html=True)

if not st.session_state.user:
    login_ui_centered()
    st.stop()

# ============================================================
# HEADER CORREGIDO
# ============================================================
st.markdown("""
<div class="header-hero">
    <div style="max-width: 1440px; margin: 0 auto; padding: 3rem 3rem 2rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; gap: 2rem;">
""", unsafe_allow_html=True)

col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=260)
    else:
        st.markdown("<h1 style='color: white; font-size: 2.8rem; margin: 0;'>🔥 Fire Form Pro</h1>", unsafe_allow_html=True)

with col_h2:
    st.markdown(f'<div class="user-card"><div style="font-size: 14px; color: rgba(255,255,255,0.9);">👤 {st.session_state.user.email}</div></div>', unsafe_allow_html=True)
    if st.button("🚪 Logout", key="logout_btn"):
        logout()

st.markdown("</div></div>", unsafe_allow_html=True)

st.markdown('<div class="main-content">', unsafe_allow_html=True)

# ============================================================
# TABS PRINCIPALES (CORREGIDAS)
# ============================================================
profile = fetch_user_profile(st.session_state.user.id)
tabs = st.tabs(["🏗️ Project Builder", "👤 Profile Settings"])

with tabs[1]:
    st.info("💾 Profile data auto-fills your FDNY forms")
    
    with st.expander("🏢 FA Company Information", expanded=True):
        col1, col2 = st.columns(2)  # ✅ SIN gap inválido
        with col1:
            c_name = st.text_input("Company Name", value=profile.get("company_name", ""), key="c_name")
            c_addr = st.text_input("Address", value=profile.get("company_address", ""), key="c_addr")
        with col2:
            c_email = st.text_input("Email", value=profile.get("company_email", ""), key="c_email")
            c_phone = st.text_input("Phone", value=profile.get("company_phone", ""), key="c_phone")
    
    # Botón save corregido
    col_save1, col_save2 = st.columns([1, 1])
    with col_save2:
        if st.button("💾 Save Profile", type="primary", use_container_width=True):
            # Tu lógica de save
            st.success("✅ Profile saved!")

with tabs[0]:
    # Project info corregido
    col_info1, col_info2 = st.columns([1, 2])  # ✅ SIN gap
    with col_info1:
        bin_number = st.text_input("Property BIN", placeholder="1012345")
    with col_info2:
        job_desc = st.text_area("Job Description", value="Installation of Fire Alarm System.", height=70)

    # Device schedule corregido
    col_dev1, col_dev2 = st.columns([1, 2])
    with col_dev1:
        floor = st.selectbox("Floor", main.FULL_FLOOR_LIST)
        # ... resto igual
    
    with col_dev2:
        if st.session_state.device_list:
            st.data_editor(st.session_state.device_list, use_container_width=True)
        else:
            st.markdown("""
            <div style='text-align: center; padding: 3rem; color: var(--text-secondary);'>
                <h3>📋 No devices</h3>
                <p>Add devices on the left</p>
            </div>
            """, unsafe_allow_html=True)

    # Generate corregido
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.checkbox("📄 TM-1", key="chk1")
    with col2: st.checkbox("📋 A-433", key="chk2")
    with col3: st.checkbox("🔍 B-45", key="chk3")
    with col4: st.checkbox("📊 Report", key="chk4")
    
    if st.button("🚀 GENERATE DOCUMENTS", type="primary", use_container_width=True):
        # Tu lógica de generación
        pass

st.markdown('</div>', unsafe_allow_html=True)
