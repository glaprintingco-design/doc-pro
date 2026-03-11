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

/* Ajustar padding y márgenes para mejor visualización en desktop */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 2rem !important;
    max-width: 1200px !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}

/* Para pantallas muy grandes, limitar aún más el ancho */
@media (min-width: 1400px) {
    .block-container {
        max-width: 1300px !important;
        padding-left: 3rem !important;
        padding-right: 3rem !important;
    }
}

/* Para tablets y pantallas medianas */
@media (max-width: 1024px) {
    .block-container {
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
    }
}

/* Para móviles */
@media (max-width: 768px) {
    .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
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

def get_profile(user_id: str):
    try:
        res = supabase.table("profiles").select("*").eq("id", user_id).execute()
        if res.data and len(res.data) > 0:
            return res.data[0]
        return None
    except Exception as e:
        st.error(f"Error loading profile: {e}")
        return None

def update_profile(user_id: str, data: dict):
    try:
        supabase.table("profiles").update(data).eq("id", user_id).execute()
        st.success("✅ Profile updated!")
    except Exception as e:
        st.error(f"Error updating profile: {e}")

def create_profile(user_id: str, email: str):
    try:
        supabase.table("profiles").insert({
            "id": user_id,
            "email": email,
            "company": "",
            "license": "",
            "principal_name": "",
            "principal_license": ""
        }).execute()
    except Exception:
        pass

def save_project(user_id: str, bin_number: str, address: str, devices: list, job_desc: str):
    try:
        existing = supabase.table("projects")\
            .select("*")\
            .eq("user_id", user_id)\
            .eq("bin_number", bin_number)\
            .execute()
        
        if existing.data and len(existing.data) > 0:
            supabase.table("projects").update({
                "address": address,
                "devices": devices,
                "job_description": job_desc
            }).eq("id", existing.data[0]["id"]).execute()
        else:
            supabase.table("projects").insert({
                "user_id": user_id,
                "bin_number": bin_number,
                "address": address,
                "devices": devices,
                "job_description": job_desc
            }).execute()
    except Exception as e:
        st.warning(f"Could not save project: {e}")

def load_projects(user_id: str):
    try:
        res = supabase.table("projects")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .execute()
        return res.data if res.data else []
    except Exception:
        return []

def delete_project(project_id: int):
    try:
        supabase.table("projects").delete().eq("id", project_id).execute()
        st.success("🗑️ Project deleted")
        st.rerun()
    except Exception as e:
        st.error(f"Error: {e}")

def load_project_data(project_id: int):
    try:
        res = supabase.table("projects").select("*").eq("id", project_id).execute()
        if res.data and len(res.data) > 0:
            p = res.data[0]
            st.session_state.bin_input = p.get("bin_number", "")
            st.session_state.job_desc_input = p.get("job_description", "")
            st.session_state.device_list = p.get("devices", [])
            st.success(f"✅ Loaded: {p.get('address', '')}")
    except Exception as e:
        st.error(f"Error: {e}")

def sync_profile_to_main(profile: dict):
    if profile:
        main.NOMBRE_COMPANIA = profile.get("company", "")
        main.NUMERO_LICENCIA = profile.get("license", "")
        main.NOMBRE_RESPONSABLE = profile.get("principal_name", "")
        main.NUMERO_LICENCIA_RESPONSABLE = profile.get("principal_license", "")

# ============================================================
# HEADER CON DEGRADADO DE FUEGO 🔥
# ============================================================
header_gradient = """
<div style='
    background: linear-gradient(135deg, #FF6B00 0%, #FF4500 50%, #E65100 100%);
    padding: 2rem 3rem;
    border-radius: 0 0 20px 20px;
    box-shadow: 0 6px 20px rgba(255,107,0,0.25);
    margin-bottom: 2rem;
'>
    <div style='display: flex; justify-content: space-between; align-items: center;'>
        <div>
            <h1 style='color: white; margin: 0; font-weight: 700; font-size: 2rem;'>
                🔥 Fire Form Pro
            </h1>
            <p style='color: rgba(255,255,255,0.9); margin: 0.3rem 0 0 0; font-size: 1rem;'>
                Automated FDNY Document Generator
            </p>
        </div>
    </div>
</div>
"""
st.markdown(header_gradient, unsafe_allow_html=True)

# ============================================================
# LÓGICA DE AUTENTICACIÓN
# ============================================================
if not st.session_state.user:
    st.markdown("""
    <div style='max-width: 480px; margin: 3rem auto; background: white; padding: 3rem; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.08);'>
        <h2 style='text-align: center; margin-bottom: 2rem; color: #2D3748;'>Welcome Back! 👋</h2>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔑 Sign In", "🆕 Sign Up"])
    
    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="you@company.com", key="login_email")
            password = st.text_input("Password", type="password", placeholder="••••••••", key="login_pass")
            submit = st.form_submit_button("Sign In", use_container_width=True, type="primary")
            
            if submit:
                if not email or not password:
                    st.error("⚠️ Please fill in all fields")
                else:
                    try:
                        response = supabase.auth.sign_in_with_password({
                            "email": email,
                            "password": password
                        })
                        if response.user:
                            st.session_state.user = response.user
                            st.success("✅ Login successful!")
                            st.rerun()
                        else:
                            st.error("❌ Invalid credentials")
                    except Exception as e:
                        st.error(f"❌ Login failed: {e}")

    with tab2:
        with st.form("signup_form"):
            new_email = st.text_input("Email", placeholder="you@company.com", key="signup_email")
            new_password = st.text_input("Password", type="password", placeholder="••••••••", key="signup_pass")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="••••••••", key="confirm_pass")
            submit_signup = st.form_submit_button("Create Account", use_container_width=True, type="primary")
            
            if submit_signup:
                if not new_email or not new_password or not confirm_password:
                    st.error("⚠️ Please fill in all fields")
                elif new_password != confirm_password:
                    st.error("⚠️ Passwords do not match")
                elif len(new_password) < 6:
                    st.error("⚠️ Password must be at least 6 characters")
                else:
                    try:
                        response = supabase.auth.sign_up({
                            "email": new_email,
                            "password": new_password
                        })
                        if response.user:
                            create_profile(response.user.id, new_email)
                            st.success("✅ Account created! You can now sign in.")
                        else:
                            st.error("❌ Registration failed")
                    except Exception as e:
                        st.error(f"❌ Registration error: {e}")

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ============================================================
# APLICACIÓN PRINCIPAL (USUARIO AUTENTICADO)
# ============================================================
col_header, col_logout = st.columns([5, 1])
with col_logout:
    if st.button("🚪 Logout", key="logout_btn", use_container_width=True):
        logout()

st.markdown("<br>", unsafe_allow_html=True)

profile = get_profile(st.session_state.user.id)
if not profile:
    create_profile(st.session_state.user.id, st.session_state.user.email)
    profile = get_profile(st.session_state.user.id)

# Tabs principales
tab_main, tab_settings, tab_projects = st.tabs(["📋 Form Generator", "⚙️ Settings", "📁 My Projects"])

# TAB: SETTINGS
with tab_settings:
    st.markdown("<h3 style='color: #2D3748;'>👤 Company Profile</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #718096;'>This info will auto-fill in your FDNY forms.</p>", unsafe_allow_html=True)
    
    with st.form("profile_form"):
        company_input = st.text_input("Company Name", value=profile.get("company", ""))
        license_input = st.text_input("Installer License Number", value=profile.get("license", ""))
        principal_name_input = st.text_input("Principal Fire Alarm Contractor Name", value=profile.get("principal_name", ""))
        principal_license_input = st.text_input("Principal License Number", value=profile.get("principal_license", ""))
        
        submitted = st.form_submit_button("💾 Save Profile", type="primary", use_container_width=True)
        if submitted:
            update_profile(st.session_state.user.id, {
                "company": company_input,
                "license": license_input,
                "principal_name": principal_name_input,
                "principal_license": principal_license_input
            })

# TAB: PROJECTS
with tab_projects:
    st.markdown("<h3 style='color: #2D3748;'>📂 Saved Projects</h3>", unsafe_allow_html=True)
    projects = load_projects(st.session_state.user.id)
    
    if not projects:
        st.markdown("""
        <div style='background-color: white; border: 1px dashed #CBD5E0; border-radius: 12px; padding: 3rem; text-align: center; color: #A0AEC0; margin-top: 2rem;'>
            <h3 style='color: #A0AEC0; margin-bottom: 0.5rem;'>📁</h3>
            <p style='margin: 0;'>No saved projects yet</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        for p in projects:
            with st.expander(f"🏢 {p.get('address', 'N/A')} — BIN: {p.get('bin_number', 'N/A')}"):
                st.markdown(f"**Job Description:** {p.get('job_description', 'N/A')}")
                st.markdown(f"**Devices:** {len(p.get('devices', []))} items")
                
                col_p1, col_p2, col_p3 = st.columns([2, 2, 1])
                with col_p1:
                    if st.button(f"📥 Load Project", key=f"load_{p['id']}", use_container_width=True, type="secondary"):
                        load_project_data(p['id'])
                        st.rerun()
                with col_p3:
                    if st.button(f"🗑️", key=f"del_{p['id']}", use_container_width=True):
                        delete_project(p['id'])

# TAB: MAIN GENERATOR
with tab_main:
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
