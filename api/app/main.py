from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy.orm import Session, joinedload

from .routers import routes, cities, stations, transport_modes, journeys, auth
from .database import SessionLocal
from .utils.graph_manager import GraphManager
from . import models

from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

# on startup we load our graph of all routes into singleton class
# this class will be used to avoid fetching all 30,000 routes from 
# db every time we want to make a dijkstra's search between 2 cities
@asynccontextmanager
async def lifespan(app: FastAPI):
    # initialise cache and the graph manager
    FastAPICache.init(InMemoryBackend())
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


# Extra tags for documentation
tags_metadata = [
    {
        "name": "Travel Routes",
        "description": "The individual intercity legs which make up a Journey."
    },
    {
        "name": "Cities",
        "description": "The 200 largest UK cities with latitude and longitude."
    },
    {
        "name": "Stations"
    },
    {
        "name": "Transport Modes",
        "description": "Categorises routes based on transport mode such as 'train' or 'coach'."
    },
    {
        "name": "Journeys",
        "description": "A collection of Travel Routes which makes a journey between any two given cities. This will return the cheapest possible combination of Travel Routes to complete a journey, as well as cost breakdown."
    },
    {
        "name": "Authentication",
        "description": "Endpoints to authenticate users via Supabase."
    }
]
    

app = FastAPI(
    lifespan=lifespan,
    title="Cheap Public Transport API",
    description="This API find the cheapest journey between UK cities via public transport. This combines national rail services, FlixBus coaches, and National Express coaches.",
    openapi_tags=tags_metadata
)

# This block is only used when running locally and we want to run
# rapipdf JS to convert our api into PDF. it stops CORS issues.
"""
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
"""

app.include_router(routes.router)
app.include_router(cities.router)
app.include_router(stations.router)
app.include_router(transport_modes.router)
app.include_router(journeys.router)
app.include_router(auth.router)