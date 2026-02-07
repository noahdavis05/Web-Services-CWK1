from fastapi import FastAPI
from .routers import routes, cities, stations

app = FastAPI()

app.include_router(routes.router)
app.include_router(cities.router)
app.include_router(stations.router)