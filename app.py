import streamlit as st
from supabase import create_client, Client
import main
import os
import zipfile
from io import BytesIO
from app_styles import get_styles, get_header_html, get_section_header, get_stat_card

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Fire Form Pro",
    layout="wide",
    page_icon="🔥",
    initial_sidebar_state="collapsed"
)

# Inject global styles
st.markdown(get_styles(), unsafe_allow_html=True)

# ============================================================
# SUPABASE SETUP
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
# HELPER FUNCTIONS
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
        st.error(f"Error loading profile: {e}")
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


# ============================================================
# LOGIN UI
# ============================================================
def login_ui_centered():
    st.markdown("""
    <style>
    .login-page-bg {
        min-height: 100vh;
        background: radial-gradient(ellipse at 20% 50%, rgba(249,115,22,0.08) 0%, transparent 60%),
                    radial-gradient(ellipse at 80% 20%, rgba(249,115,22,0.05) 0%, transparent 50%),
                    #0F1117;
    }
    .login-card {
        max-width: 420px;
        margin: 5vh auto;
        background: #16181F;
        border: 1px solid #2A2D3E;
        border-radius: 20px;
        padding: 2.5rem;
        box-shadow: 0 24px 64px rgba(0,0,0,0.5), 0 0 0 1px rgba(249,115,22,0.1);
        position: relative;
        overflow: hidden;
    }
    .login-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, #F97316, #FB923C, transparent);
    }
    .login-logo-area {
        text-align: center;
        margin-bottom: 2rem;
    }
    .login-flame {
        font-size: 48px;
        line-height: 1;
        margin-bottom: 0.5rem;
        filter: drop-shadow(0 0 20px rgba(249,115,22,0.6));
    }
    .login-brand {
        font-size: 26px;
        font-weight: 800;
        color: #F1F3F9;
        letter-spacing: -0.5px;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    .login-tagline {
        font-size: 13px;
        color: #5C6380;
        margin-top: 4px;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    </style>
    <div class="login-page-bg">
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="login-card">
            <div class="login-logo-area">
                <div class="login-flame">🔥</div>
                <div class="login-brand">Fire Form <span style="color:#FB923C;">Pro</span></div>
                <div class="login-tagline">Automated FDNY form generation platform</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["🔑  Sign In", "📝  Create Account"])

        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            email = st.text_input("Email Address", key="login_email", placeholder="you@company.com")
            password = st.text_input("Password", type="password", key="login_password", placeholder="••••••••")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Sign In →", use_container_width=True, type="primary"):
                if not email or not password:
                    st.error("Please enter both email and password.")
                    return
                with st.spinner("Authenticating..."):
                    try:
                        response = supabase.auth.sign_in_with_password({"email": email.strip(), "password": password})
                        if response.user:
                            st.session_state.user = response.user
                            st.success("✅ Welcome back!")
                            st.rerun()
                        else:
                            st.error("❌ Login failed. No user returned.")
                    except Exception as e:
                        error_msg = str(e)
                        st.error(f"❌ {error_msg}")
                        if "Invalid login credentials" in error_msg:
                            st.warning("⚠️ Invalid email or password.")
                        elif "Email not confirmed" in error_msg:
                            st.warning("⚠️ Please confirm your email first.")
                        elif "rate limit" in error_msg.lower():
                            st.warning("⚠️ Too many attempts. Please wait.")

        with tab2:
            st.markdown("<br>", unsafe_allow_html=True)
            email = st.text_input("Email Address", key="signup_email", placeholder="you@company.com")
            password = st.text_input("Password", type="password", key="signup_password", placeholder="Min. 6 characters")
            password_confirm = st.text_input("Confirm Password", type="password", key="signup_password_confirm", placeholder="Repeat password")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Create Account →", use_container_width=True, type="primary"):
                if not email or not password:
                    st.error("Please fill in all fields.")
                    return
                if password != password_confirm:
                    st.error("❌ Passwords do not match.")
                    return
                if len(password) < 6:
                    st.error("Password must be at least 6 characters.")
                    return
                with st.spinner("Creating account..."):
                    try:
                        response = supabase.auth.sign_up({"email": email.strip(), "password": password})
                        if response.user:
                            st.success("✅ Account created! Check your email to confirm.")
                            try:
                                supabase.table("profiles").insert({"id": response.user.id, "email": email}).execute()
                            except Exception:
                                pass
                        else:
                            st.error("Sign up completed but no user data returned.")
                    except Exception as e:
                        error_msg = str(e)
                        st.error(f"❌ {error_msg}")
                        if "already registered" in error_msg.lower():
                            st.warning("⚠️ Email already registered. Use Sign In.")

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# ACCESS CONTROL
# ============================================================
if not st.session_state.user:
    login_ui_centered()
    st.stop()


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("""
    <div style="padding: 1.5rem 0 0.5rem; text-align:center;">
        <div style="font-size:36px; filter: drop-shadow(0 0 12px rgba(249,115,22,0.6));">🔥</div>
        <div style="font-size:16px; font-weight:800; color:#F1F3F9; margin-top:6px;">
            Fire Form <span style="color:#FB923C;">Pro</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("""
    <div style="font-size:11px; text-transform:uppercase; letter-spacing:1px; color:#5C6380; font-weight:700; padding: 0 0.5rem; margin-bottom:0.5rem;">
        Current Session
    </div>
    """, unsafe_allow_html=True)

    email_display = st.session_state.user.email
    st.markdown(f"""
    <div style="background:#12141C; border:1px solid #2A2D3E; border-radius:10px; padding:10px 12px; margin-bottom:1rem;">
        <div style="font-size:11px; color:#5C6380; margin-bottom:2px;">Signed in as</div>
        <div style="font-size:13px; color:#F1F3F9; font-weight:600; word-break:break-all;">{email_display}</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚪  Sign Out", use_container_width=True, type="secondary"):
        logout()

    st.markdown("---")

    # Quick stats
    device_count = len(st.session_state.device_list)
    total_qty = sum(d.get("qty", 0) for d in st.session_state.device_list)

    st.markdown("""
    <div style="font-size:11px; text-transform:uppercase; letter-spacing:1px; color:#5C6380; font-weight:700; padding: 0 0.5rem; margin-bottom:0.75rem;">
        Session Stats
    </div>
    """, unsafe_allow_html=True)

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown(f"""
        <div style="background:#12141C; border:1px solid #2A2D3E; border-radius:10px; padding:12px; text-align:center;">
            <div style="font-size:24px; font-weight:800; color:#FB923C; font-family:'JetBrains Mono',monospace;">{device_count}</div>
            <div style="font-size:10px; color:#5C6380; text-transform:uppercase; letter-spacing:0.5px; margin-top:2px;">Device Types</div>
        </div>
        """, unsafe_allow_html=True)
    with col_s2:
        st.markdown(f"""
        <div style="background:#12141C; border:1px solid #2A2D3E; border-radius:10px; padding:12px; text-align:center;">
            <div style="font-size:24px; font-weight:800; color:#FB923C; font-family:'JetBrains Mono',monospace;">{total_qty}</div>
            <div style="font-size:10px; color:#5C6380; text-transform:uppercase; letter-spacing:0.5px; margin-top:2px;">Total Units</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="text-align:center;">
        <div style="font-size:11px; color:#5C6380; font-family:'JetBrains Mono',monospace;">v1.1.0  •  © 2026</div>
        <div style="font-size:11px; color:#5C6380; margin-top:2px;">NYC Fire Alarm Industry</div>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# MAIN HEADER
# ============================================================
st.markdown(get_header_html(st.session_state.user.email), unsafe_allow_html=True)

# Logout button in header area (positioned via the sidebar instead)

# ============================================================
# LOAD PROFILE & TABS
# ============================================================
profile = fetch_user_profile(st.session_state.user.id)

tabs = st.tabs(["🏗️  Project Builder", "👤  Profile Settings"])


# ============================================================
# TAB 1: PROFILE SETTINGS
# ============================================================
with tabs[1]:
    st.markdown(get_section_header("01", "Professional Profile"), unsafe_allow_html=True)
    st.markdown("""
    <div style="background:rgba(249,115,22,0.06); border:1px solid rgba(249,115,22,0.2); border-radius:10px; padding:12px 16px; margin-bottom:1.5rem; font-size:13px; color:#9BA3BF;">
        💾 &nbsp; Data saved here is stored securely in the cloud and auto-fills your FDNY forms on every project.
    </div>
    """, unsafe_allow_html=True)

    with st.expander("🏢  FA Company / Expeditor Information", expanded=True):
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
            c_exp   = st.text_input("Expiration Date",value=profile.get("company_expiration", ""), key="c_exp")

    with st.expander("📐  Architect / Engineer Information"):
        col1, col2 = st.columns(2)
        with col1:
            a_name    = st.text_input("Company Name",   value=profile.get("arch_name", ""),        key="a_name")
            a_addr    = st.text_input("Address",         value=profile.get("arch_address", ""),     key="a_addr")
            a_city    = st.text_input("City",            value=profile.get("arch_city", ""),        key="a_city")
            a_state   = st.text_input("State",           value=profile.get("arch_state", ""),       key="a_state")
            a_zip     = st.text_input("Zip Code",        value=profile.get("arch_zip", ""),         key="a_zip")
            a_phone   = st.text_input("Phone",           value=profile.get("arch_phone", ""),       key="a_phone")
        with col2:
            a_email   = st.text_input("Email",           value=profile.get("arch_email", ""),       key="a_email")
            a_first   = st.text_input("First Name",      value=profile.get("arch_first_name", ""),  key="a_first")
            a_last    = st.text_input("Last Name",        value=profile.get("arch_last_name", ""),   key="a_last")
            a_license = st.text_input("License No",      value=profile.get("arch_license", ""),     key="a_license")
            a_role    = st.selectbox("Role", ["PE", "RA"],
                                     index=0 if profile.get("arch_role") == "PE" else 1, key="a_role")

    with st.expander("⚡  Electrical Contractor Information"):
        col1, col2 = st.columns(2)
        with col1:
            e_name    = st.text_input("Company Name",   value=profile.get("elec_name", ""),        key="e_name")
            e_addr    = st.text_input("Address",         value=profile.get("elec_address", ""),     key="e_addr")
            e_city    = st.text_input("City",            value=profile.get("elec_city", ""),        key="e_city")
            e_state   = st.text_input("State",           value=profile.get("elec_state", ""),       key="e_state")
            e_zip     = st.text_input("Zip Code",        value=profile.get("elec_zip", ""),         key="e_zip")
            e_phone   = st.text_input("Phone",           value=profile.get("elec_phone", ""),       key="e_phone")
        with col2:
            e_email   = st.text_input("Email",           value=profile.get("elec_email", ""),       key="e_email")
            e_first   = st.text_input("First Name",      value=profile.get("elec_first_name", ""),  key="e_first")
            e_last    = st.text_input("Last Name",        value=profile.get("elec_last_name", ""),   key="e_last")
            e_license = st.text_input("License No",      value=profile.get("elec_license", ""),     key="e_license")
            e_exp     = st.text_input("License Expiration", value=profile.get("elec_expiration", ""), key="e_exp")

    col1, col2 = st.columns(2)
    with col1:
        with st.expander("🛠️  A-433 Defaults"):
            t_man   = st.text_input("Default Manufacturer",  value=profile.get("tech_manufacturer", ""), key="t_man")
            t_appr  = st.text_input("BSA/MEA/COA Approval",  value=profile.get("tech_approval", ""),     key="t_appr")
            t_gauge = st.text_input("Wire Gauge",             value=profile.get("tech_wire_gauge", ""),   key="t_gauge")
            t_wire  = st.text_input("Wire Type",              value=profile.get("tech_wire_type", ""),    key="t_wire")
    with col2:
        with st.expander("📡  Central Station Information"):
            cs_name  = st.text_input("CS Name",    value=profile.get("cs_name", ""),    key="cs_name")
            cs_code  = st.text_input("CS Code",    value=profile.get("cs_code", ""),    key="cs_code")
            cs_addr  = st.text_input("CS Address", value=profile.get("cs_address", ""), key="cs_addr")
            cs_city  = st.text_input("CS City",    value=profile.get("cs_city", ""),    key="cs_city")
            cs_state = st.text_input("CS State",   value=profile.get("cs_state", ""),   key="cs_state")
            cs_zip   = st.text_input("CS Zip",     value=profile.get("cs_zip", ""),     key="cs_zip")
            cs_phone = st.text_input("CS Phone",   value=profile.get("cs_phone", ""),   key="cs_phone")

    st.markdown("<br>", unsafe_allow_html=True)
    col_save1, col_save2, col_save3 = st.columns([1.5, 1, 1.5])
    with col_save2:
        if st.button("💾  Save Profile", use_container_width=True, type="primary"):
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
                st.error(f"Error saving: {e}")


# ============================================================
# TAB 0: PROJECT BUILDER
# ============================================================
with tabs[0]:

    # --- SECTION 1: PROJECT INFO ---
    st.markdown(get_section_header("01", "Project Information"), unsafe_allow_html=True)
    
    col_info1, col_info2 = st.columns([1, 2])
    with col_info1:
        bin_number = st.text_input(
            "Property BIN Number",
            placeholder="e.g. 1012345",
            help="Building Identification Number assigned by NYC DOB"
        )
    with col_info2:
        job_desc = st.text_area(
            "TM-1 Job Description",
            value="Installation of Fire Alarm System.",
            height=72
        )

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color:#2A2D3E; margin:0 0 1.5rem;'>", unsafe_allow_html=True)

    # --- SECTION 2: DEVICE LIST ---
    st.markdown(
        get_section_header("02", "Device Schedule") +
        "<span style='font-size:12px; color:#5C6380; margin-left:8px; position:relative; top:-1px;'>— Optional · Required for A-433</span>",
        unsafe_allow_html=True
    )

    col_dev_left, col_dev_right = st.columns([1, 2])

    with col_dev_left:
        st.markdown("""
        <div style="background:#1C1F2A; border:1px solid #2A2D3E; border-radius:14px; padding:1.25rem; margin-bottom:1rem;">
            <div style="font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:0.8px; color:#5C6380; margin-bottom:1rem;">
                Add Device
            </div>
        """, unsafe_allow_html=True)

        floor    = st.selectbox("Floor Location", main.FULL_FLOOR_LIST)
        category = st.selectbox("Category", list(main.MASTER_DEVICE_LIST.keys()))
        device   = st.selectbox("Device Type", main.MASTER_DEVICE_LIST.get(category, []))
        qty      = st.number_input("Quantity", min_value=1, value=1)

        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("➕  Add to Schedule", use_container_width=True, type="primary"):
            st.session_state.device_list.append({
                "device": device,
                "floor": floor,
                "qty": qty,
            })
            st.success(f"Added: {qty}× {device} on {floor}")

    with col_dev_right:
        st.markdown("""
        <div style="font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:0.8px; color:#5C6380; margin-bottom:0.75rem;">
            Device Schedule
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.device_list:
            edited_list = st.data_editor(
                st.session_state.device_list,
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    "qty":    st.column_config.NumberColumn("Qty", min_value=1, max_value=999, step=1, required=True),
                    "device": st.column_config.TextColumn("Device Type", disabled=True),
                    "floor":  st.column_config.TextColumn("Floor", disabled=True),
                },
                key="device_editor",
            )
            if edited_list != st.session_state.device_list:
                st.session_state.device_list = edited_list
                st.rerun()

            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
            if st.button("🗑️  Clear Schedule", use_container_width=True, type="secondary"):
                st.session_state.device_list = []
                st.rerun()
        else:
            st.markdown("""
            <div style="border:1px dashed #2A2D3E; border-radius:14px; padding:3rem; text-align:center;">
                <div style="font-size:32px; opacity:0.4; margin-bottom:0.75rem;">📋</div>
                <div style="font-size:14px; color:#5C6380; font-weight:500;">No devices added yet</div>
                <div style="font-size:12px; color:#3A3D4E; margin-top:4px;">Use the panel on the left to add devices</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:#2A2D3E; margin:1.5rem 0;'>", unsafe_allow_html=True)

    # --- SECTION 3: DOCUMENT GENERATION ---
    st.markdown(get_section_header("03", "Document Generation"), unsafe_allow_html=True)

    # Form selection cards
    col_chk1, col_chk2, col_chk3, col_chk4 = st.columns(4)
    with col_chk1:
        st.markdown("""<div style="background:#1C1F2A; border:1px solid #2A2D3E; border-radius:12px; padding:1rem; margin-bottom:0.5rem;">
        <div style="font-size:20px; margin-bottom:6px;">📄</div>
        <div style="font-size:12px; font-weight:700; color:#F1F3F9; margin-bottom:2px;">TM-1</div>
        <div style="font-size:11px; color:#5C6380;">Plan Examination</div>
        </div>""", unsafe_allow_html=True)
        gen_tm1 = st.checkbox("Include TM-1", value=True, key="chk_gen_tm1")

    with col_chk2:
        st.markdown("""<div style="background:#1C1F2A; border:1px solid #2A2D3E; border-radius:12px; padding:1rem; margin-bottom:0.5rem;">
        <div style="font-size:20px; margin-bottom:6px;">📋</div>
        <div style="font-size:12px; font-weight:700; color:#F1F3F9; margin-bottom:2px;">A-433</div>
        <div style="font-size:11px; color:#5C6380;">Device Schedule</div>
        </div>""", unsafe_allow_html=True)
        gen_a433 = st.checkbox("Include A-433", value=True, key="chk_gen_a433")

    with col_chk3:
        st.markdown("""<div style="background:#1C1F2A; border:1px solid #2A2D3E; border-radius:12px; padding:1rem; margin-bottom:0.5rem;">
        <div style="font-size:20px; margin-bottom:6px;">🔍</div>
        <div style="font-size:12px; font-weight:700; color:#F1F3F9; margin-bottom:2px;">B-45</div>
        <div style="font-size:11px; color:#5C6380;">Inspection Request</div>
        </div>""", unsafe_allow_html=True)
        gen_b45 = st.checkbox("Include B-45", value=True, key="chk_gen_b45")

    with col_chk4:
        st.markdown("""<div style="background:#1C1F2A; border:1px solid #2A2D3E; border-radius:12px; padding:1rem; margin-bottom:0.5rem;">
        <div style="font-size:20px; margin-bottom:6px;">📊</div>
        <div style="font-size:12px; font-weight:700; color:#F1F3F9; margin-bottom:2px;">Audit Report</div>
        <div style="font-size:11px; color:#5C6380;">Summary</div>
        </div>""", unsafe_allow_html=True)
        gen_report = st.checkbox("Include Report", value=True, key="chk_gen_report")

    st.markdown("<div style='height:1.25rem'></div>", unsafe_allow_html=True)

    # Generate button
    col_gen1, col_gen2, col_gen3 = st.columns([1, 2, 1])
    with col_gen2:
        st.markdown('<div class="ffp-generate-btn">', unsafe_allow_html=True)
        generate_clicked = st.button("🔥  GENERATE DOCUMENTS", type="primary", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if generate_clicked:
            if not bin_number:
                st.error("⚠️ Please enter a Property BIN number.")
            elif not (gen_tm1 or gen_a433 or gen_b45 or gen_report):
                st.warning("⚠️ Select at least one form to generate.")
            else:
                with st.spinner("Fetching property data and generating documents..."):
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
                            st.error("❌ Could not retrieve data for this BIN. Verify the number and try again.")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")

        # --- DOWNLOAD SECTION ---
        if st.session_state.generated_data:
            datos = st.session_state.generated_data
            count = len(datos['archivos'])

            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, rgba(34,197,94,0.08), rgba(34,197,94,0.04));
                border: 1px solid rgba(34,197,94,0.2);
                border-radius: 12px;
                padding: 12px 16px;
                margin: 1rem 0 0.75rem;
                display: flex;
                align-items: center;
                gap: 10px;
            ">
                <span style="font-size:18px;">✅</span>
                <div>
                    <div style="font-size:14px; font-weight:700; color:#86EFAC;">{count} document{'s' if count != 1 else ''} ready</div>
                    <div style="font-size:11px; color:#5C6380; margin-top:1px;">BIN: {datos['bin']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.download_button(
                label="📦  Download All as ZIP",
                data=datos["zip_buffer"],
                file_name=f"FDNY_Forms_{datos['bin']}.zip",
                mime="application/zip",
                use_container_width=True,
                type="primary"
            )

            st.markdown("""
            <div style="text-align:center; color:#5C6380; font-size:12px; margin:0.75rem 0 0.5rem;">
                Or download individually
            </div>
            """, unsafe_allow_html=True)

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
                                label=f"{icon}  {short_name}",
                                data=f_bytes,
                                file_name=f_name,
                                mime=mime_type,
                                use_container_width=True,
                                key=f"dl_{f_name}"
                            )
