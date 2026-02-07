from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import models, schemas

# create a router - similar to a mini-app for endpoints to do with 
# routes between cities
router = APIRouter(
    prefix="/routes",
    tags=["Travel Routes"] # for the docs, keeps these endpoints together
)

@router.post("/", response_model=schemas.RouteRead, status_code=201)
def create_new_route(route: schemas.RouteCreate, db: Session = Depends(get_db)):
    """
    # Create a new travel route
    - Add a new route between an origin and destination city.
    - Can define travel mode, either train or coach.
    - Can define the price of the journey.
    - Optionally can add notes about the journey, e.g. *take train route which goes through station xyz*
    """

    # check if the start and end stations exist
    origin_station = db.query(models.Station).filter(models.Station.id == route.origin_station_id).first()
    destination_station = db.query(models.Station).filter(models.Station.id == route.destination_station_id).first()
    transport_mode = db.query(models.TransportMode).filter(models.TransportMode.id == route.transport_mode_id).first()

    if not origin_station:
        raise HTTPException(status_code=404, detail="Origin station not found") 
    if not destination_station:
        raise HTTPException(status_code=404, detail="Destination Station not found")
    if not transport_mode:
        raise HTTPException(status_code=404, detail="Transport Mode not found")

    db_route = models.Route(**route.model_dump())
    db.add(db_route)
    db.commit()
    db.refresh(db_route)
    return db_route

@router.get("/", response_model=List[schemas.RouteRead])
def get_all_routes(db: Session = Depends(get_db)):
    """
    # Get all travel routes
    """
    return db.query(models.Route).all()

@router.get("/{route_id}", response_model=schemas.RouteRead)
def get_route_by_id(route_id: int, db: Session = Depends(get_db)):
    """
    Get Route by ID
    """
    route = db.query(models.Route).filter(models.Route.id == route_id).first()

    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    return route