import streamlit as st
from supabase import create_client, Client
import main
import os
import zipfile
from io import BytesIO

# ============================================================
# CONFIGURACIÓN Y TEMA VISUAL (UI PRO)
# ============================================================
st.set_page_config(
    page_title="Fire Form Pro", 
    layout="wide", 
    page_icon="🔥",
    initial_sidebar_state="collapsed"
)

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

/* Reducir padding superior para aprovechar la pantalla */
.block-container {
    padding-top: 0rem !important;
    max-width: 100% !important;
    padding-left: 0rem !important;
    padding-right: 0rem !important;
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

if "user" not in st.session_state:
    st.session_state.user = None
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
    st.session_state.user = None
    st.session_state.device_list = []
    st.session_state.generated_data = None
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
        "Reg No":       profile.get("company_reg_no", ""),
        "COF S97":      profile.get("company_cof_s97", ""),
        "Expiration":   profile.get("company_expiration", ""),
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
            st.markdown("<p style='color: #718096 !important; font-size: 15px; margin-top: -90px; margin-bottom: 2rem;'>Automated form generation for the NYC Fire Alarm Industry</p>", unsafe_allow_html=True)
        else:
            st.markdown("<h1 style='color: #FF6B00; margin-bottom: 0;'>🔥 Fire Form Pro</h1>", unsafe_allow_html=True)
            st.markdown("<p style='color: #718096; font-size: 15px; margin-bottom: 2rem;'>Automated form generation for the NYC Fire Alarm Industry</p>", unsafe_allow_html=True)
            
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
                            response = supabase.auth.sign_in_with_password({"email": email.strip(), "password": password})
                            if response.user:
                                st.session_state.user = response.user
                                st.rerun()
                        except Exception as e:
                            st.error("⚠️ Invalid email or password.")
        
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
# CABECERA PRINCIPAL DE LA APP (HEADER ELEGANTE A PANTALLA COMPLETA)
# ============================================================
st.markdown("""
<div style="background: linear-gradient(135deg, #FF6B00 0%, #E65100 100%); 
            padding: 2.5rem 0; 
            margin: -1rem 0 0 0;
            box-shadow: 0 4px 20px rgba(255, 107, 0, 0.2);">
    <div style="max-width: 1400px; margin: 0 auto; padding: 0 3rem;">
""", unsafe_allow_html=True)

col_h_izq, col_h_der = st.columns([3, 1])

with col_h_izq:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=280)
        st.markdown("<p style='color: rgb(220 30 45); font-size: 15px; margin-top: -90px; margin-bottom: -15px; margin-left: 8px; font-weight: 500; letter-spacing: 0.3px;'>Automated form generation for the NYC Fire Alarm Industry</p>", unsafe_allow_html=True)
    else:
        st.markdown("<h1 style='color: white; margin: 0; font-size: 2.8rem; font-weight: 700; letter-spacing: -0.5px;'>🔥 Fire Form Pro</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: rgba(255,255,255,0.95); font-size: 15px; margin: 0; margin-top: 8px; font-weight: 500; letter-spacing: 0.3px;'>Automated form generation for the NYC Fire Alarm Industry</p>", unsafe_allow_html=True)

with col_h_der:
    st.markdown(f"""
    <div style='text-align: right; margin-bottom: 12px;'>
        <div style='background: rgba(255,255,255,0.2); 
                    backdrop-filter: blur(10px); 
                    padding: 10px 20px; 
                    border-radius: 25px; 
                    display: inline-block;
                    border: 1px solid rgba(255,255,255,0.3);'>
            <span style='color: white !important; font-weight: 600; font-size: 14px;'>👤 {st.session_state.user.email}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
        logout()

st.markdown("</div></div>", unsafe_allow_html=True)

# Contenedor para el contenido principal
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# ============================================================
# APP PRINCIPAL (PESTAÑAS)
# ============================================================
profile = fetch_user_profile(st.session_state.user.id)
tabs = st.tabs(["🏗️ Project Builder", "👤 Profile Settings"])

# ------------------------------------------------------------
# TAB 1: PROFILE SETTINGS
# ------------------------------------------------------------
with tabs[1]:
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("💾 Data saved here is stored securely in the cloud and auto-fills your FDNY forms on every project.")

    with st.expander("🏢 FA Company / Expeditor Information", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            c_name  = st.text_input("Company Name",  value=profile.get("company_name", ""),       key="c_name")
            c_addr  = st.text_input("Address",        value=profile.get("company_address", ""),    key="c_addr")
            c_city  = st.text_input("City",           value=profile.get("company_city", ""),       key="c_city")
            c_state = st.text_input("State",          value=profile.get("company_state", "NY"),      key="c_state")
            c_zip   = st.text_input("Zip Code",       value=profile.get("company_zip", ""),        key="c_zip")
            c_phone = st.text_input("Phone",          value=profile.get("company_phone", ""),      key="c_phone")
        with col2:
            c_email = st.text_input("Email",          value=profile.get("company_email", ""),      key="c_email")
            c_first = st.text_input("First Name",     value=profile.get("company_first_name", ""), key="c_first")
            c_last  = st.text_input("Last Name",      value=profile.get("company_last_name", ""),  key="c_last")
            c_reg   = st.text_input("Reg No",         value=profile.get("company_reg_no", ""),     key="c_reg")
            c_cof   = st.text_input("COF S97",        value=profile.get("company_cof_s97", ""),    key="c_cof")
            c_exp   = st.text_input("Exp. Date",      value=profile.get("company_expiration", ""), key="c_exp")

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
                "company_name": c_name, "company_address": c_addr, "company_city": c_city,
                "company_state": c_state, "company_zip": c_zip, "company_phone": c_phone,
                "company_email": c_email, "company_first_name": c_first, "company_last_name": c_last,
                "company_reg_no": c_reg, "company_cof_s97": c_cof, "company_expiration": c_exp,
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

    # SECCIÓN 1 (CORREGIDA CON SANGREÍA CORRECTA)
    st.markdown("<h4 style='color: #2D3748;'>1️⃣ Project Information</h4>", unsafe_allow_html=True)
    col_info1, col_info2 = st.columns([1, 2])

    with col_info1:
        # Fíjate que bin_number ahora está indentado 4 espacios hacia adentro
        bin_number = st.text_input(
            "Property BIN Number", 
            value=st.session_state.get('bin_input', ''), 
            placeholder="e.g. 1012345",
            key="bin_input" 
        )
        st.session_state.bin_input = bin_number

    with col_info2:
        # Fíjate que job_desc ahora está indentado 4 espacios hacia adentro
        job_desc = st.text_area(
            "TM-1 Job Description", 
            value=st.session_state.get('job_desc_input', "Installation of Fire Alarm System."), 
            height=68,
            key="job_desc_widget"
        )
        st.session_state.job_desc_input = job_desc        
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
    
    col_gen1, col_gen2, col_gen3 = st.columns([1, 2, 1])
    with col_gen2:
        if st.button("🔥 GENERATE DOCUMENTS", type="primary", use_container_width=True):
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
                            address_full = f"{info.get('house')} {info.get('street')}, {info.get('borough')}"
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
                                main.generar_tm1(full_data, "tm-1-application-for-plan-examination-doc-review.pdf", f"TM1_{bin_number}.pdf")
                                generated_files.append(f"TM1_{bin_number}.pdf")
                            if gen_a433:
                                main.generar_a433(full_data, "application-a-433-c.pdf", f"A433_{bin_number}.pdf")
                                generated_files.append(f"A433_{bin_number}.pdf")
                            if gen_b45:
                                main.generar_b45(full_data, "b45-inspection-request.pdf", f"B45_{bin_number}.pdf")
                                generated_files.append(f"B45_{bin_number}.pdf")
                            if gen_report:
                                main.generar_reporte_auditoria(full_data, f"REPORT_{bin_number}.txt")
                                generated_files.append(f"REPORT_{bin_number}.txt")

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
                                "bin": bin_number
                            }
                        else:
                            st.error("❌ Could not retrieve data for this BIN.")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")

        # Bloque de descargas
        if "generated_data" in st.session_state and st.session_state.generated_data:
            st.markdown("<hr style='margin: 2rem 0;'>", unsafe_allow_html=True)
            datos = st.session_state.generated_data
            
            st.success(f"✅ {len(datos['archivos'])} documents ready for BIN {datos['bin']}!")
            
            st.download_button(
                label="📦 Download All as ZIP",
                data=datos["zip_buffer"],
                file_name=f"FDNY_Forms_{datos['bin']}.zip",
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
                            short_name = f_name.split('_')[0]
                            
                            st.download_button(
                                label=f"{icon} {short_name}",
                                data=f_bytes,
                                file_name=f_name,
                                mime=mime_type,
                                use_container_width=True
                            )

st.markdown('</div>', unsafe_allow_html=True)
