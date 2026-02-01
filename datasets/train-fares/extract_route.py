from extract_NLC import get_all_codes

TICKET_TYPES = {
    "CDS":"Off Peak Single",
    "SDS":"Anytime Single",
    "SOS":"Anytime Single"
}


def find_routes_efficient(ffl_path, start_codes, end_codes):
    routes = []
    
    # Convert lists to Sets for O(1) lookup speed
    start_set = set(start_codes)
    end_set = set(end_codes)

    with open(ffl_path, 'r', encoding='latin-1') as f:
        for line in f:
            # We only care about 'RF' records
            if line[0:2] == "RF":
                origin = line[2:6]
                destination = line[6:10]

                # Check if this line matches ANY combination in either direction
                # (Forward: Taunton -> Bath | Reverse: Bath -> Taunton)
                if (origin in start_set and destination in end_set):      
                    routes.append((line.strip(), origin, destination, line[42:49].strip()))
                elif (origin in end_set and destination in start_set):
                    routes.append((line.strip(), destination, origin, line[42:49].strip()))
                    
    return routes

def extract_fares(ffl_path, routes):
    # iterate over our routes and get the fare codes
    route_codes = set()
    for r in routes:
        flow_id = r[0][42:49].strip()
        #print(flow_id)
        route_codes.add(flow_id)

    # now iterate over all RT records and get prices
    results = []
    with open(ffl_path, 'r', encoding='latin-1') as f:
        for line in f:
            if line.startswith("RT"):
                # check if the code is in our route_codes set
                if line[2:9] in route_codes:
                    # now get the ticket type
                    ticket_type = line[9:12]
                    if ticket_type == "CDS" or ticket_type == "SDS" or ticket_type == "SOS": # of peak day single
                        price_string = line[12:20]
                        price = int(price_string) / 100.0
                        results.append((price, ticket_type, line[2:9])) # the price, ticket type, and the route code

    return results


def inter_city_routes(city1, city2):
    # codes with their station names
    city1_c = get_all_codes(city1)
    city2_c = get_all_codes(city2)

    # make copies of these without station names
    city1_codes = []
    for code in city1_c:
        city1_codes.append(code[0])

    city2_codes = []
    for code in city2_c:
        city2_codes.append(code[0])


    # get all routes between cities
    all_routes = find_routes_efficient("fares_data/RJFAF658.FFL", city1_codes, city2_codes)

    # all routes contains

    print(all_routes)

    prices = extract_fares("fares_data/RJFAF658.FFL", all_routes)

    # now go through the prices and make full journey
    for price in prices:
        ticket_price = price[0]
        ticket_type = TICKET_TYPES[price[1]]
        ticket_route = price[2]

        # now get the route with these tickets
        destination = ""
        origin = ""
        for route in all_routes:
            if route[3] == ticket_route:
                # this is our route for this journey - now we can work out which stations we go from
                origin_code = route[1]
                destination_code = route[2]

                # iterate through city codes - need to check both destinations in city1_c and city2_c as routes can be forwards or backwards
                for c in city1_c:
                    if origin_code == c[0]:
                        origin = c[1]
                    if destination_code == c[0]:
                        destination = c[1]

                for c in city2_c:
                    if origin_code == c[0]:
                        origin = c[1]
                    if destination_code == c[0]:
                        destination = c[1]

        print("Ticket from", origin, "to", destination, "is £" + str(ticket_price), "for a ", ticket_type, "ticket")




inter_city_routes("Leeds", "Nottingham")