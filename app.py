import os
import sys
import builtins
os.environ['PYTHONIOENCODING'] = 'utf-8'
from flask import Flask, render_template, request, jsonify, send_file, session, redirect
import json
from supabase import create_client
import main
import zipfile
from io import BytesIO
from flask_cors import CORS

app = Flask(__name__, static_url_path='/static', static_folder='static')
CORS(app) # Habilitar CORS

# Llave secreta para las sesiones
app.secret_key = os.environ.get("FLASK_SECRET", "fire_form_pro_secret_nyc_2026")

# Variable requerida por Namecheap (Passenger WSGI)
application = app

# ==========================================
# CONEXIÓN A SUPABASE (GLOBAL PARA AUTH)
# ==========================================
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# --- INICIO DEL DIAGNÓSTICO (CHISMOSO) ---
print("=======================================")
print("--- DIAGNÓSTICO DE SUPABASE ---")
print(f"URL detectada en Render: {'SÍ' if SUPABASE_URL else 'NO'}")
print(f"KEY detectada en Render: {'SÍ' if SUPABASE_KEY else 'NO'}")
if SUPABASE_URL:
    print(f"La URL empieza con https: {SUPABASE_URL.startswith('https')}")
print("=======================================")
# --- FIN DEL DIAGNÓSTICO ---

supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Supabase cliente creado EXITOSAMENTE.")
    except Exception as e:
        print(f"❌ ERROR CRÍTICO creando cliente Supabase: {e}")
else:
    print("⚠️ FALTAN CREDENCIALES: Flask no intentará conectarse a Supabase.")

# ==========================================
# HELPER: CLIENTE SUPABASE AUTENTICADO
# ==========================================
def get_user_supabase():
    if 'access_token' not in session or 'refresh_token' not in session:
        return None
        
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    try:
        client.auth.set_session(session['access_token'], session['refresh_token'])
        return client
    except Exception as e:
        print(f"Error setting Supabase session: {e}")  # Sin acentos
        session.clear()  # <-- NUEVO: limpia la sesión expirada automáticamente
        return None

# ==========================================
# RUTAS DE PANTALLAS (HTML)
# ==========================================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    # Proteger la ruta: Si no hay usuario en sesion, lo devolvemos al inicio
    if 'user_id' not in session:
        return redirect('/')
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

# ==========================================
# RUTAS DE API: AUTENTICACIÓN (SUPABASE)
# ==========================================
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if not supabase:
        return jsonify({"error": "Database not connected"}), 500

    try:
        # Intentamos iniciar sesion con Supabase
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        
        # Si es exitoso, guardamos el ID y los TOKENS en la sesion de Flask
        session['user_id'] = response.user.id
        session['user_email'] = response.user.email
        session['access_token'] = response.session.access_token
        session['refresh_token'] = response.session.refresh_token
        
        return jsonify({"status": "success", "user_id": response.user.id})
    except Exception as e:
        # Supabase devuelve un error si la contraseña es incorrecta o el usuario no existe
        return jsonify({"error": str(e)}), 401

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if not supabase:
        return jsonify({"error": "Database not connected"}), 500

    try:
        # Creamos el usuario en Supabase
        response = supabase.auth.sign_up({"email": email, "password": password})
        
        if response.user:
            # Iniciamos sesion automáticamente al registrar y guardamos los TOKENS
            session['user_id'] = response.user.id
            session['user_email'] = response.user.email
            if response.session:
                session['access_token'] = response.session.access_token
                session['refresh_token'] = response.session.refresh_token
            
            # Opcional: Crear un perfil vacío en la tabla 'profiles'
            # (Usamos el cliente global aquí solo para inicializar, o puedes omitirlo si tu upsert lo maneja)
            try:
                supabase.table("profiles").insert({"id": response.user.id}).execute()
            except:
                pass 

            return jsonify({"status": "success"})
        else:
            return jsonify({"error": "Could not create account"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ==========================================
# RUTAS DE API: PROPERTY LOOKUP
# ==========================================
@app.route('/search_property', methods=['POST'])
def search_property():
    """Recibe la dirección o BIN desde el frontend y devuelve los datos"""
    data = request.json
    search_type = data.get('type')
    
    try:
        if search_type == 'bin':
            bin_val = data.get('bin')
        else:
            bin_val = main.obtener_bin_por_direccion(
                data.get('house'), data.get('street'), data.get('borough')
            )
            
        if not bin_val:
            return jsonify({"error": "No BIN found for this address. Check spelling."}), 404
            
        info = main.obtener_datos_completos(bin_val)
        
        # Guardar registro de búsqueda (Métricas) solo si la búsqueda fue exitosa
        if info:
            user_id = session.get('user_id')
            user_client = get_user_supabase()
            if user_client:
                try:
                    user_client.table("property_searches").insert({
                        "user_id": user_id,
                        "bin": bin_val,
                        "loa_account_found": "Manual Search" 
                    }).execute()
                except:
                    pass # Ignorar error silenciosamente para no frenar la UI
            
            return jsonify(info)
        else:
            return jsonify({"error": "No data retrieved from NYC databases"}), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==========================================
# RUTAS DE API: GENERADOR DE PDFS
# ==========================================
@app.route('/api/generate', methods=['POST'])
def generate_pdfs():
    """Recibe los datos del proyecto, inyecta el perfil, genera PDFs y devuelve un ZIP"""
    try:
        import tempfile
        import time
        import traceback
        
        data = request.json
        bin_number = data.get('bin')
        job_desc = data.get('job_desc', 'Installation of Fire Alarm System.')
        devices = data.get('devices', [])
        forms_to_gen = data.get('forms', ['TM-1', 'A-433', 'B-45', 'REPORT'])
        
        user_id = session.get('user_id') 
        user_client = get_user_supabase()

        # --- 1. LÓGICA DE SUSCRIPCIÓN Y LÍMITES ---
        if user_client:
            try:
                sub_res = user_client.table("user_subscriptions").select("*").eq("user_id", user_id).execute()
                sub_data = sub_res.data[0] if sub_res.data else {"plan_type": "free", "forms_generated_this_month": 0}
                
                is_pro = sub_data.get("plan_type") == "pro"
                usos_mes = sub_data.get("forms_generated_this_month", 0)
                
                if not is_pro and usos_mes >= 2:
                    return jsonify({"error": "You have reached your free limit (2 forms/month). Please upgrade to Pro."}), 403
                    
                if not is_pro:
                    nuevo_uso = usos_mes + 1
                    user_client.table("user_subscriptions").upsert({
                        "user_id": user_id,
                        "plan_type": "free",
                        "forms_generated_this_month": nuevo_uso,
                        "last_reset_date": "now()"
                    }).execute()
            except Exception as e:
                print("Error checking subscription:", e)

        # --- 2. Obtenemos la info fresca de la propiedad ---
        info = main.obtener_datos_completos(bin_number)
        if not info:
             return jsonify({"error": "Data fetch failed for this BIN"}), 400

        # --- 3. Sincronizamos el Perfil de Supabase hacia main.py ---
        if user_client:
            try:
                prof_res = user_client.table("profiles").select("*").eq("id", user_id).execute()
                if prof_res.data:
                    profile = prof_res.data[0]
                    
                    main.COMPANY.update({
                        "Company Name": profile.get("company_name", ""), "Address": profile.get("company_address", ""),
                        "City": profile.get("company_city", ""), "State": profile.get("company_state", "NY"),
                        "Zip": profile.get("company_zip", ""), "Phone": profile.get("company_phone", ""),
                        "Email": profile.get("company_email", ""), "First Name": profile.get("company_first_name", ""),
                        "Last Name": profile.get("company_last_name", ""), "COF S97": profile.get("company_cof_s97", ""),
                        "Expiration": profile.get("company_expiration", ""),
                    })
                    main.EXPEDITOR.update({
                        "Company Name": profile.get("exp_name", ""), "Address": profile.get("exp_address", ""),
                        "City": profile.get("exp_city", ""), "State": profile.get("exp_state", "NY"),
                        "Zip": profile.get("exp_zip", ""), "Phone": profile.get("exp_phone", ""),
                        "Email": profile.get("exp_email", ""), "First Name": profile.get("exp_first_name", ""),
                        "Last Name": profile.get("exp_last_name", ""), "Reg No": profile.get("exp_reg_no", ""),
                    })
                    main.ARCHITECT.update({
                        "Company Name": profile.get("arch_name", ""), "Address": profile.get("arch_address", ""),
                        "City": profile.get("arch_city", ""), "State": profile.get("arch_state", ""),
                        "Zip": profile.get("arch_zip", ""), "Phone": profile.get("arch_phone", ""),
                        "Email": profile.get("arch_email", ""), "First Name": profile.get("arch_first_name", ""),
                        "Last Name": profile.get("arch_last_name", ""), "License No": profile.get("arch_license", ""),
                        "Role": profile.get("arch_role", "PE"),
                    })
                    main.ELECTRICIAN.update({
                        "Company Name": profile.get("elec_name", ""), "Address": profile.get("elec_address", ""),
                        "City": profile.get("elec_city", ""), "State": profile.get("elec_state", ""),
                        "Zip": profile.get("elec_zip", ""), "Phone": profile.get("elec_phone", ""),
                        "Email": profile.get("elec_email", ""), "First Name": profile.get("elec_first_name", ""),
                        "Last Name": profile.get("elec_last_name", ""), "License No": profile.get("elec_license", ""),
                        "Expiration": profile.get("elec_expiration", ""),
                    })
                    main.TECH_DEFAULTS.update({
                        "Manufacturer": profile.get("tech_manufacturer", ""), "Approval": profile.get("tech_approval", ""),
                        "WireGauge": profile.get("tech_wire_gauge", ""), "WireType": profile.get("tech_wire_type", ""),
                    })
                    main.CENTRAL_STATION.update({
                        "Company Name": profile.get("cs_name", ""), "CS Code": profile.get("cs_code", ""),
                        "Address": profile.get("cs_address", ""), "City": profile.get("cs_city", ""),
                        "State": profile.get("cs_state", ""), "Zip": profile.get("cs_zip", ""),
                        "Phone": profile.get("cs_phone", ""),
                    })
            except Exception as e:
                print(" Warning: Could not sync profile ->", e)

        # --- 4. Preparamos datos y RUTAS SEGURAS (TEMP DIR) ---
        full_data = {**info, "job_desc": job_desc, "devices": devices}
        safe_address = f"{info.get('house', '')} {info.get('street', '')}".replace("/", "-").strip() or bin_number

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        TEMP_DIR = os.path.join(BASE_DIR, 'tmp_pdfs')
        if not os.path.exists(TEMP_DIR):
            os.makedirs(TEMP_DIR)
            
        timestamp = str(int(time.time()))
        generated_files = []
        
        # NOTA: Usamos solo el nombre del archivo asumiendo que están en la raíz del proyecto
        if 'TM-1' in forms_to_gen:
            out_file = os.path.join(TEMP_DIR, f"TM-1_{timestamp}.pdf")
            main.generar_tm1(full_data, "tm-1-application-for-plan-examination-doc-review.pdf", out_file)
            generated_files.append((out_file, f"TM-1 - {safe_address}.pdf"))
            
        if 'A-433' in forms_to_gen:
            out_file = os.path.join(TEMP_DIR, f"A-433_{timestamp}.pdf")
            main.generar_a433(full_data, "application-a-433-c.pdf", out_file)
            generated_files.append((out_file, f"A-433 - {safe_address}.pdf"))
            
        if 'B-45' in forms_to_gen:
            out_file = os.path.join(TEMP_DIR, f"B-45_{timestamp}.pdf")
            main.generar_b45(full_data, "b45-inspection-request.pdf", out_file)
            generated_files.append((out_file, f"B-45 - {safe_address}.pdf"))
            
        if 'REPORT' in forms_to_gen:
            out_file = os.path.join(TEMP_DIR, f"REPORT_{timestamp}.txt")
            main.generar_reporte_auditoria(full_data, out_file)
            generated_files.append((out_file, f"REPORT - {safe_address}.txt"))

        # --- 5. Empaquetamos en ZIP en memoria ---
        import base64
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            for sys_path, user_filename in generated_files:
                if os.path.exists(sys_path):
                    zip_file.write(sys_path, arcname=user_filename)

        # --- 6. Preparamos Respuesta JSON con Base64 para descargas individuales ---
        response_data = {
            "zip_base64": base64.b64encode(zip_buffer.getvalue()).decode('utf-8'),
            "files": []
        }
        
        for sys_path, user_filename in generated_files:
            if os.path.exists(sys_path):
                with open(sys_path, "rb") as f:
                    b64_content = base64.b64encode(f.read()).decode('utf-8')
                    response_data["files"].append({
                        "filename": user_filename,
                        "mime_type": "application/pdf" if user_filename.endswith(".pdf") else "text/plain",
                        "content": b64_content
                    })
                try:
                    os.remove(sys_path) # Limpiar temporal
                except: pass

        # Guardamos en el Historial
        if user_client:
            try:
                user_client.table("projects").upsert({
                    "user_id": user_id, "bin": bin_number, "address": safe_address,
                    "device_list": devices, "job_description": job_desc
                }, on_conflict="user_id, bin").execute()
            except: pass

        return jsonify(response_data)
        
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"CRITICAL ERROR: {error_details}")
        return jsonify({"error": f"Internal Error: {str(e)}", "traceback": error_details}), 500  
# ==========================================
# RUTAS DE API: PROFILE SETTINGS
# ==========================================
@app.route('/api/profile', methods=['GET', 'POST'])
def handle_profile():
    """Lee (GET) o Guarda (POST) el perfil en Supabase usando el cliente autenticado"""
    user_id = session.get('user_id')
    user_client = get_user_supabase()
    
    if not user_client: 
        return jsonify({"error": "Unauthorized or session expired. Please log in again."}), 401
        
    if request.method == 'GET':
        try:
            res = user_client.table("profiles").select("*").eq("id", user_id).execute()
            return jsonify(res.data[0] if res.data else {})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
    if request.method == 'POST':
        data = request.json
        data['id'] = user_id
        data['updated_at'] = 'now()'
        try:
            user_client.table("profiles").upsert(data).execute()
            return jsonify({"status": "success", "message": "Profile saved!"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

# ==========================================
# RUTAS DE API: HISTORIAL DE PROYECTOS
# ==========================================
@app.route('/api/projects', methods=['GET'])
def get_projects():
    """Obtiene los últimos proyectos guardados por el usuario usando el cliente autenticado"""
    user_id = session.get('user_id')
    user_client = get_user_supabase()
    
    if not user_client: 
        return jsonify([])
        
    try:
        res = user_client.table("projects").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        return jsonify(res.data if res.data else [])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/projects/<project_id>', methods=['DELETE'])
def delete_project(project_id):
    """Elimina un proyecto del historial"""
    user_id = session.get('user_id')
    user_client = get_user_supabase()
    
    if not user_client: 
        return jsonify({"error": "Unauthorized"}), 401
        
    try:
        # Importante: aseguramos que el usuario solo borre SUS propios proyectos
        user_client.table("projects").delete().eq("id", project_id).eq("user_id", user_id).execute()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500 

# ==========================================
# INICIO DE LA APLICACIÓN
# ==========================================
if __name__ == '__main__':
    app.run(debug=True)  
