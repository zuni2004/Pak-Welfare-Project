# import os
# from minio import Minio
# from minio.error import S3Error
# import json


# class MinIOConfig:
#     def __init__(self):
#         # Environment detection
#         self.is_production = os.getenv("RAILWAY_ENVIRONMENT") == "production"

#         if self.is_production:
#             # Railway MinIO settings
#             self.MINIO_ENDPOINT = os.getenv(
#                 "MINIO_ENDPOINT", "bucket-production-78ff.up.railway.app"
#             )
#             self.MINIO_ACCESS_KEY = os.getenv(
#                 "MINIO_ACCESS_KEY", "YsnfstrJ3lIXTlj4uKDo8dnd2Cfu14e7"
#             )
#             self.MINIO_SECRET_KEY = os.getenv(
#                 "MINIO_SECRET_KEY", "dCbL4nwJg6eSlBNvUy524WJhbu76SbSt06MtNEJPjYTJxeXU"
#             )
#             self.MINIO_SECURE = True
#             self.MINIO_PUBLIC_URL = f"https://{self.MINIO_ENDPOINT}"
#         else:
#             # Local development settings
#             self.MINIO_ENDPOINT = "localhost:9000"
#             self.MINIO_ACCESS_KEY = "minioadmin"
#             self.MINIO_SECRET_KEY = "minioadmin"
#             self.MINIO_SECURE = False
#             self.MINIO_PUBLIC_URL = "http://localhost:9000"

#         # Common settings
#         self.BUCKET_NAME = "assets"
#         self.MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
#         self.ALLOWED_IMAGE_TYPES = [
#             "image/jpeg",
#             "image/png",
#             "image/webp",
#             "image/gif",
#         ]

#         # Initialize client
#         self.client = self._create_client()

#     def _create_client(self):
#         """Create MinIO client"""
#         return Minio(
#             self.MINIO_ENDPOINT,
#             access_key=self.MINIO_ACCESS_KEY,
#             secret_key=self.MINIO_SECRET_KEY,
#             secure=self.MINIO_SECURE,
#         )

#     # Not used right now. Bucket created manually. If used, chnage policy to read write and public access
#     def setup_bucket(self):
#         """Create bucket and set policies"""
#         try:
#             # Create bucket if it doesn't exist
#             if not self.client.bucket_exists(self.BUCKET_NAME):
#                 self.client.make_bucket(self.BUCKET_NAME)
#                 print(f"Bucket '{self.BUCKET_NAME}' created")

#             # Set public read policy for images
#             bucket_policy = {
#                 "Version": "2012-10-17",
#                 "Statement": [
#                     {
#                         "Effect": "Allow",
#                         "Principal": {"AWS": "*"},
#                         "Action": ["s3:GetObject"],
#                         "Resource": [f"arn:aws:s3:::{self.BUCKET_NAME}/*"],
#                     }
#                 ],
#             }

#             self.client.set_bucket_policy(self.BUCKET_NAME, json.dumps(bucket_policy))
#             print(f"Bucket policy set for public read access")

#         except S3Error as e:
#             print(f"MinIO setup error: {e}")
#             raise e

#     def get_public_url(self, filename: str) -> str:
#         """Generate public URL for uploaded file"""
#         return f"{self.MINIO_PUBLIC_URL}/{self.BUCKET_NAME}/{filename}"


# # Global instance
# minio_config = MinIOConfig()
