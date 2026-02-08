from datetime import datetime

def get_clean_station_nlc(loc_path, search_term):
    search_term = search_term.upper()
    valid_results = []
    
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

                if search_term in name:
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
