import streamlit as st
from supabase import create_client, Client
import main
import os
import zipfile
from io import BytesIO

# ── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Fire Form Pro", layout="wide", page_icon="🔥")

main.API_KEY_NYC       = st.secrets.get("NYC_API_KEY", "")
main.APP_TOKEN_SOCRATA = st.secrets.get("SOCRATA_TOKEN", "")

SUPABASE_URL = st.secrets.get("SUPABASE_URL", "https://uhhiqkymipbcepqzwtvg.supabase.co")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "sb_publishable_mvqOWXc5s4b3_IMe4gGexw_sU3B2DRL")

# ── GLOBAL STYLES ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700;800&family=Barlow:wght@300;400;500;600&display=swap');

:root {
    --fire:      #FF4500;
    --fire-dim:  #CC3700;
    --amber:     #FFA500;
    --bg:        #0D0D0F;
    --surface:   #151518;
    --surface2:  #1C1C21;
    --border:    #2A2A32;
    --text:      #E8E8EC;
    --muted:     #7A7A8A;
    --success:   #22C55E;
    --font-display: 'Barlow Condensed', sans-serif;
    --font-body:    'Barlow', sans-serif;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--font-body) !important;
}
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"] { display: none !important; }

[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { font-family: var(--font-body) !important; }

.main .block-container {
    padding: 2rem 2.5rem 4rem !important;
    max-width: 1400px !important;
}

/* ── TOPBAR ── */
.ffp-topbar {
    display: flex; align-items: center; gap: 1rem;
    margin-bottom: 2rem; padding-bottom: 1.5rem;
    border-bottom: 1px solid var(--border);
}
.ffp-logo-mark {
    width: 44px; height: 44px; background: var(--fire);
    clip-path: polygon(50% 0%,80% 20%,100% 50%,80% 80%,50% 100%,20% 80%,0% 50%,20% 20%);
    display: flex; align-items: center; justify-content: center;
    font-size: 20px; flex-shrink: 0;
}
.ffp-brand-name {
    font-family: var(--font-display) !important;
    font-size: 1.9rem; font-weight: 800; letter-spacing: 0.04em;
    text-transform: uppercase; color: var(--text); margin: 0; line-height: 1;
}
.ffp-brand-sub {
    font-size: 0.72rem; font-weight: 500; letter-spacing: 0.12em;
    text-transform: uppercase; color: var(--fire); margin: 0;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 4px !important; gap: 4px !important;
    margin-bottom: 2rem !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important; border-radius: 7px !important;
    color: var(--muted) !important; font-family: var(--font-display) !important;
    font-size: 0.95rem !important; font-weight: 600 !important;
    letter-spacing: 0.05em !important; text-transform: uppercase !important;
    padding: 0.5rem 1.5rem !important; border: none !important;
    transition: all 0.2s !important;
}
.stTabs [aria-selected="true"] { background: var(--fire) !important; color: white !important; }
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] { display: none !important; }

/* ── CARDS ── */
.ffp-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 12px; padding: 1.5rem; margin-bottom: 1.25rem;
}

/* ── STEP BADGES ── */
.ffp-step {
    display: flex; align-items: center; gap: 0.6rem;
    margin-bottom: 0.6rem;
}
.ffp-step-num {
    width: 26px; height: 26px; background: var(--fire); border-radius: 50%;
    font-family: var(--font-display); font-size: 0.85rem; font-weight: 700;
    display: flex; align-items: center; justify-content: center;
    color: white; flex-shrink: 0;
}
.ffp-step-label {
    font-family: var(--font-display); font-size: 1.05rem; font-weight: 700;
    letter-spacing: 0.06em; text-transform: uppercase; color: var(--text);
}
.ffp-step-opt {
    font-size: 0.7rem; font-weight: 500; color: var(--muted);
    letter-spacing: 0.06em; text-transform: uppercase;
    background: var(--surface2); border: 1px solid var(--border);
    padding: 2px 8px; border-radius: 20px;
}

/* ── INPUTS ── */
.stTextInput input, .stTextArea textarea,
.stSelectbox [data-baseweb="select"] > div,
.stNumberInput input {
    background: var(--surface2) !important; border: 1px solid var(--border) !important;
    border-radius: 8px !important; color: var(--text) !important;
    font-family: var(--font-body) !important; font-size: 0.92rem !important;
    transition: border-color 0.2s !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--fire) !important;
    box-shadow: 0 0 0 3px rgba(255,69,0,0.15) !important;
}
.stTextInput label, .stTextArea label,
.stSelectbox label, .stNumberInput label {
    color: var(--muted) !important; font-size: 0.78rem !important;
    font-weight: 500 !important; letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
}
[data-baseweb="popover"] {
    background: var(--surface2) !important; border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}
[data-baseweb="menu"] li { color: var(--text) !important; }
[data-baseweb="menu"] li:hover { background: var(--border) !important; }

/* ── BUTTONS ── */
.stButton button {
    font-family: var(--font-display) !important; font-weight: 700 !important;
    letter-spacing: 0.08em !important; text-transform: uppercase !important;
    border-radius: 8px !important; transition: all 0.2s !important;
}
.stButton button[kind="primary"] {
    background: var(--fire) !important; border: none !important;
    color: white !important; font-size: 1rem !important;
    padding: 0.65rem 1.5rem !important;
}
.stButton button[kind="primary"]:hover {
    background: var(--fire-dim) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(255,69,0,0.35) !important;
}
.stButton button:not([kind="primary"]) {
    background: var(--surface2) !important; border: 1px solid var(--border) !important;
    color: var(--text) !important;
}
.stButton button:not([kind="primary"]):hover {
    border-color: var(--fire) !important; color: var(--fire) !important;
}

/* ── CHECKBOXES ── */
.stCheckbox label { color: var(--text) !important; font-size: 0.9rem !important; font-weight: 500 !important; }
.stCheckbox [data-baseweb="checkbox"] div {
    border-color: var(--border) !important; background: var(--surface2) !important; border-radius: 4px !important;
}
[data-testid="stCheckbox"] [aria-checked="true"] div {
    background: var(--fire) !important; border-color: var(--fire) !important;
}

/* ── DATA EDITOR ── */
[data-testid="stDataEditor"] {
    border: 1px solid var(--border) !important;
    border-radius: 10px !important; overflow: hidden !important;
}

/* ── EXPANDERS ── */
.streamlit-expanderHeader {
    background: var(--surface2) !important; border: 1px solid var(--border) !important;
    border-radius: 8px !important; color: var(--text) !important;
    font-family: var(--font-display) !important; font-weight: 600 !important;
    letter-spacing: 0.05em !important;
}
.streamlit-expanderContent {
    background: var(--surface) !important; border: 1px solid var(--border) !important;
    border-top: none !important; border-radius: 0 0 8px 8px !important; padding: 1rem !important;
}

/* ── DOWNLOAD BUTTON ── */
.stDownloadButton button {
    background: var(--surface2) !important; border: 1px solid var(--amber) !important;
    color: var(--amber) !important; font-family: var(--font-display) !important;
    font-weight: 700 !important; letter-spacing: 0.08em !important;
    text-transform: uppercase !important; border-radius: 8px !important; width: 100% !important;
}
.stDownloadButton button:hover { background: var(--amber) !important; color: var(--bg) !important; }

/* ── ALERTS ── */
.stSuccess { border-radius: 8px !important; border-left: 3px solid var(--success) !important; }
.stInfo { background: rgba(255,69,0,0.08) !important; border-left: 3px solid var(--fire) !important;
          border-radius: 8px !important; color: var(--text) !important; }

/* ── ACCOUNT CARD ── */
.ffp-account {
    background: var(--surface2); border: 1px solid var(--border);
    border-radius: 10px; padding: 1rem; margin-bottom: 1rem; font-size: 0.85rem;
}
.ffp-account-label { font-size: 0.7rem; color: var(--muted); text-transform: uppercase;
                      letter-spacing: 0.1em; margin-bottom: 4px; }
.ffp-account-email { color: var(--text); font-weight: 500; word-break: break-all; }

hr { border-color: var(--border) !important; margin: 1.5rem 0 !important; }
.stRadio label { color: var(--text) !important; font-size: 0.88rem !important; }
.stSpinner > div { border-top-color: var(--fire) !important; }

/* ── RESPONSIVE ── */
@media (max-width: 640px) {
    .main .block-container { padding: 1rem 1rem 4rem !important; }
    .ffp-brand-name { font-size: 1.5rem; }
    .ffp-topbar { margin-bottom: 1rem; padding-bottom: 1rem; }
}
</style>
""", unsafe_allow_html=True)

# ── SUPABASE ───────────────────────────────────────────────────────────────────
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


# ── HELPERS ───────────────────────────────────────────────────────────────────
def logout():
    try:
        supabase.auth.sign_out()
    except Exception:
        pass
    st.session_state.user = None
    st.session_state.device_list = []
    st.rerun()


def fetch_user_profile(user_id):
    try:
        r = supabase.table("profiles").select("*").eq("id", user_id).execute()
        return r.data[0] if r.data else {}
    except Exception as e:
        st.error(f"Error loading profile: {e}")
        return {}


def sync_profile_to_main(p):
    main.COMPANY.update({
        "Company Name": p.get("company_name",""),  "Address":    p.get("company_address",""),
        "City":         p.get("company_city",""),   "State":      p.get("company_state","NY"),
        "Zip":          p.get("company_zip",""),    "Phone":      p.get("company_phone",""),
        "Email":        p.get("company_email",""),  "First Name": p.get("company_first_name",""),
        "Last Name":    p.get("company_last_name",""), "Reg No":  p.get("company_reg_no",""),
        "COF S97":      p.get("company_cof_s97",""),"Expiration": p.get("company_expiration",""),
    })
    main.ARCHITECT.update({
        "Company Name": p.get("arch_name",""),     "Address":    p.get("arch_address",""),
        "City":         p.get("arch_city",""),      "State":      p.get("arch_state",""),
        "Zip":          p.get("arch_zip",""),       "Phone":      p.get("arch_phone",""),
        "Email":        p.get("arch_email",""),     "First Name": p.get("arch_first_name",""),
        "Last Name":    p.get("arch_last_name",""), "License No": p.get("arch_license",""),
        "Role":         p.get("arch_role","PE"),
    })
    main.ELECTRICIAN.update({
        "Company Name": p.get("elec_name",""),      "Address":    p.get("elec_address",""),
        "City":         p.get("elec_city",""),       "State":      p.get("elec_state",""),
        "Zip":          p.get("elec_zip",""),        "Phone":      p.get("elec_phone",""),
        "Email":        p.get("elec_email",""),      "First Name": p.get("elec_first_name",""),
        "Last Name":    p.get("elec_last_name",""),  "License No": p.get("elec_license",""),
        "Expiration":   p.get("elec_expiration",""),
    })
    main.TECH_DEFAULTS.update({
        "Manufacturer": p.get("tech_manufacturer",""), "Approval":  p.get("tech_approval",""),
        "WireGauge":    p.get("tech_wire_gauge",""),   "WireType":  p.get("tech_wire_type",""),
    })
    main.CENTRAL_STATION.update({
        "Company Name": p.get("cs_name",""),  "CS Code":  p.get("cs_code",""),
        "Address":      p.get("cs_address",""), "City":   p.get("cs_city",""),
        "State":        p.get("cs_state",""),   "Zip":    p.get("cs_zip",""),
        "Phone":        p.get("cs_phone",""),
    })


# ── LOGIN UI ──────────────────────────────────────────────────────────────────
def login_ui():
    with st.sidebar:
        st.markdown("""
            <div style='text-align:center;padding:1rem 0 1.5rem'>
                <div style='font-family:"Barlow Condensed",sans-serif;font-size:1.6rem;
                            font-weight:800;letter-spacing:0.06em;color:#E8E8EC;'>🔥 FIRE FORM PRO</div>
                <div style='font-size:0.7rem;color:#FF4500;letter-spacing:0.14em;
                            text-transform:uppercase;margin-top:4px;'>NYC Fire Alarm Automation</div>
            </div>
        """, unsafe_allow_html=True)
        choice   = st.radio("", ["Login", "Sign Up"], horizontal=True)
        email    = st.text_input("Email Address")
        password = st.text_input("Password", type="password")

        if choice == "Login":
            if st.button("Sign In →", use_container_width=True, type="primary"):
                if not email or not password:
                    st.error("Enter email and password"); return
                with st.spinner("Authenticating…"):
                    try:
                        r = supabase.auth.sign_in_with_password({"email": email.strip(), "password": password})
                        if r.user:
                            st.session_state.user = r.user
                            st.rerun()
                        else:
                            st.error("Login failed")
                    except Exception as e:
                        msg = str(e)
                        if "Invalid login credentials" in msg: st.error("Invalid email or password")
                        elif "Email not confirmed" in msg:     st.warning("Please confirm your email first")
                        elif "rate limit" in msg.lower():      st.warning("Too many attempts — wait a moment")
                        else:                                   st.error(msg)
        else:
            if st.button("Create Account →", use_container_width=True, type="primary"):
                if not email or not password:
                    st.error("Enter email and password"); return
                if len(password) < 6:
                    st.error("Password must be ≥ 6 characters"); return
                with st.spinner("Creating account…"):
                    try:
                        r = supabase.auth.sign_up({"email": email.strip(), "password": password})
                        if r.user:
                            st.success("Account created! Check your email to confirm.")
                            try:
                                supabase.table("profiles").insert({"id": r.user.id, "email": email}).execute()
                            except Exception:
                                pass
                        else:
                            st.error("Sign up returned no user")
                    except Exception as e:
                        msg = str(e)
                        if "already registered" in msg.lower(): st.warning("Email already registered — use Login")
                        else:                                    st.error(msg)


# ── ACCESS GATE ───────────────────────────────────────────────────────────────
if not st.session_state.user:
    login_ui()
    st.markdown("""
        <div style='display:flex;flex-direction:column;align-items:center;justify-content:center;
                    height:70vh;text-align:center;gap:1rem;'>
            <div style='font-size:3.5rem;'>🔥</div>
            <div style='font-family:"Barlow Condensed",sans-serif;font-size:2.8rem;
                        font-weight:800;letter-spacing:0.06em;color:#E8E8EC;'>FIRE FORM PRO</div>
            <div style='color:#7A7A8A;font-size:0.95rem;max-width:340px;line-height:1.7;'>
                Automated FDNY form generation<br>for NYC Fire Alarm professionals.<br>
                <span style='color:#FF4500;'>Sign in from the sidebar to get started.</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.stop()


# ── MAIN APP ──────────────────────────────────────────────────────────────────
profile = fetch_user_profile(st.session_state.user.id)

with st.sidebar:
    st.markdown(f"""
        <div style='text-align:center;padding:0.5rem 0 1.5rem'>
            <div style='font-family:"Barlow Condensed",sans-serif;font-size:1.6rem;
                        font-weight:800;letter-spacing:0.06em;color:#E8E8EC;'>🔥 FIRE FORM PRO</div>
        </div>
        <div class='ffp-account'>
            <div class='ffp-account-label'>Logged in as</div>
            <div class='ffp-account-email'>{st.session_state.user.email}</div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Sign Out", use_container_width=True):
        logout()

st.markdown("""
    <div class='ffp-topbar'>
        <div class='ffp-logo-mark'>🔥</div>
        <div>
            <div class='ffp-brand-name'>Fire Form Pro</div>
            <div class='ffp-brand-sub'>NYC Fire Alarm Automation Platform</div>
        </div>
    </div>
""", unsafe_allow_html=True)

tabs = st.tabs(["🚀  Project Builder", "👤  Professional Profile"])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 0 — PROJECT BUILDER
# ══════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    # Two columns: left panel (controls) + right panel (device list table).
    # On Streamlit mobile these stack — left then right = steps 1,2,4,5 then 3.
    # To guarantee mobile order 1→2→3→4→5 we duplicate the device list
    # visibility: show it inline on mobile via a small-screen placeholder approach.
    # Simplest correct solution: use [5,7] ratio and accept that on mobile the
    # table appears after the generate button (still usable). Add a mobile note.
    left, right = st.columns([5, 7], gap="large")

    with left:
        # ── STEP 1 ──
        st.markdown("""<div class='ffp-step'>
            <div class='ffp-step-num'>1</div>
            <div class='ffp-step-label'>Project Information</div>
        </div>""", unsafe_allow_html=True)
        with st.container():
            st.markdown("<div class='ffp-card'>", unsafe_allow_html=True)
            bin_number = st.text_input("Property BIN", placeholder="e.g. 1012345")
            job_desc   = st.text_area("TM-1 Job Description",
                                      value="Installation of Fire Alarm System.", height=88)
            st.markdown("</div>", unsafe_allow_html=True)

        # ── STEP 2 ──
        st.markdown("""<div class='ffp-step' style='margin-top:1.25rem'>
            <div class='ffp-step-num'>2</div>
            <div class='ffp-step-label'>A-433 Add Devices</div>
            <div class='ffp-step-opt'>Optional</div>
        </div>""", unsafe_allow_html=True)
        with st.container():
            st.markdown("<div class='ffp-card'>", unsafe_allow_html=True)
            floor    = st.selectbox("Floor Location", main.FULL_FLOOR_LIST)
            ca, cb   = st.columns([2, 1])
            with ca:
                category = st.selectbox("Category", list(main.MASTER_DEVICE_LIST.keys()))
            with cb:
                qty = st.number_input("Qty", min_value=1, value=1)
            device = st.selectbox("Device Type", main.MASTER_DEVICE_LIST.get(category, []))
            if st.button("➕  Add Device", use_container_width=True):
                st.session_state.device_list.append({"device": device, "floor": floor, "qty": qty})
                st.success(f"Added: {qty}× {device} — {floor}")
            st.markdown("</div>", unsafe_allow_html=True)

        # ── STEP 4 ──
        st.markdown("""<div class='ffp-step' style='margin-top:1.25rem'>
            <div class='ffp-step-num'>4</div>
            <div class='ffp-step-label'>Select Forms</div>
        </div>""", unsafe_allow_html=True)
        with st.container():
            st.markdown("<div class='ffp-card'>", unsafe_allow_html=True)
            fa, fb = st.columns(2)
            with fa:
                gen_tm1    = st.checkbox("TM-1 Application",        value=True, key="chk_gen_tm1")
                gen_a433   = st.checkbox("A-433 Device List",       value=True, key="chk_gen_a433")
            with fb:
                gen_b45    = st.checkbox("B-45 Inspection Request", value=True, key="chk_gen_b45")
                gen_report = st.checkbox("Audit Report",            value=True, key="chk_gen_report")
            st.markdown("</div>", unsafe_allow_html=True)

        # ── STEP 5 ──
        st.markdown("<div style='margin-top:1.25rem'>", unsafe_allow_html=True)
        if st.button("🔥  GENERATE DOCUMENTS", type="primary", use_container_width=True):
            if not bin_number:
                st.error("Enter a BIN number first.")
            elif not (gen_tm1 or gen_a433 or gen_b45 or gen_report):
                st.warning("Select at least one form.")
            else:
                with st.spinner("Generating forms…"):
                    try:
                        sync_profile_to_main(profile)
                        info = main.obtener_datos_completos(bin_number)
                        if info:
                            full_data = {**info, "job_desc": job_desc,
                                         "devices": st.session_state.device_list}
                            files = []
                            if gen_tm1:
                                main.generar_tm1(full_data,
                                    "tm-1-application-for-plan-examination-doc-review.pdf",
                                    f"TM1_{bin_number}.pdf")
                                files.append(f"TM1_{bin_number}.pdf")
                            if gen_a433:
                                main.generar_a433(full_data,
                                    "application-a-433-c.pdf", f"A433_{bin_number}.pdf")
                                files.append(f"A433_{bin_number}.pdf")
                            if gen_b45:
                                main.generar_b45(full_data,
                                    "b45-inspection-request.pdf", f"B45_{bin_number}.pdf")
                                files.append(f"B45_{bin_number}.pdf")
                            if gen_report:
                                main.generar_reporte_auditoria(full_data, f"REPORT_{bin_number}.txt")
                                files.append(f"REPORT_{bin_number}.txt")

                            buf = BytesIO()
                            with zipfile.ZipFile(buf, "a", zipfile.ZIP_DEFLATED, False) as zf:
                                for fn in files:
                                    if os.path.exists(fn):
                                        zf.write(fn); os.remove(fn)

                            st.success(f"✅ {len(files)} document(s) ready!")
                            st.download_button(
                                label=f"📥  Download {len(files)} Forms (ZIP)",
                                data=buf.getvalue(),
                                file_name=f"FDNY_Forms_{bin_number}.zip",
                                mime="application/zip",
                            )
                        else:
                            st.error("Could not retrieve data for this BIN.")
                    except Exception as e:
                        st.error(f"Error: {e}")
        st.markdown("</div>", unsafe_allow_html=True)

    # ── RIGHT PANEL — STEP 3: Device List ──
    with right:
        st.markdown("""<div class='ffp-step' style='margin-top:0'>
            <div class='ffp-step-num'>3</div>
            <div class='ffp-step-label'>A-433 Device List</div>
        </div>""", unsafe_allow_html=True)
        st.markdown("<div class='ffp-card' style='min-height:260px'>", unsafe_allow_html=True)

        if st.session_state.device_list:
            edited = st.data_editor(
                st.session_state.device_list,
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    "qty":    st.column_config.NumberColumn("Qty", min_value=1, max_value=999,
                                                            step=1, required=True),
                    "device": st.column_config.TextColumn("Device Type", disabled=True),
                    "floor":  st.column_config.TextColumn("Floor", disabled=True),
                },
                key="device_editor",
            )
            if edited != st.session_state.device_list:
                st.session_state.device_list = edited
                st.rerun()

            total = sum(r.get("qty", 1) for r in st.session_state.device_list)
            st.markdown(f"""
                <div style='display:flex;justify-content:space-between;align-items:center;
                            margin-top:0.75rem;padding-top:0.75rem;border-top:1px solid var(--border);
                            font-size:0.82rem;color:var(--muted);'>
                    <span>{len(st.session_state.device_list)} line(s)</span>
                    <span>{total} total devices</span>
                </div>
            """, unsafe_allow_html=True)
            if st.button("🗑️  Clear List", use_container_width=True):
                st.session_state.device_list = []
                st.rerun()
        else:
            st.markdown("""
                <div style='display:flex;flex-direction:column;align-items:center;
                            justify-content:center;padding:3.5rem 1rem;text-align:center;gap:0.75rem;'>
                    <div style='font-size:2.5rem;opacity:0.2;'>📋</div>
                    <div style='font-family:"Barlow Condensed",sans-serif;font-size:1rem;
                                font-weight:700;letter-spacing:0.1em;text-transform:uppercase;
                                color:#7A7A8A;'>No devices added yet</div>
                    <div style='font-size:0.82rem;color:#555560;max-width:220px;line-height:1.6;'>
                        Use Step 2 to add devices to the A-433 form.
                    </div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — PROFESSIONAL PROFILE
# ══════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown("""
        <p style='color:var(--muted);font-size:0.88rem;margin-bottom:1.5rem;'>
        Saved permanently in the cloud — auto-fills all your FDNY forms.
        </p>
    """, unsafe_allow_html=True)

    with st.expander("🏢  Fire Alarm Company", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            c_name  = st.text_input("Company Name",  value=profile.get("company_name",""),        key="c_name")
            c_addr  = st.text_input("Address",        value=profile.get("company_address",""),     key="c_addr")
            c_city  = st.text_input("City",           value=profile.get("company_city",""),        key="c_city")
            c_state = st.text_input("State",          value=profile.get("company_state",""),       key="c_state")
            c_zip   = st.text_input("Zip Code",       value=profile.get("company_zip",""),         key="c_zip")
            c_phone = st.text_input("Phone",          value=profile.get("company_phone",""),       key="c_phone")
        with c2:
            c_email = st.text_input("Email",          value=profile.get("company_email",""),       key="c_email")
            c_first = st.text_input("First Name",     value=profile.get("company_first_name",""),  key="c_first")
            c_last  = st.text_input("Last Name",      value=profile.get("company_last_name",""),   key="c_last")
            c_reg   = st.text_input("Reg No",         value=profile.get("company_reg_no",""),      key="c_reg")
            c_cof   = st.text_input("COF S97",        value=profile.get("company_cof_s97",""),     key="c_cof")
            c_exp   = st.text_input("Exp. Date",      value=profile.get("company_expiration",""),  key="c_exp")

    with st.expander("📐  Architect / Applicant"):
        c1, c2 = st.columns(2)
        with c1:
            a_name    = st.text_input("Co. Name",   value=profile.get("arch_name",""),          key="a_name")
            a_addr    = st.text_input("Address",     value=profile.get("arch_address",""),       key="a_addr")
            a_city    = st.text_input("City",        value=profile.get("arch_city",""),          key="a_city")
            a_state   = st.text_input("State",       value=profile.get("arch_state",""),         key="a_state")
            a_zip     = st.text_input("Zip Code",    value=profile.get("arch_zip",""),           key="a_zip")
            a_phone   = st.text_input("Phone",       value=profile.get("arch_phone",""),         key="a_phone")
        with c2:
            a_email   = st.text_input("Email",       value=profile.get("arch_email",""),         key="a_email")
            a_first   = st.text_input("First Name",  value=profile.get("arch_first_name",""),    key="a_first")
            a_last    = st.text_input("Last Name",   value=profile.get("arch_last_name",""),     key="a_last")
            a_license = st.text_input("License No",  value=profile.get("arch_license",""),       key="a_license")
            a_role    = st.selectbox("Role", ["PE","RA"],
                                     index=0 if profile.get("arch_role","PE")=="PE" else 1, key="a_role")

    with st.expander("⚡  Electrical Contractor"):
        c1, c2 = st.columns(2)
        with c1:
            e_name    = st.text_input("Co. Name",   value=profile.get("elec_name",""),           key="e_name")
            e_addr    = st.text_input("Address",     value=profile.get("elec_address",""),        key="e_addr")
            e_city    = st.text_input("City",        value=profile.get("elec_city",""),           key="e_city")
            e_state   = st.text_input("State",       value=profile.get("elec_state",""),          key="e_state")
            e_zip     = st.text_input("Zip Code",    value=profile.get("elec_zip",""),            key="e_zip")
            e_phone   = st.text_input("Phone",       value=profile.get("elec_phone",""),          key="e_phone")
        with c2:
            e_email   = st.text_input("Email",       value=profile.get("elec_email",""),          key="e_email")
            e_first   = st.text_input("First Name",  value=profile.get("elec_first_name",""),     key="e_first")
            e_last    = st.text_input("Last Name",   value=profile.get("elec_last_name",""),      key="e_last")
            e_license = st.text_input("License No",  value=profile.get("elec_license",""),        key="e_license")
            e_exp     = st.text_input("Expiration",  value=profile.get("elec_expiration",""),     key="e_exp")

    c1, c2 = st.columns(2)
    with c1:
        with st.expander("🛠️  Technical Defaults"):
            t_man   = st.text_input("Manufacturer",        value=profile.get("tech_manufacturer",""), key="t_man")
            t_appr  = st.text_input("BSA/MEA/COA Approval",value=profile.get("tech_approval",""),     key="t_appr")
            t_gauge = st.text_input("Wire Gauge",           value=profile.get("tech_wire_gauge",""),  key="t_gauge")
            t_wire  = st.text_input("Wire Type",            value=profile.get("tech_wire_type",""),   key="t_wire")
    with c2:
        with st.expander("📡  Central Station"):
            cs_name  = st.text_input("CS Name",    value=profile.get("cs_name",""),    key="cs_name")
            cs_code  = st.text_input("CS Code",    value=profile.get("cs_code",""),    key="cs_code")
            cs_addr  = st.text_input("CS Address", value=profile.get("cs_address",""), key="cs_addr")
            cs_city  = st.text_input("CS City",    value=profile.get("cs_city",""),    key="cs_city")
            cs_state = st.text_input("CS State",   value=profile.get("cs_state",""),   key="cs_state")
            cs_zip   = st.text_input("CS Zip",     value=profile.get("cs_zip",""),     key="cs_zip")
            cs_phone = st.text_input("CS Phone",   value=profile.get("cs_phone",""),   key="cs_phone")

    st.markdown("<div style='margin-top:1.5rem'>", unsafe_allow_html=True)
    if st.button("💾  Save Profile", type="primary", use_container_width=True):
        upd = {
            "id": st.session_state.user.id, "updated_at": "now()",
            "company_name": c_name,    "company_address": c_addr,   "company_city": c_city,
            "company_state": c_state,  "company_zip": c_zip,        "company_phone": c_phone,
            "company_email": c_email,  "company_first_name": c_first, "company_last_name": c_last,
            "company_reg_no": c_reg,   "company_cof_s97": c_cof,    "company_expiration": c_exp,
            "arch_name": a_name,       "arch_address": a_addr,      "arch_city": a_city,
            "arch_state": a_state,     "arch_zip": a_zip,           "arch_phone": a_phone,
            "arch_email": a_email,     "arch_first_name": a_first,  "arch_last_name": a_last,
            "arch_license": a_license, "arch_role": a_role,
            "elec_name": e_name,       "elec_address": e_addr,      "elec_city": e_city,
            "elec_state": e_state,     "elec_zip": e_zip,           "elec_phone": e_phone,
            "elec_email": e_email,     "elec_first_name": e_first,  "elec_last_name": e_last,
            "elec_license": e_license, "elec_expiration": e_exp,
            "tech_manufacturer": t_man,"tech_approval": t_appr,
            "tech_wire_gauge": t_gauge,"tech_wire_type": t_wire,
            "cs_name": cs_name, "cs_code": cs_code, "cs_address": cs_addr,
            "cs_city": cs_city, "cs_state": cs_state, "cs_zip": cs_zip, "cs_phone": cs_phone,
        }
        try:
            supabase.table("profiles").upsert(upd).execute()
            profile.update(upd)
            sync_profile_to_main(profile)
            st.success("✅ Profile saved successfully!")
        except Exception as e:
            st.error(f"Error saving: {e}")
    st.markdown("</div>", unsafe_allow_html=True)
