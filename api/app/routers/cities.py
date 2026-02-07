from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import models, schemas


# create a router for routes to do with the City model
router = APIRouter(
    prefix="/city",
    tags=["Cities"]
)

@router.post("/", response_model=schemas.CityRead, status_code=201)
def create_new_city(city: schemas.CityCreate, db: Session = Depends(get_db)):
    """
    # Add a new city 

    - **name**: City Name - Must be Unique. Example - "Leeds".
    - **latitude/longitude**: Latitude and Longitude of the city..
    
    *Returns the created city object including its database-assigned ID.*
    """
    db_city = models.City(**city.model_dump())
    db.add(db_city)
    db.commit()
    db.refresh(db_city)
    return db_city

@router.get("/", response_model=List[schemas.CityRead])
def get_all_cities(db: Session = Depends(get_db)):
    """
   # Get all cities
    """
    return db.query(models.City).all()

@router.get("/{city_id}", response_model=schemas.CityRead)
def get_city_by_id(city_id: int, db: Session = Depends(get_db)):
    """
    # Get a city by ID
    """
    city = db.query(models.City).filter(models.City.id == city_id).first()
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    return city