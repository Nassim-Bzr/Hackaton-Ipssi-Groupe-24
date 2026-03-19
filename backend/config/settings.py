import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017")
MONGO_DB = os.getenv("MONGO_DB", "hackathon")
MONGO_COLLECTION = "documents"

VALIDATION_SERVICE_URL = os.getenv(
    "VALIDATION_SERVICE_URL", "http://validations:8000/data-validation"
)

UPLOAD_DIR = "/tmp/uploads"

DATA_LAKE_ENABLED = os.getenv("DATA_LAKE_ENABLED", "true").lower() == "true"
DATA_LAKE_ENDPOINT = os.getenv("DATA_LAKE_ENDPOINT", "minio:9000")
DATA_LAKE_ACCESS_KEY = os.getenv("DATA_LAKE_ACCESS_KEY", "minioadmin")
DATA_LAKE_SECRET_KEY = os.getenv("DATA_LAKE_SECRET_KEY", "minioadmin")
DATA_LAKE_SECURE = os.getenv("DATA_LAKE_SECURE", "false").lower() == "true"

RAW_BUCKET = os.getenv("RAW_BUCKET", "raw")
CLEAN_BUCKET = os.getenv("CLEAN_BUCKET", "clean")
CURATED_BUCKET = os.getenv("CURATED_BUCKET", "curated")

# Configuration de l'API Airflow pour déclencher la DAG depuis le backend
AIRFLOW_API_URL = os.getenv(
    "AIRFLOW_API_URL",
    "http://airflow:8080/api/v1/dags/pipeline_documentaire/dagRuns",
)
AIRFLOW_USERNAME = os.getenv("AIRFLOW_USERNAME", "admin")
AIRFLOW_PASSWORD = os.getenv("AIRFLOW_PASSWORD", "admin")
