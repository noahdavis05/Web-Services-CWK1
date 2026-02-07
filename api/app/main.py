from fastapi import FastAPI
from .routers import routes, cities, stations, transport_modes

app = FastAPI()

app.include_router(routes.router)
app.include_router(cities.router)
app.include_router(stations.router)
app.include_router(transport_modes.router)