import streamlit as st
from supabase import create_client, Client
import main
import os
import zipfile
from io import BytesIO

# ── PAGE CONFIGURATION ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="Fire Form Pro", 
    layout="wide", 
    page_icon="🔥", 
    initial_sidebar_state="expanded"
)

# ── SECRETS & CONNECTION ─────────────────────────────────────────────────────
main.API_KEY_NYC       = st.secrets.get("NYC_API_KEY", "")
main.APP_TOKEN_SOCRATA = st.secrets.get("SOCRATA_TOKEN", "")
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "https://uhhiqkymipbcepqzwtvg.supabase.co")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "sb_publishable_mvqOWXc5s4b3_IMe4gGexw_sU3B2DRL")

# ── CUSTOM CSS (PRO SAAS - CLEAN LIGHT THEME) ────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    :root {
        --primary: #E03131; 
        --primary-hover: #C92A2A;
        --bg-main: #F8F9FA;
        --card-bg: #FFFFFF;
        --border: #E9ECEF;
        --text-muted: #868E96;
    }

    html, body, [data-testid="stAppViewContainer"] {
        background-color: var(--bg-main);
        font-family: 'Inter', sans-serif;
    }

    [data-testid="stHeader"], [data-testid="stDecoration"] { display: none; }

    /* Step Headers Styling */
    .step-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 20px;
        margin-top: 10px;
    }
    .step-number {
        background-color: var(--primary);
        color: white;
        border-radius: 8px;
        width: 28px;
        height: 28px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 14px;
        box-shadow: 0 2px 4px rgba(224, 49, 49, 0.2);
    }
    .step-title {
        font-weight: 600;
        font-size: 1.1rem;
        color: #2C2E33;
    }

    /* Primary Button Style */
    div.stButton > button[kind="primary"] {
        background-color: var(--primary);
        border: none;
        padding: 0.6rem 2rem;
        font-weight: 600;
        border-radius: 8px;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: var(--primary-hover);
    }
    
    /* Sidebar User Box */
    .sidebar-user-box {
        padding: 1rem;
        background: #FFFFFF;
        border: 1px solid var(--border);
        border-radius: 12px;
        margin-bottom: 1.5rem;
    }

    /* Form Expanders */
    .streamlit-expanderHeader {
        background-color: white !important;
        border-radius: 8px !important;
        border: 1px solid var(--border) !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# ── SUPABASE INITIALIZATION ──────────────────────────────────────────────────
if "supabase" not in st.session_state:
    try:
        st.session_state.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Failed to connect to Supabase: {e}"); st.stop()

supabase = st.session_state.supabase

# Session Management
if "user" not in st.session_state:
    st.session_state.user = None
    try:
        session = supabase.auth.get_session()
        if session and session.user: st.session_state.user = session.user
    except: pass

if "device_list" not in st.session_state:
    st.session_state.device_list = []

# ── HELPER FUNCTIONS ─────────────────────────────────────────────────────────
def logout():
    try: supabase.auth.sign_out()
    except: pass
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

def sync_profile_to_main(p):
    """Syncs Supabase profile with global variables in main.py. No fields skipped."""
    main.COMPANY.update({
        "Company Name": p.get("company_name", ""), "Address": p.get("company_address", ""),
        "City": p.get("company_city", ""), "State": p.get("company_state", "NY"),
        "Zip": p.get("company_zip", ""), "Phone": p.get("company_phone", ""),
        "Email": p.get("company_email", ""), "First Name": p.get("company_first_name", ""),
        "Last Name": p.get("company_last_name", ""), "Reg No": p.get("company_reg_no", ""),
        "COF S97": p.get("company_cof_s97", ""), "Expiration": p.get("company_expiration", ""),
    })
    main.ARCHITECT.update({
        "Company Name": p.get("arch_name", ""), "Address": p.get("arch_address", ""),
        "City": p.get("arch_city", ""), "State": p.get("arch_state", ""),
        "Zip": p.get("arch_zip", ""), "Phone": p.get("arch_phone", ""),
        "Email": p.get("arch_email", ""), "First Name": p.get("arch_first_name", ""),
        "Last Name": p.get("arch_last_name", ""), "License No": p.get("arch_license", ""),
        "Role": p.get("arch_role", "PE"),
    })
    main.ELECTRICIAN.update({
        "Company Name": p.get("elec_name", ""), "Address": p.get("elec_address", ""),
        "City": p.get("elec_city", ""), "State": p.get("elec_state", ""),
        "Zip": p.get("elec_zip", ""), "Phone": p.get("elec_phone", ""),
        "Email": p.get("elec_email", ""), "First Name": p.get("elec_first_name", ""),
        "Last Name": p.get("elec_last_name", ""), "License No": p.get("elec_license", ""),
        "Expiration": p.get("elec_expiration", ""),
    })
    main.TECH_DEFAULTS.update({
        "Manufacturer": p.get("tech_manufacturer", ""), "Approval": p.get("tech_approval", ""),
        "WireGauge": p.get("tech_wire_gauge", ""), "WireType": p.get("tech_wire_type", ""),
    })
    main.CENTRAL_STATION.update({
        "Company Name": p.get("cs_name", ""), "CS Code": p.get("cs_code", ""),
        "Address": p.get("cs_address", ""), "City": p.get("cs_city", ""),
        "State": p.get("cs_state", ""), "Zip": p.get("cs_zip", ""),
        "Phone": p.get("cs_phone", ""),
    })

# ── AUTHENTICATION UI ────────────────────────────────────────────────────────
if not st.session_state.user:
    with st.sidebar:
        st.title("🔥 Fire Form Pro")
        choice = st.radio("Action", ["Login", "Sign Up"])
        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")

        if st.button("Continue", type="primary", use_container_width=True):
            try:
                if choice == "Login":
                    res = supabase.auth.sign_in_with_password({"email": email.strip(), "password": password})
                else:
                    res = supabase.auth.sign_up({"email": email.strip(), "password": password})
                    if res.user: supabase.table("profiles").insert({"id": res.user.id, "email": email}).execute()
                
                if res.user:
                    st.session_state.user = res.user
                    st.rerun()
            except Exception as e: st.error(f"Authentication Error: {e}")

    st.title("FDNY Automated Form Generator")
    st.info("Please log in using the sidebar to access the dashboard.")
    if os.path.exists("logo.png"): st.image("logo.png", width=250)
    st.stop()

# ── PROFILE LOADING ─────────────────────────────────────────────────────────
profile = fetch_user_profile(st.session_state.user.id)

with st.sidebar:
    st.markdown(f"""
    <div class="sidebar-user-box">
        <small style="color:var(--text-muted)">Signed in as</small><br>
        <strong>{st.session_state.user.email}</strong>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Logout", use_container_width=True): logout()

tabs = st.tabs(["🚀 Project Builder", "👤 Professional Profile"])

# ============================================================
# TAB 0: PROJECT BUILDER
# ============================================================
with tabs[0]:
    col_main, col_list = st.columns([1, 1.2], gap="large")

    with col_main:
        # Step 1: Basic Information
        st.markdown('<div class="step-header"><div class="step-number">1</div><div class="step-title">Project Details</div></div>', unsafe_allow_html=True)
        bin_number = st.text_input("Property BIN", placeholder="e.g. 1012345")
        job_description = st.text_area("TM-1 Job Description", value="Installation of Fire Alarm System.", height=100)

        # Step 2: Add Devices
        st.markdown('<div class="step-header"><div class="step-number">2</div><div class="step-title">Add Devices (A-433)</div></div>', unsafe_allow_html=True)
        c1, c2 = st.columns([2,1])
        with c1: floor = st.selectbox("Floor Level", main.FULL_FLOOR_LIST)
        with c2: qty = st.number_input("Qty", min_value=1, value=1)
        
        category = st.selectbox("Category", list(main.MASTER_DEVICE_LIST.keys()))
        device = st.selectbox("Device Type", main.MASTER_DEVICE_LIST.get(category, []))
        
        if st.button("➕ Add Device", use_container_width=True):
            st.session_state.device_list.append({"device": device, "floor": floor, "qty": qty})
            st.toast(f"Added: {qty}x {device}")

        # Step 3: Select Forms
        st.markdown('<div class="step-header"><div class="step-number">3</div><div class="step-title">Generate Documents</div></div>', unsafe_allow_html=True)
        f1, f2 = st.columns(2)
        with f1:
            gen_tm1 = st.checkbox("TM-1 Application", value=True)
            gen_a433 = st.checkbox("A-433 Device List", value=True)
        with f2:
            gen_b45 = st.checkbox("B-45 Inspection Request", value=True)
            gen_report = st.checkbox("Audit Report", value=True)

        if st.button("🔥 RUN GENERATOR", type="primary", use_container_width=True):
            if not bin_number:
                st.error("Property BIN is required to fetch building data.")
            else:
                with st.spinner("Processing documents..."):
                    try:
                        sync_profile_to_main(profile)
                        info = main.obtener_datos_completos(bin_number)
                        if info:
                            full_data = {**info, "job_desc": job_description, "devices": st.session_state.device_list}
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

                            zip_buffer = BytesIO()
                            with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                                for fn in generated_files:
                                    if os.path.exists(fn): zip_file.write(fn); os.remove(fn)

                            st.success(f"Successfully generated {len(generated_files)} documents.")
                            st.download_button("📥 Download ZIP Package", data=zip_buffer.getvalue(), file_name=f"FDNY_Forms_{bin_number}.zip")
                        else:
                            st.error("BIN not found in NYC database.")
                    except Exception as e: st.error(f"Critical Error: {e}")

    with col_list:
        st.markdown('<div class="step-header"><div class="step-number">4</div><div class="step-title">Project Device List</div></div>', unsafe_allow_html=True)
        if st.session_state.device_list:
            # FIX: Direct assignment for smooth editing and deletion
            st.session_state.device_list = st.data_editor(
                st.session_state.device_list,
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    "qty": st.column_config.NumberColumn("Quantity", min_value=1, required=True),
                    "device": st.column_config.TextColumn("Device Type", disabled=True),
                    "floor": st.column_config.TextColumn("Floor/Location", disabled=True),
                },
                key="device_editor_final_v1"
            )
            
            if st.button("🗑️ Clear Entire List", use_container_width=True):
                st.session_state.device_list = []
                st.rerun()
        else:
            st.info("No devices added yet. Please use Step 2 to add items.")

# ============================================================
# TAB 1: PROFESSIONAL PROFILE
# ============================================================
with tabs[1]:
    st.subheader("Account & Professional Settings")
    st.markdown("This information is stored in your cloud profile and used to auto-populate all form signatures and company fields.")

    # 🏢 Fire Alarm Company
    with st.expander("🏢 Fire Alarm Company Details", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            c_name = st.text_input("Company Name", value=profile.get("company_name", ""), key="c_name")
            c_addr = st.text_input("Business Address", value=profile.get("company_address", ""), key="c_addr")
            c_city = st.text_input("City", value=profile.get("company_city", ""), key="c_city")
            c_state = st.text_input("State", value=profile.get("company_state", "NY"), key="c_state")
            c_zip = st.text_input("Zip Code", value=profile.get("company_zip", ""), key="c_zip")
        with col2:
            c_phone = st.text_input("Phone", value=profile.get("company_phone", ""), key="c_phone")
            c_email = st.text_input("Email", value=profile.get("company_email", ""), key="c_email")
            c_reg = st.text_input("Registration No.", value=profile.get("company_reg_no", ""), key="c_reg")
            c_cof = st.text_input("COF S-97 Holder", value=profile.get("company_cof_s97", ""), key="c_cof")
            c_exp = st.text_input("COF Expiration Date", value=profile.get("company_expiration", ""), key="c_exp")

    # 📐 Architect / Applicant
    with st.expander("📐 Architect / Applicant Information"):
        col1, col2 = st.columns(2)
        with col1:
            a_name = st.text_input("Architecture Firm Name", value=profile.get("arch_name", ""), key="a_name")
            a_addr = st.text_input("Firm Address", value=profile.get("arch_address", ""), key="a_addr")
            a_city = st.text_input("Firm City", value=profile.get("arch_city", ""), key="a_city")
            a_state = st.text_input("Firm State", value=profile.get("arch_state", ""), key="a_state")
            a_zip = st.text_input("Firm Zip Code", value=profile.get("arch_zip", ""), key="a_zip")
        with col2:
            a_phone = st.text_input("Firm Phone", value=profile.get("arch_phone", ""), key="a_phone")
            a_email = st.text_input("Firm Email", value=profile.get("arch_email", ""), key="a_email")
            a_license = st.text_input("License No. (PE/RA)", value=profile.get("arch_license", ""), key="a_license")
            a_role = st.selectbox("Professional Role", ["PE", "RA"], index=0 if profile.get("arch_role") == "PE" else 1, key="a_role")

    # ⚡ Electrical Contractor
    with st.expander("⚡ Electrical Contractor Information"):
        col1, col2 = st.columns(2)
        with col1:
            e_name = st.text_input("Electrical Co. Name", value=profile.get("elec_name", ""), key="e_name")
            e_addr = st.text_input("Elec. Co. Address", value=profile.get("elec_address", ""), key="e_addr")
            e_city = st.text_input("Elec. Co. City", value=profile.get("elec_city", ""), key="e_city")
            e_state = st.text_input("Elec. Co. State", value=profile.get("elec_state", ""), key="e_state")
        with col2:
            e_phone = st.text_input("Elec. Co. Phone", value=profile.get("elec_phone", ""), key="e_phone")
            e_license = st.text_input("License No.", value=profile.get("elec_license", ""), key="e_license")
            e_exp = st.text_input("License Expiration", value=profile.get("elec_expiration", ""), key="e_exp")

    # 🛠️ Tech Defaults & 📡 Central Station
    col1, col2 = st.columns(2)
    with col1:
        with st.expander("🛠️ Technical Defaults"):
            t_man = st.text_input("Default Manufacturer", value=profile.get("tech_manufacturer", ""), key="t_man")
            t_appr = st.text_input("BSA/MEA/COA Approval", value=profile.get("tech_approval", ""), key="t_appr")
            t_gauge = st.text_input("Default Wire Gauge", value=profile.get("tech_wire_gauge", ""), key="t_gauge")
            t_wire = st.text_input("Default Wire Type", value=profile.get("tech_wire_type", ""), key="t_wire")
    with col2:
        with st.expander("📡 Central Station Details"):
            cs_name = st.text_input("CS Name", value=profile.get("cs_name", ""), key="cs_name")
            cs_code = st.text_input("CS ID Code", value=profile.get("cs_code", ""), key="cs_code")
            cs_phone = st.text_input("CS Phone Number", value=profile.get("cs_phone", ""), key="cs_phone")

    if st.button("💾 SAVE PROFILE PERMANENTLY", type="primary", use_container_width=True):
        full_update = {
            "id": st.session_state.user.id, "updated_at": "now()",
            # Company
            "company_name": c_name, "company_address": c_addr, "company_city": c_city, "company_state": c_state, "company_zip": c_zip,
            "company_phone": c_phone, "company_email": c_email, "company_reg_no": c_reg, "company_cof_s97": c_cof, "company_expiration": c_exp,
            # Architect
            "arch_name": a_name, "arch_address": a_addr, "arch_city": a_city, "arch_state": a_state, "arch_zip": a_zip, "arch_phone": a_phone, "arch_email": a_email, "arch_license": a_license, "arch_role": a_role,
            # Electrician
            "elec_name": e_name, "elec_address": e_addr, "elec_city": e_city, "elec_state": e_state, "elec_phone": e_phone, "elec_license": e_license, "elec_expiration": e_exp,
            # Tech
            "tech_manufacturer": t_man, "tech_approval": t_appr, "tech_wire_gauge": t_gauge, "tech_wire_type": t_wire,
            # Central Station
            "cs_name": cs_name, "cs_code": cs_code, "cs_phone": cs_phone
        }
        try:
            supabase.table("profiles").upsert(full_update).execute()
            profile.update(full_update)
            sync_profile_to_main(profile)
            st.success("✅ Profile updated successfully! Your forms will now use these credentials.")
        except Exception as e: st.error(f"Error saving to database: {e}")
