import datetime
from typing import Any, Dict

import requests
from fastapi import APIRouter, HTTPException

from config.settings import AIRFLOW_API_URL, AIRFLOW_PASSWORD, AIRFLOW_USERNAME

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

