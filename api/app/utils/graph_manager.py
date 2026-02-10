# This is a singleton class which will give endpoints direct access
# to the adjacency list of all nodes. This will ensure that endpoints
# don't have to fetch all possible routes between nodes.

class GraphManager:
    _instance = None 

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GraphManager, cls).__new__(cls)
            cls._instance.graph = {}
            cls._instance.last_updated = None
            cls._instance.is_loaded = False
        
        return cls._instance
    
    def build_graph(self, routes_from_db):
        """
        Takes all routes between cities from the database and builds adjacency graph between them
        
        :param self: 
        :param routes_from_db: Array of Route Models from them
        """
        new_graph = {}

        for route in routes_from_db:
            # we need to work out the origin city, destination city, price, origin station, destinatino station
            try:
                origin_city = route.origin_station.city.id
                dest_city = route.destination_station.city.id
                
                edge_data = {
                    "route_id": route.id,
                    "destination_city": dest_city,
                    "price": float(route.price)
                }

                if origin_city not in new_graph:
                    new_graph[origin_city] = []
                
                new_graph[origin_city].append(edge_data)
            except AttributeError as e:
                continue

        self.graph = new_graph