from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import models, schemas
from ..utils.verify_auth_token import validate_user_role

router = APIRouter(
    prefix="/stations",
    tags=["Stations"],
    dependencies=[Depends(validate_user_role(["admin"]))]
)

@router.post("/", response_model=schemas.StationRead, status_code=201)
def create_new_station(station: schemas.StationCreate, db: Session = Depends(get_db)):
    """
    Create a new Station
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
def get_all_stations(db: Session = Depends(get_db)):
    """
    Get all stations
    """
    return db.query(models.Station).all()

@router.get("/{station_id}", response_model=schemas.StationRead)
def get_station_by_id(station_id: int, db: Session = Depends(get_db)):
    """
    Get station by ID
    """
    station = db.query(models.Station).filter(models.City.id == station_id).first()

    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    
    return station