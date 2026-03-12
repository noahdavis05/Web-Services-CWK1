from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import models, schemas
from ..utils.verify_auth_token import validate_user_role

router = APIRouter(
    prefix="/transport_mode",
    tags=["Transport Modes"],
)

@router.post(
    "/", 
    response_model=schemas.TransportModeRead, 
    status_code=201,
    responses={
        401: {"description": "Unauthorized - Missing or invalid authentication token."},
        403: {"description": "Forbidden - User does not have administrative privileges."},
        422: {"description": "Validation Error - Improperly formatted request body."}
    }
)
def create_new_transport_mode(transport_mode: schemas.TransportModeCreate, db: Session = Depends(get_db), current_user = Depends(validate_user_role(["admin"]))):
    """
    ### Register a new transport mode
    Adds a new category of transport (e.g., **Train**, **Coach**) to the system.

    **Access Level:** **Admin only**.
    """
    db_transport_mode = models.TransportMode(**transport_mode.model_dump())
    db.add(db_transport_mode)
    db.commit()
    db.refresh(db_transport_mode)
    return db_transport_mode

@router.get(
    "/", 
    response_model=List[schemas.TransportModeRead],
    responses={
        401: {"description": "Unauthorized - Missing or invalid authentication token."},
        403: {"description": "Forbidden - User role not recognized."}
    }
)
def get_all_transport_mode(db: Session = Depends(get_db), current_user = Depends(validate_user_role(["admin", "user"]))):
    """
    ### Retrieve all transport modes
    Fetches a complete list of all transport categories available in the database.

    **Access Level:** **Admin** and **User**.

    """
    return db.query(models.TransportMode).all()

@router.get(
    "/{transport_mode_id}", 
    response_model=schemas.TransportModeRead,
    responses={
        401: {"description": "Unauthorized - Missing or invalid authentication token."},
        403: {"description": "Forbidden - User role not recognized."},
        404: {"description": "Not Found - No transport mode exists with the provided ID."}
    }
)
def get_transport_mode_by_id(transport_mode_id: int, db: Session = Depends(get_db), current_user = Depends(validate_user_role(["admin", "user"]))):
    """
    ### Get transport mode by ID
    Retrieves the specific details of a transport category using its **unique integer ID**.

    **Access Level:** **Admin** and **User**.
    """
    transport_mode = db.query(models.TransportMode).filter(models.TransportMode.id == transport_mode_id).first()
    if not transport_mode:
        raise HTTPException(status_code=404, detail="Transport mode not found")
    return transport_mode