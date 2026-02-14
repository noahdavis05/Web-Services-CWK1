import re
import pandas as pd

def get_clean_station_nlc(loc_path, search_term):
    search_term = search_term.upper()
    valid_results = []

    # create regex for matching
    pattern = re.compile(rf'^{re.escape(search_term)}\b')
    
    with open(loc_path, 'r', encoding='latin-1') as f:
        for line in f:
            if line.startswith('RL'):
                # Slicing based on RSPS5045
                nlc = line[36:40].strip()
                name = line[40:56].strip()
                crs = line[56:59].strip()      # CRS Code (e.g. BTH)
                end_date = line[9:17].strip()   # 31122999 is active
                fare_group = line[69:75].strip()
                
                # FILTER 1: Active records only
                if end_date != "31122999":
                    continue
                
                # FILTER 2: Ignore non-rail locations
                # Most 'Conf', '+Bus', and 'Coach' records have no CRS code
                # and often contain specific keywords.
                if "+BUS" in name or "CONF" in name or "PKING" in name:
                    continue

                if pattern.search(name):
                    
                    # the regex ensure that if a name such as chester doesn't work for manchester
                    # but not for if the name contains a name e.g.
                    # bradford and bradford on avon
                    if len(name) > len(search_term):
                        excluded_suffixes = [" ROAD", " SOUTH", " NORTH", " EAST", " WEST", " PARADE"]
                    
                        # If name has a suffix we didn't ask for, skip it
                        # Example: Search "CHESTER", name "CHESTER ROAD" -> Skip.
                        if any(name.endswith(s) for s in excluded_suffixes) and name != search_term:
                            if search_term not in name: # unless the search term actually includes the suffix
                                continue

                        # Handle the "Bradford on Avon" / "Matlock Bath" logic
                        if len(name) > len(search_term):
                            different_place_indicators = ["ON AVON", "UNDER LYME", "UPON THAMES", "ON SEA", "MATLOCK"]
                            if any(ind in name for ind in different_place_indicators if ind not in search_term):
                                continue

                    # Logic: If it's a City Group (STNS), it usually has no CRS.
                    # If it's a Station, it MUST have a CRS.
                    is_real_location = (len(crs) == 3 or " STNS" in name or " GROUP" in name) and nlc.isdigit()  
                    if is_real_location:
                        valid_results.append({
                            "name": name,
                            "nlc": nlc,
                            "crs": crs,
                            "master_nlc": fare_group if fare_group else nlc
                        })
    #print(valid_results)
    return valid_results


def get_cluster_ids(fsc_path, station_nlc):
    """
    Finds all Cluster IDs for a given Station NLC.
    Based on RSPS5045:
    Field 2 (CLUSTER_ID): Pos 2-5 (Index 1:5)
    Field 3 (CLUSTER_NLC): Pos 6-9 (Index 5:9)
    """
    cluster_ids = []
    
    # Ensure NLC is a 4-character string
    target_nlc = str(station_nlc).zfill(4)

    with open(fsc_path, 'r', encoding='latin-1') as f:
        for line in f:
            # Check if it's a valid Cluster record (usually starts with R or S)
            if len(line) >= 10:
                # The doc says Field 3 (the member NLC) starts at Position 6
                member_nlc = line[5:9]
                
                if member_nlc == target_nlc:
                    # Field 2 (the Cluster ID) starts at Position 2
                    cluster_id = line[1:5]
                    cluster_ids.append(cluster_id)
                    
    return list(set(cluster_ids)) # Use set to remove duplicates


def get_all_codes(station_name):
    all_codes = set()
    stations = get_clean_station_nlc("fares_data/RJFAF658.LOC", station_name)

    for station in stations:
        all_codes.add((station['nlc'], station['name']))
        all_codes.add((station['master_nlc'], station['name']))
        clusters = get_cluster_ids("fares_data/RJFAF658.FSC", station['nlc'])
        for cluster_id in clusters:
            all_codes.add((cluster_id, station['name']))

    return list(all_codes)


def get_cities_and_CRS():
    # 1. Load the ATCO codes (The "Truth List" from NaPTAN)
    # We force ATCOCode and Town to strings to avoid type-mismatch errors
    all_stations = pd.read_csv(
        "Stops.csv", 
        dtype={'Town': str, 'ATCOCode': str},
        low_memory=False
    )
    
    # Filter for Rail only and select columns
    all_stations = all_stations[all_stations['StopType'] == 'RLY']
    atco_data = all_stations[['LocalityName', 'ATCOCode']]

    # 2. Load the Rail References (The "Bridge")
    # Columns: 'AtcoCode', 'CrsCode'
    rail_refs = pd.read_csv(
        "RailReferences.csv", 
        dtype={'AtcoCode': str, 'CrsCode': str}
    )

    # 3. Efficiently Merge (The Handshake)
    # We use a 'left' join to keep all our NaPTAN stations
    # left_on/right_on handles the different capitalization of 'AtcoCode'
    merged_data = pd.merge(
        atco_data, 
        rail_refs, 
        left_on='ATCOCode', 
        right_on='AtcoCode', 
        how='left'
    )

    # Clean up: Remove the duplicate AtcoCode column from the merge
    merged_data = merged_data.drop(columns=['AtcoCode'])
    
    # 4. Final Verification
    # Drop any stations that don't have a CRS code (virtual/bus stops)
    merged_data = merged_data.dropna(subset=['CrsCode'])

    # Keep only the necessary columns 
    merged_data = merged_data[['LocalityName', 'CrsCode', 'ATCOCode', 'StationName']]


    print(f"Successfully mapped {len(merged_data)} rail stations to CRS codes.")
    return merged_data


def filter_cities_and_codes():

    # download all desired cities from cities.txt
    f = open("cities.txt")
    cities = [city.strip() for city in f.readlines()]
    f.close()
    
    # get all cities and crs codes
    data = get_cities_and_CRS()
    filtered_data = data[data['LocalityName'].isin(cities)]
    return filtered_data

def map_NLC_codes(df):
    """
    df: Pandas DataFrame containing ['Town', 'ATCOCode', 'CrsCode']
    Returns: Updated DataFrame with 'NLC' column
    """
    loc_path = "fares_data/RJFAF658.LOC"
    crs_to_nlc = {}

    print("Parsing .LOC file for CRS -> NLC mapping...")

    # 1. Build a dictionary from the .LOC file
    with open(loc_path, 'r', encoding='latin-1') as f:
        for line in f:
            if line.startswith('RL'):
                # Slicing based on the record structure we confirmed:
                # NLC (Chars 5-8), CRS (Chars 82-84)
                nlc_code = line[4:8].strip()
                crs_code = line[56:59].strip()
                
                if crs_code not in crs_to_nlc:
                    crs_to_nlc[crs_code] = []
                
                if nlc_code in crs_to_nlc[crs_code]:
                    continue
                crs_to_nlc[crs_code].append(nlc_code)
    print(crs_to_nlc["BTH"])
    # 2. Map the dictionary to your DataFrame
    # .map() looks at the 'CrsCode' column and finds the value in our dictionary
    df['NLC'] = df['CrsCode'].map(crs_to_nlc)

    # 3. Handle any misses
    # Some stations might be in NaPTAN but missing from this specific .LOC file version
    missing_count = df['NLC'].isna().sum()
    if missing_count > 0:
        print(f"Warning: {missing_count} stations could not be mapped to an NLC.")
        # Optional: Remove rows we couldn't map, as we can't get fares for them anyway
        df = df.dropna(subset=['NLC'])

    print(f"Successfully mapped {len(df)} stations to NLC codes.")
    return df





