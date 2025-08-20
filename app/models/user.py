import uuid
from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import relationship

from app.utils.database import Base
from .base import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_user_confirmed = Column(Boolean, default=False, nullable=False)
    user_data = Column(MutableDict.as_mutable(JSONB), default={}, nullable=True)
    last_password_reset_token_hash = Column(String, nullable=True)
    last_password_reset_at = Column(DateTime(timezone=True), nullable=True)

    noc_applications = relationship(
        "NOCApplication", back_populates="user", uselist=True
    )

    documents = relationship(
        "Document", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User(email='{self.email}', first_name='{self.first_name}', last_name='{self.last_name}')>"
