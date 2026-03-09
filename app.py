import streamlit as st
from supabase import create_client
import main
import os
import zipfile
from io import BytesIO

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Fire Form Pro",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# CSS STYLES
# ============================================================

def load_css():

    st.markdown("""
    <style>

    #MainMenu {visibility:hidden;}
    footer {visibility:hidden;}
    header {visibility:hidden;}

    [data-testid="stAppViewContainer"] {
        background-color: #F4F7F9;
    }

    .block-container {
        padding-top:0rem;
        max-width:1400px;
    }

    /* Buttons */

    .stButton > button {
        border-radius:8px;
        font-weight:600;
        padding:0.6rem 1.4rem;
        border:none;
    }

    .stButton > button[kind="primary"]{
        background:linear-gradient(135deg,#FF6B00,#E65100);
        color:white;
        box-shadow:0 4px 10px rgba(255,107,0,0.25);
    }

    .stButton > button[kind="primary"]:hover{
        transform:translateY(-1px);
        box-shadow:0 6px 16px rgba(255,107,0,0.35);
    }

    /* Inputs */

    input, textarea {
        border-radius:8px !important;
        border:1px solid #E2E8F0 !important;
    }

    input:focus, textarea:focus{
        border-color:#FF6B00 !important;
        box-shadow:0 0 0 1px #FF6B00 !important;
    }

    /* Cards */

    [data-testid="stExpander"]{
        background:white;
        border-radius:12px;
        border:1px solid #E2E8F0;
        box-shadow:0 4px 8px rgba(0,0,0,0.03);
    }

    /* Tabs */

    .stTabs [data-baseweb="tab"]{
        font-weight:600;
        font-size:16px;
    }

    .stTabs [aria-selected="true"]{
        color:#FF6B00;
        border-bottom-color:#FF6B00;
    }

    </style>
    """, unsafe_allow_html=True)

load_css()

# ============================================================
# INIT SESSION STATE
# ============================================================

def init_session():

    defaults = {
        "user": None,
        "device_list": [],
        "generated_data": None,
    }

    for k,v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()

# ============================================================
# SUPABASE
# ============================================================

SUPABASE_URL = st.secrets.get("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY")

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error("Supabase connection failed")
    st.stop()

# ============================================================
# AUTH
# ============================================================

def logout():

    try:
        supabase.auth.sign_out()
    except:
        pass

    st.session_state.user = None
    st.rerun()

# ============================================================
# LOGIN
# ============================================================

def login_screen():

    col1,col2,col3 = st.columns([1,2,1])

    with col2:

        if os.path.exists("logo.png"):
            st.image("logo.png",width=240)
        else:
            st.title("🔥 Fire Form Pro")

        tab1,tab2 = st.tabs(["Sign In","Create Account"])

        with tab1:

            email = st.text_input("Email")
            password = st.text_input("Password",type="password")

            if st.button("Sign In",type="primary",use_container_width=True):

                try:
                    r = supabase.auth.sign_in_with_password({
                        "email":email,
                        "password":password
                    })

                    st.session_state.user = r.user
                    st.rerun()

                except:
                    st.error("Invalid login")

        with tab2:

            email = st.text_input("Email",key="su_email")
            password = st.text_input("Password",type="password",key="su_pw")

            if st.button("Create Account",type="primary",use_container_width=True):

                try:

                    r = supabase.auth.sign_up({
                        "email":email,
                        "password":password
                    })

                    st.success("Account created")

                except Exception as e:
                    st.error(str(e))


if not st.session_state.user:
    login_screen()
    st.stop()

# ============================================================
# HEADER
# ============================================================

def render_header():

    st.markdown("""
    <div style="
    background:linear-gradient(135deg,#FF6B00,#E65100);
    padding:2rem;
    margin:-1rem -1rem 2rem -1rem;
    color:white;
    ">
    """, unsafe_allow_html=True)

    col1,col2 = st.columns([3,1])

    with col1:

        if os.path.exists("logo.png"):
            st.image("logo.png",width=260)

        st.markdown(
        "<p style='color:white;margin-top:-10px'>Automated FDNY form generation</p>",
        unsafe_allow_html=True)

    with col2:

        st.markdown(f"**👤 {st.session_state.user.email}**")

        if st.button("Logout"):
            logout()

    st.markdown("</div>",unsafe_allow_html=True)

render_header()

# ============================================================
# TABS
# ============================================================

tabs = st.tabs([
"🏗 Project Builder",
"👤 Profile"
])

# ============================================================
# PROJECT BUILDER
# ============================================================

with tabs[0]:

    st.subheader("Project Information")

    bin_number = st.text_input("BIN Number")

    job_desc = st.text_area(
        "Job Description",
        value="Installation of Fire Alarm System."
    )

    st.divider()

    st.subheader("Device Schedule")

    col1,col2 = st.columns([1,2])

    with col1:

        floor = st.selectbox("Floor",main.FULL_FLOOR_LIST)

        category = st.selectbox(
            "Category",
            list(main.MASTER_DEVICE_LIST.keys())
        )

        device = st.selectbox(
            "Device",
            main.MASTER_DEVICE_LIST.get(category,[])
        )

        qty = st.number_input("Quantity",1,999,1)

        if st.button("Add Device"):

            st.session_state.device_list.append({
                "device":device,
                "floor":floor,
                "qty":qty
            })

    with col2:

        if st.session_state.device_list:

            edited = st.data_editor(
                st.session_state.device_list,
                num_rows="dynamic",
                use_container_width=True
            )

            st.session_state.device_list = edited

# ============================================================
# GENERATE DOCS
# ============================================================

    st.divider()

    if st.button("🔥 GENERATE DOCUMENTS",type="primary",use_container_width=True):

        if not bin_number:
            st.error("Enter BIN number")
            st.stop()

        with st.spinner("Generating..."):

            info = main.obtener_datos_completos(bin_number)

            if not info:
                st.error("BIN not found")
                st.stop()

            data = {
                **info,
                "devices":st.session_state.device_list,
                "job_desc":job_desc
            }

            files=[]

            main.generar_tm1(data,"tm1.pdf","TM1.pdf")
            files.append("TM1.pdf")

            zip_buffer = BytesIO()

            with zipfile.ZipFile(zip_buffer,"a") as z:

                for f in files:

                    with open(f,"rb") as file:
                        z.writestr(f,file.read())

            st.download_button(
                "Download ZIP",
                zip_buffer.getvalue(),
                "fdny_forms.zip",
                "application/zip",
                use_container_width=True
            )

# ============================================================
# PROFILE
# ============================================================

with tabs[1]:

    st.subheader("Profile Settings")

    company = st.text_input("Company Name")

    phone = st.text_input("Phone")

    email = st.text_input("Email")

    if st.button("Save Profile"):

        try:

            supabase.table("profiles").upsert({
                "id":st.session_state.user.id,
                "company_name":company,
                "phone":phone,
                "email":email
            }).execute()

            st.success("Saved")

        except Exception as e:

            st.error(str(e))
