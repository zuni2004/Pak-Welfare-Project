import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from app.utils.database import Base
from .base import TimestampMixin
from sqlalchemy.orm import relationship

class Guest(Base, TimestampMixin):
    __tablename__ = "guest"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(150), nullable=False)
    phone_number = Column(String(50), nullable=False)
    email = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)
    noc_application = relationship("NOCApplication", back_populates="guest", uselist=False, cascade="all, delete")
    tracking_application = relationship("TrackingApplication", back_populates="guest", uselist=False)


    def __repr__(self):
        return f"<GuestApplication {self.full_name}>"
