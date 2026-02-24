import heapq
from fastapi_cache.decorator import cache
from math import radians, sin, cos, sqrt, atan2

GENERAL_CHANGEOVER_COST = 1 # a general cost added to each changeover to punish routes with too many legs
RAIL_SPLIT_PENALTY = 20 # only when trains changeover - algorithm may detect this as good but in reality more expensive


@cache(expire=3600)
async def find_cheapest_path(graph_manager, start_id, finish_id, railcard_discount, advanced = True, max_coach_legs=1):
    discount_multiplier = (100 - railcard_discount) / 100
    graph = graph_manager.graph
    dest_station_id = 0

    pq = [(0, start_id, dest_station_id, [], 0, 0, 0, 0, 0, None)]
    
    cheapest_known_costs = {}
    cheapest_known_costs[(start_id, 0, None)] = 0

    while pq:
        current_cost, current_city, destination_station, path_route_ids, extra_costs, ticket_costs, ticket_discounts, advanced_discounts, coach_legs, last_transport_mode = heapq.heappop(pq)

        # check if search completed
        if current_city == finish_id:
            return {
                "route_ids": path_route_ids,
                "ticket_costs": ticket_costs,
                "extra_costs": extra_costs - 3, # as always an extra 3 pounds added for first station
                "ticket_discounts": ticket_discounts,
                "advanced_discounts": advanced_discounts
            }

        # skip more expensive routes
        if current_cost > cheapest_known_costs.get((current_city, coach_legs), float('inf')):
            continue

        # explore all neighbours
        for edge in graph.get(current_city, []):

            # check if they want to use advanced fares
            advanced_multiplier = 1
            if advanced and edge["transport_mode_id"] == 2:
                advanced_multiplier = get_advanced_discount(edge["origin_city_loc"], edge["destination_city_loc"])

            next_city = edge["destination_city"]

            # punish algorithm splitting rail journeys in multiple sections
            split_penalty = 0
            if last_transport_mode == 2 and edge["transport_mode_id"] == 2:
                split_penalty = RAIL_SPLIT_PENALTY

            # calculate the costs
            if edge["transport_mode_id"] == 2: # rail       
                new_cost = current_cost + edge["price"] * discount_multiplier * advanced_multiplier + GENERAL_CHANGEOVER_COST + split_penalty
            else:
                new_cost = current_cost + edge["price"] + GENERAL_CHANGEOVER_COST

            this_ticket_price = edge["price"]
            this_discount = 0
            this_extra_cost = 0
            this_advanced_discount = (edge["price"] * discount_multiplier) * (1 - advanced_multiplier)

            
            if edge["transport_mode_id"] == 2: # train travel - apply railcard
                this_discount = edge["price"] * (railcard_discount / 100)

            # check if stations are not the same
            # if not, we add an extra 2 pounds
            # this is a transfer cost between stations in the same city
            if edge["origin_station_id"] != destination_station:
                new_cost += 3      
                this_extra_cost = 3  

            final_ticket_cost = this_ticket_price + ticket_costs
            final_ticket_discount = this_discount + ticket_discounts
            final_ticket_extra_cost = this_extra_cost + extra_costs 
            final_advanced_discount = this_advanced_discount + advanced_discounts
            final_coach_legs = coach_legs
            final_travel_mode = edge["transport_mode_id"]

            if edge["transport_mode_id"] == 1:
                final_coach_legs += 1

            # now check coach legs
            if final_coach_legs > max_coach_legs:
                continue


            state = (next_city, final_coach_legs, final_travel_mode)

            if new_cost < cheapest_known_costs.get(state, float('inf')):
                cheapest_known_costs[state] = new_cost
                # add the route_id to the path so we can reconstruct the journey later
                new_path = path_route_ids + [edge["route_id"]]
                heapq.heappush(pq, (new_cost, next_city, edge["destination_station_id"], new_path, final_ticket_extra_cost, final_ticket_cost, final_ticket_discount, final_advanced_discount, final_coach_legs, final_travel_mode))

    return None # No path found


def get_advanced_discount(coord1, coord2):
    # get the discount for the journey
    journey_distance = miles_between_coords(coord1, coord2)
    if journey_distance > 100:
        # large discount
        advanced_multiplier = 0.6
    elif journey_distance > 30:
        advanced_multiplier = 0.8
    else:
        advanced_multiplier = 1
    return advanced_multiplier


def miles_between_coords(coord1, coord2):
    lon1, lat1 = coord1
    lon2, lat2 = coord2

    R = 3959  # Earth's radius in miles

    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)
    delta_lat = radians(lat2 - lat1)
    delta_lon = radians(lon2 - lon1)

    a = sin(delta_lat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c

    return distance