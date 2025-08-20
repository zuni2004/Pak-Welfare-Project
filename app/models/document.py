import uuid
import enum
from sqlalchemy import Column, String, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.utils.database import Base
from .base import TimestampMixin
from .guest import NationalityEnum
from app.models.user import User


class DocumentTypeEnum(str, enum.Enum):
    NICOP_FRONT = "NICOP_FRONT"
    NICOP_BACK = "NICOP_BACK"
    PASSPORT = "PASSPORT"
    IQAMA = "IQAMA"
    SAUDI_NATIONAL_ID = "SAUDI_NATIONAL_ID"


class Document(Base, TimestampMixin):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_url = Column(String(500), nullable=False)

    guest_id = Column(UUID(as_uuid=True), ForeignKey("guest.id"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    noc_application_id = Column(
        UUID(as_uuid=True), ForeignKey("noc_application.tracking_number"), nullable=True
    )

    guest = relationship("Guest", back_populates="documents")
    user = relationship("User", back_populates="documents")
    noc_application = relationship("NOCApplication", back_populates="documents")

    nationality = Column(Enum(NationalityEnum, name="nationality_enum"), nullable=False)
    type = Column(Enum(DocumentTypeEnum, name="document_type_enum"), nullable=False)

    def __repr__(self):
        return f"<Document {self.type} for nationality={self.nationality}>"
