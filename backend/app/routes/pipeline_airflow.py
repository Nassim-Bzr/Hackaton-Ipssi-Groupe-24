import datetime
from typing import Any, Dict

import requests
from fastapi import APIRouter, HTTPException

from app.services.data_lake_service import object_exists
from app.services.mongo_service import get_document_by_id
from config.settings import AIRFLOW_API_URL, AIRFLOW_PASSWORD, AIRFLOW_USERNAME
from config.settings import DATA_LAKE_ENABLED

router = APIRouter()


@router.post("/pipeline/trigger")
def trigger_pipeline(payload: Dict[str, Any]):
    """
    Déclenche la DAG Airflow `pipeline_documentaire`.

    Le frontend doit appeler cette route une fois l'upload PDF terminé,
    en lui passant au minimum un `doc_id` (et éventuellement d'autres méta-données).
    """
    doc_id = payload.get("doc_id")
    if not doc_id:
        raise HTTPException(status_code=400, detail="Champ `doc_id` manquant dans le payload.")

    now = datetime.datetime.utcnow().replace(microsecond=0).isoformat()
    dag_run_id = f"doc-{doc_id}-{now}"

    body = {
        "dag_run_id": dag_run_id,
        "conf": payload,
    }

    try:
        response = requests.post(
            AIRFLOW_API_URL,
            json=body,
            auth=(AIRFLOW_USERNAME, AIRFLOW_PASSWORD),
            timeout=10,
        )
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Impossible d'appeler Airflow: {exc}",
        ) from exc

    if not response.ok:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Airflow a renvoyé une erreur: {response.text}",
        )

    return {
        "message": "Pipeline Airflow déclenchée avec succès.",
        "dag_run_id": dag_run_id,
    }


@router.get("/pipeline/minio-status/{doc_id}")
def minio_status(doc_id: str):
    """
    Retourne l'état (existe / n'existe pas) des objets data-lake pour un `doc_id`.

    Utilisé par la DAG Airflow pour “vérifier les étapes Minio”.
    """
    document = get_document_by_id(doc_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document introuvable.")

    metadata = document.get("metadata") or {}
    raw_uri = metadata.get("raw_uri")
    clean_uri = metadata.get("clean_uri")
    curated_uri = metadata.get("curated_uri")

    # Si une URI n'est pas présente, on considère l'objet comme manquant.
    raw_exists = object_exists(raw_uri) if raw_uri else False
    clean_exists = object_exists(clean_uri) if clean_uri else False
    curated_exists = object_exists(curated_uri) if curated_uri else False

    return {
        "enabled": DATA_LAKE_ENABLED,
        "raw": {"uri": raw_uri, "exists": raw_exists},
        "clean": {"uri": clean_uri, "exists": clean_exists},
        "curated": {"uri": curated_uri, "exists": curated_exists},
    }

