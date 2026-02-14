import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

# --- CONFIG ---
BASE_URL = "http://127.0.0.1:8000"
TRANSPORT_MODE_ID = 2
MAX_WORKERS = 15  

# --- LOOKUP LOGIC ---
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
        return {(s['city_id'], s['name'].lower()): s['id'] for s in resp.json()}
    except Exception as e:
        print(f"Error fetching stations: {e}")
        return {}

city_lookup = get_city_lookup()
station_lookup = get_station_lookup()

def resolve_station(name, city_id):
    name = name.lower().strip()
    key = (city_id, name)
    
    if key in station_lookup:
        return station_lookup[key]
    

    payload = {"name": name, "city_id": city_id}
    try:
        r = requests.post(f"{BASE_URL}/stations/", json=payload)
        r.raise_for_status()
        new_id = r.json()["id"]
        station_lookup[key] = new_id 
        return new_id
    except Exception as e:
        return None

# --- WORKER FUNCTION ---
def upload_route(record):
    """Function executed by each thread."""
    o_city_name = str(record["origin_city"]).lower().strip()
    d_city_name = str(record["destination_city"]).lower().strip()
    o_stat_name = str(record["origin_station"]).lower().strip()
    d_stat_name = str(record["destination_station"]).lower().strip()
    
    o_city_id = city_lookup.get(o_city_name)
    d_city_id = city_lookup.get(d_city_name)

    if not o_city_id or not d_city_id:
        return f"Skip: City not found for {o_city_name} or {d_city_name}"

    o_stat_id = resolve_station(o_stat_name, o_city_id)
    d_stat_id = resolve_station(d_stat_name, d_city_id)

    if o_stat_id and d_stat_id:
        payload = {
            "origin_station_id": o_stat_id,
            "destination_station_id": d_stat_id,
            "price": float(record["price"]),
            "transport_mode_id": TRANSPORT_MODE_ID,
            "notes": "Imported from Rail Fares Dataset"
        }
        try:
            res = requests.post(f"{BASE_URL}/routes/", json=payload, timeout=10)
            if res.status_code in [200, 201]:
                return f"Success: {o_stat_name} -> {d_stat_name}"
            return f"Error {res.status_code}: {o_stat_name} -> {d_stat_name}"
        except Exception as e:
            return f"Request Failed: {e}"
    return f"Failed to resolve stations for {o_stat_name}/{d_stat_name}"

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    df = pd.read_csv('extracted_fares2.csv')
    data = df.to_dict(orient='records')
    
    print(f"Starting parallel upload of {len(data)} routes using {MAX_WORKERS} workers...")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Map the upload function to our data
        futures = [executor.submit(upload_route, record) for record in data]
        
        for i, future in enumerate(as_completed(futures)):
            result = future.result()
            # Print status every 10 records to avoid flooding the console
            if i % 10 == 0 or "Error" in result:
                print(f"[{i}/{len(data)}] {result}")

    print("Upload process complete.")