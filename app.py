import streamlit as st
from supabase import create_client, Client
import main
import os
import zipfile
from io import BytesIO

# --- 1. CONFIGURACIÓN Y CONEXIÓN (CONSOLIDADA) ---
st.set_page_config(page_title="Fire Form Pro", layout="wide", page_icon="🔥")

import main
main.API_KEY_NYC = st.secrets.get("NYC_API_KEY", "")
main.APP_TOKEN_SOCRATA = st.secrets.get("SOCRATA_TOKEN", "")

# Uso de Secrets para seguridad (Configura esto en el panel de Streamlit Cloud)
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "https://uhhiqkymipbcepqzwtvg.supabase.co")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "sb_publishable_mvqOWXc5s4b3_IMe4gGexw_sU3B2DRL")

if "supabase" not in st.session_state:
    st.session_state.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = st.session_state.supabase

# FIX 2: INICIALIZACIÓN CON RECUPERACIÓN DE SESIÓN
# ============================================
if "supabase" not in st.session_state:
    try:
        st.session_state.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        st.sidebar.success("✅ Supabase connected")
    except Exception as e:
        st.error(f"❌ Failed to connect to Supabase: {e}")
        st.stop()

supabase = st.session_state.supabase

# ============================================
# FIX 3: RECUPERAR SESIÓN EXISTENTE
# ============================================
if "user" not in st.session_state:
    st.session_state.user = None
    
    # Intentar recuperar sesión activa
    try:
        session = supabase.auth.get_session()
        if session and session.user:
            st.session_state.user = session.user
            st.sidebar.success(f"🔄 Session restored: {session.user.email}")
    except Exception as e:
        # No hay sesión activa, está bien
        pass

if "device_list" not in st.session_state:
    st.session_state.device_list = []

# --- 3. FUNCIONES DE APOYO ---
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

# ============================================
# FIX 4: MEJOR UI DE AUTENTICACIÓN CON DEBUGGING
# ============================================
def login_ui():
    with st.sidebar:
        st.header("🔑 User Access")
        
        choice = st.radio("Action", ["Login", "Sign Up"])
        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")
        
        if choice == "Login":
            if st.button("Sign In", use_container_width=True):
                if not email or not password:
                    st.error("Please enter both email and password")
                    return
                
                with st.spinner("Authenticating..."):
                    try:
                        # Intentar login con mejor manejo de errores
                        response = supabase.auth.sign_in_with_password({
                            "email": email.strip(),
                            "password": password
                        })
                        
                        if response.user:
                            st.session_state.user = response.user
                            st.success(f"✅ Welcome back, {email}!")
                            st.rerun()
                        else:
                            st.error("❌ Login failed: No user returned")
                            
                    except Exception as e:
                        error_msg = str(e)
                        st.error(f"❌ Login Error: {error_msg}")
                        
                        # Mensajes de ayuda específicos
                        if "Invalid login credentials" in error_msg:
                            st.warning("⚠️ Invalid email or password. Please try again.")
                            st.info("💡 If you forgot your password, use the Sign Up tab to reset it.")
                        elif "Email not confirmed" in error_msg:
                            st.warning("⚠️ Please check your email and confirm your account first.")
                        elif "rate limit" in error_msg.lower():
                            st.warning("⚠️ Too many attempts. Please wait a moment and try again.")
                        else:
                            st.info(f"🔍 Debug info: Check your Supabase Authentication settings")
                            with st.expander("Show full error"):
                                st.code(error_msg)
        
        else:  # Sign Up
            if st.button("Create Account", use_container_width=True):
                if not email or not password:
                    st.error("Please enter both email and password")
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
                            st.info("📧 Please check your email to confirm your account before logging in.")
                            
                            # Crear perfil automáticamente
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
                            st.warning("⚠️ This email is already registered. Please use the Login tab.")
                        elif "valid email" in error_msg.lower():
                            st.warning("⚠️ Please enter a valid email address.")
                        else:
                            with st.expander("Show full error"):
                                st.code(error_msg)

# --- 5. CONTROL DE ACCESO ---
if not st.session_state.user:
    login_ui()
    st.title("Fire Form Pro")
    if os.path.exists("logo.png"):
        st.image("logo.png", width=200)
    st.warning("Please log in from the sidebar to access the generator.")
    st.stop()

# --- 6. APP PRINCIPAL (USUARIO LOGUEADO) ---
profile = fetch_user_profile(st.session_state.user.id)
st.sidebar.success(f"Logged in as: {st.session_state.user.email}")

if st.sidebar.button("Logout", use_container_width=True):
    logout()

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
        
        # Section: Add Devices
        st.markdown(
            "<h3>2. A-433 Add Devices <span style='color:gray; font-size:14px;'>Optional</span></h3>",
            unsafe_allow_html=True
        )

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
                    # Usamos data_editor para permitir edición y borrado fila por fila
                    # num_rows="dynamic" permite al usuario borrar filas seleccionándolas
                    edited_list = st.data_editor(
                        st.session_state.device_list,
                        num_rows="dynamic", 
                        use_container_width=True,
                        column_config={
                            "qty": st.column_config.NumberColumn(
                                "Quantity",
                                min_value=1,
                                max_value=999,
                                step=1,
                                required=True,
                            ),
                            "device": st.column_config.TextColumn("Device Type", disabled=True),
                            "floor": st.column_config.TextColumn("Floor Location", disabled=True),
                        },
                        key="device_editor"
                    )

                    # Sincronizamos los cambios: si el usuario editó algo, actualizamos el state
                    if edited_list != st.session_state.device_list:
                        st.session_state.device_list = edited_list
                        st.rerun()

                    # Botón de pánico (solo si realmente quieren limpiar todo)
                    if st.button("🗑️ Clear Entire List", use_container_width=True):
                        st.session_state.device_list = []
                        st.rerun()
                else:
                    st.info("No devices added yet. Use the left panel to add them.")

        st.divider()

        # --- 1. SELECCIÓN DE FORMULARIOS (Colócalo antes del botón) ---
        st.subheader("📝 Select Forms to Generate")
        col_a, col_b = st.columns(2)

        with col_a:
            # Agregamos el parámetro key para evitar el error de ID duplicado
            gen_tm1 = st.checkbox("TM-1 Application", value=True, key="chk_gen_tm1")
            gen_a433 = st.checkbox("A-433 Device List", value=True, key="chk_gen_a433")
        with col_b:
            gen_b45 = st.checkbox("B-45 Inspection Request", value=True, key="chk_gen_b45")
            gen_report = st.checkbox("Audit Report", value=True, key="chk_gen_report")

        st.divider()

        # --- 2. BOTÓN DE GENERACIÓN DINÁMICO ---
        if st.button("🔥 GENERATE DOCUMENTS", type="primary", use_container_width=True):
            if not bin_number:
                st.error("Please enter a BIN number.")
            elif not (gen_tm1 or gen_a433 or gen_b45 or gen_report):
                st.warning("⚠️ Please select at least one form to generate.")
            else:
                with st.spinner("Sincronizando perfil y generando formularios..."):
                    try:
                        # --- MAPEO TOTAL: SUPABASE -> MAIN.PY ---
                        # 1. Fire Alarm Company
                        main.COMPANY.update({
                            "Company Name": profile.get("company_name", ""),
                            "Address": profile.get("company_address", ""),
                            "City": profile.get("company_city", ""),
                            "State": profile.get("company_state", "NY"),
                            "Zip": profile.get("company_zip", ""),
                            "Phone": profile.get("company_phone", ""),
                            "Email": profile.get("company_email", ""),
                            "First Name": profile.get("company_first_name", ""),
                            "Last Name": profile.get("company_last_name", ""),
                            "Reg No": profile.get("company_reg_no", ""),
                            "COF S97": profile.get("company_cof_s97", ""),
                            "Expiration": profile.get("company_expiration", "")
                        })

                        # 2. Architect / Applicant
                        main.ARCHITECT.update({
                            "Company Name": profile.get("arch_name", ""),
                            "Address": profile.get("arch_address", ""),
                            "City": profile.get("arch_city", ""),
                            "State": profile.get("arch_state", ""),
                            "Zip": profile.get("arch_zip", ""),
                            "Phone": profile.get("arch_phone", ""),
                            "Email": profile.get("arch_email", ""),
                            "First Name": profile.get("arch_first_name", ""),
                            "Last Name": profile.get("arch_last_name", ""),
                            "License No": profile.get("arch_license", ""),
                            "Role": profile.get("arch_role", "PE")
                        })

                        # 3. Electrical Contractor
                        main.ELECTRICIAN.update({
                            "Company Name": profile.get("elec_name", ""),
                            "Address": profile.get("elec_address", ""),
                            "City": profile.get("elec_city", ""),
                            "State": profile.get("elec_state", ""),
                            "Zip": profile.get("elec_zip", ""),
                            "Phone": profile.get("elec_phone", ""),
                            "First Name": profile.get("elec_first_name", ""),
                            "Last Name": profile.get("elec_last_name", ""),
                            "License No": profile.get("elec_license", ""),
                            "Expiration": profile.get("elec_expiration", "")
                        })

                        # 4. Technical Defaults
                        main.TECH_DEFAULTS.update({
                            "Manufacturer": profile.get("tech_manufacturer", ""),
                            "Approval": profile.get("tech_approval", ""),
                            "WireGauge": profile.get("tech_wire_gauge", ""),
                            "WireType": profile.get("tech_wire_type", "")
                        })

                        # 5. Central Station
                        main.CENTRAL_STATION.update({
                            "Company Name": profile.get("cs_name", ""),
                            "CS Code": profile.get("cs_code", ""),
                            "Address": profile.get("cs_address", ""),
                            "City": profile.get("cs_city", ""),
                            "State": profile.get("cs_state", ""),
                            "Zip": profile.get("cs_zip", ""),
                            "Phone": profile.get("cs_phone", "")
                        })

                        # --- PROCESO DE GENERACIÓN ---
                        info = main.obtener_datos_completos(bin_number)
                        if info:
                            job_specs = {"job_desc": job_desc, "devices": st.session_state.device_list}
                            full_data = {**info, **job_specs}
                            
                            generated_files = []

                            # Generación condicional basada en checkboxes
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

                            # Empaquetado en ZIP
                            zip_buffer = BytesIO()
                            with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                                for file_name in generated_files:
                                    if os.path.exists(file_name):
                                        zip_file.write(file_name)
                                        os.remove(file_name) # Borrar archivo temporal después de añadir al ZIP

                            st.success(f"✅ {len(generated_files)} documents generated successfully!")
                            st.download_button(
                                label="📥 Download All Selected Forms (ZIP)",
                                data=zip_buffer.getvalue(),
                                file_name=f"FDNY_Forms_{bin_number}.zip",
                                mime="application/zip"
                            )
                        else:
                            st.error("Could not retrieve data for this BIN.")
                    except Exception as e:
                        st.error(f"Critical Error: {e}")
