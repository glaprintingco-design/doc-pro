import streamlit as st
from supabase import create_client, Client
import main
import os
import zipfile
from io import BytesIO

# ── PAGE CONFIGURATION ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="Fire Form Pro | NYC FDNY Automation", 
    layout="wide", 
    page_icon="🔥", 
    initial_sidebar_state="expanded"
)

# ── SECRETS & CONNECTION ─────────────────────────────────────────────────────
main.API_KEY_NYC       = st.secrets.get("NYC_API_KEY", "")
main.APP_TOKEN_SOCRATA = st.secrets.get("SOCRATA_TOKEN", "")
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "https://uhhiqkymipbcepqzwtvg.supabase.co")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "sb_publishable_mvqOWXc5s4b3_IMe4gGexw_sU3B2DRL")

# ── CUSTOM CSS (PRO SAAS - CLEAN & PROFESSIONAL) ─────────────────────────────
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

    /* Step Headers */
    .step-header {
        display: flex; align-items: center; gap: 12px;
        margin-bottom: 20px; margin-top: 10px;
    }
    .step-number {
        background-color: var(--primary); color: white;
        border-radius: 8px; width: 28px; height: 28px;
        display: flex; align-items: center; justify-content: center;
        font-weight: 700; font-size: 14px;
    }
    .step-title { font-weight: 600; font-size: 1.1rem; color: #2C2E33; }

    /* Buttons */
    div.stButton > button[kind="primary"] {
        background-color: var(--primary); border: none;
        padding: 0.6rem 2rem; font-weight: 600; border-radius: 8px;
    }
    
    /* Login Box */
    .login-box {
        max-width: 450px; margin: 80px auto; padding: 40px;
        background: white; border-radius: 16px;
        border: 1px solid var(--border);
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ── SUPABASE & SESSION INITIALIZATION ────────────────────────────────────────
if "supabase" not in st.session_state:
    try:
        st.session_state.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Supabase Connection Error: {e}"); st.stop()

supabase = st.session_state.supabase

# Attempt to restore session on refresh
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

# ── AUTHENTICATION GATE ──────────────────────────────────────────────────────
if not st.session_state.user:
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.title("🔥 Fire Form Pro")
    st.markdown("<p style='color:#666'>FDNY Form Automation Platform</p>", unsafe_allow_html=True)
    
    auth_mode = st.radio("Select Action", ["Login", "Sign Up"], horizontal=True)
    email_input = st.text_input("Email Address")
    pass_input = st.text_input("Password", type="password")
    
    if st.button("Continue to Dashboard", type="primary", use_container_width=True):
        try:
            if auth_mode == "Login":
                res = supabase.auth.sign_in_with_password({"email": email_input.strip(), "password": pass_input})
            else:
                res = supabase.auth.sign_up({"email": email_input.strip(), "password": pass_input})
                if res.user:
                    supabase.table("profiles").insert({"id": res.user.id, "email": email_input}).execute()
            
            if res.user:
                st.session_state.user = res.user
                st.rerun()
            else:
                st.error("Authentication failed. Please check your credentials.")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ── HELPER FUNCTIONS ─────────────────────────────────────────────────────────
def logout():
    supabase.auth.sign_out()
    st.session_state.user = None
    st.session_state.device_list = []
    st.rerun()

def fetch_user_profile(uid):
    try:
        res = supabase.table("profiles").select("*").eq("id", uid).execute()
        return res.data[0] if res.data else {}
    except: return {}

def sync_profile_to_main(p):
    """Zero Abbreviations: Syncs every single professional field."""
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
        "State": p.get("cs_state", ""), "Zip": p.get("cs_zip", ""), "Phone": p.get("cs_phone", ""),
    })

# ── MAIN APPLICATION UI ──────────────────────────────────────────────────────
profile = fetch_user_profile(st.session_state.user.id)

with st.sidebar:
    st.title("🔥 Fire Form Pro")
    st.markdown(f"**Account:** {st.session_state.user.email}")
    if st.button("Log Out", use_container_width=True): logout()

tabs = st.tabs(["🚀 Project Builder", "👤 Professional Profile"])

# ============================================================
# TAB 0: PROJECT BUILDER
# ============================================================
with tabs[0]:
    left, right = st.columns([1, 1.2], gap="large")
    with left:
        st.markdown('<div class="step-header"><div class="step-number">1</div><div class="step-title">Project Info</div></div>', unsafe_allow_html=True)
        bin_no = st.text_input("Property BIN", placeholder="e.g. 1012345")
        job_description = st.text_area("TM-1 Job Description", value="Installation of Fire Alarm System.", height=100)

        st.markdown('<div class="step-header"><div class="step-number">2</div><div class="step-title">Add Devices (A-433)</div></div>', unsafe_allow_html=True)
        c1, c2 = st.columns([2,1])
        with c1: flr = st.selectbox("Floor Location", main.FULL_FLOOR_LIST)
        with c2: q = st.number_input("Qty", min_value=1, value=1)
        cat = st.selectbox("Category", list(main.MASTER_DEVICE_LIST.keys()))
        dtype = st.selectbox("Device Type", main.MASTER_DEVICE_LIST.get(cat, []))
        if st.button("➕ Add to Device List", use_container_width=True):
            st.session_state.device_list.append({"device": dtype, "floor": flr, "qty": q})
            st.toast(f"Added {q}x {dtype}")

        st.markdown('<div class="step-header"><div class="step-number">3</div><div class="step-title">Generate Documents</div></div>', unsafe_allow_html=True)
        f1, f2 = st.columns(2)
        with f1:
            g_tm1 = st.checkbox("TM-1 Application", value=True); g_a433 = st.checkbox("A-433 List", value=True)
        with f2:
            g_b45 = st.checkbox("B-45 Request", value=True); g_rpt = st.checkbox("Audit Report", value=True)

        if st.button("🔥 RUN GENERATOR", type="primary", use_container_width=True):
            if not bin_no: st.error("BIN is required")
            else:
                with st.spinner("Processing..."):
                    sync_profile_to_main(profile)
                    info = main.obtener_datos_completos(bin_no)
                    if info:
                        full_data = {**info, "job_desc": job_description, "devices": st.session_state.device_list}
                        files = []
                        if g_tm1: main.generar_tm1(full_data, "tm-1-application-for-plan-examination-doc-review.pdf", f"TM1_{bin_no}.pdf"); files.append(f"TM1_{bin_no}.pdf")
                        if g_a433: main.generar_a433(full_data, "application-a-433-c.pdf", f"A433_{bin_no}.pdf"); files.append(f"A433_{bin_no}.pdf")
                        if g_b45: main.generar_b45(full_data, "b45-inspection-request.pdf", f"B45_{bin_no}.pdf"); files.append(f"B45_{bin_no}.pdf")
                        if g_rpt: main.generar_reporte_auditoria(full_data, f"REPORT_{bin_no}.txt"); files.append(f"REPORT_{bin_no}.txt")
                        buf = BytesIO()
                        with zipfile.ZipFile(buf, "a", zipfile.ZIP_DEFLATED, False) as zf:
                            for fn in files: 
                                if os.path.exists(fn): zf.write(fn); os.remove(fn)
                        st.success("Forms generated!")
                        st.download_button("📥 Download ZIP", data=buf.getvalue(), file_name=f"FDNY_{bin_no}.zip")

    with right:
        st.markdown('<div class="step-header"><div class="step-number">4</div><div class="step-title">Device List Review</div></div>', unsafe_allow_html=True)
        if st.session_state.device_list:
            # FIX: Direct assignment for table stability
            st.session_state.device_list = st.data_editor(
                st.session_state.device_list, num_rows="dynamic", use_container_width=True,
                column_config={"qty": st.column_config.NumberColumn("Qty", min_value=1), "device": st.column_config.TextColumn("Device", disabled=True), "floor": st.column_config.TextColumn("Floor", disabled=True)},
                key="editor_pro_usa"
            )
            if st.button("🗑️ Clear List", use_container_width=True):
                st.session_state.device_list = []; st.rerun()
        else:
            st.info("List is empty. Add devices on the left.")

# ============================================================
# TAB 1: PROFESSIONAL PROFILE (ALL FIELDS INCLUDED)
# ============================================================
with tabs[1]:
    st.subheader("Professional Credentials")
    
    # 🏢 FIRE ALARM COMPANY
    with st.expander("🏢 Fire Alarm Company Data", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            c_name = st.text_input("Company Name", value=profile.get("company_name", ""), key="c_name")
            c_addr = st.text_input("Address", value=profile.get("company_address", ""), key="c_addr")
            c_city = st.text_input("City", value=profile.get("company_city", ""), key="c_city")
            c_state = st.text_input("State", value=profile.get("company_state", ""), key="c_state")
            c_zip = st.text_input("Zip Code", value=profile.get("company_zip", ""), key="c_zip")
            c_phone = st.text_input("Phone", value=profile.get("company_phone", ""), key="c_phone")
        with col2:
            c_email = st.text_input("Email", value=profile.get("company_email", ""), key="c_email")
            c_first = st.text_input("First Name", value=profile.get("company_first_name", ""), key="c_first")
            c_last = st.text_input("Last Name", value=profile.get("company_last_name", ""), key="c_last")
            c_reg = st.text_input("Reg No", value=profile.get("company_reg_no", ""), key="c_reg")
            c_cof = st.text_input("COF S97", value=profile.get("company_cof_s97", ""), key="c_cof")
            c_exp = st.text_input("Exp. Date", value=profile.get("company_expiration", ""), key="c_exp")

    # 📐 ARCHITECT
    with st.expander("📐 Architect / Applicant Information"):
        col1, col2 = st.columns(2)
        with col1:
            a_name = st.text_input("Architect Co. Name", value=profile.get("arch_name", ""), key="a_name")
            a_addr = st.text_input("Arch. Address", value=profile.get("arch_address", ""), key="a_addr")
            a_city = st.text_input("Arch. City", value=profile.get("arch_city", ""), key="a_city")
            a_state = st.text_input("Arch. State", value=profile.get("arch_state", ""), key="a_state")
            a_zip = st.text_input("Arch. Zip", value=profile.get("arch_zip", ""), key="a_zip")
            a_phone = st.text_input("Arch. Phone", value=profile.get("arch_phone", ""), key="a_phone")
        with col2:
            a_email = st.text_input("Arch. Email", value=profile.get("arch_email", ""), key="a_email")
            a_first = st.text_input("Arch. First Name", value=profile.get("arch_first_name", ""), key="a_first")
            a_last = st.text_input("Arch. Last Name", value=profile.get("arch_last_name", ""), key="a_last")
            a_license = st.text_input("License No", value=profile.get("arch_license", ""), key="a_license")
            a_role = st.selectbox("Role", ["PE", "RA"], index=0 if profile.get("arch_role")=="PE" else 1, key="a_role")

    # ⚡ ELECTRICIAN
    with st.expander("⚡ Electrical Contractor Information"):
        col1, col2 = st.columns(2)
        with col1:
            e_name = st.text_input("Electrician Co. Name", value=profile.get("elec_name", ""), key="e_name")
            e_addr = st.text_input("Elec. Address", value=profile.get("elec_address", ""), key="e_addr")
            e_city = st.text_input("Elec. City", value=profile.get("elec_city", ""), key="e_city")
            e_state = st.text_input("Elec. State", value=profile.get("elec_state", ""), key="e_state")
            e_zip = st.text_input("Elec. Zip", value=profile.get("elec_zip", ""), key="e_zip")
            e_phone = st.text_input("Elec. Phone", value=profile.get("elec_phone", ""), key="e_phone")
        with col2:
            e_email = st.text_input("Elec. Email", value=profile.get("elec_email", ""), key="e_email")
            e_first = st.text_input("Elec. First Name", value=profile.get("elec_first_name", ""), key="e_first")
            e_last = st.text_input("Elec. Last Name", value=profile.get("elec_last_name", ""), key="e_last")
            e_license = st.text_input("Elec. License No", value=profile.get("elec_license", ""), key="e_license")
            e_exp = st.text_input("Elec. Expiration", value=profile.get("elec_expiration", ""), key="e_exp")

    # 🛠️ TECH & 📡 CENTRAL STATION
    t1, cs1 = st.columns(2)
    with t1:
        with st.expander("🛠️ Technical Defaults"):
            t_man = st.text_input("Manufacturer", value=profile.get("tech_manufacturer", ""), key="t_man")
            t_appr = st.text_input("BSA/MEA/COA Approval", value=profile.get("tech_approval", ""), key="t_appr")
            t_gauge = st.text_input("Wire Gauge", value=profile.get("tech_wire_gauge", ""), key="t_gauge")
            t_wire = st.text_input("Wire Type", value=profile.get("tech_wire_type", ""), key="t_wire")
    with cs1:
        with st.expander("📡 Central Station"):
            cs_name = st.text_input("CS Name", value=profile.get("cs_name", ""), key="cs_name")
            cs_code = st.text_input("CS Code", value=profile.get("cs_code", ""), key="cs_code")
            cs_addr = st.text_input("CS Address", value=profile.get("cs_address", ""), key="cs_addr")
            cs_city = st.text_input("CS City", value=profile.get("cs_city", ""), key="cs_city")
            cs_state = st.text_input("CS State", value=profile.get("cs_state", ""), key="cs_state")
            cs_zip = st.text_input("CS Zip", value=profile.get("cs_zip", ""), key="cs_zip")
            cs_phone = st.text_input("CS Phone", value=profile.get("cs_phone", ""), key="cs_phone")

    if st.button("💾 SAVE PROFILE PERMANENTLY", type="primary", use_container_width=True):
        full_upd = {
            "id": st.session_state.user.id, "updated_at": "now()",
            "company_name": c_name, "company_address": c_addr, "company_city": c_city, "company_state": c_state, "company_zip": c_zip, "company_phone": c_phone, "company_email": c_email, "company_first_name": c_first, "company_last_name": c_last, "company_reg_no": c_reg, "company_cof_s97": c_cof, "company_expiration": c_exp,
            "arch_name": a_name, "arch_address": a_addr, "arch_city": a_city, "arch_state": a_state, "arch_zip": a_zip, "arch_phone": a_phone, "arch_email": a_email, "arch_first_name": a_first, "arch_last_name": a_last, "arch_license": a_license, "arch_role": a_role,
            "elec_name": e_name, "elec_address": e_addr, "elec_city": e_city, "elec_state": e_state, "elec_zip": e_zip, "elec_phone": e_phone, "elec_email": e_email, "elec_first_name": e_first, "elec_last_name": e_last, "elec_license": e_license, "elec_expiration": e_exp,
            "tech_manufacturer": t_man, "tech_approval": t_appr, "tech_wire_gauge": t_gauge, "tech_wire_type": t_wire,
            "cs_name": cs_name, "cs_code": cs_code, "cs_address": cs_addr, "cs_city": cs_city, "cs_state": cs_state, "cs_zip": cs_zip, "cs_phone": cs_phone
        }
        supabase.table("profiles").upsert(full_upd).execute()
        profile.update(full_upd); sync_profile_to_main(profile)
        st.success("✅ Profile Saved!")
