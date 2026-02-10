import os
from itertools import combinations
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
    cities = []
    for stop in root.findall('.//txc:AnnotatedStopPointRef', ns):
        stop_ref = stop.find('txc:StopPointRef', ns).text
        
        city_node = stop.find('txc:LocalityQualifier', ns)
        if city_node is None:
            city_node = stop.find('txc:LocalityName', ns)
            
        if city_node is not None:
            cities.append(city_node.text)

    #print(cities)
    final_cities = []
    for city in cities:
        for c in allowed_cities:
            if c in city or city in c: # check either way - for example newcaste upon tyne and newcastle
                final_cities.append(c)

    # now find all possible routes between final_cities
    routes = [tuple(sorted(pair)) for pair in combinations(final_cities, 2)]
    routes = list(set(routes))
    # add both directions
    routes = [(a, b) for (a, b) in routes] + [(b, a) for (a, b) in routes]
    return routes

   # now find all possible combinations between any two cities

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

