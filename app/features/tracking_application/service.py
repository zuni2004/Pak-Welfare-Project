from sqlalchemy.orm import Session
from uuid import UUID
from app.models import TrackingApplication, NOCApplication
from app.models import Guest

def get_tracking_by_tracking_number(db: Session, noc_tracking_number: UUID):
    return db.query(TrackingApplication).filter_by(noc_tracking_number=noc_tracking_number).first()

