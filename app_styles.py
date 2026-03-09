"""
Fire Form Pro - Modern UI Styles
Inject this CSS into your Streamlit app via st.markdown(get_styles(), unsafe_allow_html=True)
"""

def get_styles():
    return """
<style>
/* ============================================================
   FIRE FORM PRO - PROFESSIONAL DARK UI
   Palette: Deep charcoal + Flame orange + Clean white
   ============================================================ */

@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* === ROOT VARIABLES === */
:root {
    --bg-primary:    #0F1117;
    --bg-secondary:  #16181F;
    --bg-card:       #1C1F2A;
    --bg-card-hover: #222535;
    --border:        #2A2D3E;
    --border-light:  #353849;
    --orange-500:    #F97316;
    --orange-400:    #FB923C;
    --orange-600:    #EA580C;
    --orange-glow:   rgba(249, 115, 22, 0.15);
    --orange-glow2:  rgba(249, 115, 22, 0.08);
    --text-primary:  #F1F3F9;
    --text-secondary:#9BA3BF;
    --text-muted:    #5C6380;
    --success:       #22C55E;
    --warning:       #EAB308;
    --error:         #EF4444;
    --radius-sm:     6px;
    --radius-md:     10px;
    --radius-lg:     14px;
    --radius-xl:     20px;
    --shadow-card:   0 2px 8px rgba(0,0,0,0.35), 0 0 0 1px var(--border);
    --shadow-orange: 0 0 20px rgba(249, 115, 22, 0.25);
    --font-main:     'Plus Jakarta Sans', sans-serif;
    --font-mono:     'JetBrains Mono', monospace;
    --transition:    all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

/* === GLOBAL RESET === */
* { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: var(--font-main) !important;
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

/* === HIDE STREAMLIT CHROME === */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
.stDeployButton { display: none !important; }

/* === MAIN LAYOUT === */
.main .block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* === SIDEBAR === */
[data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border) !important;
    padding-top: 0 !important;
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 0 !important;
}

[data-testid="stSidebar"] .stImage {
    padding: 1.5rem 1.5rem 1rem;
}

[data-testid="stSidebar"] hr {
    border-color: var(--border) !important;
    margin: 0.75rem 0 !important;
}

[data-testid="stSidebar"] .stMarkdown p {
    color: var(--text-secondary) !important;
    font-size: 13px !important;
}

[data-testid="stSidebar"] .stAlert {
    background: var(--orange-glow2) !important;
    border: 1px solid var(--border-light) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-primary) !important;
    font-size: 13px !important;
}

/* Sidebar version info */
[data-testid="stSidebar"] .stCaption {
    color: var(--text-muted) !important;
    font-size: 11px !important;
    font-family: var(--font-mono) !important;
}

/* === HEADER BAR === */
.ffp-header {
    background: linear-gradient(135deg, #1A0A00 0%, #2D1200 40%, #1C1510 100%);
    border-bottom: 1px solid var(--border);
    padding: 1.25rem 2.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: relative;
    overflow: hidden;
}

.ffp-header::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, var(--orange-500), var(--orange-400), transparent);
}

.ffp-header::after {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(249,115,22,0.12) 0%, transparent 70%);
    pointer-events: none;
}

.ffp-brand {
    display: flex;
    flex-direction: column;
    gap: 2px;
}

.ffp-tagline {
    font-size: 12px;
    color: var(--text-muted);
    letter-spacing: 0.5px;
    font-weight: 400;
    margin-top: 4px;
}

.ffp-user-badge {
    display: flex;
    align-items: center;
    gap: 10px;
    background: var(--bg-card);
    border: 1px solid var(--border-light);
    border-radius: 50px;
    padding: 6px 14px 6px 8px;
}

.ffp-user-avatar {
    width: 30px; height: 30px;
    background: linear-gradient(135deg, var(--orange-500), var(--orange-600));
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 12px; font-weight: 700; color: white;
}

.ffp-user-email {
    font-size: 13px;
    color: var(--text-secondary);
    font-weight: 500;
}

/* === CONTENT WRAPPER === */
.ffp-content {
    padding: 2rem 2.5rem;
    background: var(--bg-primary);
}

/* === SECTION HEADERS === */
.ffp-section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 1.25rem;
    margin-top: 0.5rem;
}

.ffp-section-badge {
    background: var(--orange-glow);
    border: 1px solid rgba(249, 115, 22, 0.3);
    color: var(--orange-400);
    font-size: 11px;
    font-weight: 700;
    font-family: var(--font-mono);
    padding: 3px 10px;
    border-radius: 50px;
    letter-spacing: 1px;
    text-transform: uppercase;
}

.ffp-section-title {
    font-size: 16px;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.2px;
}

/* === CARDS === */
.ffp-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    transition: var(--transition);
}

.ffp-card:hover {
    border-color: var(--border-light);
    box-shadow: var(--shadow-card);
}

/* === STREAMLIT INPUTS (override) === */
[data-testid="stTextInput"] > div > div,
[data-testid="stTextArea"] > div > div,
[data-testid="stNumberInput"] > div > div,
[data-testid="stSelectbox"] > div > div {
    background: #12141C !important;
    border: 1px solid var(--border-light) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-primary) !important;
    font-family: var(--font-main) !important;
    font-size: 14px !important;
    transition: var(--transition) !important;
}

[data-testid="stTextInput"] > div > div:focus-within,
[data-testid="stTextArea"] > div > div:focus-within,
[data-testid="stSelectbox"] > div > div:focus-within {
    border-color: var(--orange-500) !important;
    box-shadow: 0 0 0 3px var(--orange-glow) !important;
}

/* Input labels */
[data-testid="stTextInput"] label,
[data-testid="stTextArea"] label,
[data-testid="stSelectbox"] label,
[data-testid="stNumberInput"] label {
    color: var(--text-secondary) !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    letter-spacing: 0.4px !important;
    text-transform: uppercase !important;
    margin-bottom: 4px !important;
}

/* Placeholder text */
input::placeholder, textarea::placeholder {
    color: var(--text-muted) !important;
}

/* Input text color */
input, textarea, select {
    color: var(--text-primary) !important;
    background: transparent !important;
}

/* === BUTTONS === */
/* Primary button */
.stButton > button[kind="primary"],
button[data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, var(--orange-500) 0%, var(--orange-600) 100%) !important;
    border: none !important;
    border-radius: var(--radius-md) !important;
    color: white !important;
    font-family: var(--font-main) !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    letter-spacing: 0.3px !important;
    padding: 0.6rem 1.5rem !important;
    box-shadow: 0 4px 12px rgba(249, 115, 22, 0.3) !important;
    transition: var(--transition) !important;
    position: relative;
    overflow: hidden;
}

.stButton > button[kind="primary"]:hover,
button[data-testid="baseButton-primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(249, 115, 22, 0.45) !important;
    filter: brightness(1.05) !important;
}

.stButton > button[kind="primary"]:active {
    transform: translateY(0) !important;
}

/* Secondary button */
.stButton > button[kind="secondary"],
button[data-testid="baseButton-secondary"] {
    background: transparent !important;
    border: 1px solid var(--border-light) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-secondary) !important;
    font-family: var(--font-main) !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    transition: var(--transition) !important;
}

.stButton > button[kind="secondary"]:hover {
    background: var(--bg-card) !important;
    border-color: var(--orange-500) !important;
    color: var(--orange-400) !important;
}

/* Download button */
.stDownloadButton > button {
    background: linear-gradient(135deg, var(--orange-500), var(--orange-600)) !important;
    border: none !important;
    border-radius: var(--radius-md) !important;
    color: white !important;
    font-family: var(--font-main) !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    box-shadow: 0 4px 12px rgba(249, 115, 22, 0.3) !important;
    transition: var(--transition) !important;
}

.stDownloadButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 24px rgba(249, 115, 22, 0.5) !important;
}

/* === TABS === */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-secondary) !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 0 !important;
    padding: 0 1rem !important;
}

.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important;
    color: var(--text-muted) !important;
    font-family: var(--font-main) !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    padding: 1rem 1.5rem !important;
    transition: var(--transition) !important;
    letter-spacing: 0.2px !important;
}

.stTabs [data-baseweb="tab"]:hover {
    color: var(--text-primary) !important;
    background: var(--orange-glow2) !important;
}

.stTabs [aria-selected="true"] {
    color: var(--orange-400) !important;
    border-bottom-color: var(--orange-500) !important;
    background: var(--orange-glow2) !important;
}

.stTabs [data-baseweb="tab-panel"] {
    padding: 2rem !important;
    background: var(--bg-primary) !important;
}

/* === EXPANDERS === */
[data-testid="stExpander"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-lg) !important;
    margin-bottom: 1rem !important;
    overflow: hidden !important;
}

[data-testid="stExpander"] > div:first-child {
    background: var(--bg-card) !important;
    border-bottom: 1px solid var(--border) !important;
    padding: 1rem 1.25rem !important;
}

[data-testid="stExpander"] summary {
    font-family: var(--font-main) !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    color: var(--text-primary) !important;
}

[data-testid="stExpander"] summary:hover {
    color: var(--orange-400) !important;
}

/* Expander content padding */
[data-testid="stExpander"] [data-testid="stVerticalBlock"] {
    padding: 1.25rem !important;
}

/* === DIVIDERS === */
hr {
    border-color: var(--border) !important;
    margin: 1.5rem 0 !important;
}

/* === ALERTS & MESSAGES === */
.stAlert {
    border-radius: var(--radius-md) !important;
    border: 1px solid !important;
    font-size: 13px !important;
    font-family: var(--font-main) !important;
}

/* Success */
[data-testid="stAlert"][data-baseweb="notification"][kind="positive"],
div[data-stale="false"] .element-container .stAlert.st-ae {
    background: rgba(34, 197, 94, 0.08) !important;
    border-color: rgba(34, 197, 94, 0.3) !important;
    color: #86EFAC !important;
}

/* Error */
[data-baseweb="notification"][kind="negative"] {
    background: rgba(239, 68, 68, 0.08) !important;
    border-color: rgba(239, 68, 68, 0.3) !important;
    color: #FCA5A5 !important;
}

/* Info */
[data-baseweb="notification"][kind="info"] {
    background: var(--orange-glow2) !important;
    border-color: rgba(249, 115, 22, 0.25) !important;
    color: var(--text-secondary) !important;
}

/* Warning */
[data-baseweb="notification"][kind="warning"] {
    background: rgba(234, 179, 8, 0.08) !important;
    border-color: rgba(234, 179, 8, 0.3) !important;
    color: #FDE047 !important;
}

/* === DATA EDITOR / TABLE === */
[data-testid="stDataEditor"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-lg) !important;
    overflow: hidden !important;
}

.dvn-scroller {
    background: var(--bg-card) !important;
}

/* === CHECKBOXES === */
[data-testid="stCheckbox"] > label {
    color: var(--text-secondary) !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    gap: 8px !important;
}

[data-testid="stCheckbox"] > label span {
    background: var(--bg-card) !important;
    border: 1.5px solid var(--border-light) !important;
    border-radius: 4px !important;
}

/* === SPINNERS / PROGRESS === */
.stSpinner > div {
    border-color: var(--orange-500) !important;
    border-top-color: transparent !important;
}

/* === NUMBER INPUT === */
[data-testid="stNumberInput"] button {
    background: var(--bg-card) !important;
    border-color: var(--border-light) !important;
    color: var(--text-secondary) !important;
}

[data-testid="stNumberInput"] button:hover {
    background: var(--orange-glow) !important;
    color: var(--orange-400) !important;
}

/* === SUBHEADERS & HEADERS === */
h1, h2, h3 {
    color: var(--text-primary) !important;
    font-family: var(--font-main) !important;
    font-weight: 700 !important;
    letter-spacing: -0.5px !important;
}

.stMarkdown h3 {
    font-size: 16px !important;
    color: var(--text-primary) !important;
    border-bottom: 1px solid var(--border) !important;
    padding-bottom: 0.5rem !important;
    margin-bottom: 1rem !important;
}

/* === SUCCESS BANNER === */
.ffp-success-banner {
    background: linear-gradient(135deg, rgba(34,197,94,0.1), rgba(34,197,94,0.05));
    border: 1px solid rgba(34, 197, 94, 0.25);
    border-radius: var(--radius-lg);
    padding: 1rem 1.5rem;
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 1rem;
}

/* === STAT CARDS === */
.ffp-stat-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.25rem 1.5rem;
    position: relative;
    overflow: hidden;
    transition: var(--transition);
}

.ffp-stat-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    right: 0; height: 2px;
    background: linear-gradient(90deg, var(--orange-500), var(--orange-400));
    opacity: 0;
    transition: var(--transition);
}

.ffp-stat-card:hover::before { opacity: 1; }
.ffp-stat-card:hover { border-color: rgba(249,115,22,0.3); }

.ffp-stat-value {
    font-size: 28px;
    font-weight: 800;
    color: var(--orange-400);
    font-family: var(--font-mono);
    line-height: 1;
    margin-bottom: 4px;
}

.ffp-stat-label {
    font-size: 11px;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 600;
}

/* === DEVICE LIST EMPTY STATE === */
.ffp-empty-state {
    text-align: center;
    padding: 3rem 2rem;
    color: var(--text-muted);
    border: 1px dashed var(--border-light);
    border-radius: var(--radius-lg);
}

.ffp-empty-icon {
    font-size: 36px;
    margin-bottom: 0.75rem;
    opacity: 0.5;
}

.ffp-empty-text {
    font-size: 14px;
    font-weight: 500;
    color: var(--text-muted);
}

/* === GENERATE BUTTON SPECIAL === */
.ffp-generate-btn > .stButton > button {
    background: linear-gradient(135deg, #F97316 0%, #C2410C 100%) !important;
    border-radius: var(--radius-xl) !important;
    font-size: 15px !important;
    font-weight: 800 !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    padding: 0.85rem 2rem !important;
    box-shadow: 0 8px 24px rgba(249, 115, 22, 0.4), 0 0 0 1px rgba(249,115,22,0.2) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.ffp-generate-btn > .stButton > button:hover {
    transform: translateY(-2px) scale(1.01) !important;
    box-shadow: 0 14px 36px rgba(249, 115, 22, 0.55) !important;
}

/* === DOWNLOAD SECTION === */
.ffp-download-section {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-xl);
    padding: 1.5rem;
    margin-top: 1.5rem;
}

/* === SELECTBOX DROPDOWN === */
[data-baseweb="select"] [data-baseweb="popover"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-light) !important;
    border-radius: var(--radius-md) !important;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4) !important;
}

[data-baseweb="menu"] li {
    background: transparent !important;
    color: var(--text-secondary) !important;
    font-size: 13px !important;
}

[data-baseweb="menu"] li:hover {
    background: var(--orange-glow) !important;
    color: var(--orange-400) !important;
}

/* === SCROLLBAR === */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb {
    background: var(--border-light);
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover { background: var(--orange-500); }

/* === RESPONSIVENESS === */
@media (max-width: 768px) {
    .ffp-header { padding: 1rem; flex-direction: column; gap: 1rem; }
    .ffp-content { padding: 1rem; }
    .stTabs [data-baseweb="tab-panel"] { padding: 1rem !important; }
}

/* === COLUMN LABEL BADGES === */
.ffp-col-label {
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: var(--text-muted);
    margin-bottom: 0.75rem;
    padding-left: 2px;
}
</style>
"""


def get_header_html(user_email: str) -> str:
    """Returns the custom header HTML."""
    initials = user_email[:2].upper() if user_email else "FF"
    return f"""
<div class="ffp-header">
    <div class="ffp-brand">
        <div style="display:flex; align-items:center; gap:10px;">
            <div style="
                width:38px; height:38px;
                background: linear-gradient(135deg, #F97316, #C2410C);
                border-radius:10px;
                display:flex; align-items:center; justify-content:center;
                font-size:20px; font-weight:900; color:white;
                box-shadow: 0 4px 12px rgba(249,115,22,0.4);
            ">🔥</div>
            <div>
                <div style="font-size:20px; font-weight:800; color:white; letter-spacing:-0.5px; line-height:1.1;">
                    Fire Form <span style="color:#FB923C;">Pro</span>
                </div>
                <div class="ffp-tagline">Automated FDNY form generation</div>
            </div>
        </div>
    </div>
    <div class="ffp-user-badge">
        <div class="ffp-user-avatar">{initials}</div>
        <span class="ffp-user-email">{user_email}</span>
    </div>
</div>
"""


def get_section_header(badge_text: str, title: str) -> str:
    return f"""
<div class="ffp-section-header">
    <span class="ffp-section-badge">{badge_text}</span>
    <span class="ffp-section-title">{title}</span>
</div>
"""


def get_stat_card(value: str, label: str) -> str:
    return f"""
<div class="ffp-stat-card">
    <div class="ffp-stat-value">{value}</div>
    <div class="ffp-stat-label">{label}</div>
</div>
"""
