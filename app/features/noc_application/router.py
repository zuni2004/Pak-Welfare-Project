import os
import cv2
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.features.noc_application.schema import UploadResponse
from app.features.noc_application.service import process_image
from app.features.noc_application.schema import NICOPFrontResponse, NICOPBackResponse, OCRResponse
from app.features.noc_application.nicop_service import process_nicop_front_improved, process_nicop_back_improved
from app.features.noc_application.schema import PassportRequest, PassportResponse
from app.features.noc_application.passport_service import process_passport_front
from .schema import OCRResponse, IqamaData
from .iqama_service import (preprocess_image_enhanced, extract_text_with_multiple_configs, extract_iqama_fields, draw_all_detections, save_extracted_data)


router = APIRouter(prefix="/noc", tags=["NOC Application"])

@router.post("/upload", response_model=UploadResponse)
async def upload_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed.")
    
    filename = await process_image(file)
    return UploadResponse(
        filename=filename,
        message="File has been uploaded successfully."
    )

@router.get("/example")
async def example():
    return {"message": "Hello PLEASE WORRKKKKKKKKKKKKKKKKK"}


@router.post("/nicop-front", response_model=OCRResponse)
async def upload_nicop_front(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed.")
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            temp_path = tmp.name
            content = await file.read()
            tmp.write(content)

        output_image_path = temp_path + "_vis.jpg"

        result = process_nicop_front_improved(temp_path, output_image_path)
        os.remove(temp_path)

        if not result:
            raise HTTPException(status_code=500, detail="OCR failed to extract data.")

        return OCRResponse(
            message="NICOP front side processed successfully.",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/nicop-back", response_model=OCRResponse)
async def upload_nicop_back(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed.")

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            temp_path = tmp.name
            content = await file.read()
            tmp.write(content)

        output_image_path = temp_path + "_vis.jpg"

        result = process_nicop_back_improved(temp_path, output_image_path)
        os.remove(temp_path) 

        if not result:
            raise HTTPException(status_code=500, detail="OCR failed to extract data.")

        return OCRResponse(
            message="NICOP back side processed successfully.",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/passport-front", response_model=OCRResponse)
async def upload_passport_front(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed.")

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            temp_path = tmp.name
            content = await file.read()
            tmp.write(content)

        output_image_path = temp_path + "_vis.jpg"

        result = process_passport_front(temp_path, output_image_path)

        os.remove(temp_path)

        if not result:
            raise HTTPException(status_code=500, detail="OCR failed to extract data.")

        return OCRResponse(
            message="Passport front side processed successfully.",
            data=result
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/Iqama-Front", response_model=OCRResponse)
async def upload_iqama(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed.")

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            temp_path = tmp.name
            content = await file.read()
            tmp.write(content)

        original_image, cleaned_image = preprocess_image_enhanced(temp_path)

        extracted_results = extract_text_with_multiple_configs(cleaned_image)

        extracted_data = extract_iqama_fields(extracted_results)

        os.remove(temp_path)

        return OCRResponse(
            message="Iqama processed successfully.",
            data=IqamaData(**extracted_data)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
