import heapq

def find_cheapest_path(graph_manager, start_id, finish_id):
    graph = graph_manager.graph
    
    pq = [(0, start_id, [])]
    
    cheapest_known_costs = {start_id: 0}

    while pq:
        current_cost, current_city, path_route_ids = heapq.heappop(pq)

        # check if search completed
        if current_city == finish_id:
            return {
                "total_price": current_cost,
                "route_ids": path_route_ids
            }

        # skip more expensive routes
        if current_cost > cheapest_known_costs.get(current_city, float('inf')):
            continue

        # explore all neighbours
        for edge in graph.get(current_city, []):
            next_city = edge["destination_city"]
            new_cost = current_cost + edge["price"]

            if new_cost < cheapest_known_costs.get(next_city, float('inf')):
                cheapest_known_costs[next_city] = new_cost
                # add the route_id to the path so we can reconstruct the journey later
                new_path = path_route_ids + [edge["route_id"]]
                heapq.heappush(pq, (new_cost, next_city, new_path))

    return None # No path found