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

@router.post(
    "/", 
    response_model=schemas.CityRead, 
    status_code=201,
    responses={
        401: {"description": "Unauthorized - Missing or invalid authentication token."},
        403: {"description": "Forbidden - User does not have administrative privileges."},
        422: {"description": "Validation Error - Input data is invalid or name is not unique."}
    }
)
def create_new_city(city: schemas.CityCreate, db: Session = Depends(get_db), current_user = Depends(validate_user_role(["admin"]))):
    """
    ### Create a new city
    Adds a unique city record to the database including coordinates for mapping.
    
    **Access Level:** **Admin only**.

    **Notes:**
    - City names are automatically converted to **lowercase** before saving.
    - The **name** field must be unique; duplicate entries will result in an error.
    """
    db_city = models.City(**city.model_dump())
    db.add(db_city)
    db.commit()
    db.refresh(db_city)
    return db_city

@router.get(
    "/", 
    response_model=List[schemas.CityRead],
    responses={
        401: {"description": "Unauthorized - Missing or invalid authentication token."},
        403: {"description": "Forbidden - User role not recognized."}
    }
)
def get_all_cities(db: Session = Depends(get_db), current_user = Depends(validate_user_role(["admin", "user"]))):
    """
    ### Get all cities
    Retrieves a complete list of every city currently stored in the database.

    **Access Level:** **Admin** and **User**.
    """
    return db.query(models.City).all()

@router.get(
    "/id/{city_id}", 
    response_model=schemas.CityRead, 
    responses={
        401: {"description": "Unauthorized - Missing or invalid authentication token."},
        403: {"description": "Forbidden - User role not recognized."},
        404: {"description": "Not Found - No city exists with the provided ID."}
    }
)
def get_city_by_id(city_id: int, db: Session = Depends(get_db), current_user = Depends(validate_user_role(["admin", "user"]))):
    """
    ### Get city by ID
    Fetches a specific city's details using its **unique integer ID**.

    **Access Level:** **Admin** and **User**.
    """
    city = db.query(models.City).filter(models.City.id == city_id).first()
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    return city

@router.get(
    "/name/{city_name}", 
    response_model=schemas.CityRead, 
    responses={
        401: {"description": "Unauthorized - Missing or invalid authentication token."},
        403: {"description": "Forbidden - User role not recognized."},
        404: {"description": "Not Found - No city exists with the provided name."}
    }
)
def get_city_by_name(city_name: str, db: Session = Depends(get_db), current_user = Depends(validate_user_role(["admin", "user"]))):
    """
    ### Get city by name
    Fetches a specific city's details using its **string name**.

    **Access Level:** **Admin** and **User**.

    **Notes:**
    - The search is **case-insensitive** as all names are stored in lowercase.
    """
    city_name = city_name.lower()
    city = db.query(models.City).filter(models.City.name == city_name).first()
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    return city


@router.put(
    "/{city_id}", 
    response_model=schemas.CityRead, 
    status_code=200, 
    responses={
        401: {"description": "Unauthorized - Missing or invalid authentication token."},
        403: {"description": "Forbidden - User does not have administrative privileges."},
        404: {"description": "Not Found - The city to update was not found."}
    }
)
def update_city(city_id: int, city_update: schemas.CityCreate, db: Session = Depends(get_db), current_user = Depends(validate_user_role(["admin"]))):
    """
    ### Update city
    Modifies an existing city record based on its **ID**.

    **Access Level:** **Admin only**.

    **Notes:**
    - All fields in the request body must be provided for a complete update.
    """
    city = db.query(models.City).filter(models.City.id == city_id).first()

    if not city:
        raise HTTPException("City not found")
    
    for key, value in city_update.model_dump().items():
        setattr(city, key, value)

    db.commit()
    db.refresh(city)
    return city