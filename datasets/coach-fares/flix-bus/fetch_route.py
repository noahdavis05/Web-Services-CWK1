import requests
import json
from pprint import pprint

def get_flixbus_fare_v4(origin_city, destination_city, date):
    from_id = get_flixbus_uuid(origin_city)
    to_id = get_flixbus_uuid(destination_city)
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
        return final_prices
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

price = get_flixbus_fare_v4("Bath", "Nottingham", "28.02.2026")
pprint(price)