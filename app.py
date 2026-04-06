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
CORS(app)

app.secret_key = os.environ.get("FLASK_SECRET", "fire_form_pro_secret_nyc_2026")
application = app

# ==========================================
# CONEXIÓN A SUPABASE
# ==========================================
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

print("=======================================")
print("--- DIAGNÓSTICO DE SUPABASE ---")
print(f"URL detectada en Render: {'SI' if SUPABASE_URL else 'NO'}")
print(f"KEY detectada en Render: {'SI' if SUPABASE_KEY else 'NO'}")
if SUPABASE_URL:
    print(f"La URL empieza con https: {SUPABASE_URL.startswith('https')}")
print("=======================================")

supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Supabase cliente creado EXITOSAMENTE.")
    except Exception as e:
        print(f"❌ ERROR CRITICO creando cliente Supabase: {e}")
else:
    print("⚠️ FALTAN CREDENCIALES: Flask no intentara conectarse a Supabase.")

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
        print(f"Error setting Supabase session: {e}")
        session.clear()
        return None

# ==========================================
# SYNC PROFILE → main.py  (IGUAL QUE STREAMLIT)
# ==========================================
def sync_profile_to_main(profile):
    """
    Inyecta los datos del perfil de Supabase en las variables globales de main.py.
    Debe llamarse ANTES de generar cualquier PDF.
    """
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
        "COF S97":      profile.get("company_cof_s97", ""),
        "Expiration":   profile.get("company_expiration", ""),
    })
    main.EXPEDITOR.update({
        "Company Name": profile.get("exp_name", ""),
        "Address":      profile.get("exp_address", ""),
        "City":         profile.get("exp_city", ""),
        "State":        profile.get("exp_state", "NY"),
        "Zip":          profile.get("exp_zip", ""),
        "Phone":        profile.get("exp_phone", ""),
        "Email":        profile.get("exp_email", ""),
        "First Name":   profile.get("exp_first_name", ""),
        "Last Name":    profile.get("exp_last_name", ""),
        "Reg No":       profile.get("exp_reg_no", ""),
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

# ==========================================
# RUTAS DE PANTALLAS (HTML)
# ==========================================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')
        
    # NUEVO: Consultar si el usuario es PRO
    is_pro = False
    user_client = get_user_supabase()
    
    if user_client:
        try:
            sub_res = user_client.table("user_subscriptions").select("plan_type").eq("user_id", session['user_id']).execute()
            if sub_res.data and sub_res.data[0].get("plan_type") == "pro":
                is_pro = True
        except Exception as e:
            print(f"Error revisando suscripción en dashboard: {e}")
            
    # Le pasamos la variable 'is_pro' al HTML
    return render_template('dashboard.html', is_pro=is_pro)

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

@app.route('/refund')
def refund():
    return render_template('refund.html')

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')
    
@app.route('/manhattan-fdny-forms')
def manhattan-fdny-forms():
    return render_template('manhattan-fdny-forms.html')   

# ==========================================
# RUTA DE DIAGNÓSTICO — /api/diagnostics
# Visita esta URL en el browser para ver el estado de todas las APIs y keys
# ==========================================
@app.route('/api/diagnostics')
def diagnostics():
    import requests as req
    import datetime

    NYC_API_KEY      = os.environ.get("NYC_API_KEY", "")
    SOCRATA_TOKEN    = os.environ.get("SOCRATA_TOKEN", "")
    TEST_BIN         = "1007239"  # 54 Crosby St — edificio conocido para pruebas

    results = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "environment": {},
        "api_tests": {}
    }

    # --- 1. VARIABLES DE ENTORNO ---
    results["environment"] = {
        "NYC_API_KEY":    "✅ SET"   if NYC_API_KEY    else "❌ MISSING",
        "SOCRATA_TOKEN":  "✅ SET"   if SOCRATA_TOKEN  else "⚠️ MISSING (optional but recommended)",
        "SUPABASE_URL":   "✅ SET"   if os.environ.get("SUPABASE_URL") else "❌ MISSING",
        "SUPABASE_KEY":   "✅ SET"   if os.environ.get("SUPABASE_KEY") else "❌ MISSING",
        "FLASK_SECRET":   "✅ SET"   if os.environ.get("FLASK_SECRET") else "⚠️ using default",
        "NYC_API_KEY_preview": (NYC_API_KEY[:6] + "..." + NYC_API_KEY[-4:]) if len(NYC_API_KEY) > 10 else ("(empty)" if not NYC_API_KEY else NYC_API_KEY),
    }

    # --- 2. TEST GEOCLIENT ---
    try:
        r = req.get(
            "https://api.nyc.gov/geoclient/v2/bin",
            params={"bin": TEST_BIN},
            headers={"Ocp-Apim-Subscription-Key": NYC_API_KEY},
            timeout=8
        )
        if r.status_code == 200:
            d = r.json().get("bin", {})
            results["api_tests"]["geoclient"] = {
                "status": "✅ OK",
                "http_code": 200,
                "bbl": d.get("bbl", "not found"),
                "address": f"{d.get('giLowHouseNumber1','')} {d.get('giStreetName1','')}".strip(),
                "borough": d.get("firstBoroughName", ""),
            }
        elif r.status_code == 401:
            results["api_tests"]["geoclient"] = {
                "status": "❌ UNAUTHORIZED — NYC_API_KEY is wrong or expired",
                "http_code": 401,
                "fix": "Go to https://api-portal.nyc.gov and check your subscription key"
            }
        elif r.status_code == 403:
            results["api_tests"]["geoclient"] = {
                "status": "❌ FORBIDDEN — Key valid but no access to Geoclient product",
                "http_code": 403,
                "fix": "Subscribe to 'Geoclient' product at https://api-portal.nyc.gov"
            }
        else:
            results["api_tests"]["geoclient"] = {
                "status": f"⚠️ Unexpected response",
                "http_code": r.status_code,
                "body_preview": r.text[:200]
            }
    except Exception as e:
        results["api_tests"]["geoclient"] = {"status": f"❌ EXCEPTION: {str(e)}"}

    # --- 3. TEST PLUTO (Socrata, por BIN directo) ---
    try:
        headers_soc = {"X-App-Token": SOCRATA_TOKEN} if SOCRATA_TOKEN else {}
        r = req.get(
            "https://data.cityofnewyork.us/resource/64uk-42ks.json",
            params={"bin": TEST_BIN, "$limit": 1},
            headers=headers_soc,
            timeout=8
        )
        if r.status_code == 200 and r.json():
            p = r.json()[0]
            results["api_tests"]["pluto"] = {
                "status": "✅ OK",
                "http_code": 200,
                "yearbuilt":  p.get("yearbuilt", "not found"),
                "numfloors":  p.get("numfloors", "not found"),
                "bldgclass":  p.get("bldgclass", "not found"),
                "zipcode":    p.get("zipcode", "not found"),
                "ownername":  p.get("ownername", "not found"),
            }
        elif r.status_code == 200 and not r.json():
            results["api_tests"]["pluto"] = {
                "status": "⚠️ OK but NO DATA for this BIN",
                "http_code": 200,
                "note": "PLUTO returned empty array — BIN may not exist in dataset"
            }
        elif r.status_code == 429:
            results["api_tests"]["pluto"] = {
                "status": "⚠️ RATE LIMITED — add SOCRATA_TOKEN to env vars",
                "http_code": 429
            }
        else:
            results["api_tests"]["pluto"] = {
                "status": f"⚠️ HTTP {r.status_code}",
                "http_code": r.status_code,
                "body_preview": r.text[:200]
            }
    except Exception as e:
        results["api_tests"]["pluto"] = {"status": f"❌ EXCEPTION: {str(e)}"}

    # --- 4. TEST BIS (Socrata) ---
    try:
        headers_soc = {"X-App-Token": SOCRATA_TOKEN} if SOCRATA_TOKEN else {}
        r = req.get(
            "https://data.cityofnewyork.us/resource/ic3t-wcy2.json",
            params={"bin__": TEST_BIN, "$limit": 2},
            headers=headers_soc,
            timeout=8
        )
        if r.status_code == 200:
            jobs = r.json()
            results["api_tests"]["bis"] = {
                "status": "✅ OK",
                "http_code": 200,
                "jobs_found": len(jobs),
                "sample": {
                    "existing_height": jobs[0].get("existing_height") if jobs else None,
                    "existingno_of_stories": jobs[0].get("existingno_of_stories") if jobs else None,
                    "existing_construction_class": jobs[0].get("existing_construction_class") if jobs else None,
                    "existing_occupancy": jobs[0].get("existing_occupancy") if jobs else None,
                    "job_description": jobs[0].get("job_description") if jobs else None,
                } if jobs else "no jobs found for this BIN"
            }
        else:
            results["api_tests"]["bis"] = {
                "status": f"⚠️ HTTP {r.status_code}",
                "http_code": r.status_code
            }
    except Exception as e:
        results["api_tests"]["bis"] = {"status": f"❌ EXCEPTION: {str(e)}"}

    # --- 5. TEST DOB NOW ---
    try:
        headers_soc = {"X-App-Token": SOCRATA_TOKEN} if SOCRATA_TOKEN else {}
        r = req.get(
            "https://data.cityofnewyork.us/resource/w9ak-ipjd.json",
            params={"bin": TEST_BIN, "$limit": 1},
            headers=headers_soc,
            timeout=8
        )
        if r.status_code == 200:
            jobs = r.json()
            results["api_tests"]["dob_now"] = {
                "status": "✅ OK",
                "http_code": 200,
                "records_found": len(jobs),
                "owner_business": jobs[0].get("owner_s_business_name") if jobs else None,
                "owner_name": f"{jobs[0].get('owner_first_name','')} {jobs[0].get('owner_last_name','')}".strip() if jobs else None,
            }
        else:
            results["api_tests"]["dob_now"] = {
                "status": f"⚠️ HTTP {r.status_code}",
                "http_code": r.status_code
            }
    except Exception as e:
        results["api_tests"]["dob_now"] = {"status": f"❌ EXCEPTION: {str(e)}"}

    # --- 6. TEST SUPABASE ---
    try:
        if supabase:
            supabase.table("profiles").select("id").limit(1).execute()
            results["api_tests"]["supabase"] = {"status": "✅ OK — connected and query succeeded"}
        else:
            results["api_tests"]["supabase"] = {"status": "❌ Client not initialized — check SUPABASE_URL and SUPABASE_KEY"}
    except Exception as e:
        results["api_tests"]["supabase"] = {"status": f"❌ EXCEPTION: {str(e)}"}

    # --- RESUMEN FINAL ---
    all_ok = all("✅" in str(v.get("status","")) for v in results["api_tests"].values())
    results["summary"] = "✅ ALL SYSTEMS OK" if all_ok else "⚠️ SOME APIS HAVE ISSUES — see api_tests above"

    return jsonify(results), 200

# ==========================================
# RUTAS DE API: AUTENTICACIÓN
# ==========================================
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    # NUEVO: Obtenemos el parámetro 'next' si existe en la URL
    next_url = request.args.get('next')

    if not supabase:
        return jsonify({"error": "Database not connected"}), 500

    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        
        # Guardamos en sesión
        session.permanent = True
        session['user_id'] = response.user.id
        session['user_email'] = response.user.email
        session['access_token'] = response.session.access_token
        session['refresh_token'] = response.session.refresh_token
        
        # NUEVO: Preparamos la URL de redirección
        # Si no hay next_url, vamos al dashboard
        redirect_target = next_url if next_url else '/dashboard'
        
        # Devolvemos la URL a la que el JS debe redirigir
        return jsonify({
            "status": "success", 
            "user_id": response.user.id,
            "redirect_url": redirect_target # <- Clave para el JS
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 401
        
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not supabase:
        return jsonify({"error": "Database not connected"}), 500

    try:
        response = supabase.auth.sign_up({"email": email, "password": password})
        if response.user:
            session.permanent = True
            session['user_id'] = response.user.id
            session['user_email'] = response.user.email
            if response.session:
                session['access_token'] = response.session.access_token
                session['refresh_token'] = response.session.refresh_token
            try:
                supabase.table("profiles").insert({"id": response.user.id}).execute()
            except:
                pass
            return jsonify({"status": "success"})
        else:
            return jsonify({"error": "Could not create account"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    data = request.json
    email = data.get('email')

    if not supabase:
        return jsonify({"error": "Database not connected"}), 500

    try:
        # Esto le dice a Supabase que dispare la plantilla de correo que diseñamos
        # hacia el correo ingresado por el usuario.
        supabase.auth.reset_password_email(email)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ==========================================
# RUTAS DE API: PROPERTY LOOKUP
# ==========================================
@app.route('/search_property', methods=['POST'])
def search_property():
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
                    pass
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

        # --- 1. LÓGICA DE SUSCRIPCIÓN ---
        if user_client:
            try:
                sub_res = user_client.table("user_subscriptions").select("*").eq("user_id", user_id).execute()
                sub_data = sub_res.data[0] if sub_res.data else {"plan_type": "free", "forms_generated_this_month": 0}
                is_pro = sub_data.get("plan_type") == "pro"
                usos_mes = sub_data.get("forms_generated_this_month", 0)

                if not is_pro and usos_mes >= 2:
                    return jsonify({"error": "You have reached your free limit (2 forms/month). Please upgrade to Pro."}), 403

                if not is_pro:
                    user_client.table("user_subscriptions").upsert({
                        "user_id": user_id,
                        "plan_type": "free",
                        "forms_generated_this_month": usos_mes + 1,
                        "last_reset_date": "now()"
                    }).execute()
            except Exception as e:
                print("Error checking subscription:", e)

        # --- 2. SINCRONIZAR PERFIL PRIMERO (igual que Streamlit) ---
        if user_client:
            try:
                prof_res = user_client.table("profiles").select("*").eq("id", user_id).execute()
                if prof_res.data:
                    profile = prof_res.data[0]
                    sync_profile_to_main(profile)  # ← PRIMERO el perfil
                    print("✅ Profile synced to main.py")
                else:
                    print("⚠️ No profile found for user, forms will have blank company fields")
            except Exception as e:
                print(f"⚠️ Warning: Could not sync profile -> {e}")

        # --- 3. DESPUÉS buscar datos de la propiedad ---
        info = main.obtener_datos_completos(bin_number)
        if not info:
            return jsonify({"error": "Data fetch failed for this BIN"}), 400

        # --- 4. Preparar datos y rutas ---
        full_data = {**info, "job_desc": job_desc, "devices": devices}
        safe_address = f"{info.get('house', '')} {info.get('street', '')}".replace("/", "-").strip() or bin_number

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        TEMP_DIR = os.path.join(BASE_DIR, 'tmp_pdfs')
        if not os.path.exists(TEMP_DIR):
            os.makedirs(TEMP_DIR)

        timestamp = str(int(time.time()))
        generated_files = []

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

        # --- 5. Empaquetar en ZIP ---
        import base64
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            for sys_path, user_filename in generated_files:
                if os.path.exists(sys_path):
                    zip_file.write(sys_path, arcname=user_filename)

        # --- 6. Respuesta con Base64 ---
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
                    os.remove(sys_path)
                except:
                    pass

        # --- 7. Guardar en historial ---
        if user_client:
            try:
                user_client.table("projects").upsert({
                    "user_id": user_id, "bin": bin_number, "address": safe_address,
                    "device_list": devices, "job_description": job_desc
                }, on_conflict="user_id, bin").execute()
            except:
                pass

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
    user_id = session.get('user_id')
    user_client = get_user_supabase()

    if not user_client:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        user_client.table("projects").delete().eq("id", project_id).eq("user_id", user_id).execute()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
        
# ==========================================
# RUTAS DE API: PADDLE WEBHOOK (PAGOS)
# ==========================================
@app.route('/api/paddle-webhook', methods=['POST'])
def paddle_webhook():
    try:
        # 1. Recibir los datos que manda Paddle
        data = request.json
        
        event_type = data.get('event_type')
        print(f"🔔 Webhook de Paddle recibido: {event_type}")

        # 2. Si es un pago exitoso o se creó la suscripción
        if event_type in ['transaction.completed', 'subscription.created']:
            
            # Navegar por el JSON de Paddle para sacar el user_id
            event_data = data.get('data', {})
            custom_data = event_data.get('custom_data', {})
            user_id = custom_data.get('user_id')
            
            if user_id and supabase:
                # 3. ¡Actualizar al usuario a PRO en Supabase!
                supabase.table("user_subscriptions").upsert({
                    "user_id": user_id,
                    "plan_type": "pro",
                    "updated_at": "now()"
                }).execute()
                
                print(f"✅ ¡ÉXITO! Usuario {user_id} actualizado a plan PRO.")
            else:
                print("⚠️ No se encontró user_id en custom_data.")
                
        return jsonify({"status": "received"}), 200

    except Exception as e:
        print(f"❌ Error en Webhook de Paddle: {str(e)}")
        return jsonify({"error": str(e)}), 500        

# ==========================================
# RUTA DE DIAGNÓSTICO (SOLO PARA DEBUG)
# ==========================================
@app.route('/api/debug/test-apis')
def test_apis():
    """
    Endpoint de diagnóstico. Llama a todas las APIs externas y reporta
    qué está funcionando y qué no. Visitar en browser: /api/debug/test-apis
    """
    import traceback
    results = {}
    BIN_TEST = "1007239"  # 54 Crosby St - BIN conocido para pruebas

    # --- 1. Variables de entorno ---
    results["env_vars"] = {
        "NYC_API_KEY": "✅ SET" if main.API_KEY_NYC else "❌ MISSING",
        "NYC_API_KEY_length": len(main.API_KEY_NYC) if main.API_KEY_NYC else 0,
        "SOCRATA_TOKEN": "✅ SET" if main.APP_TOKEN_SOCRATA else "⚠️ MISSING (optional but recommended)",
        "SUPABASE_URL": "✅ SET" if os.environ.get("SUPABASE_URL") else "❌ MISSING",
        "SUPABASE_KEY": "✅ SET" if os.environ.get("SUPABASE_KEY") else "❌ MISSING",
    }

    # --- 2. Test Geoclient ---
    try:
        import requests as req
        r = req.get(
            "https://api.nyc.gov/geoclient/v2/bin",
            params={"bin": BIN_TEST},
            headers={"Ocp-Apim-Subscription-Key": main.API_KEY_NYC},
            timeout=10
        )
        if r.status_code == 200:
            d = r.json().get("bin", {})
            results["geoclient"] = {
                "status": "✅ OK",
                "http_code": r.status_code,
                "address_found": f"{d.get('giLowHouseNumber1','')} {d.get('giStreetName1','')}".strip(),
                "bbl": d.get("bbl", ""),
                "borough": d.get("firstBoroughName", ""),
            }
        else:
            results["geoclient"] = {
                "status": "❌ FAILED",
                "http_code": r.status_code,
                "response_preview": r.text[:300]
            }
    except Exception as e:
        results["geoclient"] = {"status": "❌ EXCEPTION", "error": str(e)}

    # --- 3. Test PLUTO por BBL (necesita BBL de Geoclient primero) ---
    bbl_from_geoclient = results.get("geoclient", {}).get("bbl", "")
    try:
        headers_soc = {"X-App-Token": main.APP_TOKEN_SOCRATA}
        pluto_params = {"bbl": bbl_from_geoclient} if bbl_from_geoclient else {"bin": BIN_TEST}
        r = req.get(
            "https://data.cityofnewyork.us/resource/64uk-42ks.json",
            params={**pluto_params, "$limit": 1},
            headers=headers_soc, timeout=10
        )
        if r.status_code == 200 and r.json():
            p = r.json()[0]
            results["pluto"] = {
                "status": "✅ OK",
                "http_code": r.status_code,
                "query_used": f"bbl={bbl_from_geoclient}" if bbl_from_geoclient else "bin fallback",
                "yearbuilt":  p.get("yearbuilt"),
                "numfloors":  p.get("numfloors"),
                "bldgclass":  p.get("bldgclass"),
                "zipcode":    p.get("zipcode"),
                "bbl":        p.get("bbl"),
                "ownername":  p.get("ownername"),
                "histdist":   p.get("histdist"),
                "xcoord":     p.get("xcoord"),
                "ycoord":     p.get("ycoord"),
            }
        elif r.status_code == 200:
            results["pluto"] = {"status": "⚠️ OK but NO DATA", "http_code": 200, "query": str(pluto_params)}
        else:
            results["pluto"] = {"status": "❌ FAILED", "http_code": r.status_code, "response": r.text[:200]}
    except Exception as e:
        results["pluto"] = {"status": "❌ EXCEPTION", "error": str(e)}

    # --- 4. Test BIS ---
    try:
        r = req.get(
            "https://data.cityofnewyork.us/resource/ic3t-wcy2.json",
            params={"bin__": BIN_TEST, "$limit": 2},
            headers=headers_soc, timeout=10
        )
        if r.status_code == 200 and r.json():
            jobs = r.json()
            j = jobs[0]
            results["bis"] = {
                "status": "✅ OK",
                "http_code": r.status_code,
                "jobs_found": len(jobs),
                "sample_height": j.get("existing_height"),
                "sample_stories": j.get("existingno_of_stories"),
                "sample_const_class": j.get("existing_construction_class"),
                "sample_occupancy": j.get("existing_occupancy"),
                "sample_owner": j.get("owner_s_business_name"),
            }
        elif r.status_code == 200:
            results["bis"] = {"status": "⚠️ OK but NO JOBS for this BIN", "http_code": 200}
        else:
            results["bis"] = {"status": "❌ FAILED", "http_code": r.status_code}
    except Exception as e:
        results["bis"] = {"status": "❌ EXCEPTION", "error": str(e)}

    # --- 5. Test DOB NOW ---
    try:
        r = req.get(
            "https://data.cityofnewyork.us/resource/w9ak-ipjd.json",
            params={"bin": BIN_TEST, "$limit": 1},
            headers=headers_soc, timeout=10
        )
        if r.status_code == 200 and r.json():
            j = r.json()[0]
            results["dob_now"] = {
                "status": "✅ OK",
                "http_code": r.status_code,
                "owner_business": j.get("owner_s_business_name"),
                "owner_first": j.get("owner_first_name"),
                "owner_last": j.get("owner_last_name"),
                "job_number": j.get("job_filing_number"),
            }
        elif r.status_code == 200:
            results["dob_now"] = {"status": "⚠️ OK but NO DATA for this BIN", "http_code": 200}
        else:
            results["dob_now"] = {"status": "❌ FAILED", "http_code": r.status_code}
    except Exception as e:
        results["dob_now"] = {"status": "❌ EXCEPTION", "error": str(e)}

    # --- 6. Test PAD fallback ---
    try:
        r = req.get(
            "https://data.cityofnewyork.us/resource/w4v2-rv29.json",
            params={"bin": BIN_TEST, "$limit": 1},
            headers=headers_soc, timeout=10
        )
        if r.status_code == 200 and r.json():
            p = r.json()[0]
            results["pad_fallback"] = {
                "status": "✅ OK",
                "http_code": r.status_code,
                "bbl": p.get("bbl"),
                "address": p.get("address") or f"{p.get('lhnd','')} {p.get('stname','')}",
            }
        elif r.status_code == 200:
            results["pad_fallback"] = {"status": "⚠️ OK but NO DATA", "http_code": 200}
        else:
            results["pad_fallback"] = {"status": "❌ FAILED", "http_code": r.status_code}
    except Exception as e:
        results["pad_fallback"] = {"status": "❌ EXCEPTION", "error": str(e)}

    # --- 7. Diagnóstico final ---
    all_ok = all("✅" in str(v.get("status","")) for v in results.values() if isinstance(v, dict) and "status" in v)
    results["_summary"] = "✅ ALL SYSTEMS OK" if all_ok else "⚠️ SOME APIS HAVE ISSUES — check individual results above"
    results["_test_bin"] = BIN_TEST
    results["_test_address"] = "54 CROSBY STREET, MANHATTAN"

    return jsonify(results), 200

# ==========================================
# INICIO
# ==========================================
if __name__ == '__main__':
    app.run(debug=True)
