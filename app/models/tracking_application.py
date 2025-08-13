import uuid
from sqlalchemy import Column, String, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.utils.database import Base
from .base import TimestampMixin


class TrackingApplication(Base, TimestampMixin):
    __tablename__ = "tracking_application"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    noc_tracking_number = Column(UUID(as_uuid=True), ForeignKey("noc_application.tracking_number"), nullable=False, unique=True)
    guest_id = Column( UUID(as_uuid=True), ForeignKey("guest.id"), nullable=False, unique=True)
    status = Column(String, nullable=False)
    note = Column(String, nullable=True)
    is_guest_application = Column(Boolean, default=True, nullable=False)

    noc_application = relationship("NOCApplication", back_populates="tracking_application", uselist=False)
    guest = relationship("Guest", back_populates="tracking_application", uselist=False)
