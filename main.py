import json
import os
import sys
import datetime
import requests
import streamlit as st
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, BooleanObject, NumberObject, TextStringObject, DictionaryObject

# ==========================================
# 0. CONFIGURATION LOADER (WEB & LOCAL)
# ==========================================
def load_configuration():
    try:
        if hasattr(st, "secrets") and len(st.secrets) > 0:
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

API_KEY_NYC = CONFIG_DATA.get("api_keys", {}).get("nyc_open_data_key", "")
APP_TOKEN_SOCRATA = CONFIG_DATA.get("api_keys", {}).get("nyc_socrata_token", "")

COMPANY = CONFIG_DATA.get("fire_alarm_company", {})
ARCHITECT = CONFIG_DATA.get("architect_applicant", {})
ELECTRICIAN = CONFIG_DATA.get("electrical_contractor", {})
TECH_DEFAULTS = CONFIG_DATA.get("technical_defaults", {})
CENTRAL_STATION = CONFIG_DATA.get("central_station", {})

fecha_hoy = datetime.date.today().strftime("%m/%d/%Y")

# ==========================================
# LISTAS MAESTRAS DEL A-433
# ==========================================

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
    "Firepanel": [
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

CATEGORIAS = {dev: cat for cat, devices in MASTER_DEVICE_LIST.items() for dev in devices}

RANGOS = {
    'Initiating': (1, 10), 'Supervisory': (11, 20), 'Control': (21, 25),
    'Signals': (26, 30), 'Communication': (31, 35), 'Firepanel': (36, 40)
}

# ==========================================
# 1. UTILITY: ADOBE COMPATIBILITY FIX
# ==========================================
def apply_adobe_fix(writer, campos):
    """
    Soluciona el problema de visibilidad en Adobe/Nitro.
    1. Fuerza NeedAppearances.
    2. Recorre anotaciones, inyecta el valor (/V) y ELIMINA el flujo de apariencia (/AP).
    Esto obliga al lector (Adobe) a generar el texto visualmente usando el valor real.
    """
    # Asegurar que el diccionario AcroForm existe y tiene NeedAppearances=True
    if "/AcroForm" not in writer.root_object:
        writer.root_object.update({
            NameObject("/AcroForm"): writer._add_object(DictionaryObject())
        })
    
    writer.root_object["/AcroForm"].update({
        NameObject("/NeedAppearances"): BooleanObject(True)
    })

    for page in writer.pages:
        if "/Annots" in page:
            for annot in page["/Annots"]:
                obj = annot.get_object()
                field_name = obj.get("/T")
                
                if field_name in campos:
                    val = campos[field_name]
                    
                    # Manejo de Checkboxes (/On, /Off) vs Texto
                    if isinstance(val, str) and val.startswith("/"):
                        obj.update({
                            NameObject("/V"): NameObject(val),
                            NameObject("/AS"): NameObject(val)
                        })
                    else:
                        obj.update({
                            NameObject("/V"): TextStringObject(str(val))
                        })
                    
                    # EL PASO CRÍTICO: Eliminar el Appearance Stream (/AP)
                    # Si existe, Adobe confía en él y no muestra el nuevo valor.
                    if "/AP" in obj:
                        del obj["/AP"]

# ==========================================
# 2. TRANSLATION & INTELLIGENCE ENGINE
# ==========================================
def traducir_datos(ocupacion_old, construccion_old, job_description="", building_class_tax=""):
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
        if tax_class.startswith("R") or tax_class.startswith("D"): res["const"] = "I-C"
        elif tax_class.startswith("C") or tax_class.startswith("S"): res["const"] = "III-B"
        elif tax_class.startswith("K") or tax_class.startswith("O"): res["const"] = "I-B"
        else: res["const"] = "III-B"
    
    mapa_occ = {"J-1": "R-1", "J-2": "R-2", "J-3": "R-3", "RES": "R-2", "PUB": "A-3", "COM": "M", "E": "B", "D-1": "F-1", "D-2": "F-2"}
    modernos = ["A-1", "A-2", "A-3", "A-4", "A-5", "B", "E", "F-1", "F-2", "H-1", "R-1", "R-2", "R-3", "S-1", "S-2", "U"]

    if occ in mapa_occ: res["occ"] = mapa_occ[occ]
    elif occ in modernos: res["occ"] = occ
    elif not occ or occ == "COM":
        if any(tax_class.startswith(k) for k in ["C", "D", "R", "L"]): res["occ"] = "R-2"
        else: res["occ"] = "B"

    if any(x in desc for x in ["WORSHIP", "SYNAGOGUE", "CHURCH", "TEMPLE"]):
        res["occ"] = "A-3"
    return res

# ==========================================
# 3. FETCH DATA (BIS, GEOCLIENT, PLUTO)
# ==========================================
def consultar_dob_now(bin_number, headers_soc):
    try:
        r = requests.get("https://data.cityofnewyork.us/resource/w9ak-ipjd.json", 
                         params={"bin": bin_number, "$order": "filing_date DESC", "$limit": 1}, headers=headers_soc)
        if r.status_code == 200 and r.json():
            job = r.json()[0]
            return {
                "owner_business": job.get("owner_s_business_name", "").strip(),
                "owner_first": job.get("owner_first_name", "").strip(),
                "owner_last": job.get("owner_last_name", "").strip(),
                "owner_email": job.get("owner_email", "").strip(),
                "owner_phone": job.get("owner_phone", "").strip(),
                "owner_address": f"{job.get('owner_s_house_number', '')} {job.get('owner_s_street_name', '')}".strip(),
                "owner_city": job.get("owner_s_city", "").strip(),
                "owner_zip": job.get("owner_s_zip", "").strip(),
                "owner_state": "NY"
            }
    except: pass
    return None

def obtener_datos_completos(bin_number):
    info = {"bin": bin_number, "house": "", "street": "", "borough": "", "zip": "", "block": "", "lot": "", "bbl_full": "", "tax_class": "", "stories": "0", "height": "0", "occupancy_group": "", "construction_class": "", "landmarked": "No", "flood_zone": "No", "owner_first": "", "owner_last": "", "owner_business": "", "owner_address": "", "owner_phone": "", "owner_email": "", "owner_city": "", "owner_state": "NY", "owner_zip": ""}
    headers_socrata = {"X-App-Token": APP_TOKEN_SOCRATA}
    
    try:
        url_geo = "https://api.nyc.gov/geoclient/v2/bin"
        r_geo = requests.get(url_geo, params={"bin": bin_number}, headers={"Ocp-Apim-Subscription-Key": API_KEY_NYC}, timeout=10)
        if r_geo.status_code == 200:
            d = r_geo.json().get('bin', {})
            info["house"] = (d.get("giLowHouseNumber1") or "").strip()
            info["street"] = (d.get("giStreetName1") or "").strip()
            info["borough"] = d.get("firstBoroughName", "").strip()
            info["block"] = d.get("bblTaxBlock", "").strip()
            info["lot"] = d.get("bblTaxLot", "").strip()
            info["bbl_full"] = d.get("bbl", "").strip()
            info["tax_class"] = d.get("rpadBuildingClassificationCode", "").strip()
    except: pass

    dob_now = consultar_dob_now(bin_number, headers_socrata)
    if dob_now: info.update(dob_now)

    try:
        r_bis = requests.get("https://data.cityofnewyork.us/resource/ic3t-wcy2.json", params={"bin__": bin_number, "$limit": 20}, headers=headers_socrata)
        if r_bis.status_code == 200 and r_bis.json():
            job = r_bis.json()[0]
            info["height"] = job.get("existing_height", "0")
            info["stories"] = job.get("existingno_of_stories", "0")
            trad = traducir_datos(job.get("existing_occupancy"), job.get("existing_construction_class"), job.get("job_description", ""), info["tax_class"])
            info["occupancy_group"] = trad["occ"]
            info["construction_class"] = trad["const"]
    except: pass

    return info

# ==========================================
# 4. GENERADOR TM-1
# ==========================================
def generar_tm1(datos, input_pdf, output_pdf):
    try:
        reader = PdfReader(input_pdf); writer = PdfWriter()
        for p in reader.pages: writer.add_page(p)

        lm_yes = "/On" if datos["landmarked"] == "Yes" else "/Off"
        lm_no  = "/On" if datos["landmarked"] == "No" else "/Off"

        campos = {
            "Last Name_3": datos["owner_last"], "First Name_2": datos["owner_first"],
            "Business Name_4": datos["owner_business"], "Business Address_3": datos["owner_address"],
            "City_3": datos["owner_city"], "State_3": datos["owner_state"], "Zip_3": datos["owner_zip"],
            "Classification": datos["construction_class"], "Stories": datos["stories"], "Height ft": datos["height"],
            "Building Dominant Occupancy Group": datos["occupancy_group"],
            "BIN": datos["bin"], "Building No": datos["house"], "Street Name": datos["street"],
            "Borough": datos["borough"], "Block": datos["block"], "Lot": datos["lot"], "ZIP": datos["zip"],
            "Initial Filing Date": fecha_hoy, "NEW SUBMISSION": "/On", "Fire AlarmFire SuppressionARCS Electrical": "/On",
            "undefined_18": lm_yes, "undefined_181": lm_no,
            "Last Name": ARCHITECT.get("Last Name"), "Firstname": ARCHITECT.get("First Name"),
            "Business Name_2": ARCHITECT.get("Company Name"), "Business Address": ARCHITECT.get("Address"),
            "License Number": ARCHITECT.get("License No"), "undefined_5": "/On",
            "Lastnamefilingrep": COMPANY.get("Last Name"), "firstnamefilingrep": COMPANY.get("First Name"),
            "Reg No": COMPANY.get("Reg No"), "Business Name_3": COMPANY.get("Company Name"), "undefined_16": "/On"
        }
        
        # Aplicamos la lógica de compatibilidad Adobe
        apply_adobe_fix(writer, campos)
        
        with open(output_pdf, "wb") as f: writer.write(f)
    except Exception as e: print(f"TM-1 Error: {e}")

# ==========================================
# 5. GENERADOR A-433
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
    try:
        reader = PdfReader(input_pdf); writer = PdfWriter()
        for p in reader.pages: writer.add_page(p)
        
        datos_instalacion = datos.get("devices", [])
        def floor_sorter(f_name):
            try: return FULL_FLOOR_LIST.index(f_name)
            except: return 999
            
        pisos_trabajados = sorted(list(set(d['floor'] for d in datos_instalacion)), key=floor_sorter)
        
        campos = {
            "Building No": datos.get("house", ""), "Street Name": datos.get("street", ""), 
            "Borough": datos.get("borough", ""), "ZIP": datos.get("zip", ""), 
            "Work on floor(s)": ", ".join(pisos_trabajados), "New": "/On",
            "Last Name": datos["owner_last"], "First Name": datos["owner_first"],
            "Business_Name": datos["owner_business"], "Business Address": datos["owner_address"]
        }

        # Datos de Contratistas
        elec, emp, cs, specs = ELECTRICIAN, COMPANY, CENTRAL_STATION, TECH_DEFAULTS
        campos.update({"First Name_2": elec.get("First Name"), "Last Name_2": elec.get("Last Name"), "Business Name_2": elec.get("Company Name"), "License Number": elec.get("License No")})
        campos.update({"First Name_3": emp.get("First Name"), "Last Name_3": emp.get("Last Name"), "Business Name_3": emp.get("Company Name"), "COF S97": emp.get("COF S97")})
        campos.update({"Business Name_4": cs.get("Company Name"), "Station Code": cs.get("CS Code"), "New_2": "/On"})

        # Mapeo de Pisos y Dispositivos
        mapa_col = {p: i+1 for i, p in enumerate(pisos_trabajados)}
        for p, i in mapa_col.items(): campos[f'floors{i}'] = p

        dispositivos = sorted(list(set(d['device'] for d in datos_instalacion)))
        fila_actual = {k: v[0] for k, v in RANGOS.items()}
        mapa_fil = {}

        for dev in dispositivos:
            cat = CATEGORIAS.get(dev, 'Initiating')
            r_ini, r_fin = RANGOS[cat]
            f = fila_actual[cat]
            if f > r_fin: continue 

            idx = f - r_ini + 1
            campos[f"{cat}{idx}"] = dev
            mapa_fil[dev] = (f, idx)
            m, a, g, t = obtener_cols_derecha(f, cat, idx)
            if m: campos[m] = specs.get('Manufacturer', '')
            if a: campos[a] = specs.get('Approval', '')
            if g: campos[g] = specs.get('WireGauge', '')
            if t: campos[t] = specs.get('WireType', '')
            fila_actual[cat] += 1

        for item in datos_instalacion:
            d, p, q = item['device'], item['floor'], int(item['qty'])
            if d in mapa_fil and p in mapa_col:
                r, _ = mapa_fil[d]; c = mapa_col[p]
                campos[f"r{r}c{c}"] = str(q)

        apply_adobe_fix(writer, campos)
        with open(output_pdf, "wb") as f: writer.write(f)
    except Exception as e: print(f"A-433 Error: {e}")

# ==========================================
# 6. GENERADOR B-45
# ==========================================
def generar_b45(datos, input_pdf, output_pdf):
    try:
        reader = PdfReader(input_pdf); writer = PdfWriter()
        for p in reader.pages: writer.add_page(p)
        emp = COMPANY
        campos = {
            "adress": f"{datos['house']} {datos['street']}, {datos['borough']}, NY {datos['zip']}",
            "name": f"{emp.get('First Name')} {emp.get('Last Name')}", 
            "lic": emp.get("Reg No"), "company": emp.get("Company Name"), "date1": fecha_hoy
        }
        apply_adobe_fix(writer, campos)
        with open(output_pdf, "wb") as f: writer.write(f)
    except Exception as e: print(f"B-45 Error: {e}")

if __name__ == "__main__":
    print("Run gui.py to start.")
