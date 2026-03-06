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

# ── STYLES ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

:root {
    --navy-900:  #111827;
    --navy-800:  #1a2438;
    --navy-700:  #1f2d47;
    --navy-600:  #253354;
    --navy-500:  #2d3f66;
    --card-bg:   rgba(31, 45, 71, 0.85);
    --card-bg2:  rgba(37, 51, 84, 0.6);
    --glass:     rgba(255,255,255,0.04);
    --border:    rgba(255,255,255,0.08);
    --border2:   rgba(255,255,255,0.12);
    --orange:    #FF6B35;
    --orange-dk: #e05520;
    --orange-lt: rgba(255,107,53,0.15);
    --text:      #f0f4ff;
    --text-2:    #a8b8d8;
    --text-3:    #6b7fa3;
    --success:   #34d399;
    --amber:     #fbbf24;
    --font:      'DM Sans', sans-serif;
    --mono:      'DM Mono', monospace;
}

/* ── RESET ── */
html, body, [data-testid="stAppViewContainer"] {
    background: var(--navy-900) !important;
    color: var(--text) !important;
    font-family: var(--font) !important;
}
/* Subtle mesh background */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background:
        radial-gradient(ellipse 60% 50% at 10% 20%, rgba(255,107,53,0.08) 0%, transparent 70%),
        radial-gradient(ellipse 50% 60% at 90% 80%, rgba(45,63,102,0.5) 0%, transparent 70%),
        radial-gradient(ellipse 40% 40% at 50% 50%, rgba(26,36,56,0.3) 0%, transparent 80%);
}
[data-testid="stHeader"], [data-testid="stToolbar"],
[data-testid="stDecoration"] { display: none !important; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: var(--navy-800) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { font-family: var(--font) !important; }
[data-testid="stSidebar"] .stButton button {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid var(--border2) !important;
    color: var(--text-2) !important;
    border-radius: 10px !important;
    font-size: 0.88rem !important;
    letter-spacing: 0.01em !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: rgba(255,107,53,0.12) !important;
    border-color: var(--orange) !important;
    color: var(--orange) !important;
}

/* ── MAIN CONTENT ── */
.main .block-container {
    padding: 1.75rem 2.25rem 4rem !important;
    max-width: 1380px !important;
    position: relative; z-index: 1;
}

/* ── TOPBAR ── */
.ffp-topbar {
    display: flex; align-items: center; gap: 1rem;
    margin-bottom: 1.75rem; padding-bottom: 1.25rem;
    border-bottom: 1px solid var(--border);
}
.ffp-icon-wrap {
    width: 42px; height: 42px; border-radius: 12px;
    background: linear-gradient(135deg, var(--orange), #ff9a5c);
    display: flex; align-items: center; justify-content: center;
    font-size: 20px; flex-shrink: 0;
    box-shadow: 0 4px 16px rgba(255,107,53,0.35);
}
.ffp-brand-name {
    font-size: 1.45rem; font-weight: 700; color: var(--text);
    margin: 0; letter-spacing: -0.01em; line-height: 1.1;
}
.ffp-brand-sub {
    font-size: 0.73rem; font-weight: 400; color: var(--text-3);
    margin: 0; letter-spacing: 0.02em;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--card-bg) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 5px !important; gap: 3px !important;
    margin-bottom: 1.75rem !important;
    backdrop-filter: blur(12px) !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important; border-radius: 9px !important;
    color: var(--text-3) !important; font-family: var(--font) !important;
    font-size: 0.9rem !important; font-weight: 500 !important;
    letter-spacing: 0.01em !important; padding: 0.5rem 1.4rem !important;
    border: none !important; transition: all 0.18s !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, var(--orange), #ff8c5a) !important;
    color: white !important;
    box-shadow: 0 3px 12px rgba(255,107,53,0.3) !important;
}
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] { display: none !important; }

/* ── CARDS ── */
.ffp-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 16px; padding: 1.35rem 1.5rem;
    margin-bottom: 1rem;
    backdrop-filter: blur(12px);
    box-shadow: 0 4px 24px rgba(0,0,0,0.2);
}
.ffp-card-label {
    font-size: 0.7rem; font-weight: 600; letter-spacing: 0.1em;
    text-transform: uppercase; color: var(--orange);
    margin: 0 0 1rem 0; display: flex; align-items: center; gap: 0.5rem;
}
.ffp-card-label::after {
    content:''; flex:1; height:1px;
    background: linear-gradient(90deg, var(--border2), transparent);
}

/* ── STEP BADGES ── */
.ffp-step {
    display: flex; align-items: center; gap: 0.55rem;
    margin-bottom: 0.55rem;
}
.ffp-step-num {
    width: 24px; height: 24px;
    background: linear-gradient(135deg, var(--orange), #ff8c5a);
    border-radius: 8px; font-size: 0.78rem; font-weight: 700;
    display: flex; align-items: center; justify-content: center;
    color: white; flex-shrink: 0;
    box-shadow: 0 2px 8px rgba(255,107,53,0.3);
}
.ffp-step-label {
    font-size: 0.95rem; font-weight: 600; color: var(--text);
    letter-spacing: -0.01em;
}
.ffp-step-opt {
    font-size: 0.67rem; font-weight: 500; color: var(--text-3);
    background: var(--glass); border: 1px solid var(--border);
    padding: 2px 8px; border-radius: 20px; letter-spacing: 0.04em;
}

/* ── INPUTS ── */
.stTextInput input, .stTextArea textarea,
.stSelectbox [data-baseweb="select"] > div,
.stNumberInput input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 10px !important; color: var(--text) !important;
    font-family: var(--font) !important; font-size: 0.9rem !important;
    transition: all 0.18s !important;
    box-shadow: inset 0 1px 3px rgba(0,0,0,0.2) !important;
}
.stTextInput input:hover, .stTextArea textarea:hover {
    border-color: rgba(255,255,255,0.18) !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--orange) !important;
    background: rgba(255,107,53,0.06) !important;
    box-shadow: 0 0 0 3px rgba(255,107,53,0.12), inset 0 1px 3px rgba(0,0,0,0.2) !important;
    outline: none !important;
}
.stTextInput label, .stTextArea label,
.stSelectbox label, .stNumberInput label {
    color: var(--text-3) !important; font-size: 0.75rem !important;
    font-weight: 500 !important; letter-spacing: 0.04em !important;
}
[data-baseweb="popover"] {
    background: var(--navy-700) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 12px !important;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4) !important;
}
[data-baseweb="menu"] li { color: var(--text) !important; font-family: var(--font) !important; }
[data-baseweb="menu"] li:hover { background: rgba(255,107,53,0.1) !important; }

/* ── BUTTONS ── */
.stButton button {
    font-family: var(--font) !important; font-weight: 600 !important;
    border-radius: 10px !important; transition: all 0.18s !important;
    letter-spacing: 0.01em !important;
}
.stButton button[kind="primary"] {
    background: linear-gradient(135deg, var(--orange), #ff8c5a) !important;
    border: none !important; color: white !important;
    font-size: 0.95rem !important; padding: 0.6rem 1.5rem !important;
    box-shadow: 0 4px 16px rgba(255,107,53,0.35) !important;
}
.stButton button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 22px rgba(255,107,53,0.45) !important;
}
.stButton button[kind="primary"]:active { transform: translateY(0) !important; }
.stButton button:not([kind="primary"]) {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid var(--border2) !important;
    color: var(--text-2) !important;
}
.stButton button:not([kind="primary"]):hover {
    background: rgba(255,107,53,0.08) !important;
    border-color: rgba(255,107,53,0.4) !important;
    color: var(--orange) !important;
}

/* ── CHECKBOXES ── */
.stCheckbox label { color: var(--text-2) !important; font-size: 0.9rem !important; font-weight: 400 !important; }
.stCheckbox [data-baseweb="checkbox"] div {
    border-color: var(--border2) !important;
    background: rgba(255,255,255,0.05) !important;
    border-radius: 6px !important;
    transition: all 0.15s !important;
}
[data-testid="stCheckbox"] [aria-checked="true"] div {
    background: linear-gradient(135deg, var(--orange), #ff8c5a) !important;
    border-color: transparent !important;
    box-shadow: 0 2px 8px rgba(255,107,53,0.3) !important;
}

/* ── DATA EDITOR ── */
[data-testid="stDataEditor"] {
    border: 1px solid var(--border) !important;
    border-radius: 12px !important; overflow: hidden !important;
}

/* ── EXPANDERS (Profile tab) ── */
.streamlit-expanderHeader {
    background: var(--card-bg) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important; color: var(--text) !important;
    font-family: var(--font) !important; font-weight: 500 !important;
    font-size: 0.9rem !important; backdrop-filter: blur(8px) !important;
}
.streamlit-expanderHeader:hover { border-color: var(--border2) !important; }
.streamlit-expanderContent {
    background: rgba(31,45,71,0.5) !important;
    border: 1px solid var(--border) !important;
    border-top: none !important; border-radius: 0 0 12px 12px !important;
    padding: 1.25rem !important; backdrop-filter: blur(8px) !important;
}

/* ── ALERTS ── */
.stSuccess {
    background: rgba(52,211,153,0.08) !important;
    border: 1px solid rgba(52,211,153,0.25) !important;
    border-radius: 10px !important; color: var(--text) !important;
}
.stError {
    background: rgba(239,68,68,0.08) !important;
    border: 1px solid rgba(239,68,68,0.25) !important;
    border-radius: 10px !important;
}
.stWarning {
    background: rgba(251,191,36,0.08) !important;
    border: 1px solid rgba(251,191,36,0.25) !important;
    border-radius: 10px !important;
}
.stInfo {
    background: rgba(255,107,53,0.06) !important;
    border: 1px solid rgba(255,107,53,0.2) !important;
    border-radius: 10px !important; color: var(--text-2) !important;
}

/* ── DOWNLOAD BUTTON ── */
.stDownloadButton button {
    background: rgba(251,191,36,0.1) !important;
    border: 1px solid rgba(251,191,36,0.4) !important;
    color: var(--amber) !important; font-family: var(--font) !important;
    font-weight: 600 !important; border-radius: 10px !important; width: 100% !important;
    transition: all 0.18s !important;
}
.stDownloadButton button:hover {
    background: rgba(251,191,36,0.18) !important;
    border-color: var(--amber) !important;
    box-shadow: 0 4px 16px rgba(251,191,36,0.2) !important;
}

/* ── ACCOUNT PILL ── */
.ffp-account {
    background: rgba(255,255,255,0.04);
    border: 1px solid var(--border);
    border-radius: 12px; padding: 0.85rem 1rem; margin-bottom: 1.25rem;
}
.ffp-account-label {
    font-size: 0.68rem; color: var(--text-3);
    text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 3px;
}
.ffp-account-email { color: var(--text-2); font-weight: 500; font-size: 0.85rem; word-break: break-all; }

/* ── DIVIDER ── */
hr { border-color: var(--border) !important; margin: 1.25rem 0 !important; }

/* ── RADIO ── */
.stRadio label { color: var(--text-2) !important; font-size: 0.88rem !important; }

/* ── SPINNER ── */
.stSpinner > div { border-top-color: var(--orange) !important; }

/* ═══════════════════════════════════════════════════════════
   RESPONSIVE DESKTOP LAYOUT
   We render all blocks in a single Streamlit column (mobile-
   first order). On ≥900px screens we use CSS Grid to pull the
   device-list panel (#ffp-right) to the right of the other
   steps via CSS Grid / absolute positioning trick.
   ═══════════════════════════════════════════════════════════ */

/* Wrap the whole builder section */
#ffp-builder-wrap {
    display: grid;
    grid-template-columns: 1fr;          /* mobile: single column */
    grid-template-areas:
        "s1"
        "s2"
        "s3"
        "s4"
        "s5";
    gap: 0;
}

#ffp-s1 { grid-area: s1; }
#ffp-s2 { grid-area: s2; }
#ffp-s3 { grid-area: s3; }
#ffp-s4 { grid-area: s4; }
#ffp-s5 { grid-area: s5; }

@media (min-width: 900px) {
    #ffp-builder-wrap {
        grid-template-columns: 380px 1fr;
        grid-template-rows: auto auto auto auto 1fr;
        grid-template-areas:
            "s1 s3"
            "s2 s3"
            "s4 s3"
            "s5 s3"
            ".  s3";
        gap: 0 1.5rem;
    }
}

@media (max-width: 640px) {
    .main .block-container { padding: 1rem 1rem 4rem !important; }
    .ffp-brand-name { font-size: 1.2rem; }
    .ffp-topbar { margin-bottom: 1rem; padding-bottom: 1rem; }
    .ffp-card { padding: 1rem 1.1rem; }
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
        "Company Name": p.get("company_name",""),   "Address":    p.get("company_address",""),
        "City":         p.get("company_city",""),    "State":      p.get("company_state","NY"),
        "Zip":          p.get("company_zip",""),     "Phone":      p.get("company_phone",""),
        "Email":        p.get("company_email",""),   "First Name": p.get("company_first_name",""),
        "Last Name":    p.get("company_last_name",""), "Reg No":   p.get("company_reg_no",""),
        "COF S97":      p.get("company_cof_s97",""), "Expiration": p.get("company_expiration",""),
    })
    main.ARCHITECT.update({
        "Company Name": p.get("arch_name",""),      "Address":    p.get("arch_address",""),
        "City":         p.get("arch_city",""),       "State":      p.get("arch_state",""),
        "Zip":          p.get("arch_zip",""),        "Phone":      p.get("arch_phone",""),
        "Email":        p.get("arch_email",""),      "First Name": p.get("arch_first_name",""),
        "Last Name":    p.get("arch_last_name",""),  "License No": p.get("arch_license",""),
        "Role":         p.get("arch_role","PE"),
    })
    main.ELECTRICIAN.update({
        "Company Name": p.get("elec_name",""),       "Address":    p.get("elec_address",""),
        "City":         p.get("elec_city",""),        "State":      p.get("elec_state",""),
        "Zip":          p.get("elec_zip",""),         "Phone":      p.get("elec_phone",""),
        "Email":        p.get("elec_email",""),       "First Name": p.get("elec_first_name",""),
        "Last Name":    p.get("elec_last_name",""),   "License No": p.get("elec_license",""),
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
            <div style='text-align:center;padding:1.5rem 0 2rem'>
                <div style='display:inline-flex;align-items:center;justify-content:center;
                            width:48px;height:48px;border-radius:14px;font-size:22px;
                            background:linear-gradient(135deg,#FF6B35,#ff9a5c);
                            box-shadow:0 4px 16px rgba(255,107,53,0.4);margin-bottom:0.75rem;'>🔥</div>
                <div style='font-family:"DM Sans",sans-serif;font-size:1.25rem;font-weight:700;
                            color:#f0f4ff;letter-spacing:-0.01em;'>Fire Form Pro</div>
                <div style='font-size:0.72rem;color:#6b7fa3;margin-top:2px;'>NYC Fire Alarm Automation</div>
            </div>
        """, unsafe_allow_html=True)
        choice   = st.radio("", ["Login", "Sign Up"], horizontal=True)
        email    = st.text_input("Email Address")
        password = st.text_input("Password", type="password")

        if choice == "Login":
            if st.button("Sign In", use_container_width=True, type="primary"):
                if not email or not password:
                    st.error("Please enter your email and password."); return
                with st.spinner("Signing in…"):
                    try:
                        r = supabase.auth.sign_in_with_password({"email": email.strip(), "password": password})
                        if r.user:
                            st.session_state.user = r.user; st.rerun()
                        else:
                            st.error("Login failed — no user returned.")
                    except Exception as e:
                        msg = str(e)
                        if "Invalid login credentials" in msg: st.error("Invalid email or password.")
                        elif "Email not confirmed" in msg:     st.warning("Please confirm your email first.")
                        elif "rate limit" in msg.lower():      st.warning("Too many attempts — please wait.")
                        else:                                   st.error(msg)
        else:
            if st.button("Create Account", use_container_width=True, type="primary"):
                if not email or not password:
                    st.error("Please enter your email and password."); return
                if len(password) < 6:
                    st.error("Password must be at least 6 characters."); return
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
                            st.error("Sign-up completed but no user was returned.")
                    except Exception as e:
                        msg = str(e)
                        if "already registered" in msg.lower(): st.warning("This email is already registered — use Login.")
                        else:                                    st.error(msg)


# ── ACCESS GATE ───────────────────────────────────────────────────────────────
if not st.session_state.user:
    login_ui()
    st.markdown("""
        <div style='display:flex;flex-direction:column;align-items:center;justify-content:center;
                    height:72vh;text-align:center;gap:1.1rem;'>
            <div style='display:inline-flex;align-items:center;justify-content:center;
                        width:64px;height:64px;border-radius:18px;font-size:28px;
                        background:linear-gradient(135deg,#FF6B35,#ff9a5c);
                        box-shadow:0 6px 24px rgba(255,107,53,0.4);'>🔥</div>
            <div style='font-family:"DM Sans",sans-serif;font-size:2rem;font-weight:700;
                        color:#f0f4ff;letter-spacing:-0.02em;'>Fire Form Pro</div>
            <div style='color:#6b7fa3;font-size:0.92rem;max-width:320px;line-height:1.75;'>
                Automated FDNY form generation for<br>NYC Fire Alarm professionals.
            </div>
            <div style='color:#FF6B35;font-size:0.85rem;font-weight:500;
                        background:rgba(255,107,53,0.1);border:1px solid rgba(255,107,53,0.25);
                        padding:0.45rem 1rem;border-radius:20px;'>
                → Sign in from the sidebar to get started
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.stop()


# ── MAIN APP ──────────────────────────────────────────────────────────────────
profile = fetch_user_profile(st.session_state.user.id)

with st.sidebar:
    st.markdown(f"""
        <div style='text-align:center;padding:1rem 0 1.5rem'>
            <div style='display:inline-flex;align-items:center;justify-content:center;
                        width:40px;height:40px;border-radius:12px;font-size:18px;
                        background:linear-gradient(135deg,#FF6B35,#ff9a5c);
                        box-shadow:0 3px 12px rgba(255,107,53,0.35);margin-bottom:0.6rem;'>🔥</div>
            <div style='font-family:"DM Sans",sans-serif;font-size:1.1rem;font-weight:700;
                        color:#f0f4ff;'>Fire Form Pro</div>
        </div>
        <div class='ffp-account'>
            <div class='ffp-account-label'>Logged in as</div>
            <div class='ffp-account-email'>{st.session_state.user.email}</div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Sign Out", use_container_width=True):
        logout()

# Top brand bar
st.markdown("""
    <div class='ffp-topbar'>
        <div class='ffp-icon-wrap'>🔥</div>
        <div>
            <div class='ffp-brand-name'>Fire Form Pro</div>
            <div class='ffp-brand-sub'>NYC Fire Alarm Automation Platform</div>
        </div>
    </div>
""", unsafe_allow_html=True)

tabs = st.tabs(["🚀  Project Builder", "👤  Professional Profile"])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 0 — PROJECT BUILDER
#
# Mobile order:  1 → 2 → 3 → 4 → 5
# Desktop:  left col = 1,2,4,5  |  right col = 3 (full height)
#
# Strategy: render all 5 sections in Streamlit's single-column flow, then
# use CSS Grid (with named areas) injected via st.markdown wrappers to
# reposition them on desktop.  The grid containers are pure <div> wrappers —
# Streamlit widgets go *inside* st.container() blocks that sit inside them.
# ══════════════════════════════════════════════════════════════════════════════
with tabs[0]:

    # Open the grid wrapper
    st.markdown("<div id='ffp-builder-wrap'>", unsafe_allow_html=True)

    # ── SECTION 1: Project Information ────────────────────────────
    st.markdown("<div id='ffp-s1'>", unsafe_allow_html=True)
    st.markdown("""<div class='ffp-step'>
        <div class='ffp-step-num'>1</div>
        <div class='ffp-step-label'>Project Information</div>
    </div>""", unsafe_allow_html=True)
    st.markdown("<div class='ffp-card'>", unsafe_allow_html=True)
    bin_number = st.text_input("Property BIN", placeholder="e.g. 1012345")
    job_desc   = st.text_area("TM-1 Job Description",
                              value="Installation of Fire Alarm System.", height=82)
    st.markdown("</div></div>", unsafe_allow_html=True)

    # ── SECTION 2: Add Devices ────────────────────────────────────
    st.markdown("<div id='ffp-s2'>", unsafe_allow_html=True)
    st.markdown("""<div class='ffp-step'>
        <div class='ffp-step-num'>2</div>
        <div class='ffp-step-label'>Add Devices to A-433</div>
        <div class='ffp-step-opt'>optional</div>
    </div>""", unsafe_allow_html=True)
    st.markdown("<div class='ffp-card'>", unsafe_allow_html=True)
    floor    = st.selectbox("Floor Location", main.FULL_FLOOR_LIST)
    _ca, _cb = st.columns([2, 1])
    with _ca:
        category = st.selectbox("Category", list(main.MASTER_DEVICE_LIST.keys()))
    with _cb:
        qty = st.number_input("Qty", min_value=1, value=1)
    device = st.selectbox("Device Type", main.MASTER_DEVICE_LIST.get(category, []))
    if st.button("➕  Add Device", use_container_width=True):
        st.session_state.device_list.append({"device": device, "floor": floor, "qty": qty})
        st.success(f"Added: {qty}× {device} — {floor}")
    st.markdown("</div></div>", unsafe_allow_html=True)

    # ── SECTION 3: A-433 Device List (right panel on desktop) ─────
    st.markdown("<div id='ffp-s3'>", unsafe_allow_html=True)
    st.markdown("""<div class='ffp-step'>
        <div class='ffp-step-num'>3</div>
        <div class='ffp-step-label'>A-433 Device List</div>
    </div>""", unsafe_allow_html=True)
    st.markdown("<div class='ffp-card' style='min-height:240px'>", unsafe_allow_html=True)

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
                        margin-top:0.75rem;padding-top:0.75rem;
                        border-top:1px solid rgba(255,255,255,0.07);
                        font-size:0.8rem;color:var(--text-3);'>
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
                        justify-content:center;padding:3rem 1rem;text-align:center;gap:0.6rem;'>
                <div style='font-size:2rem;opacity:0.15;'>📋</div>
                <div style='font-size:0.9rem;font-weight:600;color:var(--text-3);'>
                    No devices added yet
                </div>
                <div style='font-size:0.8rem;color:var(--text-3);opacity:0.6;
                            max-width:200px;line-height:1.6;'>
                    Use Step 2 to add devices to the A-433 form.
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)

    # ── SECTION 4: Select Forms ───────────────────────────────────
    st.markdown("<div id='ffp-s4'>", unsafe_allow_html=True)
    st.markdown("""<div class='ffp-step'>
        <div class='ffp-step-num'>4</div>
        <div class='ffp-step-label'>Select Forms to Generate</div>
    </div>""", unsafe_allow_html=True)
    st.markdown("<div class='ffp-card'>", unsafe_allow_html=True)
    _fa, _fb = st.columns(2)
    with _fa:
        gen_tm1    = st.checkbox("TM-1 Application",        value=True, key="chk_gen_tm1")
        gen_a433   = st.checkbox("A-433 Device List",       value=True, key="chk_gen_a433")
    with _fb:
        gen_b45    = st.checkbox("B-45 Inspection Request", value=True, key="chk_gen_b45")
        gen_report = st.checkbox("Audit Report",            value=True, key="chk_gen_report")
    st.markdown("</div></div>", unsafe_allow_html=True)

    # ── SECTION 5: Generate ───────────────────────────────────────
    st.markdown("<div id='ffp-s5'>", unsafe_allow_html=True)
    if st.button("🔥  Generate Documents", type="primary", use_container_width=True):
        if not bin_number:
            st.error("Please enter a BIN number.")
        elif not (gen_tm1 or gen_a433 or gen_b45 or gen_report):
            st.warning("Please select at least one form to generate.")
        else:
            with st.spinner("Generating documents…"):
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

                        st.success(f"✅ {len(files)} document(s) ready to download.")
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

    # Close grid wrapper
    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — PROFESSIONAL PROFILE
# ══════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown("""
        <p style='color:var(--text-3);font-size:0.86rem;margin-bottom:1.5rem;line-height:1.6;'>
        Your professional data is saved securely in the cloud and automatically
        populates all FDNY form fields when you generate documents.
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
            a_name    = st.text_input("Company Name", value=profile.get("arch_name",""),         key="a_name")
            a_addr    = st.text_input("Address",       value=profile.get("arch_address",""),      key="a_addr")
            a_city    = st.text_input("City",          value=profile.get("arch_city",""),         key="a_city")
            a_state   = st.text_input("State",         value=profile.get("arch_state",""),        key="a_state")
            a_zip     = st.text_input("Zip Code",      value=profile.get("arch_zip",""),          key="a_zip")
            a_phone   = st.text_input("Phone",         value=profile.get("arch_phone",""),        key="a_phone")
        with c2:
            a_email   = st.text_input("Email",         value=profile.get("arch_email",""),        key="a_email")
            a_first   = st.text_input("First Name",    value=profile.get("arch_first_name",""),   key="a_first")
            a_last    = st.text_input("Last Name",     value=profile.get("arch_last_name",""),    key="a_last")
            a_license = st.text_input("License No",    value=profile.get("arch_license",""),      key="a_license")
            a_role    = st.selectbox("Role", ["PE","RA"],
                                     index=0 if profile.get("arch_role","PE")=="PE" else 1, key="a_role")

    with st.expander("⚡  Electrical Contractor"):
        c1, c2 = st.columns(2)
        with c1:
            e_name    = st.text_input("Company Name", value=profile.get("elec_name",""),          key="e_name")
            e_addr    = st.text_input("Address",       value=profile.get("elec_address",""),       key="e_addr")
            e_city    = st.text_input("City",          value=profile.get("elec_city",""),          key="e_city")
            e_state   = st.text_input("State",         value=profile.get("elec_state",""),         key="e_state")
            e_zip     = st.text_input("Zip Code",      value=profile.get("elec_zip",""),           key="e_zip")
            e_phone   = st.text_input("Phone",         value=profile.get("elec_phone",""),         key="e_phone")
        with c2:
            e_email   = st.text_input("Email",         value=profile.get("elec_email",""),         key="e_email")
            e_first   = st.text_input("First Name",    value=profile.get("elec_first_name",""),    key="e_first")
            e_last    = st.text_input("Last Name",     value=profile.get("elec_last_name",""),     key="e_last")
            e_license = st.text_input("License No",    value=profile.get("elec_license",""),       key="e_license")
            e_exp     = st.text_input("Expiration",    value=profile.get("elec_expiration",""),    key="e_exp")

    c1, c2 = st.columns(2)
    with c1:
        with st.expander("🛠️  Technical Defaults"):
            t_man   = st.text_input("Default Manufacturer",   value=profile.get("tech_manufacturer",""), key="t_man")
            t_appr  = st.text_input("BSA/MEA/COA Approval",   value=profile.get("tech_approval",""),     key="t_appr")
            t_gauge = st.text_input("Wire Gauge",              value=profile.get("tech_wire_gauge",""),   key="t_gauge")
            t_wire  = st.text_input("Wire Type",               value=profile.get("tech_wire_type",""),    key="t_wire")
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
            "company_name": c_name,    "company_address": c_addr,    "company_city": c_city,
            "company_state": c_state,  "company_zip": c_zip,         "company_phone": c_phone,
            "company_email": c_email,  "company_first_name": c_first, "company_last_name": c_last,
            "company_reg_no": c_reg,   "company_cof_s97": c_cof,     "company_expiration": c_exp,
            "arch_name": a_name,       "arch_address": a_addr,       "arch_city": a_city,
            "arch_state": a_state,     "arch_zip": a_zip,            "arch_phone": a_phone,
            "arch_email": a_email,     "arch_first_name": a_first,   "arch_last_name": a_last,
            "arch_license": a_license, "arch_role": a_role,
            "elec_name": e_name,       "elec_address": e_addr,       "elec_city": e_city,
            "elec_state": e_state,     "elec_zip": e_zip,            "elec_phone": e_phone,
            "elec_email": e_email,     "elec_first_name": e_first,   "elec_last_name": e_last,
            "elec_license": e_license, "elec_expiration": e_exp,
            "tech_manufacturer": t_man, "tech_approval": t_appr,
            "tech_wire_gauge": t_gauge, "tech_wire_type": t_wire,
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
