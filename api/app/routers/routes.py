from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import models, schemas
from ..utils.verify_auth_token import validate_user_role

# create a router - similar to a mini-app for endpoints to do with 
# routes between cities
router = APIRouter(
    prefix="/routes",
    tags=["Travel Routes"], # for the docs, keeps these endpoints together
    dependencies=[Depends(validate_user_role(["admin"]))]
)

@router.post("/", response_model=schemas.RouteRead, status_code=201)
def create_new_route(route: schemas.RouteCreate, db: Session = Depends(get_db)):
    """
    # Create a new travel route

    Validates that the provided stations and transport mode exist before establishing the link.
    
    - **origin_station_id**: ID of the starting station.
    - **destination_station_id**: ID of the arrival station.
    - **transport_mode_id**: ID of the transport category (e.g., Train).
    - **price**: Total cost with 2-decimal precision.
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
    # List all travel routes

    Returns a comprehensive list of all routes, including nested station and city details.
    """
    return db.query(models.Route).all()

@router.get("/{route_id}", response_model=schemas.RouteRead)
def get_route_by_id(route_id: int, db: Session = Depends(get_db)):
    """
    # Get specific route details

    Retrieves full information for a single route by its unique ID. 
    Returns a **404 error** if the ID is invalid.
    """
    route = db.query(models.Route).filter(models.Route.id == route_id).first()

    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    return route

@router.delete("/{route_id}", status_code=204)
def delete_route(route_id: int, db: Session = Depends(get_db)):
    """
    # Delete a route

    Permanently removes a route record. 
    *Note: This does not delete the associated stations or cities.*
    """
    route = db.query(models.Route).filter(models.Route.id == route_id).first()
    
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    
    db.delete(route)
    db.commit()
    return None

@router.put("/{route_id}", response_model=schemas.RouteRead, status_code=200)
def update_route(route_id: int, route_update: schemas.RouteCreate, db: Session = Depends(get_db)):
    """
    # Update an entire route 

    Replaces the route's data with the new values provided. 
    Checks for the existence of related stations and transport modes before saving.
    """
    route = db.query(models.Route).filter(models.Route.id == route_id).first()
    
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    
    # Verify related entities exist
    origin_station = db.query(models.Station).filter(models.Station.id == route_update.origin_station_id).first()
    destination_station = db.query(models.Station).filter(models.Station.id == route_update.destination_station_id).first()
    transport_mode = db.query(models.TransportMode).filter(models.TransportMode.id == route_update.transport_mode_id).first()
    
    if not origin_station or not destination_station or not transport_mode:
        raise HTTPException(status_code=404, detail="Invalid station or transport mode")
    
    # Update route fields
    for key, value in route_update.model_dump().items():
        setattr(route, key, value)
    
    db.commit()
    db.refresh(route)
    return route