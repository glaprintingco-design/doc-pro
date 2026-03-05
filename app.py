import streamlit as st
import main
import os
import zipfile
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="FDNY Auto-Filer Pro 2026", layout="wide")

st.title("🚀 FDNY Auto-Filer Pro v1.0")
st.markdown("Generación automatizada de formularios para la industria de alarmas contra incendios.")

# --- BARRA LATERAL (SETTINGS) ---
with st.sidebar:
    st.header("⚙️ Configuración")
    # En la Fase 3 esto se conectará a una base de datos (Supabase)
    st.info("Actualmente usando datos de config.json local.")
    
# --- DASHBOARD PRINCIPAL ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("1. Información del Proyecto")
    bin_number = st.text_input("Ingrese el número BIN", placeholder="Ej: 1012345")
    job_desc = st.text_area("Descripción del Trabajo", value="Installation of Fire Alarm System.")

    st.divider()
    
    st.subheader("2. Agregar Dispositivos")
    floor = st.selectbox("Piso", main.FULL_FLOOR_LIST)
    category = st.selectbox("Categoría", list(main.MASTER_DEVICE_LIST.keys()))
    
    # Filtrar dispositivos por categoría
    devices_in_cat = main.MASTER_DEVICE_LIST.get(category, [])
    device = st.selectbox("Dispositivo", devices_in_cat)
    qty = st.number_input("Cantidad", min_value=1, value=1)

    if st.button("➕ Agregar a la lista"):
        if 'device_list' not in st.session_state:
            st.session_state.device_list = []
        
        st.session_state.device_list.append({
            "device": device,
            "floor": floor,
            "qty": qty
        })
        st.success(f"Agregado: {device} en {floor}")

with col2:
    st.subheader("📋 Lista de Dispositivos del Proyecto")
    if 'device_list' in st.session_state and st.session_state.device_list:
        # Mostrar tabla interactiva
        st.table(st.session_state.device_list)
        
        if st.button("🗑️ Limpiar Lista"):
            st.session_state.device_list = []
            st.rerun()
    else:
        st.write("No hay dispositivos agregados aún.")

    st.divider()

    # --- PROCESAMIENTO ---
    if st.button("🔥 GENERAR DOCUMENTOS", type="primary", use_container_width=True):
        if not bin_number:
            st.error("Por favor, ingrese un número BIN.")
        elif 'device_list' not in st.session_state or not st.session_state.device_list:
            st.error("La lista de dispositivos está vacía.")
        else:
            with st.spinner("Consultando bases de datos de NYC y generando PDFs..."):
                try:
                    # Llamada a tu lógica de main.py
                    info = main.obtener_datos_completos(bin_number)
                    if info:
                        job_specs = {
                            "job_desc": job_desc,
                            "devices": st.session_state.device_list
                        }
                        full_data = {**info, **job_specs}
                        
                        # Generar archivos (Nombres temporales para el ZIP)
                        main.generar_tm1(full_data, "tm-1-application-for-plan-examination-doc-review.pdf", f"TM1_{bin_number}.pdf")
                        main.generar_a433(full_data, "application-a-433-c.pdf", f"A433_{bin_number}.pdf")
                        main.generar_b45(full_data, "b45-inspection-request.pdf", f"B45_{bin_number}.pdf")
                        main.generar_reporte_auditoria(full_data, f"REPORT_{bin_number}.txt")

                        # Crear un archivo ZIP en memoria para descarga
                        zip_buffer = BytesIO()
                        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                            for file_name in [f"TM1_{bin_number}.pdf", f"A433_{bin_number}.pdf", f"B45_{bin_number}.pdf", f"REPORT_{bin_number}.txt"]:
                                if os.path.exists(file_name):
                                    zip_file.write(file_name)
                                    os.remove(file_name) # Limpiar el servidor después de agregar al ZIP

                        st.success("✅ ¡Documentos generados con éxito!")
                        st.download_button(
                            label="📥 Descargar todos los formularios (ZIP)",
                            data=zip_buffer.getvalue(),
                            file_name=f"FDNY_Forms_{bin_number}.zip",
                            mime="application/zip"
                        )
                    else:
                        st.error("No se pudieron obtener datos para ese BIN.")
                except Exception as e:
                    st.error(f"Error crítico: {e}")