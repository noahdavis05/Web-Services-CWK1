from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy.orm import Session, joinedload

from .routers import routes, cities, stations, transport_modes
from .database import SessionLocal
from .graph_manager import GraphManager
from . import models

# on startup we load our graph of all routes into singleton class
# this class will be used to avoid fetching all 30,000 routes from 
# db every time we want to make a dijkstra's search between 2 cities
@asynccontextmanager
async def lifespan(app: FastAPI):
    gm = GraphManager()
    
    db: Session = SessionLocal()
    try:        
        db_routes = db.query(models.Route).options(
            joinedload(models.Route.origin_station).joinedload(models.Station.city),
            joinedload(models.Route.destination_station).joinedload(models.Station.city)
        ).all()
        
        # build the graph
        gm.build_graph(db_routes)
        
        # attach the graph manager class to app state
        # this allows us to access it in endpoints
        app.state.gm = gm
        print(f"Graph loaded successfully with {len(db_routes)} routes.")
    except Exception as e:
        print(f"Error loading graph: {e}")
    finally:
        db.close()
    
    yield
    

app = FastAPI(lifespan=lifespan)

app.include_router(routes.router)
app.include_router(cities.router)
app.include_router(stations.router)
app.include_router(transport_modes.router)