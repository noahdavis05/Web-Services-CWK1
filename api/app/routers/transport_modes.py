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

@router.post("/", response_model=schemas.TransportModeRead, status_code=201)
def create_new_transport_mode(transport_mode: schemas.TransportModeCreate, db: Session = Depends(get_db), current_user = Depends(validate_user_role(["admin"]))):
    """
    ### Register a new transport mode
    Adds a new category of transport (e.g., Train, Coach) to the system.

    **Access Level:** - Admin only.

    **Args:**
    - **transport_mode**: Schema containing the name of the transport mode.
    - **db**: Database session dependency.

    **Errors:**
    - **401**: Unauthorized - Missing or invalid authentication token.
    - **403**: Forbidden - User does not have administrative privileges.

    **Notes:**
    - This creates a parent category that individual routes must be associated with.
    """
    db_transport_mode = models.TransportMode(**transport_mode.model_dump())
    db.add(db_transport_mode)
    db.commit()
    db.refresh(db_transport_mode)
    return db_transport_mode

@router.get("/", response_model=List[schemas.TransportModeRead])
def get_all_transport_mode(db: Session = Depends(get_db), current_user = Depends(validate_user_role(["admin", "user"]))):
    """
    ### Retrieve all transport modes
    Fetches a complete list of all available transport categories.

    **Access Level:** - Admin and User.

    **Args:**
    - **db**: Database session dependency.

    **Returns:**
    - A list of TransportMode objects, useful for UI filters or dropdown menus.

    **Errors:**
    - **401**: Unauthorized - Missing or invalid authentication token.
    - **403**: Forbidden - User role not recognized.
    """
    return db.query(models.TransportMode).all()

@router.get("/{transport_mode_id}", response_model=schemas.TransportModeRead)
def get_transport_mode_by_id(transport_mode_id: int, db: Session = Depends(get_db), current_user = Depends(validate_user_role(["admin", "user"]))):
    """
    ### Get transport mode by ID
    Retrieves the details of a specific transport category using its unique ID.

    **Access Level:** - Admin and User.

    **Args:**
    - **transport_mode_id**: The unique identifier of the transport mode.
    - **db**: Database session dependency.

    **Errors:**
    - **401**: Unauthorized - Missing or invalid authentication token.
    - **403**: Forbidden - User role not recognized.
    - **404**: Not Found - If no transport mode exists with the provided ID.
    """
    transport_mode = db.query(models.TransportMode).filter(models.TransportMode.id == transport_mode_id).first()
    if not transport_mode:
        raise HTTPException(status_code=404, detail="Transport mode not found")
    return transport_mode