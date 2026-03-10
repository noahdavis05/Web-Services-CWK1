from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import models, schemas
from ..utils.verify_auth_token import validate_user_role

router = APIRouter(
    prefix="/routes",
    tags=["Travel Routes"], 
)

@router.post("/", response_model=schemas.RouteRead, status_code=201)
def create_new_route(route: schemas.RouteCreate, db: Session = Depends(get_db), current_user = Depends(validate_user_role(["admin"]))):
    """
    ### Create a new travel route
    Adds a new route record after validating that the stations and transport mode exist.
    
    **Access Level:** - Admin only.

    **Args:**
    - **route**: Schema containing origin/destination station IDs, transport mode ID, and price.
    - **db**: Database session dependency.

    **Errors:**
    - **401**: Unauthorized - Missing or invalid authentication token.
    - **403**: Forbidden - User does not have administrative privileges.
    - **404**: Not Found - If the origin station, destination station, or transport mode does not exist.
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
def get_all_routes(db: Session = Depends(get_db), current_user = Depends(validate_user_role(["admin", "user"]))):
    """
    ### List all travel routes
    Retrieves every available route between stations from the database.

    **Access Level:** - Admin and User.

    **Args:**
    - **db**: Database session dependency.

    **Returns:**
    - A list of all Route objects.

    **Errors:**
    - **401**: Unauthorized - Missing or invalid authentication token.
    - **403**: Forbidden - User role not recognized.

    **Notes:**
    - **Caution**: This dataset contains ~20,000 records. Testing this in a browser may cause performance issues or crashes.
    """
    return db.query(models.Route).all()

@router.get("/{route_id}", response_model=schemas.RouteRead, responses={404: {"description": "Route not found"}})
def get_route_by_id(route_id: int, db: Session = Depends(get_db), current_user = Depends(validate_user_role(["admin", "user"]))):
    """
    ### Get specific route details
    Fetches the full details of a single travel route using its unique ID.

    **Access Level:** - Admin and User.

    **Args:**
    - **route_id**: The unique identifier of the route.
    - **db**: Database session dependency.

    **Errors:**
    - **401**: Unauthorized - Missing or invalid authentication token.
    - **403**: Forbidden - User role not recognized.
    - **404**: Not Found - No route exists with the provided ID.
    """
    route = db.query(models.Route).filter(models.Route.id == route_id).first()

    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    return route

@router.delete("/{route_id}", status_code=204, responses={404: {"description": "Route not found"}})
def delete_route(route_id: int, db: Session = Depends(get_db), current_user = Depends(validate_user_role(["admin"]))):
    """
    ### Delete a route
    Permanently removes a specific route record from the database.

    **Access Level:** - Admin only.

    **Args:**
    - **route_id**: The unique identifier of the route to be deleted.
    - **db**: Database session dependency.

    **Errors:**
    - **401**: Unauthorized - Missing or invalid authentication token.
    - **403**: Forbidden - User does not have administrative privileges.
    - **404**: Not Found - No route exists with the provided ID.

    **Notes:**
    - This action is destructive but does not affect associated station or city records.
    """
    route = db.query(models.Route).filter(models.Route.id == route_id).first()
    
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    
    db.delete(route)
    db.commit()
    return None

@router.put("/{route_id}", response_model=schemas.RouteRead, status_code=200, responses={404: {"description": "Route not found"}})
def update_route(route_id: int, route_update: schemas.RouteCreate, db: Session = Depends(get_db), current_user = Depends(validate_user_role(["admin"]))):
    """
    ### Update an entire route
    Replaces an existing route's data. Validates the existence of related entities before saving.

    **Access Level:** - Admin only.

    **Args:**
    - **route_id**: The unique identifier of the route to update.
    - **route_update**: The new data to apply to the route.
    - **db**: Database session dependency.

    **Errors:**
    - **401**: Unauthorized - Missing or invalid authentication token.
    - **403**: Forbidden - User does not have administrative privileges.
    - **404**: Not Found - If the route, either station, or the transport mode is not found.
    """
    route = db.query(models.Route).filter(models.Route.id == route_id).first()
    
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    
    # Verify related entities exist
    origin_station = db.query(models.Station).filter(models.Station.id == route_update.origin_station_id).first()
    destination_station = db.query(models.Station).filter(models.Station.id == route_update.destination_station_id).first()
    transport_mode = db.query(models.TransportMode).filter(models.TransportMode.id == route_update.transport_mode_id).first()
    
    if not origin_station or not destination_station or not transport_mode:
        raise HTTPException(status_code=404, detail="Station, or transport mode not found.")
    
    # Update route fields
    for key, value in route_update.model_dump().items():
        setattr(route, key, value)
    
    db.commit()
    db.refresh(route)
    return route