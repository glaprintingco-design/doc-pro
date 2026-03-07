import json
import os
import sys
import datetime
import requests
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, BooleanObject, NumberObject

# ==========================================
# 0. CONFIGURATION LOADER (WEB & LOCAL)
# ==========================================
import streamlit as st

def load_configuration():
    try:
        if hasattr(st, "secrets") and len(st.secrets) > 0:
            # Usamos dict() para crear una copia editable y evitar el error de "Read Only"
            return {
                "api_keys": dict(st.secrets.get("api_keys", {})),
                "fire_alarm_company": dict(st.secrets.get("fire_alarm_company", {})),
                "architect_applicant": dict(st.secrets.get("architect_applicant", {})),
                "electrical_contractor": dict(st.secrets.get("electrical_contractor", {})),
                "technical_defaults": dict(st.secrets.get("technical_defaults", {})),
                "central_station": dict(st.secrets.get("central_station", {}))
            }
    except Exception:
        pass 

    # 2. INTENTAR CARGAR DESDE ARCHIVO LOCAL (FALLBACK)
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    json_path = os.path.join(base_path, "config.json")
    
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    
    return {}

CONFIG_DATA = load_configuration()

# Cargar variables globales desde el diccionario unificado
API_KEY_NYC = CONFIG_DATA.get("api_keys", {}).get("nyc_open_data_key", "")
APP_TOKEN_SOCRATA = CONFIG_DATA.get("api_keys", {}).get("nyc_socrata_token", "")

COMPANY = CONFIG_DATA.get("fire_alarm_company", {})
ARCHITECT = CONFIG_DATA.get("architect_applicant", {})
ELECTRICIAN = CONFIG_DATA.get("electrical_contractor", {})
TECH_DEFAULTS = CONFIG_DATA.get("technical_defaults", {})
CENTRAL_STATION = CONFIG_DATA.get("central_station", {})

fecha_hoy = datetime.date.today().strftime("%m/%d/%Y")

# ==========================================
# LISTAS MAESTRAS DEL A-433 (LA "BASE DE DATOS" OFICIAL)
# ==========================================

# 1. PISOS (Ordenados lógicamente para el PDF)
FULL_FLOOR_LIST = [
    "Sub Cellar", "Sub Cellar #1", "Sub Cellar #2", "Sub Cellar #3", "Sub Cellar #4", "Sub Cellar #5",
    "Sub Cellar #6", "Sub Cellar #7", "Sub Cellar #8", "Sub Cellar #9", "Sub Cellar #10",
    "Cellar", "Sub Basement", "Basement", "Vault Space", "Elevator Pit", "Escalator Pit",
    "Dining Hall", "Arcade", 
    "Parking Level #1", "Parking Level #2", "Parking Level #3", "Parking Level #4", "Parking Level #5",
    "Parking Level #6", "Parking Level #7", "Parking Level #8", "Parking Level #9", "Parking Level #10",
    "Ground Floor", "Mall", "Lower Concourse", "Concourse", "Upper Concourse",
    "Stage", "Auditorium", "Gymnasium", "Conference Hall", "Atrium", "Annex", "Concert Hall",
    "Theater", "Ball Room", "Meeting Hall", "Stadium Level", "Lecture Hall", "Catering Hall",
    "Mezz Between 1 & 2 Flrs", "Mezz Between 2 & 3 Flrs", "Mezz Between 3 & 4 Flrs",
    "1st Floor", "1st Floor Mezzanine", "2nd Floor", "2nd Floor Mezzanine",
    "Lower Lobby", "Lobby", "Upper Lobby", "Sky Lobby", "Balcony", "Upper Balcony",
    "3rd Floor", "3rd Floor Mezzanine", "4th Floor", "5th Floor", "6th Floor", "7th Floor", "8th Floor", "9th Floor",
    "10th Floor", "11th Floor", "12th Floor", "13th Floor", "14th Floor", "15th Floor", "16th Floor", "17th Floor",
    "18th Floor", "19th Floor", "20th Floor", "21st Floor", "22nd Floor", "23rd Floor", "24th Floor", "25th Floor",
    "26th Floor", "27th Floor", "28th Floor", "29th Floor", "30th Floor", "31st Floor", "32nd Floor", "33rd Floor",
    "34th Floor", "35th Floor", "36th Floor", "37th Floor", "38th Floor", "39th Floor", "40th Floor", "41st Floor",
    "42nd Floor", "43rd Floor", "44th Floor", "45th Floor", "46th Floor", "47th Floor", "48th Floor", "49th Floor",
    "50th Floor", "51st Floor", "52nd Floor", "53rd Floor", "54th Floor", "55th Floor", "56th Floor", "57th Floor",
    "58th Floor", "59th Floor", "60th Floor", "61st Floor", "62nd Floor", "63rd Floor", "64th Floor", "65th Floor",
    "66st Floor", "66th Floor", "67th Floor", "68th Floor", "69th Floor", "70th Floor", "71st Floor", "72nd Floor",
    "73rd Floor", "74th Floor", "75th Floor", "76th Floor", "77th Floor", "78th Floor", "79th Floor", "80th Floor",
    "81st Floor", "82nd Floor", "83rd Floor", "84th Floor", "85th Floor", "86th Floor", "87th Floor", "88th Floor",
    "89th Floor", "90th Floor", "91st Floor", "92nd Floor", "93rd Floor", "94th Floor", "95th Floor", "96th Floor",
    "97th Floor", "98th Floor", "99th Floor", "100th Floor", "101st Floor", "102nd Floor", "103rd Floor", "104th Floor",
    "105th Floor", "106th Floor", "107th Floor", "108th Floor", "109th Floor", "110th Floor", "111th Floor", "112th Floor",
    "113th Floor", "114th Floor", "115th Floor", "116th Floor", "117th Floor", "118th Floor", "119th Floor", "120th Floor",
    "Mechanical Floor", "Penthouse", "Upper Penthouse", "Penthouse #1", "Penthouse #2", "Penthouse #3",
    "Stair Bulkhead", "Stairwell", "Elevator Shaft", "Passenger Elevator Shaft", "Freight Elevator Shaft",
    "Emergency FD Elevator Shaft", "Passenger Elevator", "Freight Elevator", "Emergency FD Elevator",
    "Compactor Shaft", "Space", "Attic", "Roof", "Roof Observation Deck", "Roof Deck", "Roof Pool",
    "Roof Health Club", "Roof Machine Room", "Roof Elevator Room", "Roof Tank Room", "Clock Tower",
    "Tower", "Fire Tower", "Antenna Room"
]

# 2. DISPOSITIVOS (Clasificados para la lógica del PDF)
MASTER_DEVICE_LIST = {
    "Initiating": [
        "Manual Pull Station", "Code Manual Pull Station", "Class 3 Manual Pull Station",
        "Water Flow Vane Switch", "Water Flow Pressure Switch", "Pressure Switch",
        "Smoke Detector", "Photo Electric Smoke Detector", "Ionization Smoke Detector",
        "Smoke Detector & Heat Detector", "Duct Smoke Detector", "Multi Criteria Detector",
        "Multi Sensor Detector", "Fixed Temperature Heat Detector", "Rate of Rise Heat Detector",
        "Fixed & Rate Of Rise Heat Detector", "Rate Compensated Heat Detector", "Linear Heat Detector",
        "Carbon Monoxide Detector", "Flame Detector", "Spark Detector", "Air Sampling Detection",
        "Beam Smoke Detector", "Gas Detector Sensor", "Natural Gas Detector Sensor",
        "Remote Indicator", "Video Image Smoke Detector Camera"
    ],
    "Supervisory": [
        "Valve Tamper Switch", "Pit Tamper Switch", "OS&Y Tamper Switch", "Wall Valve Tamper Switch",
        "Built In Valve Tamper Switch", "Post Indicator Valve TS", "Butter Fly Valve TS",
        "Gate Valve Tamper Switch", "Low Rising Stem Valve Tamper Switch", "High/Low Air Switch",
        "Low Air Switch", "High/Low Water Switch", "Tank Temperature Switch", "Room Temperature Switch",
        "Low Temperature Switch", "Low Room Temperature Switch", "Tank Low Temperature Switch",
        "Pump Running", "Pump Power Failure", "Phase Reversal", "Generator Running",
        "Generator Failure", "Generator Low Fuel", "Generator Low Oil Pressure", "UPS Failure",
        "UPS Battery Failure", "Fire Pump", "Combination Fire Pump", "Special Service Pump",
        "Sprinkler Booster Pump", "Automatic Standpipe Fire Pump", "Manual Standpipe Fire Pump"
    ],
    "Control": [
        "Fire Door Holder", "Fire Shutter Release", "FIre Damper Control", "Fire Damper",
        "Smoke Damper", "Damper", "Shutter", "Exhaust Damper", "Release", "Elevator Recall",
        "HVAC Shut Down", "Fire Suppression Release","Isolation Module", "Access Control Release", "Fire Door Release",
        "Automatic Smoke Exhaust", "BMS Signal", "Release Control Activation", "Auxillary Relay Operation",
        "Fossil Fuel Shutdown", "Natural Gas Shutdown"
    ],
    "Signals": [
        "Horn", "Vibrating Bell", "Signal Stroke Bell", "Chime", "Multi Electronic Sounder",
        "Sounder Base", "Mini Sounder", "Speaker", "Horn Strobe", "Vibrating Bell Strobe",
        "Single Stroke Bell Strobe", "Chime Strobe", "Multi Electronic Sounder Strobe",
        "Speaker Strobe", "Strobe", "Auxiliary Audible Signal", "Auxiliary Visual Signal"
    ],
    "Communication": [
        "Warden Telephone", "Warden Jack", "Warden Telephone Extended Hand Set",
        "Remote Microphone", "Strap Key Station", "Remote Antenna", "Radio Repeater",
        "Radio Transmitter", "Radio Receiver", "Radio Signal Booster", "Radio Antenna"
    ],
    "Firepanel": [ # Nota: En el PDF se llama 'Fire & Control Panels' pero la lógica usa 'Firepanel'
        "Fire Alarm Control", "Fire Command Center", "Secondary Fire Command Center",
        "Smoke Detection Control", "Heat Detection Control", "Fire Sprinkler Control",
        "Flame Detection Control", "Special Hazard Control", "Video Image Smoke Control",
        "Tank Alarm Control", "Gas Alarm Control", "Medical Gas Alarm Control",
        "Smoke Purge Control", "Smoke Control Panel", "Data Gathering Panel",
        "Network Sub Control", "Sub Amplifier", "Sub Panel", "Auxiliary Power Supply",
        "Signal Power Booster", "Auxiliary Battery Charger", "One Way Voice Com Control",
        "Warden Telephone Control", "Remote Annunciator", "Graphic Annunciator",
        "Detector Address Map", "Uninterrupted Power Suppy", "Central Station Transmitter",
        "Radiating Cable System", "Distributed Antenna System", "Repeater/Simplex System"
    ]
}

# --- GENERACIÓN AUTOMÁTICA DEL MAPA DE CATEGORÍAS ---
# Esto permite que main.py sepa automáticamente que "Spark Detector" es "Initiating"
CATEGORIAS = {}
for cat, devices in MASTER_DEVICE_LIST.items():
    for dev in devices:
        CATEGORIAS[dev] = cat

# Rangos de filas en el PDF A-433
RANGOS = {
    'Initiating': (1, 10),
    'Supervisory': (11, 20),
    'Control': (21, 25),
    'Signals': (26, 30),
    'Communication': (31, 35),
    'Firepanel': (36, 40)
}

# ==========================================
# 1. TRANSLATION & INTELLIGENCE ENGINE
# ==========================================
def traducir_datos(ocupacion_old, construccion_old, job_description="", building_class_tax=""):
    # (El código de traducción se mantiene igual, abreviado aquí por espacio)
    # ... COPIA TU FUNCIÓN traducir_datos AQUÍ ...
    # Si quieres te la pego completa, pero es la misma de la V19.
    # Para asegurar que funcione, usaré la versión completa abajo:
    occ = str(ocupacion_old or "").upper().strip()
    const = str(construccion_old or "").upper().strip()
    desc = str(job_description or "").upper()
    tax_class = str(building_class_tax or "").upper().strip()
    
    res = {"occ": occ, "const": const, "nota": ""}

    mapa_numerico = {"1": "I-B", "2": "II-B", "3": "III-B", "4": "V-B", "5": "II-B", "6": "IV-HT"}
    codigos_validos = ["I-A", "I-B", "I-C", "I-D", "I-E", "II-A", "II-B", "II-C", "II-D", "II-E", "III-A", "III-B", "IV-HT", "V-A", "V-B"]

    if const in mapa_numerico:
        res["const"] = mapa_numerico[const]; res["nota"] += f"[Const: Translated {const}->{res['const']}] "
    elif const in codigos_validos:
        res["const"] = const; res["nota"] += f"[Const: Code {const} maintained] "
    elif not const:
        if tax_class.startswith("R") or tax_class.startswith("D"): res["const"] = "I-C"; res["nota"] += "[Const: Auto I-C via Residential Tax Class] "
        elif tax_class.startswith("C") or tax_class.startswith("S"): res["const"] = "III-B"; res["nota"] += "[Const: Auto III-B via Walk-up Tax Class] "
        elif tax_class.startswith("K") or tax_class.startswith("O"): res["const"] = "I-B"; res["nota"] += "[Const: Auto I-B via Commercial Tax Class] "
        else: res["const"] = "III-B"; res["nota"] += "[Const: Auto III-B default] "
    else: res["nota"] += f"[Const: Unknown value '{const}' maintained] "

    mapa_occ = {"J-1": "R-1", "J-2": "R-2", "J-3": "R-3", "RES": "R-2", "PUB": "A-3", "COM": "M", "C": "M", "E": "B", "D-1": "F-1", "D-2": "F-2", "F-1A": "A-1", "F-1B": "A-3", "F-2": "A-5", "F-3": "A-3", "F-4": "A-2", "G": "E"}
    modernos = ["A-1", "A-2", "A-3", "A-4", "A-5", "B", "E", "F-1", "F-2", "H-1", "H-2", "H-3", "H-4", "H-5", "I-1", "I-2", "I-3", "I-4", "M", "R-1", "R-2", "R-3", "S-1", "S-2", "U"]

    if occ in mapa_occ: res["occ"] = mapa_occ[occ]; res["nota"] += f"[Occ: Translated {occ}->{res['occ']}]"
    elif occ in modernos: res["occ"] = occ; res["nota"] += f"[Occ: Code {occ} maintained]"
    elif not occ or occ == "COM":
        if any(tax_class.startswith(k) for k in ["C", "D", "R", "L"]): res["occ"] = "R-2"; res["nota"] += "[Occ: Auto R-2 via Tax Class]"
        elif tax_class.startswith("S"): res["occ"] = "R-3"; res["nota"] += "[Occ: Auto R-3 via Tax Class]"
        elif tax_class.startswith("K") or tax_class.startswith("O"): res["occ"] = "B"; res["nota"] += "[Occ: Auto B (Office) via Tax Class]"
        elif tax_class.startswith("P"): res["occ"] = "A-3"; res["nota"] += "[Occ: Auto A-3 (Public) via Tax Class]"
        else: res["nota"] += "[Occ: No data, left blank]"
    else: res["nota"] += f"[Occ: Atypical value '{occ}' maintained]"

    if any(x in desc for x in ["WORSHIP", "SYNAGOGUE", "CHURCH", "TEMPLE"]):
        if res["occ"] in ["E", "G", "F-1B", "", "F-3", "M", "COM", "B", "R-2", "R-3"]:
            old_occ = res["occ"]; res["occ"] = "A-3"; res["nota"] += f" [Auto: Corrected {old_occ}->A-3 via religious keywords]"
    return res

# ==========================================
# 2. FETCH DATA
# ==========================================
def consultar_dob_now(bin_number, headers_soc):
    print(f"   🚀 Querying DOB NOW (Fresh Data)...")
    dob_now_data = {}
    try:
        r = requests.get("https://data.cityofnewyork.us/resource/w9ak-ipjd.json", 
                         params={"bin": bin_number, "$order": "filing_date DESC", "$limit": 1}, headers=headers_soc)
        if r.status_code == 200 and r.json():
            job = r.json()[0]
            print(f"      ✅ Found Recent Job: {job.get('job_filing_number')}")
            dob_now_data["owner_business"] = job.get("owner_s_business_name", "").strip()
            dob_now_data["owner_first"] = job.get("owner_first_name", "").strip() 
            dob_now_data["owner_last"] = job.get("owner_last_name", "").strip()
            dob_now_data["owner_email"] = job.get("owner_email", "").strip()
            dob_now_data["owner_phone"] = job.get("owner_phone", "").strip()
            addr_st = job.get("owner_s_street_name", "").strip()
            addr_no = job.get("owner_s_house_number", "").strip()
            if addr_st:
                dob_now_data["owner_address"] = f"{addr_no} {addr_st}".strip()
                dob_now_data["owner_city"] = job.get("owner_s_city", job.get("city", "")).strip()
                dob_now_data["owner_zip"] = job.get("owner_s_zip", job.get("zip", "")).strip()
                dob_now_data["owner_state"] = job.get("state", "NY")
            return dob_now_data
    except: pass
    return None

def buscar_co_dob_now(bin_number, headers_soc):
    try:
        r = requests.get("https://data.cityofnewyork.us/resource/bs8b-p36n.json", 
                         params={"bin": bin_number, "$limit": 1}, headers=headers_soc)
        if r.status_code == 200 and r.json(): return True
    except: pass
    return False

def obtener_datos_completos(bin_number):
    print(f"📡 1. Fetching master data for BIN: {bin_number}...")
    
    # Estructura base de datos
    info = {
        "bin": bin_number, "house": "", "street": "", "borough": "", "zip": "", 
        "block": "", "lot": "", "bbl_full": "", "tax_class": "",
        "stories": "", "height": "", "occupancy_group": "", "construction_class": "", 
        "landmarked": "No", "flood_zone": "No", 
        "owner_first": "", "owner_last": "", "owner_business": "", "owner_address": "", 
        "owner_phone": "", "owner_email": "", "owner_city": "", "owner_state": "NY", 
        "owner_zip": "", "has_digital_co": False
    }

    headers_socrata = {"X-App-Token": APP_TOKEN_SOCRATA}
    
    # --- NIVEL 1: GEOCLIENT (Dirección Oficial) ---
    try:
        # Importante: API_KEY_NYC debe ser inyectada desde app.py usando st.secrets
        url_geo = "https://api.nyc.gov/geoclient/v2/bin"
        r_geo = requests.get(url_geo, params={"bin": bin_number}, 
                             headers={"Ocp-Apim-Subscription-Key": API_KEY_NYC}, timeout=10)
        
        if r_geo.status_code == 200:
            d = r_geo.json().get('bin', {})
            # Usamos .strip() para evitar espacios que rompan el PDF
            info["house"] = (d.get("giLowHouseNumber1") or d.get("houseNumber", "")).strip()
            info["street"] = (d.get("giStreetName1") or d.get("streetName", "")).strip()
            info["borough"] = d.get("firstBoroughName", "").strip()
            info["block"] = d.get("bblTaxBlock", "").strip()
            info["lot"] = d.get("bblTaxLot", "").strip()
            info["bbl_full"] = d.get("bbl", "").strip()
            info["tax_class"] = d.get("rpadBuildingClassificationCode", "").strip()
            print(f"   ✅ [Geoclient] Address Found: {info['house']} {info['street']}")
        else:
            print(f"   ⚠️ [Geoclient] Error {r_geo.status_code}: Verify NYC API Key.")
            
    except Exception as e:
        print(f"   ❌ [Geoclient] Connection failed: {e}")

    # --- NIVEL 2: PLUTO / SOCRATA (Respaldo de Dirección y ZIP) ---
    if info["bbl_full"]:
        try:
            r_pluto = requests.get("https://data.cityofnewyork.us/resource/64uk-42ks.json", 
                                 params={"bbl": info["bbl_full"]}, headers=headers_socrata, timeout=10)
            if r_pluto.status_code == 200 and r_pluto.json():
                pluto = r_pluto.json()[0]
                info["zip"] = str(pluto.get("zipcode", "")).strip()
                if pluto.get("pfirm15_flag") == "1": info["flood_zone"] = "Yes"
                info["owner_business_backup"] = pluto.get("ownername", "").strip()
                if not info["tax_class"]: info["tax_class"] = pluto.get("bldgclass", "").strip()
                
                # FALLBACK: Si Geoclient falló, intentamos reconstruir la dirección desde PLUTO
                if not info["house"] and pluto.get("address"):
                    addr_raw = pluto.get("address").split(" ", 1)
                    info["house"] = addr_raw[0]
                    info["street"] = addr_raw[1] if len(addr_raw) > 1 else ""
                    print(f"   🔄 [PLUTO] Address recovered via BBL: {info['house']} {info['street']}")
        except Exception as e:
            print(f"   ⚠️ [PLUTO] Fallback failed: {e}")

    # --- CONSULTAS DE DOB NOW (Dueños y C.O.) ---
    dob_now_info = consultar_dob_now(bin_number, headers_socrata)
    if dob_now_info: info.update(dob_now_info)
    if buscar_co_dob_now(bin_number, headers_socrata): info["has_digital_co"] = True

    # --- NIVEL 3: ESCANEO HISTÓRICO BIS (Para Altura, Pisos y Dueños antiguos) ---
    print(f"   📡 [BIS] Scanning job history...")
    try:
        r_bis = requests.get("https://data.cityofnewyork.us/resource/ic3t-wcy2.json", 
                           params={"bin__": bin_number, "$order": "latest_action_date DESC", "$limit": 50}, 
                           headers=headers_socrata, timeout=10)
        if r_bis.status_code == 200:
            jobs = r_bis.json()
            raw_h, raw_s, raw_c, raw_o, desc = "0", "0", "", "", ""
            
            for job in jobs:
                # Si aún no tenemos dueño, lo buscamos en el historial
                if not info["owner_business"] and not info["owner_last"]:
                    bn = str(job.get("owner_s_business_name") or "").strip()
                    if bn:
                        info["owner_business"] = bn
                        info["owner_first"] = str(job.get("owner_s_first_name") or "").strip()
                        info["owner_last"] = str(job.get("owner_s_last_name") or "").strip()
                        info["owner_phone"] = str(job.get("owner_sphone__") or "").replace("-","")
                        oh = job.get("owner_s_house_number", ""); os = job.get("owner_s_street_name", "")
                        # Si no hay dirección de dueño, usamos la de la propiedad
                        info["owner_address"] = f"{oh} {os}" if oh else f"{info['house']} {info['street']}"
                        info["owner_city"] = job.get("owner_s_city", info["borough"])
                        info["owner_zip"] = job.get("owner_s_zip", info["zip"])

                # Datos técnicos
                if raw_h == "0": raw_h = str(job.get("existing_height") or "0")
                if raw_s == "0": raw_s = str(job.get("existingno_of_stories") or "0")
                if not raw_c: raw_c = job.get("existing_construction_class", "")
                if not raw_o: raw_o = job.get("existing_occupancy", "")
                desc += " " + str(job.get("job_description") or "")
                if info["landmarked"] == "No" and job.get("landmarked") in ["Y", "YES"]: info["landmarked"] = "Yes"

            info["height"], info["stories"] = raw_h, raw_s
            
            # Traducción inteligente (Asegúrate de tener esta función en main.py)
            trad = traducir_datos(raw_o, raw_c, desc, info["tax_class"])
            info["occupancy_group"] = trad["occ"]
            info["construction_class"] = trad["const"]
            info["raw_occupancy"], info["raw_construction_class"] = raw_o, raw_c
            info["debug_nota_occ"] = info["debug_nota_const"] = trad["nota"]
    except Exception as e:
        print(f"   ⚠️ [BIS] History scan error: {e}")

    # Limpieza final
    if not info["owner_business"]: 
        info["owner_business"] = info.get("owner_business_backup", "")
        
    return info
    
    from pypdf.generic import TextStringObject

def fix_adobe_visibility(writer, campos):
    """
    Asegura que Adobe/Nitro regeneren la visualización del texto.
    """
    # 1. Forzamos al lector a generar apariencias nuevas
    if "/AcroForm" not in writer.root_object:
        writer.root_object.update({
            NameObject("/AcroForm"): writer._add_object(DictionaryObject())
        })
    
    writer.root_object["/AcroForm"].update({
        NameObject("/NeedAppearances"): BooleanObject(True)
    })

    # 2. Limpiamos flujos de apariencia viejos para cada campo mapeado
    for page in writer.pages:
        if "/Annots" in page:
            for annot in page["/Annots"]:
                obj = annot.get_object()
                if obj.get("/T") in campos:
                    # Si existe un flujo de apariencia (/AP), lo borramos
                    # Esto obliga a Adobe a usar el valor (/V) para crear uno nuevo
                    if "/AP" in obj:
                        del obj["/AP"]
    
    
# ==========================================
# 3. GENERADOR TM-1
# ==========================================
def generar_tm1(datos, input_pdf, output_pdf):
    print(f"📄 2. Generating TM-1...")
    try:
        reader = PdfReader(input_pdf); writer = PdfWriter()
        for p in reader.pages: writer.add_page(p)
        if "/AcroForm" in reader.root_object: writer.root_object[NameObject("/AcroForm")] = reader.root_object["/AcroForm"]
        writer.root_object["/AcroForm"][NameObject("/NeedAppearances")] = BooleanObject(True)

        lm_yes = "/On" if datos["landmarked"] == "Yes" else "/Off"
        lm_no  = "/On" if datos["landmarked"] == "No" else "/Off"
        fl_yes = "/On" if datos["flood_zone"] == "Yes" else "/Off"
        fl_no  = "/On" if datos["flood_zone"] == "No" else "/Off"

        campos = {
            "Last Name_3": datos["owner_last"], "First Name_2": datos["owner_first"],
            "Business Name_4": datos["owner_business"], "Business Address_3": datos["owner_address"],
            "City_3": datos["owner_city"], "State_3": datos["owner_state"], "Zip_3": datos["owner_zip"],
            "Business Tel_2": datos["owner_phone"], "Mobile Tel": datos["owner_phone"], "EMail_3": datos["owner_email"],
            "Classification": datos["construction_class"], 
            "Stories": datos["stories"], "Height ft": datos["height"],
            "Building Dominant Occupancy Group": datos["occupancy_group"],
            "Occupancy classification of the area of work": datos["occupancy_group"],
            "undefined_18": lm_yes, "undefined_181": lm_no, "undefined_19": fl_yes, "undefined_191": fl_no,
            "Initial Filing Date": fecha_hoy, "Total Fee": "585.00", "NEW SUBMISSION": "/On",
            "Fire AlarmFire SuppressionARCS Electrical": "/On", "undefined": "/On",
            "BIN": datos["bin"], "Building No": datos["house"], "Street Name": datos["street"],
            "Borough": datos["borough"], "Block": datos["block"], "Lot": datos["lot"], "ZIP": datos["zip"],
            "Job Description": datos.get("job_desc", ""),
            "Last Name": ARCHITECT.get("Last Name"), "Firstname": ARCHITECT.get("First Name"),
            "Business Name_2": ARCHITECT.get("Company Name"), "Business Address": ARCHITECT.get("Address"),
            "City": ARCHITECT.get("City"), "State": ARCHITECT.get("State"), "Zip": ARCHITECT.get("Zip"),
            "bsn_phone": str(ARCHITECT.get("Phone")), "EMail": ARCHITECT.get("Email"), 
            "License Number": ARCHITECT.get("License No"), "undefined_5": "/On",
            "Lastnamefilingrep": COMPANY.get("Last Name"), "firstnamefilingrep": COMPANY.get("First Name"),
            "Filing Rep Tel": COMPANY.get("Phone"), "Reg No": COMPANY.get("Reg No"),
            "Business Name_3": COMPANY.get("Company Name"), "Business Address_2": COMPANY.get("Address"),
            "City_2": COMPANY.get("City"), "State_2": COMPANY.get("State"), "Zip_2": COMPANY.get("Zip"),
            "EMail_2": COMPANY.get("Email"), "undefined_16": "/On", "2025": "/On", "Code Section": "BC 907"
        }
        for i in range(len(writer.pages)): writer.update_page_form_field_values(writer.pages[i], campos)
        fix_adobe_visibility(writer, campos)
        with open(output_pdf, "wb") as f: writer.write(f)
        print("   ✅ TM-1 Generated.")
    except Exception as e: print(f"   ❌ TM-1 Error: {e}")

# ==========================================
# 4. GENERADOR A-433 (EL MÁS IMPORTANTE)
# ==========================================
def obtener_cols_derecha(fila, categoria, idx):
    if fila == 1: m, a = "Manufacturer", "BSA MEA COA or Agency Approval"
    elif 2 <= fila <= 16: m, a = f"Manufacturer_{fila}", f"BSA MEA COA or Agency Approval_{fila}"
    else: m, a = f"ManufacturerRow{fila}", f"BSA MEA COA or Agency Approval Row{fila}"
    
    if categoria == 'Initiating': g, t = f"WireGuageInitiating{idx}", f"Insulation/WireType-Initiating{idx}"
    elif categoria == 'Supervisory': g, t = f"WireGuageSupervisory{idx}", f"Insulation/WireType-Initiating{10+idx}"
    elif categoria == 'Control': g, t = f"WireGuageControl{idx}", f"Insulation/WireType-Control{idx}"
    elif categoria == 'Signals': g, t = f"WireGuageSignals{idx}", f"Insulation/WireType-Signals{idx}"
    elif categoria == 'Firepanel': g, t = f"WireGuageFireAlarmControl{idx}", f"Insulation/WireType-Control&Fire{idx}"
    else: g, t = None, None
    return m, a, g, t

def generar_a433(datos, input_pdf, output_pdf):
    print("📄 3. Generating A-433...")
    try:
        reader = PdfReader(input_pdf); writer = PdfWriter()
        for p in reader.pages: writer.add_page(p)
        if "/AcroForm" in reader.root_object: writer.root_object[NameObject("/AcroForm")] = reader.root_object["/AcroForm"]
        writer.root_object["/AcroForm"][NameObject("/NeedAppearances")] = BooleanObject(True)
        
        datos_instalacion = datos.get("devices", [])
        
        # --- ORDENAMIENTO DE PISOS INTELIGENTE ---
        # Usamos la lista maestra. Si el usuario escribe un piso raro que no está en la lista, lo pone al final.
        def floor_sorter(f_name):
            try: return FULL_FLOOR_LIST.index(f_name)
            except ValueError: return 9999
            
        pisos_trabajados = sorted(list(set(d['floor'] for d in datos_instalacion)), key=floor_sorter)
        
        campos = {}
        campos.update({
            "Building No": datos.get("house", ""), "Street Name": datos.get("street", ""), 
            "Borough": datos.get("borough", ""), "State": "NY", "ZIP": datos.get("zip", ""), 
            "Work on floor(s)": ", ".join(pisos_trabajados), "New": "/On"
        })
        campos.update({
            "Last Name": datos["owner_last"], "First Name": datos["owner_first"],
            "Business_Name": datos["owner_business"], "Business Address": datos["owner_address"],
            "City": datos["owner_city"], "State_2": datos["owner_state"], "Zip": datos["owner_zip"],
            "Business Tel": datos["owner_phone"], "Mobile Tel": datos["owner_phone"], "EMail": datos["owner_email"]
        })

        elec = ELECTRICIAN; emp = COMPANY; cs = CENTRAL_STATION; specs = TECH_DEFAULTS
        campos.update({"First Name_2": elec.get("First Name"), "Last Name_2": elec.get("Last Name"), "Business Name_2": elec.get("Company Name"), "Business Address_2": elec.get("Address"), "City_2": elec.get("City"), "State_3": elec.get("State"), "Zip_2": elec.get("Zip"), "Business Tel_2": elec.get("Phone"), "License Number": elec.get("License No"), "Date of Expiration": elec.get("Expiration")})
        campos.update({"First Name_3": emp.get("First Name"), "Last Name_3": emp.get("Last Name"), "Business Name_3": emp.get("Company Name"), "Business Address_3": emp.get("Address"), "City_3": emp.get("City"), "State_4": emp.get("State"), "Zip_3": emp.get("Zip"), "Business Tel_3": emp.get("Phone"), "COF S97": emp.get("COF S97"), "Date of Expiration_2": emp.get("Expiration")})
        campos.update({"Business Name_4": cs.get("Company Name"), "Station Code": cs.get("CS Code"), "Business Address_4": cs.get("Address"), "City_4": cs.get("City"), "State_5": cs.get("State"), "Zip_4": cs.get("Zip"), "Business Tel_4": cs.get("Phone"), "New_2": "/On"})

        mapa_col = {p: i+1 for i, p in enumerate(pisos_trabajados)}
        for p, i in mapa_col.items(): campos[f'floors{i}'] = p

        dispositivos = sorted(list(set(d['device'] for d in datos_instalacion)))
        fila_actual = {k: v[0] for k, v in RANGOS.items()}
        mapa_fil = {}

        for dev in dispositivos:
            # --- AQUÍ ESTÁ LA MAGIA ---
            # Buscamos en el mapa automático en qué categoría cae el dispositivo
            cat = CATEGORIAS.get(dev, 'Initiating') # Default a Initiating si no se encuentra
            
            r_ini, r_fin = RANGOS[cat]
            f = fila_actual[cat]
            if f > r_fin: continue 

            idx = f - r_ini + 1
            campos[f"{cat}{idx}"] = dev
            mapa_fil[dev] = (f, cat, idx)
            
            m, a, g, t = obtener_cols_derecha(f, cat, idx)
            if m: campos[m] = specs.get('Manufacturer', '')
            if a: campos[a] = specs.get('Approval', '')
            if g: campos[g] = specs.get('WireGauge', '')
            if t: campos[t] = specs.get('WireType', '')
            
            fila_actual[cat] += 1

        totales = {}
        for item in datos_instalacion:
            d, p, q = item['device'], item['floor'], int(item['qty'])
            if d in mapa_fil and p in mapa_col:
                r, cat, idx = mapa_fil[d]
                c = mapa_col[p]
                campos[f"r{r}c{c}"] = str(q)
                totales[r] = totales.get(r, 0) + q

        for r, t in totales.items(): campos[f"r{r}c32"] = str(t)

        for i in range(len(writer.pages)): writer.update_page_form_field_values(writer.pages[i], campos)
        with open(output_pdf, "wb") as f: writer.write(f)
        print("   ✅ A-433 Generated.")
    except Exception as e: print(f"   ❌ A-433 Error: {e}")

# ==========================================
# 5. GENERADOR B-45
# ==========================================
def generar_b45(datos, input_pdf, output_pdf):
    print("📄 4. Generating B-45...")
    try:
        reader = PdfReader(input_pdf); writer = PdfWriter()
        for p in reader.pages: writer.add_page(p)
        if "/AcroForm" in reader.root_object: writer.root_object[NameObject("/AcroForm")] = reader.root_object["/AcroForm"]
        writer.root_object["/AcroForm"][NameObject("/NeedAppearances")] = BooleanObject(True)
        emp = COMPANY
        campos = {
            "adress": f"{datos['house']} {datos['street']}, {datos['borough']}, NY {datos['zip']}",
            "name": f"{emp.get('First Name')} {emp.get('Last Name')}", "title": "Expeditor",
            "lic": emp.get("Reg No"), "company": emp.get("Company Name"), 
            "caddress": f"{emp.get('Address')}, {emp.get('City')}, {emp.get('State')} {emp.get('Zip')}",
            "cphone": emp.get("Phone"), "email": emp.get("Email"), "pname": f"{emp.get('First Name')} {emp.get('Last Name')}", "date1": fecha_hoy
        }
        for i in range(len(writer.pages)):
            writer.update_page_form_field_values(writer.pages[i], campos)
            for annot in writer.pages[i].get("/Annots", []):
                obj = annot.get_object()
                if obj.get("/T") in ["gp1", "gp2", "gp3", "gp4", "gp5", "inspector"]:
                    flags = obj.get("/Ff", 0)
                    if flags & 1: obj[NameObject("/Ff")] = NumberObject(flags & ~1)
        with open(output_pdf, "wb") as f: writer.write(f)
        print("   ✅ B-45 Generated.")
    except Exception as e: print(f"   ❌ B-45 Error: {e}")

# ==========================================
# 6. REPORTE DE AUDITORÍA
# ==========================================
def generar_reporte_auditoria(datos, nombre_archivo="REPORTE_LOGICA.txt"):
    print(f"📄 5. Generating Audit Report...")
    try:
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            f.write("AUTOMATED GENERATION REPORT - FDNY SYSTEM\n")
            f.write("=================================================\n")
            f.write(f"DATE: {fecha_hoy}\n")
            f.write(f"BIN: {datos.get('bin')}\n")
            f.write(f"ADDRESS: {datos.get('house')} {datos.get('street')}\n\n")
            f.write("⚠️ ARTIFICIAL INTELLIGENCE NOTES (PLEASE REVIEW):\n")
            f.write("-------------------------------------------------\n")
            f.write(f"1. CONSTRUCTION CLASS:\n   - Original Value (DB): {datos.get('raw_construction_class', 'N/A')}\n   - Final Value on PDF:  {datos.get('construction_class')}\n   - System Note:         {datos.get('debug_nota_const', '')}\n\n")
            f.write(f"2. OCCUPANCY GROUP:\n   - Original Value (DB): {datos.get('raw_occupancy', 'N/A')}\n   - Final Value on PDF:  {datos.get('occupancy_group')}\n   - System Note:         {datos.get('debug_nota_occ', '')}\n\n")
            f.write("LEGAL DISCLAIMER:\nThis form has been pre-filled using public data from BIS/DOB/PLUTO.\nThe Architect/Engineer of Record is responsible for verifying the accuracy\nof this data before signing and sealing the final documents.\n")
        print(f"   ✅ Report Generated: {nombre_archivo}")
    except Exception as e: print(f"   ❌ Report Error: {e}")    

if __name__ == "__main__":
    print("Run gui.py to start the application.")

