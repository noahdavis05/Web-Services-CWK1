import requests
import json
from pprint import pprint
import os

def get_flixbus_fare_v4(from_id, to_id, origin_city, destination_city, date):
    url = "https://global.api.flixbus.com/search/service/v4/search"
    
    # These headers are essential to avoid being blocked
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:147.0) Gecko/20100101 Firefox/147.0",
        "Accept": "*/*",
        "Origin": "https://shop.flixbus.co.uk",
        "Referer": "https://shop.flixbus.co.uk/"
    }
    
    params = {
        "from_city_id": from_id,
        "to_city_id": to_id,
        "departure_date": date, 
        "products": json.dumps({"adult": 1}),
        "currency": "GBP",
        "locale": "en_GB",
        "search_by": "cities"
    }

    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        # The price logic in v4 is nested inside 'trips' -> 'results'
        all_prices = []
        for trip in data.get('trips', []):
            #print(trip)
            results = trip.get('results', {})
            for journey_id, details in results.items():
                if details.get('transfer_type_key') == 'direct':
                    departure_id = details["departure"]["station_id"]
                    arrival_id = details["arrival"]["station_id"]
                    price = details["price"]["total_with_platform_fee"]
                    res = {
                        "origin_station_id":departure_id,
                        "destination_station_id":arrival_id,
                        "price":price
                    }
                    all_prices.append(res)
                
        
        final_prices = []
        # now convert our dictionary to have origin and destination cities and stations
        stations = data["stations"]
        for price in all_prices:
            final_price = {
                "origin_city":origin_city,
                "destination_city":destination_city,
                "origin_station":stations[price["origin_station_id"]]["name"],
                "destination_station":stations[price["destination_station_id"]]["name"],
                "price":price["price"]
            }
            final_prices.append(final_price)
        
        # now we need to work out which result to add to the database.
        # for each route (e.g. each starting and ending station pair)
        # we will calculate the mean price. We will return the cheapest mean route

        unique_routes = {}

        for route in final_prices:
            pair = (route['origin_station'], route['destination_station'])
            if pair in unique_routes:
                unique_routes[pair]['records'] += 1
                unique_routes[pair]['average'] = ((unique_routes[pair]['average'] * (unique_routes[pair]['records'] - 1)) + route['price']) / unique_routes[pair]['records']
            else:
                unique_routes[pair] = {
                    "average" : route['price'],
                    "records" : 1
                }
        
        # choose route with lowest average
        best_route = min(unique_routes.items(), key=lambda item: item[1]['average'])
        final_price = {
            "origin_city": origin_city,
            "destination_city": destination_city,
            "origin_station": best_route[0][0],
            "destination_station": best_route[0][1],
            "price": best_route[1]['average']
        }
        print(final_prices)
        print(unique_routes)
        print(final_price)
        return final_price
    return None


def get_flixbus_uuid(city_name):
    url = "https://global.api.flixbus.com/search/autocomplete/cities"
    params = {
        "q": city_name,
        "lang": "en_GB",
        "country": "gb"
    }
    
    # Remember to use a User-Agent so you don't get blocked!
    headers = {"User-Agent": "Mozilla/5.0"} 
    
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        results = response.json()
        if results:
            # Sort by score and filter for flixbus cities
            flix_cities = [c for c in results if c.get('is_flixbus_city')]
            if flix_cities:
                # Return the ID of the highest-scored match
                return flix_cities[0]['id']
    return None

OUTPUT_CSV = "extracted_fares.csv"
# write the headers to the csv file
file_exists = os.path.isfile(OUTPUT_CSV) and os.stat(OUTPUT_CSV).st_size > 0
f_out = open(OUTPUT_CSV, "a", encoding='utf-8')
if not file_exists:
    f_out.write("origin_city,destination_city,origin_station,destination_station,price\n")
f_out.close()

# iterate over the list of allowed cities
f = open("cities.txt", "r")
allowed_cities = [line.strip() for line in f.readlines()]
f.close()
for city1, i in enumerate(allowed_cities):
    for j in range(i+1, len(allowed_cities)):
        city2 = allowed_cities[j]

        # find prices between cities
        origin_id = get_flixbus_uuid(city1)
        destination_id = get_flixbus_uuid(city2)
        if not origin_id or not destination_id:
            continue # if city isn't used by flixbus

        price_forward = get_flixbus_fare_v4(origin_id, destination_id, city1, city2, "28.03.2026")
        price_backward = get_flixbus_fare_v4(destination_id, origin_id, city2, city1, "28.03.2026")

        # write the routes to a csv file
        f_out = open(OUTPUT_CSV, "a", encoding='utf-8')
