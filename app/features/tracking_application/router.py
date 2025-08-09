from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.utils.database import get_db
from .schema import TrackingCreate, TrackingResponse
from .service import get_tracking_by_tracking_number

router = APIRouter(prefix="/tracking", tags=["Tracking"])

@router.get("/by-tracking/{tracking_number}", response_model=TrackingResponse)
async def track_by_tracking_number(tracking_number: UUID, db: Session = Depends(get_db)):
    tracking = get_tracking_by_tracking_number(db, tracking_number)
    if not tracking:
        raise HTTPException(status_code=404, detail="Application not found")
    return tracking
