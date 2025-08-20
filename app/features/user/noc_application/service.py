from fastapi import UploadFile


async def process_image(file: UploadFile) -> str:
    await file.read()
    print(f"Uploaded file: {file.filename}")
    return file.filename
