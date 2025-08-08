import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.utils.database import Base
from .base import TimestampMixin

class Guest(Base, TimestampMixin):
    __tablename__ = "guests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(150), nullable=False)
    phone_number = Column(String(50), nullable=False)
    email = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)
    tracking_number = Column(UUID(as_uuid=True), ForeignKey("noc_application.tracking_number"), nullable=True)
    noc_applications = relationship("NOCApplication", back_populates="guest")

    def __repr__(self):
        return f"<GuestApplication {self.full_name} | TrackingNumber={self.tracking_number}>"

