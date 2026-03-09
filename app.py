import streamlit as st
from supabase import create_client, Client
import main
import os
import zipfile
from io import BytesIO

# --- CONFIGURACIÓN Y CONEXIÓN ---
st.set_page_config(
    page_title="Fire Form Pro", 
    layout="wide", 
    page_icon="🔥",
    initial_sidebar_state="collapsed"  # Sidebar colapsado por defecto
)

# Ocultar elementos del menú de Streamlit excepto theme
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
/* Mostrar solo el botón de theme */
[data-testid="stToolbar"] {
    display: none;
}
button[kind="header"] {
    display: none;
}
/* Mejorar la nitidez de las imágenes */
img {
    image-rendering: -webkit-optimize-contrast;
    image-rendering: crisp-edges;
}
/* Reducir padding superior de la página */
.block-container {
    padding-top: 2rem;
    padding-bottom: 0rem;
}
/* Reducir espacio en tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 2rem;
}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

main.API_KEY_NYC = st.secrets.get("NYC_API_KEY", "")
main.APP_TOKEN_SOCRATA = st.secrets.get("SOCRATA_TOKEN", "")

SUPABASE_URL = st.secrets.get("SUPABASE_URL", "https://uhhiqkymipbcepqzwtvg.supabase.co")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "sb_publishable_mvqOWXc5s4b3_IMe4gGexw_sU3B2DRL")

# --- INICIALIZACIÓN SUPABASE ---
if "supabase" not in st.session_state:
    try:
        st.session_state.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"❌ Failed to connect to Supabase: {e}")
        st.stop()

supabase = st.session_state.supabase

# --- RECUPERAR SESIÓN EXISTENTE ---
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


# --- FUNCIONES DE APOYO ---
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
        st.error(f"Error loading profile: {e}")
        return {}


def sync_profile_to_main(profile):
    """Sincroniza el perfil de Supabase con las variables globales de main.py."""
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


# --- UI DE AUTENTICACIÓN MEJORADA (CUANDO NO ESTÁ LOGUEADO) ---
def login_ui_centered():
    st.markdown("""
        <style>
        .login-wrapper {
            max-width: 450px;
            margin: 4rem auto;
            padding: 2.5rem;
            background-color: rgba(255, 255, 255, 0.03);
            border-radius: 12px;
            border: 1px solid rgba(211, 84, 0, 0.3);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            text-align: center;
        }
        .login-subtitle {
            color: gray;
            font-size: 14px;
            margin-bottom: 2rem;
            margin-top: -10px;
        }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div class='login-wrapper'>", unsafe_allow_html=True)
        
        # Logo en el login
        if os.path.exists("logo.png"):
            st.image("logo.png", use_column_width=True)
        
        st.markdown("<p class='login-subtitle'>Automated form generation for the NYC Fire Alarm Industry</p>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])
        
        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            email = st.text_input("Email Address", key="login_email", placeholder="user@example.com")
            password = st.text_input("Password", type="password", key="login_password", placeholder="••••••••")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Sign In", use_container_width=True, type="primary"):
                if not email or not password:
                    st.error("Please enter both email and password")
                    return
                with st.spinner("Authenticating..."):
                    try:
                        response = supabase.auth.sign_in_with_password({
                            "email": email.strip(),
                            "password": password
                        })
                        if response.user:
                            st.session_state.user = response.user
                            st.success(f"✅ Welcome back!")
                            st.rerun()
                        else:
                            st.error("❌ Login failed: No user returned")
                    except Exception as e:
                        error_msg = str(e)
                        st.error(f"❌ Login Error: {error_msg}")
                        if "Invalid login credentials" in error_msg:
                            st.warning("⚠️ Invalid email or password.")
                        elif "Email not confirmed" in error_msg:
                            st.warning("⚠️ Please confirm your email first.")
                        elif "rate limit" in error_msg.lower():
                            st.warning("⚠️ Too many attempts. Please wait.")
        
        with tab2:
            st.markdown("<br>", unsafe_allow_html=True)
            email = st.text_input("Email Address", key="signup_email", placeholder="user@example.com")
            password = st.text_input("Password", type="password", key="signup_password", placeholder="••••••••")
            password_confirm = st.text_input("Confirm Password", type="password", key="signup_password_confirm", placeholder="••••••••")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Create Account", use_container_width=True, type="primary"):
                if not email or not password:
                    st.error("Please enter both email and password")
                    return
                if password != password_confirm:
                    st.error("Passwords do not match")
                    return
                if len(password) < 6:
                    st.error("Password must be at least 6 characters")
                    return
                with st.spinner("Creating account..."):
                    try:
                        response = supabase.auth.sign_up({
                            "email": email.strip(),
                            "password": password
                        })
                        if response.user:
                            st.success("✅ Account created successfully!")
                            st.info("📧 Please check your email to confirm your account.")
                            try:
                                supabase.table("profiles").insert({
                                    "id": response.user.id,
                                    "email": email
                                }).execute()
                            except Exception as profile_error:
                                st.warning(f"Profile creation note: {profile_error}")
                        else:
                            st.error("Sign up completed but no user data returned")
                    except Exception as e:
                        error_msg = str(e)
                        st.error(f"❌ Sign Up Error: {error_msg}")
                        if "already registered" in error_msg.lower():
                            st.warning("⚠️ Email already registered. Use the Login tab.")
                        elif "valid email" in error_msg.lower():
                            st.warning("⚠️ Please enter a valid email address.")
                            
        st.markdown("</div>", unsafe_allow_html=True)


# --- CONTROL DE ACCESO ---
if not st.session_state.user:
    login_ui_centered()
    st.stop()


# ============================================================
# CABECERA PRINCIPAL CON FONDO DE COLOR (DISEÑO PRO)
# ============================================================
header_style = """
<style>
    /* Contenedor principal del Header */
    .fireform-header {
        background-color: #D35400; /* Naranja quemado profesional */
        color: white;              /* Todo el texto dentro será blanco */
        padding: 1.5rem 2rem;       /* Espaciado interno generoso */
        margin-top: -3rem;         /* Sube el header para que pegue arriba */
        margin-bottom: 1.5rem;      /* Espacio debajo del header */
        width: 100%;               /* Ancho completo */
        border-radius: 8px;        /* Bordes suavemente redondeados */
        position: relative;        /* Necesario para la alineación interna */
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); /* Pequeña sombra elegante */
    }

    /* Estilo para el Eslogan (pegado debajo del logo) */
    .fireform-slogan {
        font-size: 14px;
        opacity: 0.9;              
        margin-top: 0.5rem;       
    }

    /* Estilo para la información del usuario */
    .user-info {
        text-align: right;         
        margin-bottom: 0.5rem;     
    }
</style>
"""
st.markdown(header_style, unsafe_allow_html=True)

st.markdown("<div class='fireform-header'>", unsafe_allow_html=True)

col_h_izq, col_h_der = st.columns([3, 1])

with col_h_izq:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=220)
    st.markdown("<p class='fireform-slogan'>Automated form generation for the NYC Fire Alarm Industry</p>", unsafe_allow_html=True)

with col_h_der:
    st.markdown(f"<p class='user-info'>👤 <b>{st.session_state.user.email}</b></p>", unsafe_allow_html=True)
    if st.button("🚪 Logout", use_container_width=True, type="secondary"):
        logout()

st.markdown("</div> ", unsafe_allow_html=True)


# --- SIDEBAR (INFO ADICIONAL) ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_column_width=True)
    
    st.markdown("---")
    st.markdown(f"**👤 Logged in as:**")
    st.info(st.session_state.user.email)
    
    st.markdown("---")
    st.caption("Fire Form Pro v1.1")
    st.caption("© 2026 - NYC Fire Alarm Industry")

# --- APP PRINCIPAL ---
profile = fetch_user_profile(st.session_state.user.id)

tabs = st.tabs(["🏗️ Project Builder", "👤 Profile Information"])

# ============================================================
# TAB 1: PROFESSIONAL PROFILE
# ============================================================
with tabs[1]:
    st.header("Profile Information")
    st.info("💾 Data saved here is stored permanently in the cloud and fills your FDNY forms.")

    with st.expander("🏢 FA Company / Expeditor Information", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            c_name  = st.text_input("Company Name",  value=profile.get("company_name", ""),       key="c_name")
            c_addr  = st.text_input("Address",        value=profile.get("company_address", ""),    key="c_addr")
            c_city  = st.text_input("City",           value=profile.get("company_city", ""),       key="c_city")
            c_state = st.text_input("State",          value=profile.get("company_state", ""),      key="c_state")
            c_zip   = st.text_input("Zip Code",       value=profile.get("company_zip", ""),        key="c_zip")
            c_phone = st.text_input("Phone",          value=profile.get("company_phone", ""),      key="c_phone")
        with col2:
            c_email = st.text_input("Email",          value=profile.get("company_email", ""),      key="c_email")
            c_first = st.text_input("First Name",     value=profile.get("company_first_name", ""), key="c_first")
            c_last  = st.text_input("Last Name",      value=profile.get("company_last_name", ""),  key="c_last")
            c_reg   = st.text_input("Reg No",         value=profile.get("company_reg_no", ""),     key="c_reg")
            c_cof   = st.text_input("COF S97",        value=profile.get("company_cof_s97", ""),    key="c_cof")
            c_exp   = st.text_input("Exp. Date",      value=profile.get("company_expiration", ""), key="c_exp")

    with st.expander("📐 Architect Information"):
        col1, col2 = st.columns(2)
        with col1:
            a_name    = st.text_input("Architect Co. Name", value=profile.get("arch_name", ""),        key="a_name")
            a_addr    = st.text_input("Address",            value=profile.get("arch_address", ""),     key="a_addr")
            a_city    = st.text_input("City",               value=profile.get("arch_city", ""),        key="a_city")
            a_state   = st.text_input("State",              value=profile.get("arch_state", ""),       key="a_state")
            a_zip     = st.text_input("Zip Code",           value=profile.get("arch_zip", ""),         key="a_zip")
            a_phone   = st.text_input("Phone",              value=profile.get("arch_phone", ""),       key="a_phone")
        with col2:
            a_email   = st.text_input("Email",              value=profile.get("arch_email", ""),       key="a_email")
            a_first   = st.text_input("First Name",         value=profile.get("arch_first_name", ""),  key="a_first")
            a_last    = st.text_input("Last Name",          value=profile.get("arch_last_name", ""),   key="a_last")
            a_license = st.text_input("License No",         value=profile.get("arch_license", ""),     key="a_license")
            a_role    = st.selectbox("Role", ["PE", "RA"],
                                     index=0 if profile.get("arch_role") == "PE" else 1, key="a_role")

    with st.expander("⚡ Electrical Contractor Information"):
        col1, col2 = st.columns(2)
        with col1:
            e_name    = st.text_input("Electrician Co. Name", value=profile.get("elec_name", ""),        key="e_name")
            e_addr    = st.text_input("Address",              value=profile.get("elec_address", ""),     key="e_addr")
            e_city    = st.text_input("City",                 value=profile.get("elec_city", ""),        key="e_city")
            e_state   = st.text_input("State",                value=profile.get("elec_state", ""),       key="e_state")
            e_zip     = st.text_input("Zip Code",             value=profile.get("elec_zip", ""),         key="e_zip")
            e_phone   = st.text_input("Phone",                value=profile.get("elec_phone", ""),       key="e_phone")
        with col2:
            e_email   = st.text_input("Email",                value=profile.get("elec_email", ""),       key="e_email")
            e_first   = st.text_input("First Name",           value=profile.get("elec_first_name", ""),  key="e_first")
            e_last    = st.text_input("Last Name",            value=profile.get("elec_last_name", ""),   key="e_last")
            e_license = st.text_input("License No",           value=profile.get("elec_license", ""),     key="e_license")
            e_exp     = st.text_input("Expiration",           value=profile.get("elec_expiration", ""),  key="e_exp")

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
                st.error(f"Error saving to database: {e}")


# ============================================================
# TAB 0: PROJECT BUILDER (DISEÑO MEJORADO)
# ============================================================
with tabs[0]:
    
    # --- SECCIÓN 1: PROJECT INFORMATION (Ancho completo dividido en 2) ---
    st.subheader("1️⃣ Project Information")
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        bin_number = st.text_input("Enter Property BIN", placeholder="e.g. 1012345")
    with col_info2:
        job_desc = st.text_area("TM-1 Job Description", value="Installation of Fire Alarm System.", height=68)

    st.divider()

    # --- SECCIÓN 2: DISPOSITIVOS (Izquierda: Controles | Derecha: Tabla) ---
    st.markdown("### 2️⃣ Devices <span style='color:gray; font-size:14px;'>(A-433 Optional)</span>", unsafe_allow_html=True)
    col_dev_left, col_dev_right = st.columns([1, 2]) 
    
    with col_dev_left:
        st.markdown("**➕ Add New Device**")
        floor    = st.selectbox("Floor Location", main.FULL_FLOOR_LIST)
        category = st.selectbox("Category", list(main.MASTER_DEVICE_LIST.keys()))
        device   = st.selectbox("Device Type", main.MASTER_DEVICE_LIST.get(category, []))
        qty      = st.number_input("Quantity", min_value=1, value=1)
        
        if st.button("Add to List", use_container_width=True):
            st.session_state.device_list.append({
                "device": device,
                "floor": floor,
                "qty": qty,
            })
            st.success(f"✅ Added: {device} at {floor}")

    with col_dev_right:
        st.markdown("**📋 Project Device List**")
        if st.session_state.device_list:
            edited_list = st.data_editor(
                st.session_state.device_list,
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    "qty": st.column_config.NumberColumn("Quantity", min_value=1, max_value=999, step=1, required=True),
                    "device": st.column_config.TextColumn("Device Type", disabled=True),
                    "floor":  st.column_config.TextColumn("Floor Location", disabled=True),
                },
                key="device_editor",
            )
            if edited_list != st.session_state.device_list:
                st.session_state.device_list = edited_list
                st.rerun()
                
            if st.button("🗑️ Clear Entire List", use_container_width=True, type="secondary"):
                st.session_state.device_list = []
                st.rerun()
        else:
            st.info("💡 No devices added yet. Use the panel on the left to add them.")

    st.divider()

    # --- SECCIÓN 3: GENERACIÓN Y DESCARGA (Centrado) ---
    st.subheader("3️⃣ Document Generation")
    
    # Centramos los checkboxes usando columnas espaciadoras
    col_chk0, col_chk1, col_chk2, col_chk3 = st.columns([1, 2, 2, 1])
    with col_chk1:
        gen_tm1    = st.checkbox("📄 TM-1 Application", value=True, key="chk_gen_tm1")
        gen_a433   = st.checkbox("📋 A-433 Device List", value=True, key="chk_gen_a433")
    with col_chk2:
        gen_b45    = st.checkbox("📄 B-45 Inspection", value=True, key="chk_gen_b45")
        gen_report = st.checkbox("📊 Audit Report", value=True, key="chk_gen_report")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Botón principal y descargas centrados
    col_gen1, col_gen2, col_gen3 = st.columns([1, 2, 1])
    with col_gen2:
        if st.button("🔥 GENERATE DOCUMENTS", type="primary", use_container_width=True):
            if not bin_number:
                st.error("⚠️ Please enter a BIN number.")
            elif not (gen_tm1 or gen_a433 or gen_b45 or gen_report):
                st.warning("⚠️ Please select at least one form to generate.")
            else:
                with st.spinner("🔄 Generating Forms..."):
                    try:
                        sync_profile_to_main(profile)
                        info = main.obtener_datos_completos(bin_number)
                        
                        if info:
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
                        st.error(f"❌ Critical Error: {e}")

        # Bloque de descargas 
        if "generated_data" in st.session_state and st.session_state.generated_data:
            st.markdown("<hr style='margin-top: 1rem; margin-bottom: 1rem;'>", unsafe_allow_html=True)
            datos = st.session_state.generated_data
            
            st.success(f"✅ {len(datos['archivos'])} documents generated successfully!")
            
            # Botón del ZIP
            st.download_button(
                label="📦 Download All Selected Forms (ZIP)",
                data=datos["zip_buffer"],
                file_name=f"FDNY_Forms_{datos['bin']}.zip",
                mime="application/zip",
                use_container_width=True,
                type="primary"
            )

            st.markdown("<p style='text-align: center; color: gray; font-size: 14px; margin-top: 10px;'>Or download individually:</p>", unsafe_allow_html=True)

            # Botones en cuadrícula 2x2
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
