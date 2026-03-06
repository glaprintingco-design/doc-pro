import streamlit as st
from supabase import create_client, Client
import main
import os
import zipfile
from io import BytesIO

# --- 1. CONFIGURACIÓN Y CONEXIÓN ---
st.set_page_config(page_title="Fire Form Pro", layout="wide", page_icon="🔥")

# Credenciales desde Secrets
main.API_KEY_NYC = st.secrets.get("NYC_API_KEY", "")
main.APP_TOKEN_SOCRATA = st.secrets.get("SOCRATA_TOKEN", "")
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")

if "supabase" not in st.session_state:
    try:
        st.session_state.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"❌ Connection Error: {e}")
        st.stop()

supabase = st.session_state.supabase

# --- 2. GESTIÓN DE SESIÓN ---
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

# --- 3. FUNCIONES DE APOYO (REFACTORIZADAS) ---
def sync_data_to_main(profile_data):
    """Sincroniza los datos del perfil con las variables globales de main.py (EVITA DUPLICADOS)"""
    main.COMPANY.update({
        "Company Name": profile_data.get("company_name", ""),
        "Address": profile_data.get("company_address", ""),
        "City": profile_data.get("company_city", ""),
        "State": profile_data.get("company_state", "NY"),
        "Zip": profile_data.get("company_zip", ""),
        "Phone": profile_data.get("company_phone", ""),
        "Email": profile_data.get("company_email", ""),
        "First Name": profile_data.get("company_first_name", ""),
        "Last Name": profile_data.get("company_last_name", ""),
        "Reg No": profile_data.get("company_reg_no", ""),
        "COF S97": profile_data.get("company_cof_s97", ""),
        "Expiration": profile_data.get("company_expiration", "")
    })
    main.ARCHITECT.update({
        "Company Name": profile_data.get("arch_name", ""),
        "License No": profile_data.get("arch_license", ""),
        "Role": profile_data.get("arch_role", "PE"),
        "Address": profile_data.get("arch_address", ""),
        "City": profile_data.get("arch_city", ""),
        "State": profile_data.get("arch_state", ""),
        "Zip": profile_data.get("arch_zip", ""),
        "Phone": profile_data.get("arch_phone", ""),
        "Email": profile_data.get("arch_email", ""),
        "First Name": profile_data.get("arch_first_name", ""),
        "Last Name": profile_data.get("arch_last_name", "")
    })
    main.ELECTRICIAN.update({
        "Company Name": profile_data.get("elec_name", ""),
        "License No": profile_data.get("elec_license", ""),
        "Address": profile_data.get("elec_address", ""),
        "City": profile_data.get("elec_city", ""),
        "State": profile_data.get("elec_state", ""),
        "Zip": profile_data.get("elec_zip", ""),
        "Phone": profile_data.get("elec_phone", ""),
        "Email": profile_data.get("elec_email", ""),
        "First Name": profile_data.get("elec_first_name", ""),
        "Last Name": profile_data.get("elec_last_name", ""),
        "Expiration": profile_data.get("elec_expiration", "")
    })
    main.TECH_DEFAULTS.update({
        "Manufacturer": profile_data.get("tech_manufacturer", ""),
        "Approval": profile_data.get("tech_approval", ""),
        "WireGauge": profile_data.get("tech_wire_gauge", ""),
        "WireType": profile_data.get("tech_wire_type", "")
    })
    main.CENTRAL_STATION.update({
        "Company Name": profile_data.get("cs_name", ""),
        "CS Code": profile_data.get("cs_code", ""),
        "Address": profile_data.get("cs_address", ""),
        "City": profile_data.get("cs_city", ""),
        "State": profile_data.get("cs_state", ""),
        "Zip": profile_data.get("cs_zip", ""),
        "Phone": profile_data.get("cs_phone", "")
    })

def logout():
    supabase.auth.sign_out()
    st.session_state.user = None
    st.session_state.device_list = []
    st.rerun()

def fetch_user_profile(user_id):
    try:
        response = supabase.table("profiles").select("*").eq("id", user_id).execute()
        return response.data[0] if response.data else {}
    except:
        return {}

# --- 4. UI DE AUTENTICACIÓN ---
def login_ui():
    with st.sidebar:
        st.header("🔑 User Access")
        choice = st.radio("Action", ["Login", "Sign Up"])
        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")
        
        if choice == "Login":
            if st.button("Sign In", use_container_width=True):
                try:
                    res = supabase.auth.sign_in_with_password({"email": email.strip(), "password": password})
                    if res.user:
                        st.session_state.user = res.user
                        st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            if st.button("Create Account", use_container_width=True):
                try:
                    res = supabase.auth.sign_up({"email": email.strip(), "password": password})
                    if res.user:
                        supabase.table("profiles").insert({"id": res.user.id, "email": email}).execute()
                        st.success("Check your email for confirmation!")
                except Exception as e:
                    st.error(f"Error: {e}")

if not st.session_state.user:
    login_ui()
    st.title("Fire Form Pro")
    st.warning("Please log in to continue.")
    st.stop()

# --- 5. APP PRINCIPAL ---
profile = fetch_user_profile(st.session_state.user.id)
st.sidebar.write(f"Logged: {st.session_state.user.email}")
if st.sidebar.button("Logout"): logout()

tabs = st.tabs(["🚀 Project Builder", "👤 Professional Profile"])

# --- TAB PROFIL (TAB 1) ---
with tabs[1]:
    st.header("My Professional Profile")
    with st.expander("🏢 Fire Alarm Company Data", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            c_name = st.text_input("Company Name", profile.get("company_name", ""), key="p_cname")
            c_addr = st.text_input("Address", profile.get("company_address", ""), key="p_caddr")
            c_city = st.text_input("City", profile.get("company_city", ""), key="p_ccity")
            c_state = st.text_input("State", profile.get("company_state", "NY"), key="p_cstate")
            c_zip = st.text_input("Zip Code", profile.get("company_zip", ""), key="p_czip")
            c_phone = st.text_input("Phone", profile.get("company_phone", ""), key="p_cphone")
        with col2:
            c_email = st.text_input("Company Email (Para TM-1)", profile.get("company_email", ""), key="p_cemail")
            c_first = st.text_input("First Name", profile.get("company_first_name", ""), key="p_cfirst")
            c_last = st.text_input("Last Name", profile.get("company_last_name", ""), key="p_clast")
            c_reg = st.text_input("Reg No", profile.get("company_reg_no", ""), key="p_creg")
            c_cof = st.text_input("COF S97", profile.get("company_cof_s97", ""), key="p_ccof")
            c_exp = st.text_input("Exp. Date", profile.get("company_expiration", ""), key="p_cexp")

    # (Para brevedad, mantén los otros expanders de Arquitecto/Electricista igual pero usa los datos del profile)
    # Aquí unificamos el guardado
    if st.button("💾 Save Profile Permanently", use_container_width=True):
        updated_data = {
            "id": st.session_state.user.id,
            "company_name": c_name, "company_address": c_addr, "company_city": c_city,
            "company_state": c_state, "company_zip": c_zip, "company_phone": c_phone,
            "company_email": c_email, "company_first_name": c_first, "company_last_name": c_last,
            "company_reg_no": c_reg, "company_cof_s97": c_cof, "company_expiration": c_exp
            # Agrega aquí el resto de campos (arch, elec, tech, cs) para que se guarden
        }
        try:
            supabase.table("profiles").upsert(updated_data).execute()
            sync_data_to_main(updated_data)
            st.success("✅ Profile saved and synced!")
        except Exception as e: st.error(f"Error: {e}")

# --- TAB BUILDER (TAB 0) ---
with tabs[0]:
    st.title("Fire Form Pro Builder")
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("1. Project Information")
        bin_num = st.text_input("Enter Property BIN", placeholder="e.g. 1012345")
        job_desc = st.text_area("Job Description", "Installation of Fire Alarm System.")
        
        st.divider()
        st.subheader("2. Add Devices")
        floor = st.selectbox("Floor Location", main.FULL_FLOOR_LIST)
        category = st.selectbox("Category", list(main.MASTER_DEVICE_LIST.keys()))
        device = st.selectbox("Device Type", main.MASTER_DEVICE_LIST.get(category, []))
        qty = st.number_input("Quantity", min_value=1, value=1)

        if st.button("➕ Add Device"):
            st.session_state.device_list.append({"device": device, "floor": floor, "qty": qty})
            st.rerun()

    with col2:
        st.subheader("📋 Project Device List")
        # MEJORA: La tabla ahora está fuera del IF del botón para que no desaparezca
        if st.session_state.device_list:
            edited = st.data_editor(
                st.session_state.device_list,
                num_rows="dynamic",
                use_container_width=True,
                key="device_editor"
            )
            if edited != st.session_state.device_list:
                st.session_state.device_list = edited
                st.rerun()
            
            if st.button("🗑️ Clear List"):
                st.session_state.device_list = []
                st.rerun()
        else:
            st.info("List is empty.")

    st.divider()
    st.subheader("📝 Select Forms")
    c_tm, c_a433, c_b45, c_rep = st.columns(4)
    with c_tm: gen_tm1 = st.checkbox("TM-1", True)
    with c_a433: gen_a433 = st.checkbox("A-433", True)
    with c_b45: gen_b45 = st.checkbox("B-45", True)
    with c_rep: gen_rep = st.checkbox("Audit", True)

    if st.button("🔥 GENERATE DOCUMENTS", type="primary", use_container_width=True):
        if not bin_num:
            st.error("BIN number is required.")
        else:
            with st.spinner("Processing..."):
                # 1. Sincronizamos el perfil actual con main.py antes de generar
                sync_data_to_main(profile)
                
                # 2. Obtenemos datos del BIN
                info = main.obtener_datos_completos(bin_num)
                if info:
                    # 3. FIX EMAIL: Inyectamos explícitamente el email del perfil en full_data
                    # También pasamos 'profile' completo para que main.py tenga acceso a todo
                    full_data = {
                        **info, 
                        **profile, 
                        "job_desc": job_desc, 
                        "devices": st.session_state.device_list,
                        "Email": profile.get("company_email", ""), # Key para main.py
                        "Filing Representative Email": profile.get("company_email", "") # Key común PDF
                    }
                    
                    files = []
                    if gen_tm1:
                        out = f"TM1_{bin_num}.pdf"
                        main.generar_tm1(full_data, "tm-1-application-for-plan-examination-doc-review.pdf", out)
                        files.append(out)
                    if gen_a433:
                        out = f"A433_{bin_num}.pdf"
                        main.generar_a433(full_data, "application-a-433-c.pdf", out)
                        files.append(out)
                    # ... genera los otros forms igual ...

                    # Crear ZIP
                    zip_buf = BytesIO()
                    with zipfile.ZipFile(zip_buf, "a") as zf:
                        for f in files:
                            if os.path.exists(f):
                                zf.write(f)
                                os.remove(f)

                    st.success("Ready!")
                    st.download_button("📥 Download ZIP", zip_buf.getvalue(), f"Forms_{bin_num}.zip")
