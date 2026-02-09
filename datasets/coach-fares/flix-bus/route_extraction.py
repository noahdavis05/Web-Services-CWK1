import os
import xml.etree.ElementTree as ET

# we will extract the routes between valid cities of ours.

def get_valid_routes(filepath, allowed_cities):
    """
    Docstring for get_valid_routes
    
    :param filepath: path to file we want to search for routes in
    :param allowed_cities: a list of valid cities which we want to find routes inbetween
    """
    ns = {'txc': 'http://www.transxchange.org.uk/'}
    
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
        return []

    # prioritize LocalityQualifier as it usually contains the city instead of stop name
    stop_to_city = {}
    for stop in root.findall('.//txc:AnnotatedStopPointRef', ns):
        stop_ref = stop.find('txc:StopPointRef', ns).text
        
        city_node = stop.find('txc:LocalityQualifier', ns)
        if city_node is None:
            city_node = stop.find('txc:LocalityName', ns)
            
        if city_node is not None:
            stop_to_city[stop_ref] = city_node.text

    # extract Route Links and filter by allowed cities
    valid_routes = []
    
    # Iterate through all RouteSections 
    for section in root.findall('.//txc:RouteSection', ns):
        current_route = []
        links = section.findall('txc:RouteLink', ns)
        
        for link in links:
            from_ref = link.find('txc:From/txc:StopPointRef', ns).text
            to_ref = link.find('txc:To/txc:StopPointRef', ns).text
            
            from_city = stop_to_city.get(from_ref)
            to_city = stop_to_city.get(to_ref)


            
            # check both cities are valid
            if from_city in allowed_cities and to_city in allowed_cities:
                if from_city != to_city:
                    valid_routes.append((from_city, to_city))
                
    # remove duplicates
    return list(set(valid_routes))

def get_all_routes():
    # get our list of allowed cities from cities.txt
    f = open("cities.txt", "r")
    allowed_cities = [line.strip() for line in f.readlines()]
    f.close()

    # store all possible routes
    all_possible_routes = []

    # iterate over all flixbus routes in dataset
    for filename in os.listdir("FLIX/"):
        if filename.endswith(".xml"):
            filepath = os.path.join("FLIX/", filename)
            routes = get_valid_routes(filepath, allowed_cities)
            all_possible_routes.extend(routes)

    
    all_possible_routes = list(set(all_possible_routes))

    return all_possible_routes