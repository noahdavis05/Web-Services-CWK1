import heapq

def find_cheapest_path(graph_manager, start_id, finish_id):
    graph = graph_manager.graph
    dest_station_id = 0
    
    pq = [(0, start_id, dest_station_id, [])]
    
    cheapest_known_costs = {start_id: 0}

    while pq:
        current_cost, current_city, destination_station, path_route_ids = heapq.heappop(pq)

        # check if search completed
        if current_city == finish_id:
            return {
                "total_price": current_cost - 5, # we subtract two as we will get an added £5 transfer fee for the first station
                "route_ids": path_route_ids
            }

        # skip more expensive routes
        if current_cost > cheapest_known_costs.get(current_city, float('inf')):
            continue

        # explore all neighbours
        for edge in graph.get(current_city, []):
            next_city = edge["destination_city"]

            new_cost = current_cost + edge["price"] + 2 # add a general + 2. This punishes routes which have lots of changes

            # check if stations are not the same
            # if not, we add an extra 2 pounds
            # this is a transfer cost between stations in the same city
            if edge["origin_station_id"] != destination_station:
                new_cost += 3         

            if new_cost < cheapest_known_costs.get(next_city, float('inf')):
                cheapest_known_costs[next_city] = new_cost
                # add the route_id to the path so we can reconstruct the journey later
                new_path = path_route_ids + [edge["route_id"]]
                heapq.heappush(pq, (new_cost, next_city, edge["destination_station_id"], new_path))

    return None # No path found