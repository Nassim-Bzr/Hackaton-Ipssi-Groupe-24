"""Service de stockage et récupération des logs du pipeline Airflow."""

from datetime import datetime
from typing import Any

from pymongo import DESCENDING
from pymongo import MongoClient

from config.settings import MONGO_COLLECTION_LOGS, MONGO_DB, MONGO_URI

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
logs_collection = db[MONGO_COLLECTION_LOGS]


def insert_log(
    dag_run_id: str,
    task_id: str,
    step_name: str,
    message: str,
    level: str,
    timestamp: str | datetime,
    doc_id: str | None = None,
    **kwargs: Any,
) -> None:
    """Insère un log du pipeline dans MongoDB."""
    doc = {
        "dag_run_id": dag_run_id,
        "task_id": task_id,
        "step_name": step_name,
        "message": message,
        "level": level,
        "timestamp": timestamp,
        **kwargs,
    }
    if doc_id is not None:
        doc["doc_id"] = doc_id
    logs_collection.insert_one(doc)


def get_logs(
    doc_id: str | None = None,
    dag_run_id: str | None = None,
    limit: int = 100,
) -> list[dict]:
    """Retourne les logs, triés par timestamp décroissant, avec filtres optionnels."""
    filt = {}
    if doc_id is not None:
        filt["doc_id"] = doc_id
    if dag_run_id is not None:
        filt["dag_run_id"] = dag_run_id
    cursor = (
        logs_collection.find(filt, {"_id": 0})
        .sort("timestamp", DESCENDING)
        .limit(limit)
    )
    return list(cursor)
