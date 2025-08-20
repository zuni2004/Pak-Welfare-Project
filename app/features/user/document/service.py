import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.models.document import Document, DocumentTypeEnum
from app.models.guest import Guest, NationalityEnum
from app.models.user import User


async def process_document(file, document_type: str) -> str:
    filename = f"{uuid.uuid4()}_{file.filename}"
    document_url = f"https://your-storage.com/documents/{filename}"
    return document_url


def create_document_record(
    db: Session,
    document_url: str,
    document_type: DocumentTypeEnum,
    nationality: NationalityEnum,
    guest_id: Optional[str] = None,
    user_id: Optional[str] = None,
) -> Document:
    document = Document(
        document_url=document_url,
        type=document_type,
        nationality=nationality,
        guest_id=guest_id,
        user_id=user_id,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def verify_user_or_guest_exists(
    db: Session, user_id: Optional[str], guest_id: Optional[str]
):
    if user_id:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User with ID {user_id} not found. Please check your user ID or register first.",
            )
        return "user", user

    if guest_id:
        guest = db.query(Guest).filter(Guest.id == guest_id).first()
        if not guest:
            raise HTTPException(
                status_code=404,
                detail=f"Guest with ID {guest_id} not found. Please check your guest ID or create guest profile first.",
            )
        return "guest", guest

    return None, None


def validate_file_type(file: UploadFile, allowed_types: List[str] = None):
    if not file or file.filename == "":
        return

    allowed_types = allowed_types or [
        "image/jpeg",
        "image/png",
        "image/jpg",
        "application/pdf",
    ]

    if (
        hasattr(file, "content_type")
        and file.content_type
        and file.content_type not in allowed_types
    ):
        raise HTTPException(
            status_code=400,
            detail=f"File type {file.content_type} not allowed. Allowed types: {', '.join(allowed_types)}",
        )
