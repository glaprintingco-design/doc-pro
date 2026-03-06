import streamlit as st
from supabase import create_client, Client
import main
import os
import zipfile
from io import BytesIO

# ── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Fire Form Pro", layout="wide", page_icon="🔥", initial_sidebar_state="expanded")

main.API_KEY_NYC       = st.secrets.get("NYC_API_KEY", "")
main.APP_TOKEN_SOCRATA = st.secrets.get("SOCRATA_TOKEN", "")
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "https://uhhiqkymipbcepqzwtvg.supabase.co")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "sb_publishable_mvqOWXc5s4b3_IMe4gGexw_sU3B2DRL")

# ── THEME STATE ────────────────────────────────────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

DARK = st.session_state.dark_mode

# ── THEME TOKENS ──────────────────────────────────────────────────────────────
if DARK:
    T = {
        "bg":           "#0f1623",
        "bg2":          "#151e2e",
        "surface":      "#1a2540",
        "surface2":     "#1f2d4a",
        "surface3":     "#243354",
        "border":       "#2a3a5c",
        "border2":      "#344670",
        "text":         "#e8edf8",
        "text2":        "#9aaac8",
        "text3":        "#5a6a8a",
        "input_bg":     "#111929",
        "input_border": "#2a3a5c",
        "table_bg":     "#1a2540",
        "table_header": "#1f2d4a",
        "table_row":    "#1a2540",
        "table_text":   "#e8edf8",
        "scrollbar":    "#2a3a5c",
        "orange":       "#ff6b35",
        "orange_dk":    "#e55a28",
        "orange_bg":    "rgba(255,107,53,0.12)",
        "orange_glow":  "rgba(255,107,53,0.25)",
        "success_bg":   "rgba(52,211,153,0.1)",
        "success_bd":   "rgba(52,211,153,0.3)",
        "success_text": "#34d399",
        "error_bg":     "rgba(239,68,68,0.1)",
        "error_bd":     "rgba(239,68,68,0.3)",
        "warning_bg":   "rgba(251,191,36,0.1)",
        "warning_bd":   "rgba(251,191,36,0.3)",
        "info_bg":      "rgba(255,107,53,0.08)",
        "info_bd":      "rgba(255,107,53,0.2)",
        "sidebar_bg":   "#0d1422",
        "sidebar_bd":   "#1e2d47",
        "cb_bg":        "#111929",
        "cb_border":    "#344670",
    }
else:
    T = {
        "bg":           "#f0f4f8",
        "bg2":          "#e8eef5",
        "surface":      "#ffffff",
        "surface2":     "#f5f8fc",
        "surface3":     "#edf2f7",
        "border":       "#d0dae8",
        "border2":      "#b8c8dc",
        "text":         "#1a2540",
        "text2":        "#3a5070",
        "text3":        "#7a90b0",
        "input_bg":     "#ffffff",
        "input_border": "#c8d8e8",
        "table_bg":     "#ffffff",
        "table_header": "#f0f5fa",
        "table_row":    "#ffffff",
        "table_text":   "#1a2540",
        "scrollbar":    "#c8d8e8",
        "orange":       "#ff6b35",
        "orange_dk":    "#e55a28",
        "orange_bg":    "rgba(255,107,53,0.08)",
        "orange_glow":  "rgba(255,107,53,0.2)",
        "success_bg":   "rgba(22,163,74,0.08)",
        "success_bd":   "rgba(22,163,74,0.25)",
        "success_text": "#16a34a",
        "error_bg":     "rgba(220,38,38,0.08)",
        "error_bd":     "rgba(220,38,38,0.25)",
        "warning_bg":   "rgba(202,138,4,0.08)",
        "warning_bd":   "rgba(202,138,4,0.25)",
        "info_bg":      "rgba(255,107,53,0.06)",
        "info_bd":      "rgba(255,107,53,0.18)",
        "sidebar_bg":   "#ffffff",
        "sidebar_bd":   "#d0dae8",
        "cb_bg":        "#ffffff",
        "cb_border":    "#b8c8dc",
    }

# ── INJECT CSS ────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── GLOBAL ── */
html, body, [data-testid="stAppViewContainer"],
[data-testid="stMain"], .main {{
    background: {T['bg']} !important;
    color: {T['text']} !important;
    font-family: 'Inter', sans-serif !important;
}}
[data-testid="stHeader"] {{ display: none !important; }}
[data-testid="stDecoration"] {{ display: none !important; }}

/* Always show sidebar collapse/expand toggle */
[data-testid="stSidebarCollapseButton"] {{
    display: flex !important;
    background: {T["orange"]} !important;
    border-radius: 50% !important;
    color: white !important;
    box-shadow: 0 2px 8px rgba(255,107,53,0.4) !important;
}}
[data-testid="stSidebarCollapseButton"]:hover {{
    transform: scale(1.1) !important;
}}

/* Sidebar nav arrow — always visible and styled */
button[data-testid="collapsedControl"] {{
    display: flex !important;
    background: {T["orange"]} !important;
    border-radius: 0 8px 8px 0 !important;
    color: white !important;
    width: 28px !important;
    box-shadow: 3px 0 12px rgba(255,107,53,0.35) !important;
}}

/* ── MAIN PADDING ── */
.main .block-container {{
    padding: 1.75rem 2rem 4rem !important;
    max-width: 1300px !important;
}}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {{
    background: {T['sidebar_bg']} !important;
    border-right: 1px solid {T['sidebar_bd']} !important;
}}
[data-testid="stSidebar"] * {{
    font-family: 'Inter', sans-serif !important;
    color: {T['text']} !important;
}}
[data-testid="stSidebar"] .stButton button {{
    background: {T['surface2']} !important;
    border: 1px solid {T['border']} !important;
    color: {T['text2']} !important;
    border-radius: 8px !important;
    font-size: 0.85rem !important;
    transition: all 0.15s !important;
}}
[data-testid="stSidebar"] .stButton button:hover {{
    border-color: {T['orange']} !important;
    color: {T['orange']} !important;
}}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {{
    background: {T['surface']} !important;
    border: 1px solid {T['border']} !important;
    border-radius: 10px !important;
    padding: 4px !important;
    gap: 3px !important;
    margin-bottom: 1.5rem !important;
}}
.stTabs [data-baseweb="tab"] {{
    background: transparent !important;
    border-radius: 7px !important;
    color: {T['text3']} !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    padding: 0.45rem 1.25rem !important;
    border: none !important;
    transition: all 0.15s !important;
}}
.stTabs [aria-selected="true"] {{
    background: {T['orange']} !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 10px {T['orange_glow']} !important;
}}
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] {{ display: none !important; }}

/* ── CARDS — no fake spacers ── */
.ffp-card {{
    background: {T['surface']} !important;
    border: 1px solid {T['border']} !important;
    border-radius: 12px !important;
    padding: 1.25rem 1.4rem !important;
    margin-bottom: 0.75rem !important;
}}

/* ── STEP HEADER ── */
.ffp-step {{
    display: flex; align-items: center; gap: 0.5rem;
    margin: 1.1rem 0 0.5rem 0;
}}
.ffp-step-num {{
    width: 26px; height: 26px; flex-shrink: 0;
    background: {T['orange']};
    border-radius: 8px;
    font-size: 0.78rem; font-weight: 700;
    display: flex; align-items: center; justify-content: center;
    color: #fff;
    box-shadow: 0 2px 8px {T['orange_glow']};
}}
.ffp-step-label {{
    font-size: 0.95rem; font-weight: 600;
    color: {T['text']};
}}
.ffp-step-opt {{
    font-size: 0.68rem; color: {T['text3']};
    background: {T['surface2']};
    border: 1px solid {T['border']};
    padding: 1px 7px; border-radius: 20px;
}}

/* ── INPUTS ── */
.stTextInput input, .stTextArea textarea,
.stSelectbox [data-baseweb="select"] > div,
.stNumberInput input {{
    background: {T['input_bg']} !important;
    border: 1px solid {T['input_border']} !important;
    border-radius: 8px !important;
    color: {T['text']} !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.88rem !important;
    transition: border-color 0.15s, box-shadow 0.15s !important;
}}
.stTextInput input:focus, .stTextArea textarea:focus {{
    border-color: {T['orange']} !important;
    box-shadow: 0 0 0 3px {T['orange_bg']} !important;
    outline: none !important;
}}
.stTextInput label, .stTextArea label,
.stSelectbox label, .stNumberInput label {{
    color: {T['text3']} !important;
    font-size: 0.75rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.03em !important;
    margin-bottom: 2px !important;
}}

/* Selectbox dropdown */
[data-baseweb="popover"],
[data-baseweb="popover"] > div {{
    background: {T['surface2']} !important;
    border: 1px solid {T['border2']} !important;
    border-radius: 10px !important;
    box-shadow: 0 8px 28px rgba(0,0,0,0.25) !important;
}}
[data-baseweb="menu"] li {{
    color: {T['text']} !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.88rem !important;
}}
[data-baseweb="menu"] li:hover {{
    background: {T['orange_bg']} !important;
}}

/* ── CHECKBOXES — fully readable ── */
.stCheckbox > label {{
    display: flex !important;
    align-items: center !important;
    gap: 0.5rem !important;
    padding: 0.55rem 0.75rem !important;
    border-radius: 8px !important;
    cursor: pointer !important;
    transition: background 0.12s !important;
    background: {T['surface2']} !important;
    border: 1px solid {T['border']} !important;
    margin-bottom: 6px !important;
}}
.stCheckbox > label:hover {{
    border-color: {T['orange']} !important;
    background: {T['orange_bg']} !important;
}}
.stCheckbox > label span[data-testid="stMarkdownContainer"] p,
.stCheckbox > label > div:last-child,
.stCheckbox > label > span {{
    color: {T['text']} !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
}}
/* The box itself */
.stCheckbox [data-baseweb="checkbox"] div[role="checkbox"] {{
    background: {T['cb_bg']} !important;
    border: 2px solid {T['cb_border']} !important;
    border-radius: 5px !important;
    width: 18px !important; height: 18px !important;
    flex-shrink: 0 !important;
    transition: all 0.15s !important;
}}
.stCheckbox [aria-checked="true"] div[role="checkbox"] {{
    background: {T['orange']} !important;
    border-color: {T['orange']} !important;
    box-shadow: 0 2px 8px {T['orange_glow']} !important;
}}

/* ── BUTTONS ── */
.stButton button {{
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    transition: all 0.15s !important;
    font-size: 0.88rem !important;
}}
.stButton button[kind="primary"] {{
    background: {T['orange']} !important;
    border: none !important;
    color: #fff !important;
    box-shadow: 0 3px 12px {T['orange_glow']} !important;
    padding: 0.55rem 1.25rem !important;
}}
.stButton button[kind="primary"]:hover {{
    background: {T['orange_dk']} !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 5px 18px {T['orange_glow']} !important;
}}
.stButton button:not([kind="primary"]) {{
    background: {T['surface2']} !important;
    border: 1px solid {T['border2']} !important;
    color: {T['text2']} !important;
}}
.stButton button:not([kind="primary"]):hover {{
    border-color: {T['orange']} !important;
    color: {T['orange']} !important;
    background: {T['orange_bg']} !important;
}}

/* ── DATA EDITOR — dark-themed table ── */
[data-testid="stDataEditor"] {{
    border: 1px solid {T['border']} !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}}
[data-testid="stDataEditor"] [role="grid"] {{
    background: {T['table_bg']} !important;
}}
[data-testid="stDataEditor"] [role="columnheader"] {{
    background: {T['table_header']} !important;
    color: {T['text2']} !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
    border-bottom: 1px solid {T['border']} !important;
    border-right: 1px solid {T['border']} !important;
}}
[data-testid="stDataEditor"] [role="gridcell"] {{
    background: {T['table_row']} !important;
    color: {T['table_text']} !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.88rem !important;
    border-bottom: 1px solid {T['border']} !important;
    border-right: 1px solid {T['border']} !important;
}}
/* Remove the "fake empty row" bottom spacer */
[data-testid="stDataEditor"] [role="gridcell"]:empty {{
    background: {T['table_header']} !important;
}}

/* ── ALERTS ── */
[data-testid="stNotification"],
.stSuccess, .stError, .stWarning, .stInfo {{
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.87rem !important;
}}
.stSuccess  {{ background: {T['success_bg']} !important; border: 1px solid {T['success_bd']} !important; color: {T['success_text']} !important; }}
.stError    {{ background: {T['error_bg']}   !important; border: 1px solid {T['error_bd']}   !important; }}
.stWarning  {{ background: {T['warning_bg']} !important; border: 1px solid {T['warning_bd']} !important; }}
.stInfo     {{ background: {T['info_bg']}    !important; border: 1px solid {T['info_bd']}    !important; color: {T['text2']} !important; }}

/* ── DOWNLOAD BUTTON ── */
.stDownloadButton button {{
    background: {T['surface2']} !important;
    border: 1px solid {T['border2']} !important;
    color: {T['text2']} !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important; border-radius: 8px !important; width: 100% !important;
}}
.stDownloadButton button:hover {{
    border-color: {T['orange']} !important;
    color: {T['orange']} !important;
    background: {T['orange_bg']} !important;
}}

/* ── EXPANDERS ── */
.streamlit-expanderHeader {{
    background: {T['surface']} !important;
    border: 1px solid {T['border']} !important;
    border-radius: 10px !important;
    color: {T['text']} !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
}}
.streamlit-expanderHeader:hover {{ border-color: {T['border2']} !important; }}
.streamlit-expanderContent {{
    background: {T['surface2']} !important;
    border: 1px solid {T['border']} !important;
    border-top: none !important;
    border-radius: 0 0 10px 10px !important;
    padding: 1.25rem !important;
}}

/* ── TOPBAR ── */
.ffp-topbar {{
    display: flex; align-items: center;
    justify-content: space-between;
    gap: 1rem; margin-bottom: 1.5rem;
    padding-bottom: 1.1rem;
    border-bottom: 1px solid {T['border']};
}}
.ffp-topbar-left {{ display: flex; align-items: center; gap: 0.85rem; }}
.ffp-icon {{
    width: 42px; height: 42px; border-radius: 12px; flex-shrink: 0;
    background: linear-gradient(135deg, {T['orange']}, #ff9a60);
    display: flex; align-items: center; justify-content: center;
    font-size: 20px;
    box-shadow: 0 3px 12px {T['orange_glow']};
}}
.ffp-brand-name {{
    font-size: 1.3rem; font-weight: 700; color: {T['text']};
    line-height: 1.1; letter-spacing: -0.01em; margin: 0;
}}
.ffp-brand-sub {{
    font-size: 0.72rem; color: {T['text3']}; margin: 0; font-weight: 400;
}}
.ffp-theme-btn {{
    cursor: pointer;
    background: {T['surface2']};
    border: 1px solid {T['border']};
    border-radius: 20px;
    padding: 0.3rem 0.9rem;
    font-size: 0.78rem; font-weight: 500;
    color: {T['text2']};
    display: flex; align-items: center; gap: 0.4rem;
    transition: all 0.15s;
    white-space: nowrap;
}}

/* ── ACCOUNT CARD ── */
.ffp-account {{
    background: {T['surface2']};
    border: 1px solid {T['border']};
    border-radius: 10px; padding: 0.8rem; margin-bottom: 1rem;
}}
.ffp-account-label {{
    font-size: 0.68rem; color: {T['text3']};
    text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 3px;
}}
.ffp-account-email {{ color: {T['text2']}; font-weight: 500; font-size: 0.83rem; word-break: break-all; }}

/* ── MISC ── */
hr {{ border-color: {T['border']} !important; margin: 0.75rem 0 !important; }}
.stRadio label {{ color: {T['text2']} !important; font-size: 0.87rem !important; }}
.stSpinner > div {{ border-top-color: {T['orange']} !important; }}
p, span, li {{ color: {T['text']} !important; }}

/* ── DEVICE LIST EMPTY STATE ── */
.ffp-empty {{
    display: flex; flex-direction: column; align-items: center;
    justify-content: center; padding: 2.5rem 1rem; text-align: center; gap: 0.5rem;
}}
.ffp-empty-icon {{ font-size: 2rem; opacity: 0.2; }}
.ffp-empty-title {{
    font-size: 0.9rem; font-weight: 600; color: {T['text3']};
}}
.ffp-empty-sub {{
    font-size: 0.8rem; color: {T['text3']}; opacity: 0.65; max-width: 200px; line-height: 1.5;
}}

/* ── STAT ROW ── */
.ffp-stat-row {{
    display: flex; justify-content: space-between; align-items: center;
    padding: 0.6rem 0; border-top: 1px solid {T['border']};
    font-size: 0.8rem; color: {T['text3']};
}}
</style>
""", unsafe_allow_html=True)

# ── SUPABASE ───────────────────────────────────────────────────────────────────
if "supabase" not in st.session_state:
    try:
        st.session_state.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Failed to connect to Supabase: {e}"); st.stop()

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
    try: supabase.auth.sign_out()
    except Exception: pass
    st.session_state.user = None
    st.session_state.device_list = []
    st.rerun()

def fetch_user_profile(user_id):
    try:
        r = supabase.table("profiles").select("*").eq("id", user_id).execute()
        return r.data[0] if r.data else {}
    except Exception as e:
        st.error(f"Error loading profile: {e}"); return {}

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
        "Company Name": p.get("cs_name",""), "CS Code":  p.get("cs_code",""),
        "Address":      p.get("cs_address",""), "City":  p.get("cs_city",""),
        "State":        p.get("cs_state",""),   "Zip":   p.get("cs_zip",""),
        "Phone":        p.get("cs_phone",""),
    })


# ── LOGIN UI ──────────────────────────────────────────────────────────────────
def login_ui():
    with st.sidebar:
        st.markdown(f"""
            <div style='text-align:center;padding:1.5rem 0 2rem'>
                <div style='display:inline-flex;align-items:center;justify-content:center;
                    width:48px;height:48px;border-radius:14px;font-size:22px;
                    background:linear-gradient(135deg,{T['orange']},#ff9a60);
                    box-shadow:0 4px 14px {T['orange_glow']};margin-bottom:0.7rem;'>🔥</div>
                <div style='font-family:Inter,sans-serif;font-size:1.15rem;font-weight:700;
                    color:{T['text']};'>Fire Form Pro</div>
                <div style='font-size:0.7rem;color:{T['text3']};margin-top:2px;'>
                    NYC Fire Alarm Automation</div>
            </div>
        """, unsafe_allow_html=True)
        choice   = st.radio("", ["Login", "Sign Up"], horizontal=True)
        email    = st.text_input("Email Address")
        password = st.text_input("Password", type="password")
        if choice == "Login":
            if st.button("Sign In", use_container_width=True, type="primary"):
                if not email or not password: st.error("Please enter email and password."); return
                with st.spinner("Signing in…"):
                    try:
                        r = supabase.auth.sign_in_with_password({"email": email.strip(), "password": password})
                        if r.user: st.session_state.user = r.user; st.rerun()
                        else: st.error("Login failed.")
                    except Exception as e:
                        msg = str(e)
                        if "Invalid login credentials" in msg: st.error("Invalid email or password.")
                        elif "Email not confirmed" in msg: st.warning("Please confirm your email first.")
                        elif "rate limit" in msg.lower(): st.warning("Too many attempts — please wait.")
                        else: st.error(msg)
        else:
            if st.button("Create Account", use_container_width=True, type="primary"):
                if not email or not password: st.error("Please enter email and password."); return
                if len(password) < 6: st.error("Password must be at least 6 characters."); return
                with st.spinner("Creating account…"):
                    try:
                        r = supabase.auth.sign_up({"email": email.strip(), "password": password})
                        if r.user:
                            st.success("Account created! Check your email to confirm.")
                            try: supabase.table("profiles").insert({"id": r.user.id, "email": email}).execute()
                            except Exception: pass
                        else: st.error("Sign-up returned no user.")
                    except Exception as e:
                        msg = str(e)
                        if "already registered" in msg.lower(): st.warning("Email already registered — use Login.")
                        else: st.error(msg)


# ── ACCESS GATE ───────────────────────────────────────────────────────────────
if not st.session_state.user:
    login_ui()
    st.markdown(f"""
        <div style='display:flex;flex-direction:column;align-items:center;justify-content:center;
            height:70vh;text-align:center;gap:1rem;'>
            <div style='display:inline-flex;align-items:center;justify-content:center;
                width:60px;height:60px;border-radius:16px;font-size:26px;
                background:linear-gradient(135deg,{T['orange']},#ff9a60);
                box-shadow:0 5px 20px {T['orange_glow']};'>🔥</div>
            <div style='font-family:Inter,sans-serif;font-size:1.8rem;font-weight:700;
                color:{T['text']};letter-spacing:-0.02em;'>Fire Form Pro</div>
            <div style='color:{T['text3']};font-size:0.9rem;line-height:1.7;max-width:300px;'>
                Automated FDNY form generation<br>for NYC Fire Alarm professionals.
            </div>
            <div style='color:{T['orange']};font-size:0.82rem;font-weight:500;
                background:{T['orange_bg']};border:1px solid {T['border2']};
                padding:0.4rem 1rem;border-radius:20px;'>
                ← Open the sidebar to sign in
            </div>
        </div>
    """, unsafe_allow_html=True)
    # Visible fallback: show login form inline if sidebar may be collapsed
    st.markdown(f"""
        <div style='max-width:360px;margin:0 auto 2rem auto;
            background:{T['surface']};border:1px solid {T['border']};
            border-radius:14px;padding:1.75rem;'>
            <div style='font-size:0.95rem;font-weight:600;color:{T['text']};
                margin-bottom:1.25rem;text-align:center;'>Sign in to your account</div>
    """, unsafe_allow_html=True)
    with st.container():
        login_email    = st.text_input("Email", key="main_email", placeholder="you@example.com")
        login_password = st.text_input("Password", type="password", key="main_pass")
        col_a, col_b   = st.columns(2)
        with col_a:
            if st.button("Sign In", use_container_width=True, type="primary", key="main_signin"):
                if login_email and login_password:
                    with st.spinner("Signing in…"):
                        try:
                            r = supabase.auth.sign_in_with_password({
                                "email": login_email.strip(), "password": login_password})
                            if r.user:
                                st.session_state.user = r.user; st.rerun()
                            else: st.error("Login failed.")
                        except Exception as e:
                            msg = str(e)
                            if "Invalid login credentials" in msg: st.error("Invalid email or password.")
                            elif "Email not confirmed" in msg:     st.warning("Please confirm your email.")
                            else: st.error(msg)
                else: st.error("Please enter email and password.")
        with col_b:
            if st.button("Sign Up", use_container_width=True, key="main_signup"):
                if login_email and login_password:
                    if len(login_password) < 6:
                        st.error("Password must be ≥ 6 characters.")
                    else:
                        with st.spinner("Creating account…"):
                            try:
                                r = supabase.auth.sign_up({
                                    "email": login_email.strip(), "password": login_password})
                                if r.user:
                                    st.success("Account created! Check your email to confirm.")
                                    try: supabase.table("profiles").insert({"id": r.user.id, "email": login_email}).execute()
                                    except Exception: pass
                                else: st.error("Sign-up returned no user.")
                            except Exception as e:
                                msg = str(e)
                                if "already registered" in msg.lower(): st.warning("Email already registered.")
                                else: st.error(msg)
                else: st.error("Please enter email and password.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()


# ── MAIN APP ──────────────────────────────────────────────────────────────────
profile = fetch_user_profile(st.session_state.user.id)

# Sidebar
with st.sidebar:
    st.markdown(f"""
        <div style='text-align:center;padding:1rem 0 1.25rem'>
            <div style='display:inline-flex;align-items:center;justify-content:center;
                width:38px;height:38px;border-radius:10px;font-size:17px;
                background:linear-gradient(135deg,{T['orange']},#ff9a60);
                box-shadow:0 3px 10px {T['orange_glow']};margin-bottom:0.5rem;'>🔥</div>
            <div style='font-family:Inter,sans-serif;font-size:1rem;font-weight:700;
                color:{T['text']};'>Fire Form Pro</div>
        </div>
        <div class='ffp-account'>
            <div class='ffp-account-label'>Logged in as</div>
            <div class='ffp-account-email'>{st.session_state.user.email}</div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Sign Out", use_container_width=True):
        logout()
    # Theme toggle
    st.markdown("<div style='margin-top:1rem'>", unsafe_allow_html=True)
    theme_label = "☀️  Switch to Light Mode" if DARK else "🌙  Switch to Dark Mode"
    if st.button(theme_label, use_container_width=True):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# Topbar
st.markdown(f"""
    <div class='ffp-topbar'>
        <div class='ffp-topbar-left'>
            <div class='ffp-icon'>🔥</div>
            <div>
                <div class='ffp-brand-name'>Fire Form Pro</div>
                <div class='ffp-brand-sub'>NYC Fire Alarm Automation Platform</div>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

tabs = st.tabs(["🚀  Project Builder", "👤  Professional Profile"])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 0 — PROJECT BUILDER
# Desktop: 2-column layout  |  Mobile: natural single-column stacking
# Column order on mobile: 1→2→3→4→5 (correct UX flow)
# ══════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    left, right = st.columns([5, 7], gap="large")

    # ── LEFT COLUMN ───────────────────────────────────────────
    with left:

        # 1 — Project Information
        st.markdown(f"""<div class='ffp-step'>
            <div class='ffp-step-num'>1</div>
            <div class='ffp-step-label'>Project Information</div>
        </div>""", unsafe_allow_html=True)
        with st.container():
            bin_number = st.text_input("Property BIN", placeholder="e.g. 1012345")
            job_desc   = st.text_area("TM-1 Job Description",
                                      value="Installation of Fire Alarm System.", height=80)

        # 2 — Add Devices
        st.markdown(f"""<div class='ffp-step'>
            <div class='ffp-step-num'>2</div>
            <div class='ffp-step-label'>Add Devices to A-433</div>
            <div class='ffp-step-opt'>optional</div>
        </div>""", unsafe_allow_html=True)
        with st.container():
            floor    = st.selectbox("Floor Location", main.FULL_FLOOR_LIST)
            _c1, _c2 = st.columns([2, 1])
            with _c1:
                category = st.selectbox("Category", list(main.MASTER_DEVICE_LIST.keys()))
            with _c2:
                qty = st.number_input("Qty", min_value=1, value=1)
            device = st.selectbox("Device Type", main.MASTER_DEVICE_LIST.get(category, []))
            if st.button("➕  Add Device", use_container_width=True):
                st.session_state.device_list.append({"device": device, "floor": floor, "qty": qty})
                st.success(f"Added: {qty}× {device} — {floor}")

        # 4 — Select Forms
        st.markdown(f"""<div class='ffp-step'>
            <div class='ffp-step-num'>4</div>
            <div class='ffp-step-label'>Select Forms to Generate</div>
        </div>""", unsafe_allow_html=True)
        with st.container():
            _fa, _fb = st.columns(2)
            with _fa:
                gen_tm1    = st.checkbox("TM-1 Application",        value=True, key="chk_gen_tm1")
                gen_a433   = st.checkbox("A-433 Device List",       value=True, key="chk_gen_a433")
            with _fb:
                gen_b45    = st.checkbox("B-45 Inspection Request", value=True, key="chk_gen_b45")
                gen_report = st.checkbox("Audit Report",            value=True, key="chk_gen_report")

        # 5 — Generate
        st.markdown("<div style='margin-top:1rem'>", unsafe_allow_html=True)
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
                                    if os.path.exists(fn): zf.write(fn); os.remove(fn)
                            st.success(f"✅ {len(files)} document(s) ready.")
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

    # ── RIGHT COLUMN — A-433 Device List ──────────────────────
    with right:
        st.markdown(f"""<div class='ffp-step' style='margin-top:0'>
            <div class='ffp-step-num'>3</div>
            <div class='ffp-step-label'>A-433 Device List</div>
        </div>""", unsafe_allow_html=True)

        if st.session_state.device_list:
            edited = st.data_editor(
                st.session_state.device_list,
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    "qty":    st.column_config.NumberColumn("Qty", min_value=1,
                                                            max_value=999, step=1, required=True),
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
                <div class='ffp-stat-row'>
                    <span>{len(st.session_state.device_list)} line(s)</span>
                    <span>{total} total devices</span>
                </div>
            """, unsafe_allow_html=True)
            if st.button("🗑️  Clear List", use_container_width=True):
                st.session_state.device_list = []
                st.rerun()
        else:
            st.markdown(f"""
                <div style='background:{T['surface']};border:1px solid {T['border']};
                    border-radius:12px;'>
                    <div class='ffp-empty'>
                        <div class='ffp-empty-icon'>📋</div>
                        <div class='ffp-empty-title'>No devices added yet</div>
                        <div class='ffp-empty-sub'>
                            Use Step 2 on the left to add devices to your A-433 form.
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — PROFESSIONAL PROFILE
# ══════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown(f"""
        <p style='color:{T['text3']};font-size:0.85rem;margin-bottom:1.25rem;line-height:1.6;'>
        Your professional data is saved securely and auto-populates all FDNY form fields.
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
            a_name    = st.text_input("Company Name", value=profile.get("arch_name",""),          key="a_name")
            a_addr    = st.text_input("Address",       value=profile.get("arch_address",""),       key="a_addr")
            a_city    = st.text_input("City",          value=profile.get("arch_city",""),          key="a_city")
            a_state   = st.text_input("State",         value=profile.get("arch_state",""),         key="a_state")
            a_zip     = st.text_input("Zip Code",      value=profile.get("arch_zip",""),           key="a_zip")
            a_phone   = st.text_input("Phone",         value=profile.get("arch_phone",""),         key="a_phone")
        with c2:
            a_email   = st.text_input("Email",         value=profile.get("arch_email",""),         key="a_email")
            a_first   = st.text_input("First Name",    value=profile.get("arch_first_name",""),    key="a_first")
            a_last    = st.text_input("Last Name",     value=profile.get("arch_last_name",""),     key="a_last")
            a_license = st.text_input("License No",    value=profile.get("arch_license",""),       key="a_license")
            a_role    = st.selectbox("Role", ["PE","RA"],
                                     index=0 if profile.get("arch_role","PE")=="PE" else 1, key="a_role")

    with st.expander("⚡  Electrical Contractor"):
        c1, c2 = st.columns(2)
        with c1:
            e_name    = st.text_input("Company Name", value=profile.get("elec_name",""),           key="e_name")
            e_addr    = st.text_input("Address",       value=profile.get("elec_address",""),        key="e_addr")
            e_city    = st.text_input("City",          value=profile.get("elec_city",""),           key="e_city")
            e_state   = st.text_input("State",         value=profile.get("elec_state",""),          key="e_state")
            e_zip     = st.text_input("Zip Code",      value=profile.get("elec_zip",""),            key="e_zip")
            e_phone   = st.text_input("Phone",         value=profile.get("elec_phone",""),          key="e_phone")
        with c2:
            e_email   = st.text_input("Email",         value=profile.get("elec_email",""),          key="e_email")
            e_first   = st.text_input("First Name",    value=profile.get("elec_first_name",""),     key="e_first")
            e_last    = st.text_input("Last Name",     value=profile.get("elec_last_name",""),      key="e_last")
            e_license = st.text_input("License No",    value=profile.get("elec_license",""),        key="e_license")
            e_exp     = st.text_input("Expiration",    value=profile.get("elec_expiration",""),     key="e_exp")

    c1, c2 = st.columns(2)
    with c1:
        with st.expander("🛠️  Technical Defaults"):
            t_man   = st.text_input("Default Manufacturer",    value=profile.get("tech_manufacturer",""), key="t_man")
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
