from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import models, schemas
from ..utils.verify_auth_token import validate_user_role


# create a router for routes to do with the City model
router = APIRouter(
    prefix="/city",
    tags=["Cities"],
)

@router.post("/", response_model=schemas.CityRead, status_code=201)
def create_new_city(city: schemas.CityCreate, db: Session = Depends(get_db), current_user = Depends(validate_user_role(["admin"]))):
    """
    ### Create a new city
    Adds a unique city record to the database.
    
    **Access Level:** - Admin only.

    **Args:**
    - **city**: Schema containing name, latitude, and longitude.
    - **db**: Database session dependency.

    **Errors:**
    - **401**: Unauthorized - Missing or invalid authentication token.
    - **403**: Forbidden - User does not have administrative privileges.
    - **422**: Validation Error - Input data is invalid.

    **Notes:**
    - City names are automatically converted to lowercase.
    - The name field must be unique.
    """
    db_city = models.City(**city.model_dump())
    db.add(db_city)
    db.commit()
    db.refresh(db_city)
    return db_city

@router.get("/", response_model=List[schemas.CityRead])
def get_all_cities(db: Session = Depends(get_db), current_user = Depends(validate_user_role(["admin", "user"]))):
    """
    ### Get all cities
    Retrieves a list of every city currently stored in the database.

    **Access Level:** - Admin and User.

    **Args:**
    - **db**: Database session dependency.

    **Returns:**
    - A list of City objects.

    **Errors:**
    - **401**: Unauthorized - Missing or invalid authentication token.
    - **403**: Forbidden - User role not recognized.
    """
    return db.query(models.City).all()

@router.get("/id/{city_id}", response_model=schemas.CityRead, responses={404: {"description": "City not found"}})
def get_city_by_id(city_id: int, db: Session = Depends(get_db), current_user = Depends(validate_user_role(["admin", "user"]))):
    """
    ### Get city by ID
    Fetches a specific city's details using its unique integer ID.

    **Access Level:** - Admin and User.

    **Args:**
    - **city_id**: The unique identifier of the city.
    - **db**: Database session dependency.

    **Errors:**
    - **401**: Unauthorized - Missing or invalid authentication token.
    - **403**: Forbidden - User role not recognized.
    - **404**: Not Found - No city exists with the provided ID.
    """
    city = db.query(models.City).filter(models.City.id == city_id).first()
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    return city

@router.get("/name/{city_name}", response_model=schemas.CityRead, responses={404: {"description": "City not found"}})
def get_city_by_name(city_name: str, db: Session = Depends(get_db), current_user = Depends(validate_user_role(["admin", "user"]))):
    """
    ### Get city by name
    Fetches a specific city's details using its name.

    **Access Level:** - Admin and User.

    **Args:**
    - **city_name**: The name string of the city.
    - **db**: Database session dependency.

    **Errors:**
    - **401**: Unauthorized - Missing or invalid authentication token.
    - **403**: Forbidden - User role not recognized.
    - **404**: Not Found - No city exists with the provided name.
    """
    city_name = city_name.lower()
    city = db.query(models.City).filter(models.City.name == city_name).first()
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    return city


@router.put("/{city_id}", response_model=schemas.CityRead, status_code=200, responses={404: {"description": "City not found"}})
def update_city(city_id: int, city_update: schemas.CityCreate, db: Session = Depends(get_db), current_user = Depends(validate_user_role(["admin"]))):
    """
    ### Update city
    Modifies an existing city record based on its ID.

    **Access Level:** - Admin only.

    **Args:**
    - **city_id**: The unique identifier of the city to update.
    - **city_update**: The new data to apply to the city.
    - **db**: Database session dependency.

    **Errors:**
    - **401**: Unauthorized - Missing or invalid authentication token.
    - **403**: Forbidden - User does not have administrative privileges.
    - **404**: Not Found - The city to update is not found.
    """
    city = db.query(models.City).filter(models.City.id == city_id).first()

    if not city:
        raise HTTPException("City not found")
    
    for key, value in city_update.model_dump().items():
        setattr(city, key, value)

    db.commit()
    db.refresh(city)
    return city