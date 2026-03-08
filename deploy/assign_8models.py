"""
Create 5 new farmers from Data_Demo.xlsx, assign 8 farmers to 8 models,
update model names, delete GL09.
"""
import sys
import requests

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

PB_URL = "https://tcn.lvtcenter.it.com"
PB_EMAIL = "admin@lvtcenter.it.com"
PB_PASS = "Admin12345#"

session = requests.Session()


def auth():
    r = session.post(f"{PB_URL}/api/collections/_superusers/auth-with-password",
                     json={"identity": PB_EMAIL, "password": PB_PASS})
    r.raise_for_status()
    token = r.json()["token"]
    session.headers.update({"Authorization": f"Bearer {token}"})
    print("Authenticated OK")


def get_all(collection, filter_str=""):
    items = []
    page = 1
    while True:
        params = {"page": page, "perPage": 500}
        if filter_str:
            params["filter"] = filter_str
        r = session.get(f"{PB_URL}/api/collections/{collection}/records", params=params)
        r.raise_for_status()
        d = r.json()
        items.extend(d.get("items", []))
        if page >= d.get("totalPages", 1):
            break
        page += 1
    return items


def create_record(collection, data):
    r = session.post(f"{PB_URL}/api/collections/{collection}/records", json=data)
    if r.status_code not in (200, 201):
        raise Exception(f"Create {collection} failed [{r.status_code}]: {r.text[:300]}")
    return r.json()


def update_record(collection, rid, data):
    r = session.patch(f"{PB_URL}/api/collections/{collection}/records/{rid}", json=data)
    if r.status_code != 200:
        raise Exception(f"Update {collection}/{rid} failed [{r.status_code}]: {r.text[:300]}")
    return r.json()


def delete_record(collection, rid):
    r = session.delete(f"{PB_URL}/api/collections/{collection}/records/{rid}")
    return r.status_code in (200, 204)


# 5 new farmers to create
NEW_FARMERS = [
    {
        "farmer_code": "DL-KB-CN-001",
        "full_name": "Mlô Y Nuêl",
        "phone": "0367896274",
        "province": "Đăk Lăk",
        "district": "Krông Buk",
        "commune": "Cư Né",
        "village": "Buôn Drah 2",
        "total_farms": 1,
        "ethnicity": "Ê đê",
        "gender": "Nam",
        "status": "active",
    },
    {
        "farmer_code": "DL-KB-CN-002",
        "full_name": "Nguyễn Văn Hải",
        "phone": "0332578567",
        "province": "Đăk Lăk",
        "district": "Krông Buk",
        "commune": "Cư Né",
        "village": "Ea Krôm",
        "total_farms": 1,
        "ethnicity": "Kinh",
        "gender": "Nam",
        "status": "active",
    },
    {
        "farmer_code": "DL-KB-ES-001",
        "full_name": "Niê Y Set",
        "province": "Đăk Lăk",
        "district": "Krông Buk",
        "commune": "Ea Sin",
        "village": "Ea Sin",
        "total_farms": 2,
        "ethnicity": "Ê đê",
        "gender": "Nam",
        "status": "active",
    },
    {
        "farmer_code": "DL-KB-CP-001",
        "full_name": "Mlô Y Thu",
        "phone": "0389995602",
        "province": "Đăk Lăk",
        "district": "Krông Buk",
        "commune": "Cư Pơng",
        "village": "Tlan",
        "total_farms": 3,
        "ethnicity": "Ê đê",
        "gender": "Nam",
        "status": "active",
    },
    {
        "farmer_code": "DL-KB-CP-002",
        "full_name": "Adrơng Y Eru",
        "phone": "0365710968",
        "province": "Đăk Lăk",
        "district": "Krông Buk",
        "commune": "Cư Pơng",
        "village": "Ea Brơ",
        "total_farms": 2,
        "ethnicity": "Ê đê",
        "gender": "Nam",
        "status": "active",
    },
]

# Model assignment: model_code -> (farmer_full_name, area_ha, commune, village)
MODEL_ASSIGNMENT = {
    "GL01-XP": ("Anưr", 2.27, None, None),           # existing farmer
    "GL02-XP": ("Mlô Y Nuêl", 1.0, "Cư Né", "Buôn Drah 2"),
    "GL03-XP": ("Nguyễn Văn Hải", 1.4, "Cư Né", "Ea Krôm"),
    "GL04-XP": ("Niê Y Set", 2.3, "Ea Sin", "Ea Sin"),
    "GL05-XP": ("Vũ Quang Trường", 1.5, None, None),  # existing farmer
    "GL06-XP": ("Mlô Y Thu", 1.8, "Cư Pơng", "Tlan"),
    "GL07-XP": ("Hồ văn Biển", 3.0, None, None),      # existing farmer
    "GL08-XP": ("Adrơng Y Eru", 5.3, "Cư Pơng", "Ea Brơ"),
}

# Income data for new farmers
NEW_INCOME = [
    {"name": "Mlô Y Nuêl", "production_tons": 0.5, "coffee_area": 1.0},
    {"name": "Nguyễn Văn Hải", "production_tons": 4.5, "coffee_area": 1.4},
    {"name": "Niê Y Set", "production_tons": 2.8, "coffee_area": 2.3},
    {"name": "Mlô Y Thu", "production_tons": 2.1, "coffee_area": 1.8},
    {"name": "Adrơng Y Eru", "production_tons": 8.3, "coffee_area": 5.3},
]


def main():
    print("=" * 60)
    print("  Assign 8 Farmers to 8 Models")
    print("=" * 60)
    auth()

    # Step 1: Create 5 new farmers
    print("\n[STEP 1] Creating 5 new farmers...")
    farmer_name_to_id = {}

    # First, get existing farmers
    existing = get_all("farmers")
    for f in existing:
        farmer_name_to_id[f["full_name"]] = f["id"]
        print(f"  EXISTING: {f['full_name']} (id={f['id']})")

    # Create new farmers
    for fd in NEW_FARMERS:
        name = fd["full_name"]
        if name in farmer_name_to_id:
            print(f"  SKIP (exists): {name}")
            continue
        try:
            rec = create_record("farmers", fd)
            farmer_name_to_id[name] = rec["id"]
            print(f"  CREATED: {name} (id={rec['id']})")
        except Exception as e:
            print(f"  ERROR creating {name}: {e}")

    # Step 2: Get all models and assign farmers
    print("\n[STEP 2] Assigning farmers to models...")
    models = get_all("demo_models")
    model_map = {m["model_code"]: m for m in models}

    for model_code, (farmer_name, area, commune, village) in MODEL_ASSIGNMENT.items():
        model = model_map.get(model_code)
        if not model:
            print(f"  SKIP: model {model_code} not found")
            continue

        farmer_id = farmer_name_to_id.get(farmer_name)
        if not farmer_id:
            # Try partial match
            for n, fid in farmer_name_to_id.items():
                if farmer_name.lower() in n.lower() or n.lower() in farmer_name.lower():
                    farmer_id = fid
                    break

        if not farmer_id:
            print(f"  ERROR: farmer '{farmer_name}' not found for {model_code}")
            continue

        update_data = {
            "farmer_id": farmer_id,
            "name": f"Mô hình {model_code.split('-')[0]} - {farmer_name}",
            "area": area,
        }
        if commune:
            update_data["location"] = f"{village}, {commune}"

        try:
            update_record("demo_models", model["id"], update_data)
            print(f"  ASSIGNED: {model_code} -> {farmer_name} (area={area}ha)")
        except Exception as e:
            print(f"  ERROR assigning {model_code}: {e}")

    # Step 3: Delete GL09
    print("\n[STEP 3] Deleting GL09-XP...")
    gl09 = model_map.get("GL09-XP")
    if gl09:
        # First check for related records
        for coll in ["model_diary", "model_inspections", "model_consumables", "annual_activities"]:
            try:
                related = get_all(coll, f"model_id='{gl09['id']}'")
                for rec in related:
                    delete_record(coll, rec["id"])
                    print(f"  Deleted related {coll} record")
            except:
                pass

        if delete_record("demo_models", gl09["id"]):
            print(f"  DELETED: GL09-XP (id={gl09['id']})")
        else:
            print(f"  ERROR deleting GL09-XP")
    else:
        print("  GL09-XP not found (already deleted?)")

    # Step 4: Create income_records for new farmers
    print("\n[STEP 4] Creating income_records for new farmers...")
    for inc in NEW_INCOME:
        fid = farmer_name_to_id.get(inc["name"])
        if not fid:
            print(f"  SKIP: farmer '{inc['name']}' not found")
            continue

        # Check if already exists
        existing_ir = get_all("income_records", f"farmer_id='{fid}'")
        if existing_ir:
            print(f"  SKIP (exists): {inc['name']} already has income record")
            continue

        data = {
            "farmer_id": fid,
            "year": 2025,
            "production_tons": inc["production_tons"],
            "coffee_revenue": inc["production_tons"] * 40000000,  # ~40M VND/ton estimate
        }
        try:
            create_record("income_records", data)
            print(f"  CREATED: income for {inc['name']} ({inc['production_tons']} tons)")
        except Exception as e:
            print(f"  ERROR: {e}")

    # Final summary
    print("\n" + "=" * 60)
    print("  FINAL STATE")
    print("=" * 60)
    for coll in ["farmers", "demo_models", "income_records"]:
        recs = get_all(coll)
        print(f"  {coll}: {len(recs)} records")

    print("\n  Model -> Farmer assignments:")
    models = get_all("demo_models")
    farmers_all = get_all("farmers")
    farmer_id_name = {f["id"]: f["full_name"] for f in farmers_all}

    for m in sorted(models, key=lambda x: x.get("model_code", "")):
        fid = m.get("farmer_id", "")
        fname = farmer_id_name.get(fid, "---")
        print(f"    {m['model_code']}: {m.get('name', '')} -> {fname}")

    print("\n  DONE!")


if __name__ == "__main__":
    main()
