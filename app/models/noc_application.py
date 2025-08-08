import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.utils.database import Base
from .base import TimestampMixin

class NOCApplication(Base, TimestampMixin):
    __tablename__ = "noc_applications"

    tracking_number = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    status = Column(String, nullable=False, default="pending")
    guest_id = Column(UUID(as_uuid=True), ForeignKey("guests.id"), nullable=False) 
    burial_location = Column(String(100), nullable=True)
    documents_uploaded = Column(Boolean, default=False, nullable=False)
    guest = relationship("Guest", back_populates="noc_applications")


