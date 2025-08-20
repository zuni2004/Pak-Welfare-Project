import uuid
import enum
from sqlalchemy import Column, String, Enum
from sqlalchemy.dialects.postgresql import UUID
from app.utils.database import Base
from .base import TimestampMixin
from sqlalchemy.orm import relationship


class NationalityEnum(str, enum.Enum):
    pakistani = "pakistani"
    saudi = "saudi"


class Guest(Base, TimestampMixin):
    __tablename__ = "guest"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(150), nullable=False)
    phone_number = Column(String(50), nullable=False)
    email = Column(String(255), nullable=True)

    nationality = Column(
        Enum(NationalityEnum, name="nationality_enum"),
        nullable=False,
        default=NationalityEnum.pakistani,
    )

    noc_application = relationship(
        "NOCApplication", back_populates="guest", uselist=False, cascade="all, delete"
    )

    documents = relationship(
        "Document", back_populates="guest", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Guest {self.full_name}>"
