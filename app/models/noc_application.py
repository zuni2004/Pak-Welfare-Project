import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.utils.database import Base
from .base import TimestampMixin

class NOCApplication(Base):
    __tablename__ = "noc_application"

    tracking_number = Column(UUID(as_uuid=True), primary_key=True)

