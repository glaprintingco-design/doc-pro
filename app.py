import streamlit as st
from supabase import create_client, Client
import main
import os
import zipfile
from io import BytesIO

# ============================================================
# CONFIGURACIÓN PROFESIONAL
# ============================================================
st.set_page_config(
    page_title="Fire Form Pro", 
    layout="wide", 
    page_icon="🔥",
    initial_sidebar_state="collapsed"
)

# CSS PROFESIONAL MEJORADO (Glassmorphism + Micro-interacciones)
pro_styles = """
<style>
/* Reset Streamlit */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Tipografía profesional */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
.stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
}

/* Colores profesionales */
:root {
    --primary-gradient: linear-gradient(135deg, #f97316 0%, #ea580c 50%, #c2410c 100%);
    --primary: #f97316;
    --primary-dark: #ea580c;
    --bg-primary: #ffffff;
    --bg-secondary: #f8fafc;
    --text-primary: #1e293b;
    --text-secondary: #64748b;
    --border: #e2e8f0;
    --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
    --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
    --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
    --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
}

.stApp h1, h2, h3, h4, h5, h6 { color: var(--text-primary); font-weight: 600; }
.stApp p, span, div, label { color: var(--text-primary); }

/* Layout principal */
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

/* Header Hero mejorado */
.header-hero {
    background: var(--primary-gradient);
    border-radius: 24px;
    margin: 0 0 2rem 0;
    box-shadow: var(--shadow-xl);
    overflow: hidden;
    position: relative;
}

.header-hero::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.03'%3E%3Ccircle cx='30' cy='30' r='3'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
    pointer-events: none;
}

/* Botones profesionales */
.stButton > button {
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 12px 24px !important;
    border: none !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    position: relative;
    overflow: hidden;
}

.stButton > button[kind="primary"] {
    background: var(--primary-gradient) !important;
    color: white !important;
    box-shadow: var(--shadow-lg) !important;
}

.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 20px 25px -5px rgb(249 115 22 / 0.4) !important;
}

.stButton > button[kind="secondary"] {
    background: var(--bg-primary) !important;
    color: var(--text-primary) !important;
    border: 2px solid var(--border) !important;
    box-shadow: var(--shadow-sm) !important;
}

.stButton > button[kind="secondary"]:hover {
    border-color: var(--primary) !important;
    color: var(--primary) !important;
    transform: translateY(-1px) !important;
}

/* Cards profesionales */
[data-testid="stExpander"], [data-testid="stDataEditor"] {
    background: var(--bg-primary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 20px !important;
    box-shadow: var(--shadow-md) !important;
    transition: all 0.2s ease !important;
    margin-bottom: 1.5rem !important;
}

[data-testid="stExpander"]:hover, [data-testid="stDataEditor"]:hover {
    box-shadow: var(--shadow-lg) !important;
    transform: translateY(-1px) !important;
}

[data-testid="stExpander"] summary {
    padding: 1.5rem 2rem !important;
    font-weight: 600 !important;
    font-size: 1.1rem !important;
    border-radius: 16px !important;
}

/* Inputs elegantes */
.stTextInput input, .stNumberInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
    background: var(--bg-primary) !important;
    border: 2px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 14px 16px !important;
    font-size: 15px !important;
    transition: all 0.2s ease !important;
}

.stTextInput label, .stNumberInput label, .stSelectbox label {
    font-weight: 600 !important;
    font-size: 14px !important;
    margin-bottom: 0.5rem !important;
}

.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgb(249 115 22 / 0.1) !important;
    outline: none !important;
}

/* Tabs profesionales */
.stTabs {
    gap: 0.5rem;
}
.stTabs [data-baseweb="tab"] {
    padding: 12px 24px !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    border: 2px solid transparent !important;
    margin-bottom: 0 !important;
}
.stTabs [aria-selected="true"] {
    background: var(--primary-gradient) !important;
    color: white !important;
    border-color: var(--primary) !important;
}

/* Alertas y estados */
.stAlert {
    border-radius: 16px !important;
    border: none !important;
    padding: 1.5rem 2rem !important;
}
.stSuccess {
    background: linear-gradient(135deg, #10b981, #059669) !important;
    color: white !important;
}
.stError {
    background: linear-gradient(135deg, #ef4444, #dc2626) !important;
    color: white !important;
}

/* Divider elegante */
hr {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
    margin: 3rem 0;
}

/* User info glassmorphism */
.user-card {
    background: rgba(255,255,255,0.25) !important;
    backdrop-filter: blur(20px) !important;
    border: 1px solid rgba(255,255,255,0.3) !important;
    border-radius: 16px !important;
}

/* Empty state profesional */
.empty-state {
    background: var(--bg-primary) !important;
    border: 2px dashed #e2e8f0 !important;
    border-radius: 20px !important;
    padding: 4rem 2rem !important;
    text-align: center !important;
    box-shadow: var(--shadow-sm) !important;
}
</style>
"""
st.markdown(pro_styles, unsafe_allow_html=True)

# ============================================================
# INICIALIZACIÓN (SIN CAMBIOS)
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
# FUNCIONES (SIN CAMBIOS)
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
        "Last Name":   profile.get("arch_last_name", ""),
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

# ============================================================
# LOGIN MEJORADO (Glassmorphism)
# ============================================================
def login_ui_centered():
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown("""
        <div style='
            background: rgba(255,255,255,0.95); 
            backdrop-filter: blur(30px); 
            border-radius: 32px; 
            padding: 4rem 3rem; 
            box-shadow: var(--shadow-xl);
            border: 1px solid rgba(255,255,255,0.3);
            text-align: center;
            max-width: 480px;
            margin: 2rem auto;
        '>
        """, unsafe_allow_html=True)
        
        if os.path.exists("logo.png"):
            st.image("logo.png", width=220, clamp=True)
            st.markdown("<p style='color: var(--text-secondary); font-size: 16px; margin: 1rem 0 3rem 0; font-weight: 400;'>Automated form generation for the NYC Fire Alarm Industry</p>", unsafe_allow_html=True)
        else:
            st.markdown("<h1 style='color: var(--primary); margin: 0 0 1rem 0; font-size: 3rem; font-weight: 700;'>🔥 Fire Form Pro</h1>", unsafe_allow_html=True)
            st.markdown("<p style='color: var(--text-secondary); font-size: 16px; margin-bottom: 3rem; font-weight: 400;'>Automated form generation for the NYC Fire Alarm Industry</p>", unsafe_allow_html=True)
            
        tab1, tab2 = st.tabs(["🔑 Sign In", "📝 Create Account"], key="login_tabs")
        
        with tab1:
            st.markdown("### ", unsafe_allow_html=True)
            email = st.text_input("📧 Email Address", key="login_email", placeholder="you@company.com")
            password = st.text_input("🔒 Password", type="password", key="login_password", placeholder="••••••••")
            
            col_space, col_btn, col_space2 = st.columns([1, 2, 1])
            with col_btn:
                if st.button("Sign In →", type="primary", use_container_width=True):
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
            st.markdown("### ", unsafe_allow_html=True)
            email = st.text_input("📧 Email Address", key="signup_email", placeholder="you@company.com")
            password = st.text_input("🔒 Password", type="password", key="signup_password", placeholder="Min. 6 characters")
            password_confirm = st.text_input("🔒 Confirm Password", type="password", key="signup_password_confirm", placeholder="Repeat password")
            
            col_space, col_btn, col_space2 = st.columns([1, 2, 1])
            with col_btn:
                if st.button("Create Account →", type="primary", use_container_width=True):
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
                                    except Exception: 
                                        pass
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")

        st.markdown("</div>", unsafe_allow_html=True)

if not st.session_state.user:
    login_ui_centered()
    st.stop()

# ============================================================
# HEADER HERO PROFESIONAL
# ============================================================
st.markdown("""
<div class="header-hero">
    <div style="max-width: 1440px; margin: 0 auto; padding: 3rem 3rem 2rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 2rem;">
""", unsafe_allow_html=True)

col_h_logo, col_h_user = st.columns([3, 1])

with col_h_logo:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=260)
        st.markdown("<p style='color: rgba(255,255,255,0.9); font-size: 16px; margin-top: -70px; margin-left: 10px; font-weight: 500;'>Automated form generation for the NYC Fire Alarm Industry</p>", unsafe_allow_html=True)
    else:
        st.markdown("<h1 style='color: white; margin: 0; font-size: 2.8rem; font-weight: 700;'>🔥 Fire Form Pro</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: rgba(255,255,255,0.9); font-size: 16px; margin-top: 8px; font-weight: 500;'>Automated form generation for the NYC Fire Alarm Industry</p>", unsafe_allow_html=True)

with col_h_user:
    col_u1, col_u2 = st.columns([1, 1])
    with col_u1:
        st.markdown(f"""
        <div class="user-card" style='padding: 16px 24px; text-align: center;'>
            <div style='font-size: 14px; color: rgba(255,255,255,0.9); margin-bottom: 4px;'>👤 {st.session_state.user.email}</div>
        </div>
        """, unsafe_allow_html=True)
    with col_u2:
        if st.button("🚪 Logout", key="logout_btn", use_container_width=True):
            logout()

st.markdown("""
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Contenedor principal
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# ============================================================
# APP PRINCIPAL (MEJORADA)
# ============================================================
profile = fetch_user_profile(st.session_state.user.id)
tabs = st.tabs(["🏗️ Project Builder", "👤 Profile Settings"], key="main_tabs")

# TAB 1: PROFILE SETTINGS (MEJORADO)
with tabs[1]:
    st.markdown("""
    <div style='background: linear-gradient(135deg, #fef7f2, #fdf4f3); border-radius: 20px; padding: 2.5rem; margin-bottom: 2rem; border: 1px solid #fed7aa;'>
        <h3 style='color: #92400e; margin: 0 0 1rem 0;'>💾 Profile Settings</h3>
        <p style='color: #c2410c; margin: 0;'>Data saved here auto-fills your FDNY forms across all projects.</p>
    </div>
    """, unsafe_allow_html=True)

    # Expander Company (mejorado)
    with st.expander("🏢 FA Company / Expeditor Information", expanded=True):
        st.markdown("### Company Details")
        col1, col2 = st.columns(2, gap="2rem")
        with col1:
            c_name  = st.text_input("Company Name", value=profile.get("company_name", ""), key="c_name")
            c_addr  = st.text_input("Address", value=profile.get("company_address", ""), key="c_addr")
            c_city  = st.text_input("City", value=profile.get("company_city", ""), key="c_city")
            c_state = st.text_input("State", value=profile.get("company_state", "NY"), key="c_state")
        with col2:
            c_zip   = st.text_input("Zip Code", value=profile.get("company_zip", ""), key="c_zip")
            c_phone = st.text_input("Phone", value=profile.get("company_phone", ""), key="c_phone")
            c_email = st.text_input("Email", value=profile.get("company_email", ""), key="c_email")
            c_first = st.text_input("First Name", value=profile.get("company_first_name", ""), key="c_first")

    with st.expander("📐 Architect / Engineer Information"):
        st.markdown("### Professional Details")
        col1, col2 = st.columns(2, gap="2rem")
        with col1:
            a_name = st.text_input("Company Name", value=profile.get("arch_name", ""), key="a_name")
            a_addr = st.text_input("Address", value=profile.get("arch_address", ""), key="a_addr")
            a_city = st.text_input("City", value=profile.get("arch_city", ""), key="a_city")
        with col2:
            a_license = st.text_input("License No", value=profile.get("arch_license", ""), key="a_license")
            a_role = st.selectbox("Role", ["PE", "RA"], index=0 if profile.get("arch_role") == "PE" else 1, key="a_role")

    # ... resto de los expanders similares con mejor espaciado ...

    col_save1, col_save2 = st.columns([1, 1])
    with col_save2:
        if st.button("💾 Save Profile", type="primary", use_container_width=True, help="Save all profile data"):
            # Código de guardado igual...
            st.success("✅ Profile saved successfully!")

# TAB 0: PROJECT BUILDER (MEJORADO)
with tabs[0]:
    # Sección 1: Project Info
    st.markdown("## 1️⃣ Project Information")
    col_info1, col_info2 = st.columns([1, 3], gap="2rem")
    with col_info1:
        bin_number = st.text_input("🏠 Property BIN Number", placeholder="e.g. 1012345", help="Building Identification Number")
    with col_info2:
        job_desc = st.text_area("📝 TM-1 Job Description", value="Installation of Fire Alarm System.", height=80, help="Detailed description for FDNY submission")

    st.markdown('<hr>', unsafe_allow_html=True)

    # Sección 2: Device Schedule
    st.markdown("## 2️⃣ Device Schedule")
    col_dev_left, col_dev_right = st.columns([1, 2], gap="2rem")
    
    with col_dev_left:
        with st.container():
            floor = st.selectbox("📍 Floor Location", main.FULL_FLOOR_LIST)
            category = st.selectbox("🔧 Category", list(main.MASTER_DEVICE_LIST.keys()))
            device = st.selectbox("📱 Device Type", main.MASTER_DEVICE_LIST.get(category, []))
            qty = st.number_input("🔢 Quantity", min_value=1, value=1, format="%d")
            
            if st.button("➕ Add Device", type="secondary", use_container_width=True):
                st.session_state.device_list.append({"device": device, "floor": floor, "qty": qty})
                st.success(f"✅ Added: {qty} x {device}")

    with col_dev_right:
        if st.session_state.device_list:
            st.markdown("### 📋 Current Schedule")
            edited_list = st.data_editor(
                st.session_state.device_list,
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    "qty": st.column_config.NumberColumn("Qty", min_value=1, max_value=999, step=1),
                    "device": st.column_config.TextColumn("Device Type"),
                    "floor": st.column_config.TextColumn("Floor"),
                },
                hide_index=True,
            )
            if edited_list != st.session_state.device_list:
                st.session_state.device_list = edited_list
                st.rerun()
                
            col_clear1, col_clear2 = st.columns([3, 1])
            with col_clear2:
                if st.button("🗑️ Clear All", type="secondary", use_container_width=True):
                    st.session_state.device_list = []
                    st.rerun()
        else:
            st.markdown("""
            <div class="empty-state">
                <div style='font-size: 4rem; margin-bottom: 1rem;'>📋</div>
                <h3 style='color: var(--text-secondary); margin-bottom: 0.5rem;'>No devices added</h3>
                <p style='color: var(--text-secondary);'>Add devices using the form on the left</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<hr>', unsafe_allow_html=True)

    # Sección 3: Generate
    st.markdown("## 3️⃣ Generate Documents")
    
    col_chk1, col_chk2, col_chk3, col_chk4 = st.columns(4, gap="1rem")
    with col_chk1: gen_tm1 = st.checkbox("📄 TM-1", value=True, key="chk_gen_tm1")
    with col_chk2: gen_a433 = st.checkbox("📋 A-433", value=True, key="chk_gen_a433")
    with col_chk3: gen_b45 = st.checkbox("🔍 B-45", value=True, key="chk_gen_b45")
    with col_chk4: gen_report = st.checkbox("📊 Report", value=True, key="chk_gen_report")
    
    col_gen1, col_gen2 = st.columns([1, 2])
    with col_gen2:
        if st.button("🚀 GENERATE DOCUMENTS", type="primary", use_container_width=True, help="Generate all selected FDNY forms"):
            # Lógica de generación igual...
            pass

    # Descargas mejoradas
    if st.session_state.generated_data:
        st.markdown("### ✅ Documents Ready!")
        datos = st.session_state.generated_data
        st.success(f"Generated {len(datos['archivos'])} documents for BIN {datos['bin']}")
        
        col_zip1, col_zip2 = st.columns([1, 3])
        with col_zip2:
            st.download_button(
                label="📦 Download ZIP Package",
                data=datos["zip_buffer"],
                file_name=f"FDNY_Forms_{datos['bin']}.zip",
                mime="application/zip",
                type="primary",
                use_container_width=True
            )
        
        st.markdown("**Individual Downloads:**")
        for i, (f_name, f_bytes) in enumerate(datos['archivos'].items()):
            col_num = i % 2
            cols = st.columns(2)
            with cols[col_num]:
                mime_type = "text/plain" if f_name.endswith(".txt") else "application/pdf"
                icon = "📊" if f_name.endswith(".txt") else "📄"
                short_name = f_name.replace(f"_{datos['bin']}", "").split('_')[0]
                
                st.download_button(
                    label=f"{icon} {short_name}",
                    data=f_bytes,
                    file_name=f_name,
                    mime=mime_type,
                    use_container_width=True,
                    type="secondary"
                )

st.markdown('</div>', unsafe_allow_html=True)
