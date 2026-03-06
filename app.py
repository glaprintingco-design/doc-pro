import streamlit as st
from supabase import create_client, Client
import main
import os
import zipfile
from io import BytesIO

# --- 1. CONFIGURACIÓN Y CONEXIÓN ---
st.set_page_config(page_title="Fire Form Pro", layout="wide", page_icon="🔥")

# Inyección de llaves NYC para main.py
main.API_KEY_NYC = st.secrets.get("NYC_API_KEY", "")
main.APP_TOKEN_SOCRATA = st.secrets.get("SOCRATA_TOKEN", "")

# Credenciales Supabase
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")

if "supabase" not in st.session_state:
    try:
        st.session_state.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"❌ Connection Error: {e}")
        st.stop()

supabase = st.session_state.supabase

# Inicialización de estados
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

# --- 2. FUNCIONES DE APOYO ---
def logout():
    try:
        supabase.auth.sign_out()
    except:
        pass
    st.session_state.user = None
    st.session_state.device_list = []
    st.rerun()

def fetch_user_profile(user_id):
    try:
        response = supabase.table("profiles").select("*").eq("id", user_id).execute()
        return response.data[0] if response.data else {}
    except Exception as e:
        st.error(f"Error loading profile: {e}")
        return {}

def login_ui():
    with st.sidebar:
        st.header("🔑 User Access")
        choice = st.radio("Action", ["Login", "Sign Up"], key="auth_choice")
        email = st.text_input("Email Address", key="auth_email")
        password = st.text_input("Password", type="password", key="auth_pass")
        
        if choice == "Login":
            if st.button("Sign In", use_container_width=True):
                with st.spinner("Authenticating..."):
                    try:
                        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                        if res.user:
                            st.session_state.user = res.user
                            st.rerun()
                    except Exception as e:
                        st.error(f"❌ Login Error: {e}")
        else:
            if st.button("Create Account", use_container_width=True):
                with st.spinner("Creating..."):
                    try:
                        res = supabase.auth.sign_up({"email": email, "password": password})
                        if res.user:
                            supabase.table("profiles").insert({"id": res.user.id, "email": email}).execute()
                            st.success("✅ Account created! Please check your email.")
                    except Exception as e:
                        st.error(f"❌ Sign Up Error: {e}")

# --- 3. CONTROL DE ACCESO ---
if not st.session_state.user:
    login_ui()
    st.title("Fire Form Pro")
    if os.path.exists("logo.png"):
        st.image("logo.png", width=200)
    st.warning("Please log in from the sidebar to access the generator.")
    st.stop()

# --- 4. APP PRINCIPAL ---
profile = fetch_user_profile(st.session_state.user.id)
st.sidebar.success(f"Logged in: {st.session_state.user.email}")
if st.sidebar.button("Logout", use_container_width=True):
    logout()

tabs = st.tabs(["🚀 Project Builder", "👤 Professional Profile"])

# --- TAB: PROFESSIONAL PROFILE (TODOS LOS CAMPOS) ---
with tabs[1]:
    st.header("My Professional Profile")
    st.info("Data saved here is stored permanently in the cloud and fills your FDNY forms.")
    
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

    with st.expander("⚡ Electrical Contractor Information"):
        col1, col2 = st.columns(2)
        with col1:
            e_name = st.text_input("Electrician Co. Name", value=profile.get("elec_name", ""))
            e_first = st.text_input("Elec. First Name", value=profile.get("elec_first_name", ""))
        with col2:
            e_license = st.text_input("Elec. License No", value=profile.get("elec_license", ""))
            e_exp = st.text_input("Elec. Expiration", value=profile.get("elec_expiration", ""))

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

    if st.button("💾 Save Profile Permanently", use_container_width=True):
        full_update = {
            "id": st.session_state.user.id,
            "updated_at": "now()",
            "company_name": c_name, "company_address": c_addr, "company_city": c_city, "company_zip": c_zip,
            "company_reg_no": c_reg, "company_cof_s97": c_cof, "company_expiration": c_exp, "company_phone": c_phone,
            "arch_name": a_name, "arch_first_name": a_first, "arch_last_name": a_last, "arch_license": a_license, 
            "arch_email": a_email, "arch_role": a_role, "elec_name": e_name, "elec_first_name": e_first,
            "elec_license": e_license, "elec_expiration": e_exp, "tech_manufacturer": t_man, 
            "tech_approval": t_appr, "tech_wire_type": t_wire, "cs_name": cs_name, "cs_code": cs_code
        }
        try:
            supabase.table("profiles").upsert(full_update).execute()
            st.success("✅ Profile Saved!")
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

# --- TAB: PROJECT BUILDER ---
with tabs[0]:
    col1, col2 = st.columns([1, 1.2], gap="large")

    with col1:
        st.subheader("1. Project Information")
        bin_number = st.text_input("Enter Property BIN", placeholder="e.g. 1012345")
        job_desc = st.text_area("Job Description", value="Installation of Fire Alarm System.")

        st.divider()
        st.subheader("2. A-433 Add Devices (Optional)")
        floor = st.selectbox("Floor Location", main.FULL_FLOOR_LIST)
        category = st.selectbox("Category", list(main.MASTER_DEVICE_LIST.keys()))
        device = st.selectbox("Device Type", main.MASTER_DEVICE_LIST.get(category, []))
        qty = st.number_input("Quantity", min_value=1, value=1)

        if st.button("➕ Add to List", use_container_width=True):
            st.session_state.device_list.append({"device": device, "floor": floor, "qty": qty})
            st.success("Added!")
            st.rerun()

    with col2:
        st.subheader("📋 Device List & Generation")
        
        # Tabla editable (Corregida para que no desaparezca)
        if st.session_state.device_list:
            edited_list = st.data_editor(
                st.session_state.device_list,
                num_rows="dynamic",
                use_container_width=True,
                key="editor_main",
                column_config={
                    "qty": st.column_config.NumberColumn("Qty", min_value=1),
                    "device": st.column_config.TextColumn("Device", disabled=True),
                    "floor": st.column_config.TextColumn("Floor", disabled=True)
                }
            )
            if edited_list != st.session_state.device_list:
                st.session_state.device_list = edited_list
                st.rerun()
            
            if st.button("🗑️ Clear List", key="btn_clear"):
                st.session_state.device_list = []
                st.rerun()
        else:
            st.info("No devices added.")

        st.divider()
        st.subheader("📝 Selection & Generation")
        c1, c2 = st.columns(2)
        with c1:
            g_tm1 = st.checkbox("TM-1 Application", value=True, key="k_tm1")
            g_a433 = st.checkbox("A-433 Device List", value=True, key="k_a433")
        with c2:
            g_b45 = st.checkbox("B-45 Request", value=True, key="k_b45")
            g_report = st.checkbox("Audit Report", value=True, key="k_rep")

        if st.button("🔥 GENERATE DOCUMENTS", type="primary", use_container_width=True):
            if not bin_number:
                st.error("BIN number required.")
            elif not (g_tm1 or g_a433 or g_b45 or g_report):
                st.warning("Select at least one form.")
            else:
                with st.spinner("Processing documents..."):
                    try:
                        # MAPEADO SUPABASE -> MAIN.PY (Solución "None")
                        main.COMPANY.update({
                            "Company Name": profile.get("company_name", ""), "Address": profile.get("company_address", ""),
                            "City": profile.get("company_city", ""), "Zip": profile.get("company_zip", ""),
                            "Phone": profile.get("company_phone", ""), "Email": profile.get("email", ""),
                            "Reg No": profile.get("company_reg_no", ""), "COF S97": profile.get("company_cof_s97", ""),
                            "First Name": profile.get("company_first_name", profile.get("arch_first_name", "")),
                            "Last Name": profile.get("company_last_name", profile.get("arch_last_name", ""))
                        })
                        main.ARCHITECT.update({
                            "Company Name": profile.get("arch_name", ""), "First Name": profile.get("arch_first_name", ""),
                            "Last Name": profile.get("arch_last_name", ""), "License No": profile.get("arch_license", ""),
                            "Role": profile.get("arch_role", "PE"), "Phone": profile.get("arch_phone", ""),
                            "Email": profile.get("arch_email", ""), "Address": profile.get("arch_address", "")
                        })

                        info = main.obtener_datos_completos(bin_number)
                        if info:
                            full_data = {**info, "job_desc": job_desc, "devices": st.session_state.device_list}
                            files = []
                            if g_tm1: 
                                main.generar_tm1(full_data, "tm-1-application-for-plan-examination-doc-review.pdf", f"TM1_{bin_number}.pdf")
                                files.append(f"TM1_{bin_number}.pdf")
                            if g_a433: 
                                main.generar_a433(full_data, "application-a-433-c.pdf", f"A433_{bin_number}.pdf")
                                files.append(f"A433_{bin_number}.pdf")
                            if g_b45: 
                                main.generar_b45(full_data, "b45-inspection-request.pdf", f"B45_{bin_number}.pdf")
                                files.append(f"B45_{bin_number}.pdf")
                            if g_report: 
                                main.generar_reporte_auditoria(full_data, f"REPORT_{bin_number}.txt")
                                files.append(f"REPORT_{bin_number}.txt")

                            zip_buf = BytesIO()
                            with zipfile.ZipFile(zip_buf, "a", zipfile.ZIP_DEFLATED) as z:
                                for f in files:
                                    if os.path.exists(f):
                                        z.write(f)
                                        os.remove(f)

                            st.success("✅ Done!")
                            st.download_button("📥 Download ZIP", zip_buf.getvalue(), f"FDNY_{bin_number}.zip", "application/zip")
                    except Exception as e:
                        st.error(f"Error: {e}")
