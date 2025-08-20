import os
import cv2
import tempfile
import time
from fastapi import APIRouter, UploadFile, File, HTTPException
from .schema import UploadResponse
from .service import process_image
from .schema import NICOPFrontResponse, NICOPBackResponse
from app.services.ocr.nicop_service import (
    process_nicop_front_improved,
    process_nicop_back_improved,
)
from .schema import PassportResponse
from app.services.ocr.passport_service import process_passport_front
from .schema import IqamaData
from app.services.ocr.iqama_service import process_iqama_front


router = APIRouter(prefix="/noc", tags=["NOC Application"])


@router.post("/upload", response_model=UploadResponse)
async def upload_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed.")

    filename = await process_image(file)
    return UploadResponse(
        filename=filename, message="File has been uploaded successfully."
    )


@router.post("/nicop-front", response_model=NICOPFrontResponse)
async def upload_nicop_front(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed.")

    try:
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=os.path.splitext(file.filename)[1]
        ) as tmp:
            temp_path = tmp.name
            content = await file.read()
            tmp.write(content)

        output_image_path = temp_path + "_vis.jpg"

        result = process_nicop_front_improved(temp_path, output_image_path)

        os.remove(temp_path)

        if not result:
            raise HTTPException(status_code=500, detail="OCR failed to extract data.")

        return NICOPFrontResponse(
            name=result["name"],
            father_name=result["father_name"],
            gender=result["gender"],
            country=result["country"],
            cnic_number=result["cnic_number"],
            date_of_birth=result["date_of_birth"],
            date_of_issue=result["date_of_issue"],
            date_of_expiry=result["date_of_expiry"],
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/nicop-back", response_model=NICOPBackResponse)
async def upload_nicop_back(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed.")

    try:
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=os.path.splitext(file.filename)[1]
        ) as tmp:
            temp_path = tmp.name
            content = await file.read()
            tmp.write(content)

        output_image_path = temp_path + "_vis.jpg"

        result = process_nicop_back_improved(temp_path, output_image_path)

        os.remove(temp_path)

        if not result:
            raise HTTPException(status_code=500, detail="OCR failed to extract data.")

        return NICOPBackResponse(
            present_address=result["present_address"],
            permanent_address=result["permanent_address"],
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/passport-front", response_model=PassportResponse)
async def upload_passport_front(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed.")

    try:
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=os.path.splitext(file.filename)[1]
        ) as tmp:
            temp_path = tmp.name
            tmp.write(await file.read())

        result = process_passport_front(temp_path)

        os.remove(temp_path)

        if not result:
            raise HTTPException(status_code=500, detail="OCR failed to extract data.")

        return PassportResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/iqama-front", response_model=IqamaData)
async def upload_iqama_front(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed.")

    try:
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=os.path.splitext(file.filename)[1]
        ) as tmp:
            temp_path = tmp.name
            tmp.write(await file.read())

        result = process_iqama_front(temp_path)

        os.remove(temp_path)

        if not result:
            raise HTTPException(status_code=500, detail="OCR failed to extract data.")

        return IqamaData(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
