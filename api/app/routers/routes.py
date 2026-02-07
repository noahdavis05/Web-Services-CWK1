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

    if not origin_station:
        raise HTTPException(status_code=404, detail="Origin station not found") 
    if not destination_station:
        raise HTTPException(status_code=404, detail="Destination Station not found")
    
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