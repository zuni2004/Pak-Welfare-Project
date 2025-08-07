# import base64
# import mimetypes
# import os
# from os.path import splitext
# from urllib.parse import urlparse

# # import httpx
# from fastapi import HTTPException, UploadFile, status

# ALLOWED_IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"]
# ALLOWED_FILE_EXTENSIONS = [".pdf"]
# ALLOWED_FONT_EXTENSIONS = [".ttf", ".otf"]


# def is_allowed_font_file(file: UploadFile):
#     _, ext = os.path.splitext(file.filename)
#     if ext.lower() not in ALLOWED_FONT_EXTENSIONS:
#         raise HTTPException(
#             status_code=400,
#             detail=f"Unsupported font format: {ext}. Only .ttf and .otf are supported.",
#         )


# def is_allowed_image_file(file: UploadFile):
#     _, ext = os.path.splitext(file.filename.lower())
#     if ext not in ALLOWED_IMAGE_EXTENSIONS:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"Unsupported image type: {ext}. Allowed types are: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}",
#         )


# def is_allowed_image_url(url: str):
#     path = urlparse(url).path
#     _, ext = splitext(path.lower())
#     if ext not in ALLOWED_IMAGE_EXTENSIONS:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"URL does not end in a supported image type: {ext}. Allowed: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}",
#         )


# async def convert_image_to_base64_url(file: UploadFile) -> str:
#     """
#     Converts an uploaded image to a base64 data URL.
#     Supports only image files.
#     """
#     if not hasattr(file, "_cached_content"):
#         await file.seek(0)
#         file._cached_content = await file.read()

#     base64_bytes = base64.b64encode(file._cached_content).decode("utf-8")
#     return f"data:{file.content_type};base64,{base64_bytes}"


# async def convert_url_to_base64_url(file_url: str) -> dict:
#     ext = os.path.splitext(file_url)[-1].lower()
#     if ext not in (ALLOWED_IMAGE_EXTENSIONS + ALLOWED_FILE_EXTENSIONS):
#         return {"url": "", "ext": ext}  # Graceful fail

#     mime_type, _ = mimetypes.guess_type(file_url)
#     if not mime_type:
#         mime_type = "application/octet-stream"

#     try:
#         async with httpx.AsyncClient(timeout=10) as client:
#             response = await client.get(file_url)
#             response.raise_for_status()
#             content = response.content

#         encoded = base64.b64encode(content).decode("utf-8")
#         return f"data:{mime_type};base64,{encoded}"

#     except Exception:
#         return ""
