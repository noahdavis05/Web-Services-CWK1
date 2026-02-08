import os
import requests
import csv
from extract_NLC import get_all_codes

# --- CONFIGURATION ---
BASE_URL = "http://127.0.0.1:8000"
FFL_PATH = "fares_data/RJFAF658.FFL"
OUTPUT_CSV = "extracted_fares2.csv"
CITIES_FILE = "cities.txt"

TICKET_TYPES = {
    "CDS": "Off Peak Single",
    "SDS": "Anytime Single",
    "SOS": "Anytime Single"
}

# --- STEP 1: LOAD CITIES & CODES ---
print("Step 1: Loading city NLC codes...")
with open(CITIES_FILE, "r") as f:
    city_names = [line.strip() for line in f.readlines()]

# all_city_data stores { 'city_name': { 'NLC_CODE': 'Station Name' } }
all_city_data = {}
all_allowed_nlcs = set()

for city in city_names:
    codes = get_all_codes(city)
    # Store as a dict for O(1) station name lookup later
    all_city_data[city.lower()] = {c[0]: c[1] for c in codes}
    for code, name in codes:
        all_allowed_nlcs.add(code)

# --- STEP 2: SINGLE-PASS FILE INDEXING ---
# Instead of searching the file 20,000 times, we read it ONCE.
print(f"Step 2: Indexing {FFL_PATH} (this may take a minute)...")
flows = {}  # flow_id -> (origin_nlc, dest_nlc)
prices = {} # flow_id -> list of (price, ticket_type)

with open(FFL_PATH, 'r', encoding='latin-1') as f:
    for line in f:
        # RF Records define the 'Flow' (Journey)
        if line.startswith("RF"):
            origin = line[2:6]
            destination = line[6:10]
            # Only index flows where BOTH stations are in our target cities
            if origin in all_allowed_nlcs and destination in all_allowed_nlcs:
                flow_id = line[42:49].strip()
                flows[flow_id] = (origin, destination)
        
        # RT Records define the 'Fare' (Price) for a Flow
        elif line.startswith("RT"):
            flow_id = line[2:9].strip()
            if flow_id in flows:
                t_type = line[9:12]
                if t_type in TICKET_TYPES:
                    price_val = int(line[12:20]) / 100.0
                    if flow_id not in prices:
                        prices[flow_id] = []
                    prices[flow_id].append((price_val, TICKET_TYPES[t_type]))

# --- STEP 3: MATCHING & CSV EXPORT ---
print(f"Step 3: Calculating cheapest routes and saving to {OUTPUT_CSV}...")

# Open CSV and write header if empty
file_exists = os.path.isfile(OUTPUT_CSV) and os.stat(OUTPUT_CSV).st_size > 0
f_out = open(OUTPUT_CSV, "a", encoding='utf-8')
if not file_exists:
    f_out.write("origin_city,destination_city,origin_station,destination_station,price\n")

for i, city_a in enumerate(city_names):
    city_a = city_a.lower()
    a_lookup = all_city_data[city_a] # {NLC: Name}
    
    print(f"Processing {city_a} ({i+1}/{len(city_names)})...")
    
    for j in range(i + 1, len(city_names)):
        city_b = city_names[j].lower()
        b_lookup = all_city_data[city_b] # {NLC: Name}
        
        pair_fares = []

        # Find all indexed flows that link these two specific cities
        for flow_id, (org, dest) in flows.items():
            # Check A -> B or B -> A
            is_fwd = (org in a_lookup and dest in b_lookup)
            is_bwd = (org in b_lookup and dest in a_lookup)

            if (is_fwd or is_bwd) and flow_id in prices:
                for price, t_name in prices[flow_id]:
                    # Map NLC back to station names
                    o_name = a_lookup.get(org) or b_lookup.get(org)
                    d_name = b_lookup.get(dest) or a_lookup.get(dest)
                    
                    pair_fares.append({
                        "o_stat": o_name,
                        "d_stat": d_name,
                        "price": price,
                        "org_city": city_a if is_fwd else city_b,
                        "dst_city": city_b if is_fwd else city_a
                    })

        if pair_fares:
            # Keep only the absolute cheapest
            cheapest = sorted(pair_fares, key=lambda x: x['price'])[0]
            
            # Write Forwards
            f_out.write(f"{cheapest['org_city']},{cheapest['dst_city']},{cheapest['o_stat']},{cheapest['d_stat']},{cheapest['price']}\n".lower())
            
            # Write Backwards (Mirroring your logic to ensure both directions exist)
            f_out.write(f"{cheapest['dst_city']},{cheapest['org_city']},{cheapest['d_stat']},{cheapest['o_stat']},{cheapest['price']}\n".lower())

    # Periodically save to disk
    f_out.flush()

f_out.close()
print("Done! All routes extracted.")