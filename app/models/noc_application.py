import uuid
from sqlalchemy import Column, String, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from app.utils.database import Base
from .base import TimestampMixin
from sqlalchemy.orm import relationship


class NOCApplication(Base, TimestampMixin):
    __tablename__ = "noc_application"

    tracking_number = Column(
        UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )
    status = Column(String, nullable=False, default="pending")
    guest_id = Column(
        UUID(as_uuid=True), ForeignKey("guest.id"), nullable=False, unique=True
    )
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    burial_location = Column(String(100), nullable=True)
    documents_uploaded = Column(Boolean, default=False, nullable=False)

    guest = relationship("Guest", back_populates="noc_application", uselist=False)
    user = relationship("User", back_populates="noc_applications", uselist=False)

    documents = relationship(
        "Document", back_populates="noc_application", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<NOCApplication(tracking_number='{self.tracking_number}', status='{self.status}')>"
