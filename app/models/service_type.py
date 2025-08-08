import uuid
from sqlalchemy import Column, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID

from app.utils.database import Base
from .base import TimestampMixin

class ServiceType(Base, TimestampMixin):
    __tablename__ = "service_types"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    active = Column(Boolean, default=True, nullable=False)

    def __repr__(self):
        return (f"<ServiceType(name='{self.name}', slug='{self.slug}')>")
