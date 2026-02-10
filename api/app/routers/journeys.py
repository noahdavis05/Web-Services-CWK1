from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import models, schemas
from ..utils.graph_manager import GraphManager
from ..utils.journey_finder import find_cheapest_path

router = APIRouter(
    prefix="/journeys",
    tags=["Journeys"]
)

@router.get("/", response_model=schemas.JourneyRead, status_code=200)
def get_journey(origin_id: int, destination_id: int, db: Session = Depends(get_db)):
    
    graph_manager = GraphManager() # gets us our instance of our singleton class

    cheapest_path = find_cheapest_path(graph_manager, origin_id, destination_id)

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
    