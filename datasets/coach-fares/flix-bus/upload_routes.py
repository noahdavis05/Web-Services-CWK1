import requests
import pandas as pd

BASE_URL = "http://127.0.0.1:8000"
TRANSPORT_MODE_ID = 1  # Set to 1 for coach

# 1. Fetch lookups once to minimize API calls
def get_city_lookup():
    try:
        resp = requests.get(f"{BASE_URL}/city/")
        resp.raise_for_status()
        return {c['name'].lower(): c['id'] for c in resp.json()}
    except Exception as e:
        print(f"Error fetching cities: {e}")
        return {}

def get_station_lookup():
    try:
        resp = requests.get(f"{BASE_URL}/stations/")
        resp.raise_for_status()
        # Key by (city_id, station_name) to be unique across the DB
        return {(s['city_id'], s['name'].lower()): s['id'] for s in resp.json()}
    except Exception as e:
        print(f"Error fetching stations: {e}")
        return {}

# Initialize local caches
city_lookup = get_city_lookup()
station_lookup = get_station_lookup()

def resolve_station(name, city_id):
    name = name.lower().strip()
    key = (city_id, name)
    
    if key in station_lookup:
        return station_lookup[key]
    
    # RESTful POST to create a new station resource if it doesn't exist
    print(f"Creating station: '{name}' in City ID: {city_id}")
    payload = {"name": name, "city_id": city_id}
    try:
        r = requests.post(f"{BASE_URL}/stations/", json=payload)
        r.raise_for_status()
        new_id = r.json()["id"]
        station_lookup[key] = new_id 
        return new_id
    except Exception as e:
        print(f"Failed to create station {name}: {e}")
        return None

# --- Main Execution ---

# Load the CSV
df = pd.read_csv('extracted_fares.csv')
# Standardize column names (ensuring they match your CSV header)
# Format: origin_city,destination_city,origin_station,destination_station,price
data = df.to_dict(orient='records')

print(f"Starting upload of {len(data)} routes...")

for record in data:
    # 1. Extract and normalize names from the CSV record
    o_city_name = str(record["origin_city"]).lower().strip()
    d_city_name = str(record["destination_city"]).lower().strip()
    o_stat_name = str(record["origin_station"]).lower().strip()
    d_stat_name = str(record["destination_station"]).lower().strip()
    price = round(record["price"], 2)

    # 2. Get City IDs (Guaranteed to exist per your requirements)
    o_city_id = city_lookup.get(o_city_name)
    d_city_id = city_lookup.get(d_city_name)

    if not o_city_id or not d_city_id:
        missing = o_city_name if not o_city_id else d_city_name
        print(f"Skipping: City '{missing}' not found in database lookup.")
        continue

    # 3. Resolve Station IDs
    o_stat_id = resolve_station(o_stat_name, o_city_id)
    d_stat_id = resolve_station(d_stat_name, d_city_id)

    if o_stat_id and d_stat_id:
        # 4. Construct Route Payload
        route_payload = {
            "origin_station_id": o_stat_id,
            "destination_station_id": d_stat_id,
            "price": float(price),
            "transport_mode_id": TRANSPORT_MODE_ID,
            "notes": "Flix Bus route"
        }

        # 5. POST the Route
        try:
            res = requests.post(f"{BASE_URL}/routes/", json=route_payload)
            if res.status_code in [200, 201]:
                print(f"Route Created: {o_stat_name} -> {d_stat_name} (£{price})")
            else:
                print("ERROR", res.status_code, res.text)
        except Exception as e:
            print(f"Error posting route: {e}")

print("Upload process complete.") #24291