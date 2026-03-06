import streamlit as st
from supabase import create_client, Client
import main
import os
import zipfile
from io import BytesIO

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(
    page_title="Fire Form Pro", 
    layout="wide", 
    page_icon="🔥",
    initial_sidebar_state="expanded"
)

# --- CSS PERSONALIZADO PARA RESPONSIVE DESIGN ---
st.markdown("""
<style>
    /* Estilos generales mejorados */
    .main {
        padding: 1rem;
    }
    
    /* Mejoras para móviles */
    @media (max-width: 768px) {
        .main {
            padding: 0.5rem;
        }
        
        .stButton > button {
            width: 100%;
            margin-bottom: 0.5rem;
        }
        
        .stTextInput > div > div > input,
        .stSelectbox > div > div > select,
        .stTextArea > div > div > textarea {
            font-size: 16px !important; /* Evita zoom en iOS */
        }
        
        /* Tabs más compactos en móvil */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            font-size: 0.9rem;
            padding: 0.5rem;
        }
    }
    
    /* Tablets */
    @media (min-width: 769px) and (max-width: 1024px) {
        .main {
            padding: 1.5rem;
        }
    }
    
    /* Mejoras visuales generales */
    .stExpander {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .warning-box {
        padding: 1rem;
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* Mejorar tabla de dispositivos */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Botones más atractivos */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
</style>
""", unsafe_allow_html=True)

# --- CONFIGURACIÓN DE SECRETS Y CONEXIÓN ---
main.API_KEY_NYC = st.secrets.get("NYC_API_KEY", "")
main.APP_TOKEN_SOCRATA = st.secrets.get("SOCRATA_TOKEN", "")

SUPABASE_URL = st.secrets.get("SUPABASE_URL", "https://uhhiqkymipbcepqzwtvg.supabase.co")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "sb_publishable_mvqOWXc5s4b3_IMe4gGexw_sU3B2DRL")

# --- INICIALIZACIÓN DE SUPABASE (UNA SOLA VEZ) ---
if "supabase" not in st.session_state:
    try:
        st.session_state.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"❌ Error conectando a Supabase: {e}")
        st.stop()

supabase = st.session_state.supabase

# --- RECUPERAR SESIÓN EXISTENTE ---
if "user" not in st.session_state:
    st.session_state.user = None
    try:
        session = supabase.auth.get_session()
        if session and session.user:
            st.session_state.user = session.user
    except:
        pass

# --- INICIALIZAR LISTA DE DISPOSITIVOS ---
if "device_list" not in st.session_state:
    st.session_state.device_list = []

# --- FUNCIONES DE APOYO ---
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
        st.error(f"Error cargando perfil: {e}")
        return {}

# --- UI DE AUTENTICACIÓN MEJORADA ---
def login_ui():
    with st.sidebar:
        st.header("🔑 Acceso de Usuario")
        
        choice = st.radio("Acción", ["Iniciar Sesión", "Registrarse"], key="auth_choice")
        email = st.text_input("Correo Electrónico", key="auth_email")
        password = st.text_input("Contraseña", type="password", key="auth_password")
        
        if choice == "Iniciar Sesión":
            if st.button("Entrar", use_container_width=True, key="login_btn"):
                if not email or not password:
                    st.error("Por favor ingresa correo y contraseña")
                    return
                
                with st.spinner("Autenticando..."):
                    try:
                        response = supabase.auth.sign_in_with_password({
                            "email": email.strip(),
                            "password": password
                        })
                        
                        if response.user:
                            st.session_state.user = response.user
                            st.success(f"✅ Bienvenido, {email}!")
                            st.rerun()
                        else:
                            st.error("❌ Error de inicio de sesión")
                            
                    except Exception as e:
                        error_msg = str(e)
                        st.error(f"❌ Error: {error_msg}")
                        
                        if "Invalid login credentials" in error_msg:
                            st.warning("⚠️ Correo o contraseña inválidos")
                        elif "Email not confirmed" in error_msg:
                            st.warning("⚠️ Por favor confirma tu cuenta por correo")
                        elif "rate limit" in error_msg.lower():
                            st.warning("⚠️ Demasiados intentos. Espera un momento")
        
        else:  # Registrarse
            if st.button("Crear Cuenta", use_container_width=True, key="signup_btn"):
                if not email or not password:
                    st.error("Por favor ingresa correo y contraseña")
                    return
                
                if len(password) < 6:
                    st.error("La contraseña debe tener al menos 6 caracteres")
                    return
                
                with st.spinner("Creando cuenta..."):
                    try:
                        response = supabase.auth.sign_up({
                            "email": email.strip(),
                            "password": password
                        })
                        
                        if response.user:
                            st.success("✅ ¡Cuenta creada exitosamente!")
                            st.info("📧 Revisa tu correo para confirmar tu cuenta")
                            
                            try:
                                supabase.table("profiles").insert({
                                    "id": response.user.id,
                                    "email": email
                                }).execute()
                            except Exception as profile_error:
                                st.warning(f"Nota: {profile_error}")
                        else:
                            st.error("Registro completado pero sin datos de usuario")
                            
                    except Exception as e:
                        error_msg = str(e)
                        st.error(f"❌ Error de registro: {error_msg}")
                        
                        if "already registered" in error_msg.lower():
                            st.warning("⚠️ Este correo ya está registrado")

# --- CONTROL DE ACCESO ---
if not st.session_state.user:
    login_ui()
    st.title("🔥 Fire Form Pro")
    if os.path.exists("logo.png"):
        st.image("logo.png", width=200)
    st.warning("Por favor inicia sesión desde la barra lateral para acceder al generador.")
    st.stop()

# --- APP PRINCIPAL ---
profile = fetch_user_profile(st.session_state.user.id)

# Sidebar con información de usuario
with st.sidebar:
    st.success(f"✅ {st.session_state.user.email}")
    if st.button("Cerrar Sesión", use_container_width=True, key="logout_btn"):
        logout()

# Logo y título
col_logo, col_title = st.columns([1, 4])
with col_logo:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=100)
with col_title:
    st.title("Fire Form Pro")
    st.caption("Generación automatizada de formularios FDNY")

# --- TABS PRINCIPALES ---
tabs = st.tabs(["🚀 Constructor de Proyectos", "👤 Perfil Profesional"])

# ==================== TAB 1: PERFIL PROFESIONAL ====================
with tabs[1]:
    st.header("Mi Perfil Profesional")
    st.info("💾 Los datos aquí guardados se almacenan permanentemente y llenan tus formularios FDNY.")
    
    # Fire Alarm Company
    with st.expander("🏢 Datos de la Compañía de Alarmas", expanded=False):
        col1, col2 = st.columns([1, 1])
        with col1:
            c_name = st.text_input("Nombre de la Compañía", value=profile.get("company_name", ""), key="c_name")
            c_addr = st.text_input("Dirección", value=profile.get("company_address", ""), key="c_addr")
            c_city = st.text_input("Ciudad", value=profile.get("company_city", ""), key="c_city")
            c_zip = st.text_input("Código Postal", value=profile.get("company_zip", ""), key="c_zip")
        with col2:
            c_reg = st.text_input("Reg No", value=profile.get("company_reg_no", ""), key="c_reg")
            c_cof = st.text_input("COF S97", value=profile.get("company_cof_s97", ""), key="c_cof")
            c_exp = st.text_input("Fecha de Expiración", value=profile.get("company_expiration", ""), key="c_exp")
            c_phone = st.text_input("Teléfono", value=profile.get("company_phone", ""), key="c_phone")

    # Architect/Applicant
    with st.expander("📐 Información del Arquitecto / Aplicante", expanded=False):
        col1, col2 = st.columns([1, 1])
        with col1:
            a_name = st.text_input("Nombre de la Compañía", value=profile.get("arch_name", ""), key="a_name")
            a_first = st.text_input("Nombre", value=profile.get("arch_first_name", ""), key="a_first")
            a_last = st.text_input("Apellido", value=profile.get("arch_last_name", ""), key="a_last")
        with col2:
            a_license = st.text_input("Número de Licencia", value=profile.get("arch_license", ""), key="a_license")
            a_email = st.text_input("Email", value=profile.get("arch_email", ""), key="a_email")
            a_role = st.selectbox("Rol", ["PE", "RA"], 
                                 index=0 if profile.get("arch_role") == "PE" else 1, key="a_role")

    # Electrical Contractor
    with st.expander("⚡ Información del Contratista Eléctrico", expanded=False):
        col1, col2 = st.columns([1, 1])
        with col1:
            e_name = st.text_input("Nombre de la Compañía", value=profile.get("elec_name", ""), key="e_name")
            e_first = st.text_input("Nombre", value=profile.get("elec_first_name", ""), key="e_first")
        with col2:
            e_license = st.text_input("Número de Licencia", value=profile.get("elec_license", ""), key="e_license")
            e_exp = st.text_input("Fecha de Expiración", value=profile.get("elec_expiration", ""), key="e_exp")

    # Technical Defaults y Central Station
    col1, col2 = st.columns([1, 1])
    with col1:
        with st.expander("🛠️ Configuración Técnica Predeterminada", expanded=False):
            t_man = st.text_input("Fabricante", value=profile.get("tech_manufacturer", ""), key="t_man")
            t_appr = st.text_input("Aprobación BSA/MEA/COA", value=profile.get("tech_approval", ""), key="t_appr")
            t_wire = st.text_input("Tipo de Cable", value=profile.get("tech_wire_type", ""), key="t_wire")
    with col2:
        with st.expander("📡 Estación Central", expanded=False):
            cs_name = st.text_input("Nombre CS", value=profile.get("cs_name", ""), key="cs_name")
            cs_code = st.text_input("Código CS", value=profile.get("cs_code", ""), key="cs_code")

    # Botón de guardado
    st.divider()
    if st.button("💾 Guardar Perfil Completo", type="primary", use_container_width=True, key="save_profile"):
        full_update = {
            "id": st.session_state.user.id,
            "updated_at": "now()",
            "company_name": c_name, "company_address": c_addr, "company_city": c_city, 
            "company_zip": c_zip, "company_reg_no": c_reg, "company_cof_s97": c_cof, 
            "company_expiration": c_exp, "company_phone": c_phone,
            "arch_name": a_name, "arch_first_name": a_first, "arch_last_name": a_last,
            "arch_license": a_license, "arch_email": a_email, "arch_role": a_role,
            "elec_name": e_name, "elec_first_name": e_first, "elec_license": e_license,
            "elec_expiration": e_exp,
            "tech_manufacturer": t_man, "tech_approval": t_appr, "tech_wire_type": t_wire,
            "cs_name": cs_name, "cs_code": cs_code
        }
        
        try:
            supabase.table("profiles").upsert(full_update).execute()
            st.success("✅ ¡Perfil guardado exitosamente!")
            
            # Actualizar datos en main.py
            main.COMPANY.update({"Company Name": c_name, "Reg No": c_reg, "COF S97": c_cof})
            main.ARCHITECT.update({"Company Name": a_name, "License No": a_license, "Role": a_role})
            main.ELECTRICIAN.update({"Company Name": e_name, "License No": e_license})
            main.TECH_DEFAULTS.update({"Manufacturer": t_man, "WireType": t_wire})
            
        except Exception as e:
            st.error(f"❌ Error guardando: {e}")

# ==================== TAB 0: CONSTRUCTOR DE PROYECTOS ====================
with tabs[0]:
    st.header("Constructor de Proyectos")
    
    # Usar contenedor para mejor control en móviles
    with st.container():
        # En móviles, las columnas se apilan automáticamente
        col1, col2 = st.columns([1, 1], gap="medium")
        
        # ===== COLUMNA IZQUIERDA: INPUTS =====
        with col1:
            st.subheader("1️⃣ Información del Proyecto")
            bin_number = st.text_input(
                "BIN de la Propiedad", 
                placeholder="ej. 1012345",
                help="Ingresa el número BIN del edificio",
                key="bin_input"
            )
            job_desc = st.text_area(
                "Descripción del Trabajo (TM-1)", 
                value="Installation of Fire Alarm System.",
                height=100,
                key="job_desc"
            )

            st.divider()
            
            st.subheader("2️⃣ Agregar Dispositivos A-433")
            st.caption("Opcional - Agrega dispositivos a la lista")
            
            floor = st.selectbox("Piso", main.FULL_FLOOR_LIST, key="floor_select")
            category = st.selectbox("Categoría", list(main.MASTER_DEVICE_LIST.keys()), key="cat_select")
            
            devices_in_cat = main.MASTER_DEVICE_LIST.get(category, [])
            device = st.selectbox("Tipo de Dispositivo", devices_in_cat, key="device_select")
            qty = st.number_input("Cantidad", min_value=1, value=1, key="qty_input")

            if st.button("➕ Agregar a la Lista", use_container_width=True, key="add_device"):
                st.session_state.device_list.append({
                    "device": device,
                    "floor": floor,
                    "qty": qty
                })
                st.success(f"✅ Agregado: {device} en {floor}")
                st.rerun()

            st.divider()
            
            st.subheader("3️⃣ Seleccionar Formularios")
            col_a, col_b = st.columns(2)
            with col_a:
                gen_tm1 = st.checkbox("TM-1 Application", value=True, key="chk_tm1")
                gen_a433 = st.checkbox("A-433 Device List", value=True, key="chk_a433")
            with col_b:
                gen_b45 = st.checkbox("B-45 Inspection", value=True, key="chk_b45")
                gen_report = st.checkbox("Audit Report", value=True, key="chk_report")

        # ===== COLUMNA DERECHA: LISTA DE DISPOSITIVOS =====
        with col2:
            st.subheader("📋 Lista de Dispositivos del Proyecto")
            
            if st.session_state.device_list:
                # Usar dataframe en lugar de data_editor para evitar problemas
                import pandas as pd
                df = pd.DataFrame(st.session_state.device_list)
                
                # Mostrar con estilos mejorados
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "device": st.column_config.TextColumn("Dispositivo", width="medium"),
                        "floor": st.column_config.TextColumn("Piso", width="small"),
                        "qty": st.column_config.NumberColumn("Cantidad", width="small"),
                    }
                )
                
                st.caption(f"Total de dispositivos: {len(st.session_state.device_list)}")
                
                # Opciones de edición/borrado
                col_edit1, col_edit2 = st.columns(2)
                with col_edit1:
                    if st.button("✏️ Editar Lista", use_container_width=True, key="edit_list"):
                        st.info("💡 Usa los controles de arriba para agregar más dispositivos")
                
                with col_edit2:
                    if st.button("🗑️ Limpiar Todo", use_container_width=True, key="clear_list"):
                        st.session_state.device_list = []
                        st.rerun()
                
                # Opción para remover el último elemento
                if st.button("↩️ Remover Último", use_container_width=True, key="remove_last"):
                    if st.session_state.device_list:
                        removed = st.session_state.device_list.pop()
                        st.success(f"Removido: {removed['device']}")
                        st.rerun()
            else:
                st.info("📌 No hay dispositivos agregados. Usa el panel izquierdo para agregar.")
                st.caption("Los dispositivos aparecerán aquí cuando los agregues")

    # ===== BOTÓN DE GENERACIÓN (ANCHO COMPLETO) =====
    st.divider()
    if st.button("🔥 GENERAR DOCUMENTOS", type="primary", use_container_width=True, key="generate_btn"):
        if not bin_number:
            st.error("⚠️ Por favor ingresa un número BIN")
        elif not (gen_tm1 or gen_a433 or gen_b45 or gen_report):
            st.warning("⚠️ Selecciona al menos un formulario para generar")
        else:
            with st.spinner("🔄 Sincronizando perfil y generando formularios..."):
                try:
                    # Sincronizar datos del perfil con main.py
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

                    main.TECH_DEFAULTS.update({
                        "Manufacturer": profile.get("tech_manufacturer", ""),
                        "Approval": profile.get("tech_approval", ""),
                        "WireGauge": profile.get("tech_wire_gauge", ""),
                        "WireType": profile.get("tech_wire_type", "")
                    })

                    main.CENTRAL_STATION.update({
                        "Company Name": profile.get("cs_name", ""),
                        "CS Code": profile.get("cs_code", ""),
                        "Address": profile.get("cs_address", ""),
                        "City": profile.get("cs_city", ""),
                        "State": profile.get("cs_state", ""),
                        "Zip": profile.get("cs_zip", ""),
                        "Phone": profile.get("cs_phone", "")
                    })

                    # Obtener datos y generar
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

                        # Crear ZIP
                        zip_buffer = BytesIO()
                        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                            for file_name in generated_files:
                                if os.path.exists(file_name):
                                    zip_file.write(file_name)
                                    os.remove(file_name)

                        st.success(f"✅ ¡{len(generated_files)} documentos generados exitosamente!")
                        st.download_button(
                            label="📥 Descargar Todos los Formularios (ZIP)",
                            data=zip_buffer.getvalue(),
                            file_name=f"FDNY_Forms_{bin_number}.zip",
                            mime="application/zip",
                            use_container_width=True
                        )
                    else:
                        st.error("❌ No se pudieron obtener datos para este BIN")
                except Exception as e:
                    st.error(f"❌ Error crítico: {e}")
                    with st.expander("Ver detalles del error"):
                        st.code(str(e))
