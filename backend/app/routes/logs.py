"""Routes pour l'écriture et la lecture des logs du pipeline."""

from typing import Any

from fastapi import APIRouter, HTTPException

from app.services.logs_service import get_logs, insert_log

router = APIRouter()


@router.post("/pipeline/logs", status_code=201)
def create_log(payload: dict[str, Any]) -> dict[str, str]:
    """
    Reçoit un log envoyé par Airflow et le stocke en BDD.
    Champs attendus : dag_run_id, task_id, step_name, message, level, timestamp.
    doc_id optionnel.
    """
    dag_run_id = payload.get("dag_run_id")
    task_id = payload.get("task_id")
    step_name = payload.get("step_name")
    message = payload.get("message")
    level = payload.get("level")
    timestamp = payload.get("timestamp")

    if not all([dag_run_id, task_id, step_name, message, level, timestamp]):
        raise HTTPException(
            status_code=400,
            detail="Champs requis manquants : dag_run_id, task_id, step_name, message, level, timestamp.",
        )

    insert_log(
        dag_run_id=dag_run_id,
        task_id=task_id,
        step_name=step_name,
        message=message,
        level=level,
        timestamp=timestamp,
        doc_id=payload.get("doc_id"),
    )
    return {"status": "created"}


@router.get("/pipeline/logs")
def list_logs(
    doc_id: str | None = None,
    dag_run_id: str | None = None,
    limit: int = 100,
) -> dict[str, Any]:
    """Retourne la liste des logs du pipeline avec filtres optionnels."""
    logs = get_logs(doc_id=doc_id, dag_run_id=dag_run_id, limit=limit)
    return {"logs": logs, "total": len(logs)}
