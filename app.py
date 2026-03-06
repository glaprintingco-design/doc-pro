import streamlit as st
from supabase import create_client, Client
import main
import os
import zipfile
from io import BytesIO

# --- 1. DATABASE CONNECTION ---
# Replace these with Streamlit Secrets in production for better security
SUPABASE_URL = "https://uhhiqkymipbcepqzwtvg.supabase.co"
SUPABASE_KEY = "sb_publishable_mvqOWXc5s4b3_IMe4gGexw_sU3B2DRL"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 2. PAGE CONFIGURATION ---
st.set_page_config(page_title="Fire Form Pro", layout="wide", page_icon="🔥")

# --- 3. SESSION STATE INITIALIZATION ---
if "user" not in st.session_state:
    st.session_state.user = None
if "device_list" not in st.session_state:
    st.session_state.device_list = []

# --- 4. AUTHENTICATION LOGIC ---
def login_ui():
    with st.sidebar:
        st.header("🔑 User Access")
        choice = st.radio("Action", ["Login", "Sign Up"])
        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")
        
        if choice == "Login":
            if st.button("Sign In", use_container_width=True):
                try:
                    res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    st.session_state.user = res.user
                    st.success("Welcome back!")
                    st.rerun()
                except Exception as e:
                    st.error("Invalid credentials.")
        else:
            if st.button("Create Account", use_container_width=True):
                try:
                    res = supabase.auth.sign_up({"email": email, "password": password})
                    st.info("Check your email for a confirmation link!")
                except Exception as e:
                    st.error(f"Error: {e}")

def logout():
    st.session_state.user = None
    supabase.auth.sign_out()
    st.rerun()

# --- 5. MAIN APP LOGIC ---
if not st.session_state.user:
    login_ui()
    st.title("Fire Form Pro")
    if os.path.exists("logo.png"):
        st.image("logo.png", width=200)
    st.warning("Please log in from the sidebar to access the generator.")
    st.stop()

# --- 6. LOGGED IN UI ---
st.sidebar.success(f"Logged in as: {st.session_state.user.email}")
if st.sidebar.button("Logout"):
    logout()

# Función para obtener los datos del perfil desde Supabase
def fetch_user_profile(user_id):
    try:
        response = supabase.table("profiles").select("*").eq("id", user_id).execute()
        if response.data:
            return response.data[0]
    except Exception as e:
        st.error(f"Error loading profile: {e}")
    return {}

# Cargar los datos actuales del usuario logueado
profile = fetch_user_profile(st.session_state.user.id)

# --- 1. DATABASE CONNECTION (PERSISTENT) ---
SUPABASE_URL = "https://uhhiqkymipbcepqzwtvg.supabase.co"
SUPABASE_KEY = "sb_publishable_mvqOWXc5s4b3_IMe4gGexw_sU3B2DRL"

# Usamos session_state para que el cliente no se resetee y pierda el token
if "supabase" not in st.session_state:
    st.session_state.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = st.session_state.supabase


# Tabs for organization
tabs = st.tabs(["🚀 Project Builder", "👤 Professional Profile"])

# --- TAB 1: PROFESSIONAL PROFILE ---
with tabs[1]:
    st.header("My Professional Profile")
    st.info("Data saved here is stored permanently in the cloud and fills your FDNY forms.")
    
    # --- 1. SECCIÓN: FIRE ALARM COMPANY ---
    with st.expander("🏢 Fire Alarm Company Data", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            c_name = st.text_input("Company Name", value=profile.get("company_name", ""))
            c_addr = st.text_input("Address", value=profile.get("company_address", ""))
            c_city = st.text_input("City", value=profile.get("company_city", ""))
            c_zip  = st.text_input("Zip Code", value=profile.get("company_zip", ""))
        with col2:
            c_reg  = st.text_input("Reg No", value=profile.get("company_reg_no", ""))
            c_cof  = st.text_input("COF S97", value=profile.get("company_cof_s97", ""))
            c_exp  = st.text_input("Exp. Date", value=profile.get("company_expiration", ""))
            c_phone = st.text_input("Phone", value=profile.get("company_phone", ""))

    # --- 2. SECCIÓN: ARCHITECT / APPLICANT ---
    with st.expander("📐 Architect / Applicant Information"):
        col1, col2 = st.columns(2)
        with col1:
            a_name = st.text_input("Architect Co. Name", value=profile.get("arch_name", ""))
            a_first = st.text_input("Arch. First Name", value=profile.get("arch_first_name", ""))
            a_last = st.text_input("Arch. Last Name", value=profile.get("arch_last_name", ""))
        with col2:
            a_license = st.text_input("License No", value=profile.get("arch_license", ""))
            a_email = st.text_input("Arch. Email", value=profile.get("arch_email", ""))
            a_role = st.selectbox("Role", ["PE", "RA"], index=0 if profile.get("arch_role") == "PE" else 1)

    # --- 3. SECCIÓN: ELECTRICAL CONTRACTOR ---
    with st.expander("⚡ Electrical Contractor Information"):
        col1, col2 = st.columns(2)
        with col1:
            e_name = st.text_input("Electrician Co. Name", value=profile.get("elec_name", ""))
            e_first = st.text_input("Elec. First Name", value=profile.get("elec_first_name", ""))
        with col2:
            e_license = st.text_input("Elec. License No", value=profile.get("elec_license", ""))
            e_exp = st.text_input("Elec. Expiration", value=profile.get("elec_expiration", ""))

    # --- 4. SECCIÓN: TECHNICAL DEFAULTS & CENTRAL STATION ---
    col1, col2 = st.columns(2)
    with col1:
        with st.expander("🛠️ Technical Defaults"):
            t_man = st.text_input("Default Manufacturer", value=profile.get("tech_manufacturer", ""))
            t_appr = st.text_input("BSA/MEA/COA Approval", value=profile.get("tech_approval", ""))
            t_wire = st.text_input("Wire Type", value=profile.get("tech_wire_type", ""))
    with col2:
        with st.expander("📡 Central Station"):
            cs_name = st.text_input("CS Name", value=profile.get("cs_name", ""))
            cs_code = st.text_input("CS Code", value=profile.get("cs_code", ""))

    # --- 5. LÓGICA DE GUARDADO COMPLETA ---
    if st.button("💾 Save Profile Permanently", use_container_width=True):
        full_update = {
            "id": st.session_state.user.id,
            "updated_at": "now()",
            # Company
            "company_name": c_name, "company_address": c_addr, "company_city": c_city, 
            "company_zip": c_zip, "company_reg_no": c_reg, "company_cof_s97": c_cof, 
            "company_expiration": c_exp, "company_phone": c_phone,
            # Architect
            "arch_name": a_name, "arch_first_name": a_first, "arch_last_name": a_last,
            "arch_license": a_license, "arch_email": a_email, "arch_role": a_role,
            # Electrician
            "elec_name": e_name, "elec_first_name": e_first, "elec_license": e_license,
            "elec_expiration": e_exp,
            # Tech
            "tech_manufacturer": t_man, "tech_approval": t_appr, "tech_wire_type": t_wire,
            # CS
            "cs_name": cs_name, "cs_code": cs_code
        }
        
        try:
            supabase.table("profiles").upsert(full_update).execute()
            st.success("✅ Complete Profile saved successfully!")
            
            # Actualizamos main.py para usar estos datos de inmediato en el generador
            main.COMPANY.update({"Company Name": c_name, "Reg No": c_reg, "COF S97": c_cof})
            main.ARCHITECT.update({"Company Name": a_name, "License No": a_license, "Role": a_role})
            main.ELECTRICIAN.update({"Company Name": e_name, "License No": e_license})
            main.TECH_DEFAULTS.update({"Manufacturer": t_man, "WireType": t_wire})
            
        except Exception as e:
            st.error(f"Error saving to database: {e}")

# --- TAB 0: PROJECT BUILDER ---
with tabs[0]:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=150)
    st.title("Fire Form Pro")
    st.markdown("Automated form generation for the NYC Fire Alarm Industry.")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("1. Project Information")
        bin_number = st.text_input("Enter Property BIN", placeholder="e.g. 1012345")
        job_desc = st.text_area("TM-1 Job Description", value="Installation of Fire Alarm System.")

        st.divider()
        
        st.subheader("2. A-433 Add Devices")
        floor = st.selectbox("Floor Location", main.FULL_FLOOR_LIST)
        category = st.selectbox("Category", list(main.MASTER_DEVICE_LIST.keys()))
        
        devices_in_cat = main.MASTER_DEVICE_LIST.get(category, [])
        device = st.selectbox("Device Type", devices_in_cat)
        qty = st.number_input("Quantity", min_value=1, value=1)

        if st.button("➕ Add to List"):
            st.session_state.device_list.append({
                "device": device,
                "floor": floor,
                "qty": qty
            })
            st.success(f"Added: {device} at {floor}")

    with col2:
        st.subheader("📋 Project Device List")
        if st.session_state.device_list:
            st.table(st.session_state.device_list)
            if st.button("🗑️ Clear List"):
                st.session_state.device_list = []
                st.rerun()
        else:
            st.info("No devices added yet.")

        st.divider()

        if st.button("🔥 GENERATE DOCUMENTS", type="primary", use_container_width=True):
            if not bin_number:
                st.error("Please enter a BIN number.")
            elif not st.session_state.device_list:
                st.error("Device list is empty.")
            else:
                with st.spinner("Fetching NYC data and filling PDFs..."):
                    try:
                        info = main.obtener_datos_completos(bin_number)
                        if info:
                            job_specs = {"job_desc": job_desc, "devices": st.session_state.device_list}
                            full_data = {**info, **job_specs}
                            
                            # Generation logic
                            main.generar_tm1(full_data, "tm-1-application-for-plan-examination-doc-review.pdf", f"TM1_{bin_number}.pdf")
                            main.generar_a433(full_data, "application-a-433-c.pdf", f"A433_{bin_number}.pdf")
                            main.generar_b45(full_data, "b45-inspection-request.pdf", f"B45_{bin_number}.pdf")
                            main.generar_reporte_auditoria(full_data, f"REPORT_{bin_number}.txt")

                            zip_buffer = BytesIO()
                            with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                                for file_name in [f"TM1_{bin_number}.pdf", f"A433_{bin_number}.pdf", f"B45_{bin_number}.pdf", f"REPORT_{bin_number}.txt"]:
                                    if os.path.exists(file_name):
                                        zip_file.write(file_name)
                                        os.remove(file_name) 

                            st.success("✅ Documents generated successfully!")
                            st.download_button(
                                label="📥 Download All Forms (ZIP)",
                                data=zip_buffer.getvalue(),
                                file_name=f"FDNY_Forms_{bin_number}.zip",
                                mime="application/zip"
                            )
                        else:
                            st.error("Could not retrieve data for this BIN.")
                    except Exception as e:
                        st.error(f"Critical Error: {e}")
