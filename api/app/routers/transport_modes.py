from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import models, schemas

router = APIRouter(
    prefix="/transport_mode",
    tags=["Transport Modes"]
)

@router.post("/", response_model=schemas.TransportModeRead, status_code=201)
def create_new_transport_mode(transport_mode: schemas.TransportModeCreate, db: Session = Depends(get_db)):
    """
    # Register a new mode of transport

    - **name**: The unique identifier for the mode (e.g., "Train", "Coach").
    
    *This creates a new category that routes can be associated with.*
    """
    db_transport_mode = models.TransportMode(**transport_mode.model_dump())
    db.add(db_transport_mode)
    db.commit()
    db.refresh(db_transport_mode)
    return db_transport_mode

@router.get("/", response_model=List[schemas.TransportModeRead])
def get_all_transport_mode(db: Session = Depends(get_db)):
    """
    # Retrieve all available transport modes 

    This could be used for:
    1. Fetching all transport modes for filters.
    2. Provide options for the 'Transport Type' dropdown when creating new routes.
    """
    return db.query(models.TransportMode).all()

@router.get("/{transport_mode_id}", response_model=schemas.TransportModeRead)
def get_transport_mode_by_id(transport_mode_id: int, db: Session = Depends(get_db)):
    """
    # Get details for a specific transport mode by ID 

    - **transport_mode_id**: The unique database ID for the mode.

    Returns a **404 error** if the ID does not correspond to an existing transport mode.
    """
    transport_mode = db.query(models.TransportMode).filter(models.TransportMode.id == transport_mode_id).first()
    if not transport_mode:
        raise HTTPException(status_code=404, detail="Transport mode not found")
    return transport_mode