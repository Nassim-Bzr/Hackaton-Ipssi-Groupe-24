import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017")
MONGO_DB = os.getenv("MONGO_DB", "hackathon")
MONGO_COLLECTION = "documents"

VALIDATION_SERVICE_URL = os.getenv(
    "VALIDATION_SERVICE_URL", "http://validations:8000/data-validation"
)

UPLOAD_DIR = "/tmp/uploads"
