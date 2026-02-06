from lxml import etree
from get_valid_files import get_valid_files

ns = {'nx': 'http://www.netex.org.uk/netex'}

def get_zone_for_stop(stop_id, root):
    # get the farezone ID for a given stop. This uses the 'atco.....'
    xpath = f"//nx:FareZone[nx:members/nx:ScheduledStopPointRef[@ref='{stop_id}']]"
    zone = root.xpath(xpath, namespaces=ns)
    if zone:
        return zone[0].get('id')
    return None

def get_fare(origin_naptan, dest_naptan, root):
    # 1. Map the naptans to fare zones
    origin_zone = get_zone_for_stop(origin_naptan, root)
    dest_zone = get_zone_for_stop(dest_naptan, root)
    
    if not origin_zone or not dest_zone:
        return f"Could not find zones for stops: {origin_naptan} -> {dest_naptan}"
    
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
        return f"No route found between zones {origin_zone} and {dest_zone}"
    
    element_id = element[0].get('id')

    # 3. Find the Cell that links this DistanceMatrixElement to a price
    # In your XML, the Cell contains a DistanceMatrixElementPrice which points to our ID
    cell_query = f'//nx:Cell[.//nx:DistanceMatrixElementRef[@ref="{element_id}"]]'
    cell = root.xpath(cell_query, namespaces=ns)
    
    if not cell:
        return f"No price cell found for route ID: {element_id}"
    
    # 4. From that cell, get the GeographicalIntervalPriceRef
    price_ref_elem = cell[0].xpath(".//nx:GeographicalIntervalPriceRef", namespaces=ns)
    if not price_ref_elem:
        return "Could not find a price reference in the cell."
    
    price_ref_id = price_ref_elem[0].get('ref')
    
    # 5. Finally, find the GeographicalIntervalPrice with that ID and get the Amount
    amount_query = f'//nx:GeographicalIntervalPrice[@id="{price_ref_id}"]/nx:Amount'
    amount = root.xpath(amount_query, namespaces=ns)
    
    if amount:
        return amount[0].text
    
    return "Price ID found, but no <Amount> tag exists for it."


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
            fare = get_fare(city["atco"].strip(), chosen_cities[j]["atco"].strip(), root)
            #print("Fare between " + city["city_name"] + " and " + chosen_cities[j]["city_name"] + " is £" + str(fare))



#print(valid_files[0])
#print(extract_all_cities(root))


# Test with your Coventry to Birmingham IDs
#print(get_fare('atco:43000005002', 'atco:43002103108'))