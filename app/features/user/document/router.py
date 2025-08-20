import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.models.document import Document, DocumentTypeEnum
from app.models.guest import Guest, NationalityEnum
from app.models.user import User
from .schema import DocumentUploadResponse, SmartDocumentUploadResponse
from .service import (
    process_document,
    create_document_record,
    verify_user_or_guest_exists,
    validate_file_type,
)

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload/pakistani", response_model=SmartDocumentUploadResponse)
async def upload_pakistani_documents(
    user_id: Optional[str] = Form(None),
    guest_id: Optional[str] = Form(None),
    passport: UploadFile = File(..., description="Pakistani Passport"),
    iqama: UploadFile = File(..., description="Saudi Iqama"),
    nicop_front: UploadFile = File(..., description="Pakistani NICOP/CNIC front"),
    nicop_back: UploadFile = File(..., description="Pakistani NICOP/CNIC back"),
    db: Session = Depends(get_db),
):
    if user_id and guest_id:
        raise HTTPException(
            status_code=400, detail="Provide either user_id or guest_id, not both."
        )

    if not user_id and not guest_id:
        raise HTTPException(
            status_code=400, detail="Either user_id or guest_id must be provided."
        )

    if guest_id == "":
        guest_id = None
    if user_id == "":
        user_id = None

    for f in [passport, iqama, nicop_front, nicop_back]:
        validate_file_type(f)

    user_type, _ = verify_user_or_guest_exists(db, user_id, guest_id)

    documents_to_process = [
        (passport, DocumentTypeEnum.PASSPORT, "Pakistani Passport"),
        (iqama, DocumentTypeEnum.IQAMA, "Saudi Iqama"),
        (nicop_front, DocumentTypeEnum.NICOP_FRONT, "Pakistani NICOP/CNIC Front"),
        (nicop_back, DocumentTypeEnum.NICOP_BACK, "Pakistani NICOP/CNIC Back"),
    ]

    uploaded_documents = []
    for file, doc_type, doc_name in documents_to_process:
        try:
            document_url = await process_document(file, doc_type.value)

            document_record = create_document_record(
                db=db,
                document_url=document_url,
                document_type=doc_type,
                nationality=NationalityEnum.pakistani,
                guest_id=guest_id,
                user_id=user_id,
            )

            uploaded_documents.append(
                DocumentUploadResponse(
                    document_id=str(document_record.id),
                    document_type=doc_type.value,
                    document_url=document_url,
                    message=f"{doc_name} uploaded successfully",
                )
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to process {doc_name}: {str(e)}"
            )

    return SmartDocumentUploadResponse(
        uploaded_documents=uploaded_documents,
        nationality=NationalityEnum.pakistani.value,
        user_type=user_type,
        user_id=user_id,
        guest_id=guest_id,
        total_documents=len(uploaded_documents),
        message=f"Successfully uploaded {len(uploaded_documents)} document(s) for Pakistani {user_type}",
    )


@router.post("/upload/saudi", response_model=SmartDocumentUploadResponse)
async def upload_saudi_documents(
    user_id: Optional[str] = Form(None),
    guest_id: Optional[str] = Form(None),
    saudi_national_id: UploadFile = File(..., description="Saudi National ID"),
    db: Session = Depends(get_db),
):
    if user_id and guest_id:
        raise HTTPException(
            status_code=400, detail="Provide either user_id or guest_id, not both."
        )

    if not user_id and not guest_id:
        raise HTTPException(
            status_code=400, detail="Either user_id or guest_id must be provided."
        )

    if guest_id == "":
        guest_id = None
    if user_id == "":
        user_id = None

    validate_file_type(saudi_national_id)

    user_type, _ = verify_user_or_guest_exists(db, user_id, guest_id)

    try:
        document_url = await process_document(
            saudi_national_id, DocumentTypeEnum.SAUDI_NATIONAL_ID.value
        )

        document_record = create_document_record(
            db=db,
            document_url=document_url,
            document_type=DocumentTypeEnum.SAUDI_NATIONAL_ID.value,
            nationality=NationalityEnum.saudi,
            guest_id=guest_id,
            user_id=user_id,
        )

        uploaded_document = DocumentUploadResponse(
            document_id=str(document_record.id),
            document_type=DocumentTypeEnum.SAUDI_NATIONAL_ID.value,
            document_url=document_url,
            message="Saudi National ID uploaded successfully",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to process Saudi National ID: {str(e)}"
        )

    return SmartDocumentUploadResponse(
        uploaded_documents=[uploaded_document],
        nationality=NationalityEnum.saudi.value,
        user_type=user_type,
        user_id=user_id,
        guest_id=guest_id,
        total_documents=1,
        message=f"Successfully uploaded Saudi National ID for Saudi {user_type}",
    )


@router.get("/user/{user_id}", response_model=List[DocumentUploadResponse])
async def get_user_documents(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    documents = db.query(Document).filter(Document.user_id == user_id).all()

    return [
        DocumentUploadResponse(
            document_id=str(doc.id),
            document_type=doc.type.value,
            document_url=doc.document_url,
            message=f"{doc.type.value} document",
        )
        for doc in documents
    ]


@router.get("/guest/{guest_id}", response_model=List[DocumentUploadResponse])
async def get_guest_documents(guest_id: str, db: Session = Depends(get_db)):
    guest = db.query(Guest).filter(Guest.id == guest_id).first()
    if not guest:
        raise HTTPException(status_code=404, detail="Guest not found")

    documents = db.query(Document).filter(Document.guest_id == guest_id).all()

    return [
        DocumentUploadResponse(
            document_id=str(doc.id),
            document_type=doc.type.value,
            document_url=doc.document_url,
            message=f"{doc.type.value} document",
        )
        for doc in documents
    ]


@router.get("/check-completeness")
async def check_document_completeness(
    user_id: Optional[str] = None,
    guest_id: Optional[str] = None,
    nationality: NationalityEnum = NationalityEnum.pakistani,
    db: Session = Depends(get_db),
):
    if not user_id and not guest_id:
        raise HTTPException(
            status_code=400, detail="Provide either user_id or guest_id"
        )

    if user_id and guest_id:
        raise HTTPException(
            status_code=400, detail="Provide either user_id OR guest_id, not both"
        )

    if user_id:
        documents = db.query(Document).filter(Document.user_id == user_id).all()
        identifier = f"User {user_id}"
    else:
        documents = db.query(Document).filter(Document.guest_id == guest_id).all()
        identifier = f"Guest {guest_id}"

    doc_types_uploaded = {doc.type for doc in documents}

    if nationality == NationalityEnum.pakistani:
        required_docs = {
            DocumentTypeEnum.PASSPORT,
            DocumentTypeEnum.IQAMA,
            DocumentTypeEnum.NICOP_FRONT,
            DocumentTypeEnum.NICOP_BACK,
        }
        required_names = [
            "Pakistani Passport",
            "Saudi Iqama",
            "Pakistani NICOP/CNIC Front",
            "Pakistani NICOP/CNIC Back",
        ]
    elif nationality == NationalityEnum.saudi:
        required_docs = {DocumentTypeEnum.SAUDI_NATIONAL_ID}
        required_names = ["Saudi National ID"]
    else:
        raise HTTPException(status_code=400, detail="Unsupported nationality")

    missing_docs = required_docs - doc_types_uploaded
    is_complete = len(missing_docs) == 0

    return {
        "identifier": identifier,
        "nationality": nationality.value,
        "is_complete": is_complete,
        "uploaded_documents": [doc.type.value for doc in documents],
        "missing_documents": [doc.value for doc in missing_docs],
        "required_documents": required_names,
        "message": (
            "All documents uploaded!"
            if is_complete
            else f"Missing documents: {', '.join([doc.value for doc in missing_docs])}"
        ),
    }
