from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import models, schemas
from ..utils.graph_manager import GraphManager
from ..utils.journey_finder import find_cheapest_path
from ..utils.verify_auth_token import get_current_user

router = APIRouter(
    prefix="/journeys",
    tags=["Journeys"]
)


@router.get("/id", response_model=schemas.JourneyRead, status_code=200)
async def get_journey(origin_id: int, destination_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    # Fetch a Journey
    
    A journey is a route between any two cities within the cities table.
    This route returns the cheapest possible route by default.
    It returns all legs of the journey.
    **Note** - The sum of the prices of all legs doesn't equal the total price. This is because we only add a £2 changeover fee at each stop where the stations aren't the same.
    """
    
    graph_manager = GraphManager() # gets us our instance of our singleton class
    

    cheapest_path = await find_cheapest_path(graph_manager, origin_id, destination_id)
    if not cheapest_path:
        raise HTTPException(status_code=404, detail="No journey found")
    
    # now need to get all the paths from the db in order
    all_routes = []
    for route_id in cheapest_path["route_ids"]:
        route = db.query(models.Route).filter(models.Route.id == route_id).first()
        all_routes.append(route)

    return {
        "total_price": cheapest_path['total_price'],
        "path": all_routes
    }


@router.get("/name", response_model=schemas.JourneyRead, status_code=200)
async def get_journey(origin_name: str, destination_name: str, railcard_discount: int = 0, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    # Fetch a Journey
    
    A journey is a route between any two cities within the cities table.
    This route returns the cheapest possible route by default.
    It returns all legs of the journey.
    **Note** - The sum of the prices of all legs doesn't equal the total price. This is because we only add a £2 changeover fee at each stop where the stations aren't the same.
    """

    # get both the origin and destination IDs from the names
    origin_city = db.query(models.City).filter(models.City.name == origin_name.lower()).first()
    destination_city = db.query(models.City).filter(models.City.name == destination_name.lower()).first()

    if not origin_city:
        raise HTTPException(status_code=404, detail=f"No city {origin_name} found.")
    if not destination_city:
        raise HTTPException(status_code=404, detail=f"No city {destination_name} found.")
    
    origin_id = origin_city.id
    destination_id = destination_city.id

    
    graph_manager = GraphManager() # gets us our instance of our singleton class
    

    cheapest_path = await find_cheapest_path(graph_manager, origin_id, destination_id)
    if not cheapest_path:
        raise HTTPException(status_code=404, detail="No journey found")
    
    # now need to get all the paths from the db in order
    all_routes = []
    for route_id in cheapest_path["route_ids"]:
        route = db.query(models.Route).filter(models.Route.id == route_id).first()
        all_routes.append(route)

    return {
        "total_price": cheapest_path['total_price'],
        "path": all_routes
    }