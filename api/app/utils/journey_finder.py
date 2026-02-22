import heapq
from fastapi_cache.decorator import cache


@cache(expire=3600)
async def find_cheapest_path(graph_manager, start_id, finish_id, railcard_discount):
    discount_multiplier = (100 - railcard_discount) / 100
    graph = graph_manager.graph
    dest_station_id = 0

    pq = [(0, start_id, dest_station_id, [], 0, 0, 0)]
    
    cheapest_known_costs = {start_id: 0}

    while pq:
        current_cost, current_city, destination_station, path_route_ids, extra_costs, ticket_costs, ticket_discounts = heapq.heappop(pq)

        # check if search completed
        if current_city == finish_id:
            return {
                "route_ids": path_route_ids,
                "ticket_costs": ticket_costs,
                "extra_costs": extra_costs - 3, # as always an extra 3 pounds added for first station
                "ticket_discounts": ticket_discounts
            }

        # skip more expensive routes
        if current_cost > cheapest_known_costs.get(current_city, float('inf')):
            continue

        # explore all neighbours
        for edge in graph.get(current_city, []):
            next_city = edge["destination_city"]
            new_cost = current_cost + edge["price"] * discount_multiplier + 10 # add a general + 10. This punishes routes which have lots of changes, but doesn't show on the final price
            
            this_ticket_price = edge["price"]
            this_discount = 0
            this_extra_cost = 0

            
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

            if new_cost < cheapest_known_costs.get(next_city, float('inf')):
                cheapest_known_costs[next_city] = new_cost
                # add the route_id to the path so we can reconstruct the journey later
                new_path = path_route_ids + [edge["route_id"]]
                heapq.heappush(pq, (new_cost, next_city, edge["destination_station_id"], new_path, final_ticket_extra_cost, final_ticket_cost, final_ticket_discount))

    return None # No path found