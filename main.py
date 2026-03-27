import json
import os
import sys
import datetime
import requests
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, BooleanObject, NumberObject, TextStringObject

# ==========================================
# 0. CONFIGURATION LOADER (FLASK / RENDER)
# ==========================================

API_KEY_NYC = os.environ.get("NYC_API_KEY", "")
APP_TOKEN_SOCRATA = os.environ.get("SOCRATA_TOKEN", "")

# Diccionarios globales que llenaremos dinámicamente desde Supabase por cada usuario
COMPANY = {}
EXPEDITOR = {}
ARCHITECT = {}
ELECTRICIAN = {}
TECH_DEFAULTS = {}
CENTRAL_STATION = {}

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
        "HVAC Shut Down", "Fire Suppression Release", "Isolation Module", "Access Control Release", "Fire Door Release",
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

CATEGORIAS = {}
for cat, devices in MASTER_DEVICE_LIST.items():
    for dev in devices:
        CATEGORIAS[dev] = cat

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
def obtener_bin_por_direccion(house, street, borough):
    print(f"Resolving Address to BIN: {house} {street}, {borough}...")
    try:
        url_geo = "https://api.nyc.gov/geoclient/v2/address"
        params = {"houseNumber": house, "street": street, "borough": borough}
        headers = {"Ocp-Apim-Subscription-Key": API_KEY_NYC}
        r = requests.get(url_geo, params=params, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json().get('address', {})
            bin_number = data.get('buildingIdentificationNumber', '')
            if bin_number and len(str(bin_number)) == 7:
                print(f"    Address resolved to BIN: {bin_number}")
                return str(bin_number)
            else:
                print(f"    BIN not found or invalid format: {bin_number}")
        else:
            print(f"    Geoclient API Error {r.status_code}")
    except Exception as e:
        print(f"    Connection failed: {e}")
    return None

def consultar_dob_now(bin_number, headers_soc):
    print(f"    Querying DOB NOW (Fresh Data)...")
    dob_now_data = {}
    try:
        r = requests.get("https://data.cityofnewyork.us/resource/w9ak-ipjd.json",
                         params={"bin": bin_number, "$order": "filing_date DESC", "$limit": 5}, headers=headers_soc)
        if r.status_code == 200 and r.json():
            # Buscar en los últimos 5 jobs el que tenga más datos técnicos
            for job in r.json():
                if not dob_now_data.get("owner_business"):
                    dob_now_data["owner_business"] = job.get("owner_s_business_name", "").strip()
                    dob_now_data["owner_first"]    = job.get("owner_first_name", "").strip()
                    dob_now_data["owner_last"]     = job.get("owner_last_name", "").strip()
                    dob_now_data["owner_email"]    = job.get("owner_email", "").strip()
                    dob_now_data["owner_phone"]    = job.get("owner_phone", "").strip()
                    addr_st = job.get("owner_s_street_name", "").strip()
                    addr_no = job.get("owner_s_house_number", "").strip()
                    dob_now_data["owner_city"]  = job.get("owner_s_city", job.get("city", "")).strip()
                    dob_now_data["owner_zip"]   = job.get("owner_s_zip", job.get("zip", "")).strip()
                    dob_now_data["owner_state"] = job.get("state", "NY") or "NY"
                    if addr_st:
                        dob_now_data["owner_address"] = f"{addr_no} {addr_st}".strip()

                # DOB NOW también tiene construction classification — fuente muy confiable
                dob_const = str(job.get("construction_classification") or "").strip().upper()
                dob_occ   = str(job.get("occupancy_classification") or job.get("occupancy_classification_of_building") or "").strip().upper()

                if dob_const and not dob_now_data.get("dob_now_const"):
                    dob_now_data["dob_now_const"] = dob_const
                    dob_now_data["dob_now_const_job"] = job.get("job_filing_number", "")
                if dob_occ and not dob_now_data.get("dob_now_occ"):
                    dob_now_data["dob_now_occ"] = dob_occ
                    dob_now_data["dob_now_occ_job"] = job.get("job_filing_number", "")

            if dob_now_data:
                print(f"   ✅ DOB NOW: owner={dob_now_data.get('owner_business')}, const={dob_now_data.get('dob_now_const')}, occ={dob_now_data.get('dob_now_occ')}")
            return dob_now_data if dob_now_data else None
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
    print(f"1. Fetching master data for BIN: {bin_number}...")

    info = {
        "bin": bin_number, "house": "", "street": "", "borough": "", "zip": "",
        "block": "", "lot": "", "bbl_full": "", "tax_class": "",
        "stories": "", "height": "", "occupancy_group": "", "construction_class": "",
        "landmarked": "No", "flood_zone": "No",
        "owner_first": "", "owner_last": "", "owner_business": "", "owner_address": "",
        "owner_phone": "", "owner_email": "", "owner_city": "", "owner_state": "NY",
        "owner_zip": "", "has_digital_co": False,
        "x_coord": "", "y_coord": "", "dcp_address": "",
        "has_sprinklers": "Unknown", "has_elevators": "Unknown",
        "fire_alarm_jobs": [], "year_built": "",
        "pluto_stories": "", "pluto_bldgclass": "", "pluto_units": "", "pluto_year": ""
    }

    headers_socrata = {"X-App-Token": APP_TOKEN_SOCRATA}

    # --- NIVEL 1A: GEOCLIENT (fuente primaria) ---
    geoclient_ok = False
    try:
        url_geo = "https://api.nyc.gov/geoclient/v2/bin"
        r_geo = requests.get(url_geo, params={"bin": bin_number},
                             headers={"Ocp-Apim-Subscription-Key": API_KEY_NYC}, timeout=10)
        if r_geo.status_code == 200:
            d = r_geo.json().get('bin', {})
            info["house"]     = (d.get("giLowHouseNumber1") or d.get("houseNumber", "")).strip()
            info["street"]    = (d.get("giStreetName1") or d.get("streetName", "")).strip()
            info["borough"]   = d.get("firstBoroughName", "").strip()
            info["block"]     = d.get("bblTaxBlock", "").strip()
            info["lot"]       = d.get("bblTaxLot", "").strip()
            info["bbl_full"]  = d.get("bbl", "").strip()
            info["tax_class"] = d.get("rpadBuildingClassificationCode", "").strip()
            info["x_coord"]   = str(d.get("xCoordinate", "")).strip()
            info["y_coord"]   = str(d.get("yCoordinate", "")).strip()
            low_hn  = str(d.get("giLowHouseNumber1", "")).strip()
            high_hn = str(d.get("giHighHouseNumber1", "")).strip()
            info["dcp_address"] = f"{low_hn}-{high_hn} {info['street']}" if (low_hn and high_hn and low_hn != high_hn) else f"{info['house']} {info['street']}"
            if info["bbl_full"]:
                geoclient_ok = True
                print(f"   ✅ Geoclient OK: {info['house']} {info['street']}, BBL={info['bbl_full']}")
        else:
            print(f"   ⚠️ Geoclient error {r_geo.status_code} — will try PLUTO direct BIN lookup")
    except Exception as e:
        print(f"   ⚠️ Geoclient failed: {e} — will try PLUTO direct BIN lookup")

    # --- NIVEL 1B: PLUTO DIRECTO POR BIN (fallback si Geoclient falla) ---
    # pad_folio dataset tiene BIN → BBL directamente sin necesitar API key
    if not geoclient_ok:
        try:
            r_pad = requests.get("https://data.cityofnewyork.us/resource/w4v2-rv29.json",
                                 params={"bin": bin_number, "$limit": 1},
                                 headers=headers_socrata, timeout=10)
            if r_pad.status_code == 200 and r_pad.json():
                pad = r_pad.json()[0]
                bbl = str(pad.get("bbl", "")).strip()
                if bbl:
                    info["bbl_full"] = bbl
                    info["house"]    = str(pad.get("lhnd", "") or pad.get("address", "")).split()[0] if pad.get("lhnd") or pad.get("address") else ""
                    info["street"]   = str(pad.get("stname", "")).strip()
                    info["borough"]  = str(pad.get("boro_nm", "")).strip().title()
                    info["block"]    = bbl[1:6].lstrip("0") if len(bbl) == 10 else ""
                    info["lot"]      = bbl[6:].lstrip("0") if len(bbl) == 10 else ""
                    info["dcp_address"] = f"{info['house']} {info['street']}".strip()
                    print(f"   ✅ PAD fallback OK: BBL={bbl}")
        except Exception as e:
            print(f"   ⚠️ PAD fallback failed: {e}")
            
    # --- NUEVO: OBTENER TODAS LAS DIRECCIONES ALTERNATIVAS (PAD COMPLETO) ---
    try:
        # Quitamos el límite de 1 para traer todas las direcciones de las esquinas/calles adyacentes
        r_pad_all = requests.get("https://data.cityofnewyork.us/resource/w4v2-rv29.json",
                                 params={"bin": bin_number, "$limit": 50},
                                 headers=headers_socrata, timeout=10)
        if r_pad_all.status_code == 200 and r_pad_all.json():
            direcciones_unicas = set()
            for record in r_pad_all.json():
                l_hnd = str(record.get("lhnd", "")).strip()
                h_hnd = str(record.get("hhnd", "")).strip()
                st_name = str(record.get("stname", "")).strip()

                if l_hnd and st_name:
                    # Armar el rango (ej. 100-104 7 AVENUE)
                    if h_hnd and l_hnd != h_hnd:
                        dir_completa = f"{l_hnd}-{h_hnd} {st_name}"
                    else:
                        dir_completa = f"{l_hnd} {st_name}"
                    direcciones_unicas.add(dir_completa)

            # Si encontró direcciones, las unimos con un separador y sobrescribimos el dcp_address
            if direcciones_unicas:
                info["dcp_address"] = " | ".join(sorted(direcciones_unicas))
                print(f"   ✅ Full Address Range: {info['dcp_address']}")
    except Exception as e:
        print(f"   ⚠️ Error fetching multiple addresses: {e}")    

    # --- NIVEL 2: PLUTO (por BBL si disponible, también por BIN directo) ---
    pluto_data = None
    # Intento 1: por BBL (más preciso)
    if info["bbl_full"]:
        try:
            r_pluto = requests.get("https://data.cityofnewyork.us/resource/64uk-42ks.json",
                                   params={"bbl": info["bbl_full"]}, headers=headers_socrata, timeout=10)
            if r_pluto.status_code == 200 and r_pluto.json():
                pluto_data = r_pluto.json()[0]
                print(f"   ✅ PLUTO by BBL OK")
        except Exception as e:
            print(f"   ⚠️ PLUTO by BBL failed: {e}")

    # Intento 2: por BIN directo (si BBL falló)
    if not pluto_data:
        try:
            r_pluto2 = requests.get("https://data.cityofnewyork.us/resource/64uk-42ks.json",
                                    params={"bin": bin_number}, headers=headers_socrata, timeout=10)
            if r_pluto2.status_code == 200 and r_pluto2.json():
                pluto_data = r_pluto2.json()[0]
                print(f"   ✅ PLUTO by BIN direct OK")
        except Exception as e:
            print(f"   ⚠️ PLUTO by BIN failed: {e}")

    if pluto_data:
        info["zip"]             = str(pluto_data.get("zipcode", "")).strip()
        info["year_built"]      = str(pluto_data.get("yearbuilt", "")).strip()
        info["pluto_year"]      = info["year_built"]
        info["pluto_stories"]   = str(pluto_data.get("numfloors", "")).split(".")[0].strip()  # "2.0000" → "2"
        info["pluto_bldgclass"] = str(pluto_data.get("bldgclass", "")).strip()
        info["pluto_units"]     = str(pluto_data.get("unitsres", "")).strip()
        info["owner_business_backup"] = pluto_data.get("ownername", "").strip()

        # Flood zone
        if pluto_data.get("pfirm15_flag") == "1":
            info["flood_zone"] = "Yes"

        # Landmark — PLUTO tiene histdist si el edificio está en un distrito histórico
        if pluto_data.get("histdist") or pluto_data.get("landmark"):
            info["landmarked"] = "Yes"

        # Tax class
        if not info["tax_class"]:
            info["tax_class"] = pluto_data.get("bldgclass", "").strip()

        # Coordinates
        if not info["x_coord"]: info["x_coord"] = str(pluto_data.get("xcoord", "")).strip()
        if not info["y_coord"]: info["y_coord"] = str(pluto_data.get("ycoord", "")).strip()

        # BBL (por si vino en formato "1004830029.00000000")
        if not info["bbl_full"]:
            bbl_raw = str(pluto_data.get("bbl", "")).split(".")[0].strip()
            info["bbl_full"] = bbl_raw

        # Dirección desde PLUTO si Geoclient falló
        if not info["house"] and pluto_data.get("address"):
            addr_raw = pluto_data.get("address").split(" ", 1)
            info["house"]  = addr_raw[0]
            info["street"] = addr_raw[1] if len(addr_raw) > 1 else ""

        # Borough desde PLUTO si falta
        if not info["borough"]:
            boro_map = {"1": "MANHATTAN", "2": "BRONX", "3": "BROOKLYN", "4": "QUEENS", "5": "STATEN ISLAND"}
            info["borough"] = boro_map.get(str(pluto_data.get("borocode", "")), "")

        if not info["dcp_address"]:
            info["dcp_address"] = f"{info['house']} {info['street']}".strip()

        # Campos extra de PLUTO útiles para el filing
        info["zoning_dist"]   = str(pluto_data.get("zonedist1", "")).strip()
        info["special_dist"]  = str(pluto_data.get("spdist1", "")).strip()
        info["hist_dist"]     = str(pluto_data.get("histdist", "")).strip()
        info["year_alter1"]   = str(pluto_data.get("yearalter1", "")).strip()
        info["year_alter2"]   = str(pluto_data.get("yearalter2", "")).strip()
        info["land_use"]      = str(pluto_data.get("landuse", "")).strip()
        info["e_desig"]       = str(pluto_data.get("edesignum", "")).strip()
        info["comm_dist"]     = str(pluto_data.get("cd", "")).strip()

        print(f"   ✅ PLUTO data: floors={info['pluto_stories']}, year={info['year_built']}, class={info['pluto_bldgclass']}, owner={info['owner_business_backup']}, landmark={info['landmarked']}, alter1={info['year_alter1']}, alter2={info['year_alter2']}")

    # --- DOB NOW ---
    dob_now_info = consultar_dob_now(bin_number, headers_socrata)
    if dob_now_info: info.update(dob_now_info)
    if buscar_co_dob_now(bin_number, headers_socrata): info["has_digital_co"] = True

    # --- NIVEL 3: BIS ---
    try:
        r_bis = requests.get("https://data.cityofnewyork.us/resource/ic3t-wcy2.json",
                           params={"bin__": bin_number, "$order": "latest_action_date DESC", "$limit": 100},
                           headers=headers_socrata, timeout=10)
        if r_bis.status_code == 200:
            jobs = r_bis.json()
            raw_h, raw_s, raw_c, raw_o, desc_total = "0", "0", "", "", ""
            alt1_jobs = []  # Para rastrear Alt-1 con cambio de ocupancia

            for job in jobs:
                if not info["owner_business"] and not info["owner_last"]:
                    bn = str(job.get("owner_s_business_name") or "").strip()
                    if bn:
                        info["owner_business"] = bn
                        info["owner_first"] = str(job.get("owner_s_first_name") or "").strip()
                        info["owner_last"] = str(job.get("owner_s_last_name") or "").strip()
                        oh, os_ = job.get("owner_s_house_number", ""), job.get("owner_s_street_name", "")
                        info["owner_address"] = f"{oh} {os_}" if oh else f"{info['house']} {info['street']}"
                        info["owner_city"] = job.get("owner_s_city", info["borough"])
                        info["owner_zip"] = job.get("owner_s_zip", info["zip"])
                        info["owner_phone"] = str(job.get("owner_sphone__") or "").replace("-", "")

                if raw_h == "0": raw_h = str(job.get("existing_height") or "0")
                if raw_s == "0": raw_s = str(job.get("existingno_of_stories") or "0")
                if not raw_c: raw_c = job.get("existing_construction_class", "")
                if not raw_o: raw_o = job.get("existing_occupancy", "")
                if info["landmarked"] == "No" and job.get("landmarked") in ["Y", "YES"]: info["landmarked"] = "Yes"

                job_desc_individual = str(job.get("job_description") or "").upper()
                job_type = str(job.get("job_type") or "").upper().strip()
                desc_total += " " + job_desc_individual
  
                # =========================================================
                # 1. DEFINIR KEYWORDS Y EVALUAR LA "X" EN LOS CHECKBOXES
                # =========================================================
                FA_KEYWORDS = ["FIRE ALARM", "SMOKE DETECTOR", "SMOKE DETECTION", "FIRE SUPPRESSION", "FIRE PROTECTION", " FA ", "F.A.", "ARCS"]
                SPRINKLER_KEYWORDS = ["SPRINKLER", "STANDPIPE", "WET PIPE", "DRY PIPE"]
                ELEV_KEYWORDS = ["ELEVATOR", "ELEV ", "ELEVATORS", " ELV ", "HYDRAULIC LIFT", "ESCALATOR"]

                is_fa_job = any(kw in job_desc_individual for kw in FA_KEYWORDS) or str(job.get("fire_alarm", "")).upper() == "X"
                
                # Buscamos en palabras clave, en casilla sprinkler o en casilla standpipe
                is_sprinkler_job = any(kw in job_desc_individual for kw in SPRINKLER_KEYWORDS) or str(job.get("sprinkler", "")).upper() == "X" or str(job.get("standpipe", "")).upper() == "X"
                
                is_elev_job = any(kw in job_desc_individual for kw in ELEV_KEYWORDS)

                # =========================================================
                # 2. ACTUALIZAR INDICADORES GLOBALES DEL DASHBOARD
                # =========================================================
                if is_sprinkler_job: 
                    info["has_sprinklers"] = "Yes"
                if is_elev_job: 
                    info["has_elevators"] = "Yes"


                # --- DETECCIÓN DE ALT-1 CON CAMBIO DE OCUPANCIA ---
                # Alt-1 = alteración mayor que puede cambiar ocupancia/uso
                if job_type == "A1":
                    job_occ_proposed = str(job.get("proposed_occupancy") or "").strip()
                    job_occ_existing = str(job.get("existing_occupancy") or "").strip()
                    job_date = fmt_date(job.get("latest_action_date", ""))
                    job_num  = job.get("job__", "")
                    job_status = str(job.get("job_status") or "").strip()
                    job_url = f"https://a810-bisweb.nyc.gov/bisweb/JobsQueryByNumberServlet?passjobnumber={job_num}&passdocnumber=01"

                    alt1_entry = {
                        "Job #":    job_num,
                        "Date":     job_date,
                        "Status":   job_status,
                        "Existing Occ": job_occ_existing,
                        "Proposed Occ": job_occ_proposed,
                        "Description":  job_desc_individual.capitalize()[:80],
                        "DOB Link": job_url
                    }

                    # Marcar si hubo cambio de ocupancia
                    if job_occ_proposed and job_occ_existing and job_occ_proposed != job_occ_existing:
                        alt1_entry["⚠️ Occupancy Changed"] = f"{job_occ_existing} → {job_occ_proposed}"
                        # Si el Alt-1 tiene propuesta de ocupancia, usarla como fuente más confiable
                        if not raw_o:
                            raw_o = job_occ_proposed

                    alt1_jobs.append(alt1_entry)

                # Helper para formatear fecha legible en inglés
                def fmt_date(raw):
                    if not raw: return "N/A"
                    try:
                        from datetime import datetime
                        dt = datetime.strptime(str(raw)[:10], "%Y-%m-%d")
                        return dt.strftime("%b %d, %Y")  # "Jun 15, 2024"
                    except:
                        return str(raw)[:10]

               
                if is_fa_job:
                    job_num = job.get("job__", "")
                    if job_num and not any(j["Job #"] == job_num for j in info["fire_alarm_jobs"]):
                        job_url = f"https://a810-bisweb.nyc.gov/bisweb/JobsQueryByNumberServlet?passjobnumber={job_num}&passdocnumber=01"
                        raw_date = str(job.get("latest_action_date") or "")
                        full_desc = job_desc_individual.capitalize()
                        info["fire_alarm_jobs"].append({
                            "Job #":       job_num,
                            "Year":        fmt_date(raw_date),
                            "Type":        job_type or "N/A",
                            "Status":      job.get("job_status", "N/A"),
                            "Description": full_desc[:100] + ("..." if len(full_desc) > 100 else ""),
                            "DOB Link":    job_url
                        })

                if is_sprinkler_job:
                    job_num = job.get("job__", "")
                    if job_num and not any(j["Job #"] == job_num for j in info.get("sprinkler_jobs", [])):
                        job_url = f"https://a810-bisweb.nyc.gov/bisweb/JobsQueryByNumberServlet?passjobnumber={job_num}&passdocnumber=01"
                        raw_date = str(job.get("latest_action_date") or "")
                        full_desc = job_desc_individual.capitalize()
                        if "sprinkler_jobs" not in info: info["sprinkler_jobs"] = []
                        info["sprinkler_jobs"].append({
                            "Job #":       job_num,
                            "Year":        fmt_date(raw_date),
                            "Type":        job_type or "N/A",
                            "Status":      job.get("job_status", "N/A"),
                            "Description": full_desc[:100] + ("..." if len(full_desc) > 100 else ""),
                            "DOB Link":    job_url
                        })

            # Guardar Alt-1 jobs en info para el dashboard
            info["alt1_jobs"] = alt1_jobs
            if alt1_jobs:
                # ¿Hay algún cambio de ocupancia detectado?
                occ_changes = [j for j in alt1_jobs if "⚠️ Occupancy Changed" in j]
                if occ_changes:
                    info["occ_change_warning"] = f"⚠️ {len(occ_changes)} Alt-1 job(s) detected with occupancy change — verify before filing"
                    print(f"   ⚠️ Occupancy change detected in {len(occ_changes)} Alt-1 job(s)")
                else:
                    info["occ_change_warning"] = f"ℹ️ {len(alt1_jobs)} major alteration(s) on record (Alt-1) — review for occupancy changes"

            info["height"], info["stories"] = raw_h, raw_s
            trad = traducir_datos(raw_o, raw_c, desc_total, info["tax_class"])
            info["occupancy_group"] = trad["occ"]
            info["construction_class"] = trad["const"]
            info["raw_occupancy"], info["raw_construction_class"] = raw_o, raw_c
            info["debug_nota_occ"], info["debug_nota_const"] = trad["nota"], trad["nota"]
    except Exception as e: print(f"   [WARNING] BIS Error: {e}")

    # --- NIVEL 4: ELEVADORES (DOB Elevator dataset) ---
    try:
        r_elev = requests.get("https://data.cityofnewyork.us/resource/p9kp-jvxn.json",
                              params={"bin_number": bin_number, "$limit": 50},
                              headers=headers_socrata, timeout=10)
        if r_elev.status_code == 200 and r_elev.json():
            elev_records = r_elev.json()
            # Contar equipos únicos activos
            active_elevs = [e for e in elev_records if str(e.get("device_status", "")).upper() in ["ACTIVE", "IN SERVICE", ""]]
            elev_count = len(active_elevs) or len(elev_records)
            info["has_elevators"] = "Yes"
            info["elevator_count"] = elev_count
            # Tipos de equipos
            types = list(set(str(e.get("device_type", "")).strip() for e in elev_records if e.get("device_type")))
            info["elevator_types"] = ", ".join(types) if types else ""
            print(f"   ✅ Elevators found: {elev_count} units — {info['elevator_types']}")
    except Exception as e:
        print(f"   ⚠️ Elevator dataset error: {e}")

    # --- FALLBACK PLUTO: Si BIS no devolvió datos técnicos, usamos PLUTO ---
    if not info["stories"] or info["stories"] == "0":
        info["stories"] = info.get("pluto_stories", "")

    # Inferir elevadores por altura si el dataset no los encontró
    # NYC BC 1002.1: edificios de 5+ pisos deben tener acceso accesible (generalmente elevador)
    # En la práctica, edificios de 6+ pisos casi siempre tienen elevador
    if info.get("has_elevators") == "Unknown":
        try:
            stories_num = int(float(info.get("stories") or info.get("pluto_stories") or 0))
            if stories_num >= 6:
                info["has_elevators"] = "Yes (inferred)"
                info["elevator_note"] = f"Inferred from building height ({stories_num} floors — NYC BC typically requires elevator at 6+ floors)"
            elif stories_num >= 4 and info.get("occupancy_group", "") in ["R-1", "R-2", "I-1", "I-2", "I-3"]:
                info["has_elevators"] = "Likely (inferred)"
                info["elevator_note"] = f"Likely required — {stories_num} floors, occupancy {info.get('occupancy_group')} (ADA/accessibility requirements)"
        except: pass
    # Height fallback: si no vino de BIS, estimamos multiplicando stories × 10 ft
    if (not info["height"] or info["height"] == "0") and info["stories"]:
        try:
            info["height"] = str(int(float(info["stories"])) * 10)
            info["debug_nota_height"] = f"[Height estimated: {info['stories']} floors × 10ft]"
        except: pass

    # ================================================================
    # CASCADA DE CONFIANZA: Construction Class + Occupancy
    # ================================================================

    if info["construction_class"]:
        info["const_source"]     = "Confirmed — on record"
        info["const_confidence"] = "high"
    elif info.get("dob_now_const"):
        dob_const = info["dob_now_const"]
        trad = traducir_datos("", dob_const, "", info["tax_class"])
        info["construction_class"] = trad["const"] or dob_const
        info["raw_construction_class"] = dob_const
        info["const_source"]     = "Confirmed — on record"
        info["const_confidence"] = "high"
        info["debug_nota_const"] = f"[DOB NOW: {dob_const} → {info['construction_class']}]"
    else:
        pluto_class = info.get("pluto_bldgclass", "")
        year_built  = int(info.get("year_built", "0") or "0")

        inferred_class = ""
        confidence     = "low"
        nota           = ""

        if pluto_class:
            first = pluto_class[0].upper()

            if first in ["A", "B"]:
                inferred_class = "V-B" if year_built > 1968 else "III-B"
                confidence = "medium"
                nota = f"Row/2-family (bldgclass={pluto_class}, built={year_built})"

            elif first == "C":
                inferred_class = "III-B"
                confidence = "medium-high" if year_built <= 1938 else "medium"
                nota = f"Walk-up apartment (bldgclass={pluto_class}, built={year_built})"

            elif first == "D":
                if year_built <= 1901:
                    inferred_class = "III-B"; confidence = "medium"
                elif year_built <= 1938:
                    inferred_class = "I-B"; confidence = "medium-high"
                else:
                    inferred_class = "I-A"; confidence = "medium"
                nota = f"Elevator apartment (bldgclass={pluto_class}, built={year_built})"

            elif first in ["E", "F", "G"]:
                inferred_class = "I-B" if year_built > 1938 else "III-B"
                confidence = "medium"
                nota = f"Industrial/warehouse (bldgclass={pluto_class}, built={year_built})"

            elif first in ["H", "I"]:
                inferred_class = "I-A" if year_built > 1968 else "I-B"
                confidence = "medium"
                nota = f"Hotel/institutional (bldgclass={pluto_class}, built={year_built})"

            elif first in ["K", "L", "O", "S"]:
                if year_built <= 1938:
                    inferred_class = "III-B"; confidence = "medium-high"
                else:
                    inferred_class = "I-B"; confidence = "medium"
                nota = f"Commercial/loft/office (bldgclass={pluto_class}, built={year_built})"

            elif first == "R":
                inferred_class = "I-B" if year_built > 1968 else "III-B"
                confidence = "medium"
                nota = f"Condo building (bldgclass={pluto_class}, built={year_built})"

            elif first in ["M", "W", "P", "Y"]:
                inferred_class = "I-B"; confidence = "low"
                nota = f"Institutional (bldgclass={pluto_class})"

            else:
                trad_fb = traducir_datos("", "", "", info["tax_class"])
                inferred_class = trad_fb["const"] or "III-B"
                confidence = "low"
                nota = f"Generic inference"

        if inferred_class:
            info["construction_class"]   = inferred_class
            info["raw_construction_class"] = f"INFERRED:{pluto_class}"
            info["const_confidence"]     = confidence
            info["debug_nota_const"]     = nota
            # Labels amigables para el contratista
            if confidence == "medium-high":
                info["const_source"] = "Estimated — verify with C of O"
            elif confidence == "medium":
                info["const_source"] = "Estimated — verify with C of O"
            else:
                info["const_source"] = "Unknown — manual verification required"

    # --- OCCUPANCY GROUP ---
    if info["occupancy_group"]:
        info["occ_source"]     = "Confirmed — on record"
        info["occ_confidence"] = "high"
    elif info.get("dob_now_occ"):
        dob_occ = info["dob_now_occ"]
        trad = traducir_datos(dob_occ, "", "", info["tax_class"])
        info["occupancy_group"] = trad["occ"] or dob_occ
        info["raw_occupancy"]   = dob_occ
        info["occ_source"]      = "Confirmed — on record"
        info["occ_confidence"]  = "high"
        info["debug_nota_occ"]  = f"[DOB NOW: {dob_occ} → {info['occupancy_group']}]"
    else:
        trad_fallback = traducir_datos("", "", "", info["tax_class"])
        if trad_fallback["occ"]:
            info["occupancy_group"] = trad_fallback["occ"]
            info["raw_occupancy"]   = f"TAX_CLASS:{info['tax_class']}"
            info["occ_confidence"]  = "low"
            info["occ_source"]      = "Unknown — manual verification required"
            info["debug_nota_occ"]  = trad_fallback["nota"]

    # Garantizar que raw_occupancy y raw_construction_class siempre existen
    if "raw_occupancy" not in info:         info["raw_occupancy"] = ""
    if "raw_construction_class" not in info: info["raw_construction_class"] = ""
    if "debug_nota_occ" not in info:         info["debug_nota_occ"] = ""
    if "debug_nota_const" not in info:       info["debug_nota_const"] = ""
    # Garantizar landmarked y flood_zone como strings limpios
    if info["landmarked"] not in ["Yes", "No"]:  info["landmarked"] = "No"
    if info["flood_zone"] not in ["Yes", "No"]:  info["flood_zone"] = "No"

    # BUG FIX #2: Si owner_city sigue vacío después de todo, usar el borough como fallback
    if not info["owner_city"] and info["borough"]:
        info["owner_city"] = info["borough"]
    # BUG FIX #3: Si owner_zip sigue vacío, usar el zip del edificio como fallback
    if not info["owner_zip"] and info["zip"]:
        info["owner_zip"] = info["zip"]
    if not info["owner_state"]:
        info["owner_state"] = "NY"

    if not info["owner_business"]: info["owner_business"] = info.get("owner_business_backup", "")
    return info


def rellenar_pdf_inteligente(input_pdf, output_pdf, campos):
    """
    Rellena un PDF con los campos dados.
    Compatible con pypdf 3.x y versiones posteriores (usa getattr para _root_object).
    """
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    # PARCHE COMPATIBILIDAD pypdf 3.17+: root pasó a ser _root_object
    root = getattr(writer, "_root_object", getattr(writer, "root_object", None))
    if root and "/AcroForm" in root:
        root["/AcroForm"].get_object()[NameObject("/NeedAppearances")] = BooleanObject(True)

    for page in writer.pages:
        if "/Annots" in page:
            for annot in page["/Annots"]:
                obj = annot.get_object()

                if obj.get("/T"):
                    key = obj.get("/T")
                    if key in campos:
                        val = campos[key]

                        # A. CHECKBOX / RADIO BUTTON
                        is_button = obj.get("/FT") == "/Btn"

                        if val in ["/On", "/Off", True, False] or is_button:
                            if val in ["/On", True]:
                                estado_activo = NameObject("/On")
                                if "/AP" in obj:
                                    ap = obj["/AP"].get_object()
                                    if "/N" in ap:
                                        n_dict = ap["/N"].get_object()
                                        if hasattr(n_dict, "keys"):
                                            for k in n_dict.keys():
                                                if k != "/Off":
                                                    estado_activo = NameObject(k)
                                                    break
                                obj.update({
                                    NameObject("/V"): estado_activo,
                                    NameObject("/AS"): estado_activo
                                })
                            else:
                                obj.update({
                                    NameObject("/V"): NameObject("/Off"),
                                    NameObject("/AS"): NameObject("/Off")
                                })

                        # B. CAMPO DE TEXTO
                        else:
                            # BUG FIX #4: Convertir None a string vacío para evitar errores al encodear
                            texto_seguro = str(val if val is not None else "").encode('latin-1', 'ignore').decode('latin-1')
                            obj.update({NameObject("/V"): TextStringObject(texto_seguro)})
                            if "/AP" in obj:
                                del obj["/AP"]

                    # LIMPIEZA GENERAL
                    if "/Ff" in obj:
                        flags = obj.get("/Ff", 0)
                        if isinstance(flags, int):
                            flags = (flags & ~0x1000000) & ~1
                            obj.update({NameObject("/Ff"): NumberObject(flags)})

    with open(output_pdf, "wb") as f:
        writer.write(f)


# ==========================================
# 3. GENERADOR TM-1
# ==========================================
def generar_tm1(datos, input_pdf, output_pdf):
    print(f"📄 2. Generating TM-1...")
    try:
        # Usar .get() con default "No" para evitar KeyError si el campo no existe
        landmarked  = datos.get("landmarked", "No")
        flood_zone  = datos.get("flood_zone", "No")
        lm_yes = "/On" if landmarked == "Yes" else "/Off"
        lm_no  = "/On" if landmarked != "Yes" else "/Off"
        fl_yes = "/On" if flood_zone == "Yes" else "/Off"
        fl_no  = "/On" if flood_zone != "Yes" else "/Off"

        # Limpiar "0" de height y stories para no escribir "0" en el PDF
        stories = datos.get("stories", "")
        height  = datos.get("height", "")
        if stories == "0": stories = ""
        if height  == "0": height  = ""

        arch_phone = str(ARCHITECT.get("Phone") or "")

        campos = {
            # --- OWNER / APPLICANT (sufijos _3 y _4 en el TM-1) ---
            "Last Name_3":      datos.get("owner_last", ""),
            "First Name_2":     datos.get("owner_first", ""),
            "Business Name_4":  datos.get("owner_business", ""),
            "Business Address_3": datos.get("owner_address", ""),
            "City_3":           datos.get("owner_city", ""),
            "State_3":          datos.get("owner_state", "NY"),
            "Zip_3":            datos.get("owner_zip", ""),
            "Business Tel_2":   datos.get("owner_phone", ""),
            "Mobile Tel":       datos.get("owner_phone", ""),
            "EMail_3":          datos.get("owner_email", ""),

            # --- BUILDING INFO ---
            "Classification":   datos.get("construction_class", ""),
            "Stories":          stories,
            "Height ft":        height,
            "Building Dominant Occupancy Group": datos.get("occupancy_group", ""),
            "Occupancy classification of the area of work": datos.get("occupancy_group", ""),
            "undefined_18": lm_yes, "undefined_181": lm_no,
            "undefined_19": fl_yes, "undefined_191": fl_no,
            "Initial Filing Date": fecha_hoy,
            "Total Fee": "585.00",
            "NEW SUBMISSION": "/On",
            "Fire AlarmFire SuppressionARCS Electrical": "/On",
            "undefined": "/On",
            "BIN":          datos.get("bin", ""),
            "Building No":  datos.get("house", ""),
            "Street Name":  datos.get("street", ""),
            "Borough":      datos.get("borough", ""),
            "Block":        datos.get("block", ""),
            "Lot":          datos.get("lot", ""),
            "ZIP":          datos.get("zip", ""),
            "Job Description": datos.get("job_desc", ""),

            # --- ARCHITECT / PE (sin sufijo en el TM-1) ---
            "Last Name":        ARCHITECT.get("Last Name", ""),
            "Firstname":        ARCHITECT.get("First Name", ""),
            "Business Name_2":  ARCHITECT.get("Company Name", ""),
            "Business Address": ARCHITECT.get("Address", ""),
            "City":             ARCHITECT.get("City", ""),
            "State":            ARCHITECT.get("State", ""),
            "Zip":              ARCHITECT.get("Zip", ""),
            "bsn_phone":        arch_phone,
            "EMail":            ARCHITECT.get("Email", ""),
            "License Number":   ARCHITECT.get("License No", ""),
            "undefined_5":      "/On",

            # --- FILING REP / EXPEDITOR (sufijos _2 en el TM-1) ---
            "Lastnamefilingrep":   EXPEDITOR.get("Last Name", ""),
            "firstnamefilingrep":  EXPEDITOR.get("First Name", ""),
            "Filing Rep Tel":      EXPEDITOR.get("Phone", ""),
            "Reg No":              EXPEDITOR.get("Reg No", ""),
            "Business Name_3":     EXPEDITOR.get("Company Name", ""),
            "Business Address_2":  EXPEDITOR.get("Address", ""),
            "City_2":              EXPEDITOR.get("City", ""),
            "State_2":             EXPEDITOR.get("State", "NY"),
            "Zip_2":               EXPEDITOR.get("Zip", ""),
            "EMail_2":             EXPEDITOR.get("Email", ""),
            "undefined_16": "/On",
            "2025": "/On",
            "Code Section": "BC 907"
        }

        rellenar_pdf_inteligente(input_pdf, output_pdf, campos)
        print("   ✅ TM-1 Generated.")
    except Exception as e:
        print(f"   ❌ TM-1 Error: {e}")
        raise


# ==========================================
# 4. GENERADOR A-433
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
        datos_instalacion = datos.get("devices", [])

        def floor_sorter(f_name):
            try: return FULL_FLOOR_LIST.index(f_name)
            except ValueError: return 9999

        pisos_trabajados = sorted(list(set(d['floor'] for d in datos_instalacion)), key=floor_sorter)

        campos = {}
        campos.update({
            "Building No":  datos.get("house", ""),
            "Street Name":  datos.get("street", ""),
            "Borough":      datos.get("borough", ""),
            "State":        "NY",
            "ZIP":          datos.get("zip", ""),
            "Work on floor(s)": ", ".join(pisos_trabajados),
            "New": "/On"
        })

        # --- OWNER ---
        campos.update({
            "Last Name":        datos.get("owner_last", ""),
            "First Name":       datos.get("owner_first", ""),
            "Business_Name":    datos.get("owner_business", ""),   # Así está en el PDF original
            "Business Address": datos.get("owner_address", ""),
            "City":             datos.get("owner_city", ""),
            "State_2":          datos.get("owner_state", "NY"),
            "Zip":              datos.get("owner_zip", ""),
            "Business Tel":     datos.get("owner_phone", ""),
            "Mobile Tel":       datos.get("owner_phone", ""),
            "EMail":            datos.get("owner_email", ""),
        })

        elec = ELECTRICIAN; emp = COMPANY; cs = CENTRAL_STATION; specs = TECH_DEFAULTS

        # --- ELECTRICIAN ---
        campos.update({
            "First Name_2": elec.get("First Name", ""), "Last Name_2": elec.get("Last Name", ""),
            "Business Name_2": elec.get("Company Name", ""), "Business Address_2": elec.get("Address", ""),
            "City_2": elec.get("City", ""), "State_3": elec.get("State", ""), "Zip_2": elec.get("Zip", ""),
            "Business Tel_2": elec.get("Phone", ""), "License Number": elec.get("License No", ""),
            "Date of Expiration": elec.get("Expiration", "")
        })

        # --- COMPANY (Fire Alarm Vendor) ---
        campos.update({
            "First Name_3": emp.get("First Name", ""), "Last Name_3": emp.get("Last Name", ""),
            "Business Name_3": emp.get("Company Name", ""), "Business Address_3": emp.get("Address", ""),
            "City_3": emp.get("City", ""), "State_4": emp.get("State", ""), "Zip_3": emp.get("Zip", ""),
            "Business Tel_3": emp.get("Phone", ""), "COF S97": emp.get("COF S97", ""),
            "Date of Expiration_2": emp.get("Expiration", "")
        })

        # --- CENTRAL STATION ---
        campos.update({
            "Business Name_4": cs.get("Company Name", ""), "Station Code": cs.get("CS Code", ""),
            "Business Address_4": cs.get("Address", ""), "City_4": cs.get("City", ""),
            "State_5": cs.get("State", ""), "Zip_4": cs.get("Zip", ""),
            "Business Tel_4": cs.get("Phone", ""), "New_2": "/On"
        })

        # --- FLOOR COLUMNS ---
        mapa_col = {p: i+1 for i, p in enumerate(pisos_trabajados)}
        for p, i in mapa_col.items(): campos[f'floors{i}'] = p

        # --- DEVICE ROWS ---
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
            mapa_fil[dev] = (f, cat, idx)

            m, a, g, t = obtener_cols_derecha(f, cat, idx)
            if m: campos[m] = specs.get('Manufacturer', '')
            if a: campos[a] = specs.get('Approval', '')
            if g: campos[g] = specs.get('WireGauge', '')
            if t: campos[t] = specs.get('WireType', '')

            fila_actual[cat] += 1

        # --- QUANTITIES ---
        totales = {}
        for item in datos_instalacion:
            d, p, q = item['device'], item['floor'], int(item['qty'])
            if d in mapa_fil and p in mapa_col:
                r, cat, idx = mapa_fil[d]
                c = mapa_col[p]
                campos[f"r{r}c{c}"] = str(q)
                totales[r] = totales.get(r, 0) + q

        for r, t in totales.items(): campos[f"r{r}c32"] = str(t)

        rellenar_pdf_inteligente(input_pdf, output_pdf, campos)
        print("   ✅ A-433 Generated.")
    except Exception as e:
        print(f"   ❌ A-433 Error: {e}")
        raise


# ==========================================
# 5. GENERADOR B-45
# ==========================================
def generar_b45(datos, input_pdf, output_pdf):
    print("📄 4. Generating B-45...")
    try:
        exp = EXPEDITOR
        campos = {
            "adress": f"{datos.get('house','')} {datos.get('street','')}, {datos.get('borough','')}, NY {datos.get('zip','')}",
            "name":     f"{exp.get('First Name','')} {exp.get('Last Name','')}".strip(),
            "title":    "Expeditor",
            "lic":      exp.get("Reg No", ""),
            "company":  exp.get("Company Name", ""),
            "caddress": f"{exp.get('Address','')}, {exp.get('City','')}, {exp.get('State','NY')} {exp.get('Zip','')}",
            "cphone":   exp.get("Phone", ""),
            "email":    exp.get("Email", ""),
            "pname":    f"{exp.get('First Name','')} {exp.get('Last Name','')}".strip(),
            "date1":    fecha_hoy
        }
        rellenar_pdf_inteligente(input_pdf, output_pdf, campos)
        print("   ✅ B-45 Generated.")
    except Exception as e:
        print(f"   ❌ B-45 Error: {e}")
        raise


# ==========================================
# 6. REPORTE DE AUDITORÍA
# ==========================================
def generar_reporte_auditoria(datos, nombre_archivo="REPORTE_LOGICA.txt"):
    print(f" 5. Generating Audit Report...")
    try:
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            f.write("AUTOMATED GENERATION REPORT\n")
            f.write("=================================================\n")
            f.write(f"DATE: {fecha_hoy}\n")
            f.write(f"BIN: {datos.get('bin')}\n")
            f.write(f"ADDRESS: {datos.get('house')} {datos.get('street')}\n\n")
            f.write("*** ARTIFICIAL INTELLIGENCE NOTES (PLEASE REVIEW):\n")
            f.write("-------------------------------------------------\n")
            f.write(f"1. CONSTRUCTION CLASS:\n   - Original Value (DB): {datos.get('raw_construction_class', 'N/A')}\n   - Final Value on PDF:  {datos.get('construction_class')}\n   - System Note:         {datos.get('debug_nota_const', '')}\n\n")
            f.write(f"2. OCCUPANCY GROUP:\n   - Original Value (DB): {datos.get('raw_occupancy', 'N/A')}\n   - Final Value on PDF:  {datos.get('occupancy_group')}\n   - System Note:         {datos.get('debug_nota_occ', '')}\n\n")
            f.write("=================================================\n")
            f.write("LEGAL DISCLAIMER & TERMS OF USE:\n")
            f.write("-------------------------------------------------\n")
            f.write("1. NO GOVERNMENT AFFILIATION:\n")
            f.write("   Fire Form Pro is an independent software tool. It is NOT affiliated with,\n")
            f.write("   endorsed by, or connected to the NYC Fire Department (FDNY), the\n")
            f.write("   Department of Buildings (DOB), or any other government agency.\n\n")
            f.write("2. DATA ACCURACY AND PUBLIC RECORDS:\n")
            f.write("   Property and ownership data are automatically retrieved from public NYC\n")
            f.write("   databases (BIS, DOB NOW, PLUTO, Geoclient) based on the provided BIN.\n")
            f.write("   Due to filing delays, database inconsistencies, and historical variations,\n")
            f.write("   this information is provided 'AS IS' and is NOT guaranteed to be 100%\n")
            f.write("   accurate or current.\n\n")
            f.write("3. PROFESSIONAL RESPONSIBILITY:\n")
            f.write("   These generated documents are intended solely as a drafting aid. The\n")
            f.write("   Architect, Engineer of Record, Expeditor, and/or Contractor assume full\n")
            f.write("   and strict responsibility for verifying, correcting, and validating all\n")
            f.write("   fields prior to signing, sealing, and submitting these forms to the FDNY.\n")
        print(f"    Report Generated: {nombre_archivo}")
    except Exception as e:
        print(f"   [ERROR] Report Error: {e}")


if __name__ == "__main__":
    print("Run app.py to start the application.")
