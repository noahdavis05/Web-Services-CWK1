from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import models, schemas
from ..utils.verify_auth_token import validate_user_role

router = APIRouter(
    prefix="/stations",
    tags=["Stations"],
)

@router.post("/", response_model=schemas.StationRead, status_code=201, responses={404: {"description": "City not found"}})
def create_new_station(station: schemas.StationCreate, db: Session = Depends(get_db), current_user = Depends(validate_user_role(["admin"]))):
    """
    ### Create a new station
    Adds a new station record to the database after verifying the associated city exists.

    **Access Level:** - Admin only.

    **Args:**
    - **station**: Schema containing the station name and city ID.
    - **db**: Database session dependency.

    **Errors:**
    - **401**: Unauthorized - Missing or invalid authentication token.
    - **403**: Forbidden - User does not have administrative privileges.
    - **404**: Not Found - If the provided `city_id` does not match any existing city.
    """
    # check the city exists
    city = db.query(models.City).filter(models.City.id == station.city_id).first()

    # if not send a 404 error
    if not city:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"City with id {station.city_id} does not exist."
        )
    
    # city does exist so can make the station
    db_station = models.Station(**station.model_dump())
    db.add(db_station)
    db.commit()
    db.refresh(db_station)
    return db_station

@router.get("/", response_model=List[schemas.StationRead])
def get_all_stations(db: Session = Depends(get_db), current_user = Depends(validate_user_role(["admin", "user"]))):
    """
    ### Get all stations
    Retrieves a complete list of all stations stored in the database.

    **Access Level:** - Admin and User.

    **Args:**
    - **db**: Database session dependency.

    **Returns:**
    - A list of Station objects.

    **Errors:**
    - **401**: Unauthorized - Missing or invalid authentication token.
    - **403**: Forbidden - User role not recognized.
    """
    return db.query(models.Station).all()

@router.get("/{station_id}", response_model=schemas.StationRead, responses={404: {"description": "Station not found"}})
def get_station_by_id(station_id: int, db: Session = Depends(get_db), current_user = Depends(validate_user_role(["admin", "user"]))):
    """
    ### Get station by ID
    Fetches the details of a specific station using its unique integer ID.

    **Access Level:** - Admin and User.

    **Args:**
    - **station_id**: The unique identifier of the station.
    - **db**: Database session dependency.

    **Errors:**
    - **401**: Unauthorized - Missing or invalid authentication token.
    - **403**: Forbidden - User role not recognized.
    - **404**: Not Found - If no station exists with the provided ID.
    """
    station = db.query(models.Station).filter(models.Station.id == station_id).first()

    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    
    return station