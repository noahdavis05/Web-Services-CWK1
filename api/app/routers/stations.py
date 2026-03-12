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

@router.post(
    "/", 
    # 
    response_model=schemas.StationRead, 
    status_code=201, 
    responses={
        401: {"description": "Unauthorized - Missing or invalid authentication token."},
        403: {"description": "Forbidden - User does not have administrative privileges."},
        404: {"description": "Not Found - The provided city_id does not match any existing city."},
        422: {"description": "Validation Error - Improperly formatted request body."}
    }
)
def create_new_station(station: schemas.StationCreate, db: Session = Depends(get_db), current_user = Depends(validate_user_role(["admin"]))):
    """
    ### Create a new station
    Adds a new station record to the database. The system verifies that the associated **city** exists before the station is created.

    **Access Level:** **Admin only**.

    **Notes:**
    - Each station must be linked to a valid **city_id**.
    - This is a prerequisite for creating routes between different locations.
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

@router.get(
    "/", 
    response_model=List[schemas.StationRead],
    responses={
        401: {"description": "Unauthorized - Missing or invalid authentication token."},
        403: {"description": "Forbidden - User role not recognized."}
    }
)
def get_all_stations(db: Session = Depends(get_db), current_user = Depends(validate_user_role(["admin", "user"]))):
    """
    ### Get all stations
    Retrieves a complete list of all transport hubs (Rail stations and Coach stops) stored in the database.

    **Access Level:** **Admin** and **User**.
    """
    return db.query(models.Station).all()

@router.get(
    "/{station_id}", 
    response_model=schemas.StationRead, 
    responses={
        401: {"description": "Unauthorized - Missing or invalid authentication token."},
        403: {"description": "Forbidden - User role not recognized."},
        404: {"description": "Not Found - No station exists with the provided ID."}
    }
)
def get_station_by_id(station_id: int, db: Session = Depends(get_db), current_user = Depends(validate_user_role(["admin", "user"]))):
    """
    ### Get station by ID
    Fetches the details of a specific station, including its parent city information, using its **unique integer ID**.

    **Access Level:** **Admin** and **User**.
    """
    station = db.query(models.Station).filter(models.Station.id == station_id).first()

    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    
    return station