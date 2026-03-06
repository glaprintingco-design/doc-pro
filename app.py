import streamlit as st
import main
import os
import zipfile
from io import BytesIO

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Fire Form Pro", layout="wide")

# --- ADD LOGO ---
# This assumes you have a file named 'logo.png' in your GitHub repository
if os.path.exists("logo.png"):
    st.image("logo.png", width=200)

st.title("Fire Form Pro")
st.markdown("Automated form generation for the NYC Fire Alarm Industry.")

# --- SIDEBAR (SETTINGS) ---
with st.sidebar:
    st.header("⚙️ Settings")
    st.info("Currently using profile data from cloud secrets.")
    
# --- MAIN DASHBOARD ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("1. Project Information")
    bin_number = st.text_input("Enter Property BIN", placeholder="e.g. 1012345")
    job_desc = st.text_area("Job Description", value="Installation of Fire Alarm System.")

    st.divider()
    
    st.subheader("2. Add Devices")
    floor = st.selectbox("Floor Location", main.FULL_FLOOR_LIST)
    category = st.selectbox("Category", list(main.MASTER_DEVICE_LIST.keys()))
    
    # Filter devices based on category
    devices_in_cat = main.MASTER_DEVICE_LIST.get(category, [])
    device = st.selectbox("Device Type", devices_in_cat)
    qty = st.number_input("Quantity", min_value=1, value=1)

    if st.button("➕ Add to List"):
        if 'device_list' not in st.session_state:
            st.session_state.device_list = []
        
        st.session_state.device_list.append({
            "device": device,
            "floor": floor,
            "qty": qty
        })
        st.success(f"Added: {device} at {floor}")

with col2:
    st.subheader("📋 Project Device List")
    if 'device_list' in st.session_state and st.session_state.device_list:
        # Show interactive table
        st.table(st.session_state.device_list)
        
        if st.button("🗑️ Clear List"):
            st.session_state.device_list = []
            st.rerun()
    else:
        st.write("No devices added yet.")

    st.divider()

    # --- DOCUMENT GENERATION ---
    if st.button("🔥 GENERATE DOCUMENTS", type="primary", use_container_width=True):
        if not bin_number:
            st.error("Please enter a BIN number.")
        elif 'device_list' not in st.session_state or not st.session_state.device_list:
            st.error("Device list is empty.")
        else:
            with st.spinner("Fetching NYC data and filling PDFs..."):
                try:
                    # Call main logic
                    info = main.obtener_datos_completos(bin_number)
                    if info:
                        job_specs = {
                            "job_desc": job_desc,
                            "devices": st.session_state.device_list
                        }
                        full_data = {**info, **job_specs}
                        
                        # Generate files using main.py logic
                        main.generar_tm1(full_data, "tm-1-application-for-plan-examination-doc-review.pdf", f"TM1_{bin_number}.pdf")
                        main.generar_a433(full_data, "application-a-433-c.pdf", f"A433_{bin_number}.pdf")
                        main.generar_b45(full_data, "b45-inspection-request.pdf", f"B45_{bin_number}.pdf")
                        main.generar_reporte_auditoria(full_data, f"REPORT_{bin_number}.txt")

                        # Create ZIP file in memory
                        zip_buffer = BytesIO()
                        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                            for file_name in [f"TM1_{bin_number}.pdf", f"A433_{bin_number}.pdf", f"B45_{bin_number}.pdf", f"REPORT_{bin_number}.txt"]:
                                if os.path.exists(file_name):
                                    zip_file.write(file_name)
                                    os.remove(file_name) 

                        st.success("✅ Documents generated successfully!")
                        st.download_button(
                            label="📥 Download All Forms (ZIP)",
                            data=zip_buffer.getvalue(),
                            file_name=f"FDNY_Forms_{bin_number}.zip",
                            mime="application/zip"
                        )
                    else:
                        st.error("Could not retrieve data for this BIN.")
                except Exception as e:
                    st.error(f"Critical Error: {e}")

