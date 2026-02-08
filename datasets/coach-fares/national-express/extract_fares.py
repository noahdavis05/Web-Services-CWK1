from lxml import etree
from get_valid_files import get_valid_files
import pprint

ns = {'nx': 'http://www.netex.org.uk/netex'}

def get_zone_for_stop(stop_id, root):
    # get the farezone ID for a given stop. This uses the 'atco.....'
    xpath = f"//nx:FareZone[nx:members/nx:ScheduledStopPointRef[@ref='{stop_id}']]"
    zone = root.xpath(xpath, namespaces=ns)
    if zone:
        return zone[0].get('id')
    return None

def get_station_name(naptan_id, root):
    """
    Finds the Name of a station based on its NaPTAN (ATCO) ID.
    """
    # Find the ScheduledStopPoint with the matching ID
    xpath = f"//nx:ScheduledStopPoint[@id='{naptan_id}']"
    stop_point = root.xpath(xpath, namespaces=ns)
    
    if stop_point:
        # 1. Try to get the specific Name (e.g., 'Pool Meadow Bus Station')
        name_elem = stop_point[0].find('nx:Name', namespaces=ns)
        # 2. Try to get the Suffix (e.g., 'Stand B') to make it precise
        suffix_elem = stop_point[0].find('nx:NameSuffix', namespaces=ns)
        
        station_name = name_elem.text if name_elem is not None else "Unknown Station"
        if suffix_elem is not None:
            station_name = f"{station_name} ({suffix_elem.text})"
            
        return station_name
        
    return "Station ID not found in file"

def get_fare(origin_naptan, dest_naptan, root):
    # 1. Map the naptans to fare zones
    origin_zone = get_zone_for_stop(origin_naptan, root)
    dest_zone = get_zone_for_stop(dest_naptan, root)
    
    if not origin_zone or not dest_zone:
        return None
    
    #print(f"DEBUG: origin_zone='{origin_zone}', dest_zone='{dest_zone}'")

    # 2. Get DistanceMatrixElement ID from the zone ids
    xpath_query = (
        f'//nx:DistanceMatrixElement['
        f'nx:StartTariffZoneRef[@ref="{origin_zone}"] and '
        f'nx:EndTariffZoneRef[@ref="{dest_zone}"]]'
    )
    element = root.xpath(xpath_query, namespaces=ns)
    #print(f"DEBUG: origin_zone='{origin_zone}', dest_zone='{dest_zone}'")
    
    if not element:
        return None
    
    element_id = element[0].get('id')

    # 3. Find the Cell that links this DistanceMatrixElement to a price
    # In your XML, the Cell contains a DistanceMatrixElementPrice which points to our ID
    cell_query = f'//nx:Cell[.//nx:DistanceMatrixElementRef[@ref="{element_id}"]]'
    cell = root.xpath(cell_query, namespaces=ns)
    
    if not cell:
        return None
    
    # 4. From that cell, get the GeographicalIntervalPriceRef
    price_ref_elem = cell[0].xpath(".//nx:GeographicalIntervalPriceRef", namespaces=ns)
    if not price_ref_elem:
        return None
    
    price_ref_id = price_ref_elem[0].get('ref')
    
    # 5. Finally, find the GeographicalIntervalPrice with that ID and get the Amount
    amount_query = f'//nx:GeographicalIntervalPrice[@id="{price_ref_id}"]/nx:Amount'
    amount = root.xpath(amount_query, namespaces=ns)
    
    if amount:
        return amount[0].text
    
    return None


# Function will take the xml file root and extract all the cities from it
# It will return the cities and their corresponding natpan
def extract_all_cities(root):
    zone_data = []

    # Find every FareZone element
    for zone in root.findall('.//nx:FareZone', ns):
        # Extract the Name (e.g., Coventry)
        name_elem = zone.find('nx:Name', ns)
        name = name_elem.text if name_elem is not None else "Unknown"
        
        # Extract the ATCO code from ScheduledStopPointRef
        # This is usually in the 'ref' attribute
        stop_ref = zone.find('.//nx:ScheduledStopPointRef', ns)
        atco_code = stop_ref.get('ref') if stop_ref is not None else "No ATCO"
        
        zone_data.append({
            'city_name': name,
            'atco_code': atco_code
        })
        
    return zone_data


# get all the adult single fares
valid_files = get_valid_files()

# read the list of all cities of interest from cities.txt
f = open("cities.txt", "r")
allowed_cities = [line.strip() for line in f.readlines()]
f.close()

# Now we want to go through every valid file, and check each valid file
# for fares between any of our cities of interest

all_fares = []
for valid_file in valid_files:
    tree = etree.parse("NATX_2025_11_05/" + valid_file) 
    root = tree.getroot()

    # now we need to check all stops on this route to see if they 
    # match any of our cities. Basically check if a stop name contains
    # any of our cities
    chosen_cities = []
    route_cities = extract_all_cities(root)
    
    for rc in route_cities:
        #print(rc["city_name"])
        for ac in allowed_cities:
            if ac.lower() in rc["city_name"].lower():
                chosen_cities.append(
                    {
                        "city_name":ac.lower(),
                        "atco": rc["atco_code"]
                    }
                )


    #print(chosen_cities)

    # now for every combination of these chosen cities work out fares between them
    for i, city in enumerate(chosen_cities):
        for j in range(i+1, len(chosen_cities)):
            # ensure the cities are not the same
            if city["city_name"] == chosen_cities[j]["city_name"]:
                continue
            
            fare = get_fare(city["atco"].strip(), chosen_cities[j]["atco"].strip(), root)
            if fare == None:
                continue
            origin_station = get_station_name(city["atco"], root)
            destination_station = get_station_name(chosen_cities[j]["atco"], root)
            route_details = {
                "origin_station_name": origin_station.lower(),
                "destination_station_name" : destination_station.lower(),
                "origin_city_name": city["city_name"].lower(),
                "destination_city_name" : chosen_cities[j]["city_name"].lower(),
                "price": fare
            }
            all_fares.append(route_details)
            #print("Fare between " + city["city_name"] + " and " + chosen_cities[j]["city_name"] + " is £" + str(fare))



#print(valid_files[0])
#print(extract_all_cities(root))


# Test with your Coventry to Birmingham IDs
#print(get_fare('atco:43000005002', 'atco:43002103108'))

#pprint.pprint(all_fares)
# we have lots of duplicates from city to city - not too important, therefore just keep one of each.
# if prices are different we keep all prices.

unique_fairs = {}

for fare in all_fares:
    key = (fare["origin_city_name"], fare["destination_city_name"], fare["price"])

    if key in unique_fairs:
        continue
    unique_fairs[key] = fare

pprint.pprint(list(unique_fairs.values()), width=120)

# now for all fares we can use our api to add these routes to the database
import requests

BASE_URL = "http://127.0.0.1:8000"

# 1. Fetch all cities once at the start to get their IDs
def get_city_lookup():
    resp = requests.get(f"{BASE_URL}/city/")
    return {c['name'].lower(): c['id'] for c in resp.json()}

# 2. Fetch all stations to avoid creating duplicates
def get_station_lookup():
    resp = requests.get(f"{BASE_URL}/stations/")
    # Key by (city_id, station_name) to be unique across the whole DB
    return {(s['city_id'], s['name'].lower()): s['id'] for s in resp.json()}

city_lookup = get_city_lookup()
station_lookup = get_station_lookup()

for fare in unique_fairs.values():
    # Normalize names
    o_city = fare["origin_city_name"].lower()
    o_stat = fare["origin_station_name"].lower()
    d_city = fare["destination_city_name"].lower()
    d_stat = fare["destination_station_name"].lower()

    # can guarantee that city ID exists
    o_city_id = city_lookup.get(o_city)
    d_city_id = city_lookup.get(d_city)

    if not o_city_id or not d_city_id:
        print(f"Skipping: City {o_city if not o_city_id else d_city} not found in DB.")
        continue

    # get or create station
    def resolve_station(name, city_id):
        key = (city_id, name)
        if key in station_lookup:
            return station_lookup[key]
        
        # RESTful POST to create a new station resource
        print(f"Creating station: {name}")
        payload = {"name": name, "city_id": city_id}
        r = requests.post(f"{BASE_URL}/stations/", json=payload)
        new_id = r.json()["id"]
        station_lookup[key] = new_id 
        return new_id

    o_stat_id = resolve_station(o_stat, o_city_id)
    d_stat_id = resolve_station(d_stat, d_city_id)

    route_payload = {
        "origin_station_id": o_stat_id,
        "destination_station_id": d_stat_id,
        "price": fare["price"],
        "transport_mode_id": 1, 
        "notes": "Imported from BODS NeTEx"
    }

    #print(route_payload)
    
    res = requests.post(f"{BASE_URL}/routes/", json=route_payload)
    if res.status_code == 200 or res.status_code == 201:
        print(f"Route Created: {o_stat} -> {d_stat} (£{fare['price']})")
    