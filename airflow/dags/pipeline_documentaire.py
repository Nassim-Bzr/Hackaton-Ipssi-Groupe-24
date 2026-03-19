from datetime import datetime, timedelta
import logging
import requests
from airflow import DAG
from airflow.operators.python import PythonOperator

VALIDATIONS_URL = "http://validations:8000"
BACKEND_URL = "http://backend:3000"
LOGS_URL = f"{BACKEND_URL}/pipeline/logs"


def _send_log(context: dict, task_id: str, step_name: str, message: str, level: str = "success") -> None:
    """Envoie un log au backend sans faire échouer la tâche en cas d'erreur."""
    try:
        dag_run = context.get("dag_run")
        dag_run_id = dag_run.run_id if dag_run else ""
        doc_id = None
        if dag_run and dag_run.conf and isinstance(dag_run.conf, dict):
            doc_id = dag_run.conf.get("doc_id")
        payload = {
            "dag_run_id": dag_run_id,
            "task_id": task_id,
            "step_name": step_name,
            "message": message,
            "level": level,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        if doc_id is not None:
            payload["doc_id"] = doc_id
        requests.post(LOGS_URL, json=payload, timeout=5)
    except Exception as e:
        logging.warning("Envoi du log au backend ignoré: %s", e)


def _get_conf_from_context(context: dict) -> dict:
    """Récupère le payload envoyé par le frontend via dag_run.conf."""
    dag_run = context.get("dag_run")
    if dag_run is None or dag_run.conf is None:
        raise ValueError("Aucune configuration de run (dag_run.conf) n'a été fournie à la DAG.")
    return dag_run.conf


def verifier_backend(**context):
    """Vérifie que le document identifié par doc_id existe bien côté backend/BDD."""
    conf = _get_conf_from_context(context)
    doc_id = conf.get("doc_id")
    if not doc_id:
        raise ValueError("Champ `doc_id` manquant dans le payload Airflow (dag_run.conf).")

    # On vérifie que le backend connaît bien le document, ce qui implique qu'il est stocké en BDD.
    r = requests.get(f"{BACKEND_URL}/documents/{doc_id}", timeout=10)
    r.raise_for_status()
    print(f"[verifier_backend] Document {doc_id} trouvé côté backend.")
    _send_log(context, "verifier_backend", "Vérification backend", f"Document {doc_id} trouvé côté backend.", "success")


def verifier_validations(**context):
    """Vérifie que le service de validations est accessible."""
    r = requests.get(f"{VALIDATIONS_URL}/docs", timeout=10)
    r.raise_for_status()
    print("[verifier_validations] Service de validations accessible.")
    _send_log(context, "verifier_validations", "Vérification validations", "Service de validations accessible.", "success")


def valider_donnees(**context):
    """Vérifie que les données associées au document sont valides côté service de validations."""
    conf = _get_conf_from_context(context)
    doc_id = conf.get("doc_id")
    if not doc_id:
        raise ValueError("Champ `doc_id` manquant dans le payload pour la validation des données.")

    # Récupération du document complet depuis le backend afin de le valider
    r_doc = requests.get(f"{BACKEND_URL}/documents/{doc_id}", timeout=10)
    r_doc.raise_for_status()
    document = r_doc.json()

    entities = document.get("entities", {}) or {}
    siret = entities.get("siret")
    montant_ttc = entities.get("montant_ttc")
    montant_ht = entities.get("montant_ht")
    montant = montant_ttc if montant_ttc is not None else montant_ht

    if not siret or montant is None:
        raise ValueError(
            f"Impossible de récupérer un SIRET et un montant valides pour le document {doc_id} "
            "afin de les envoyer au service de validation."
        )

    payload = {
        "siret": siret,
        "montant": float(montant),
    }

    # Envoie du payload au service de validation pour valider
    r = requests.post(f"{VALIDATIONS_URL}/data-validation", json=payload, timeout=20)
    r.raise_for_status()
    print(f"[valider_donnees] Données validées pour le document {doc_id} (siret={siret}, montant={montant}).")
    _send_log(context, "valider_donnees", "Validation des données", f"Données validées pour le document {doc_id} (siret={siret}, montant={montant}).", "success")


def verifier_coherence(**context):
    """Vérifie la cohérence documentaire pour le document ciblé."""
    conf = _get_conf_from_context(context)
    doc_id = conf.get("doc_id")
    if not doc_id:
        raise ValueError("Champ `doc_id` manquant dans le payload pour la vérification de cohérence.")

    # Récupération du document depuis le backend pour construire le payload attendu
    r_doc = requests.get(f"{BACKEND_URL}/documents/{doc_id}", timeout=10)
    r_doc.raise_for_status()
    document = r_doc.json()
    entities = document.get("entities") or {}
    doc_type = document.get("document_type") or "facture"
    date_echeance = entities.get("date_expiration") or entities.get("date_echeance")

    doc_coherence = {
        "document_type": doc_type,
        "siret": entities.get("siret"),
        "montant_ht": entities.get("montant_ht"),
        "tva": entities.get("tva"),
        "montant_ttc": entities.get("montant_ttc"),
        "date_echeance": str(date_echeance) if date_echeance is not None else None,
    }

    # Retirer les clés à None pour éviter tout souci de sérialisation
    # Ternaire pour faire ça en une ligne
    doc_coherence = {k: v for k, v in doc_coherence.items() if v is not None}

    payload = {"documents": [doc_coherence]}

    r = requests.post(f"{VALIDATIONS_URL}/coherence-check", json=payload, timeout=20)
    r.raise_for_status()
    print(f"[verifier_coherence] Cohérence documentaire vérifiée pour le document {doc_id}.")
    _send_log(context, "verifier_coherence", "Vérification cohérence", f"Cohérence documentaire vérifiée pour le document {doc_id}.", "success")


def fin_pipeline(**context):
    """Tâche finale marquant la fin de la pipeline pour un doc_id donné."""
    conf = {}
    try:
        conf = _get_conf_from_context(context)
    except Exception:
        # Au cas ou si conf n'est pas disponible, on ne bloque pas l'exécution du DAG
        pass

    doc_id = conf.get("doc_id") if isinstance(conf, dict) else None
    if doc_id:
        print(f"Pipeline terminée pour le document {doc_id}.")
        _send_log(context, "fin_pipeline", "Fin pipeline", f"Pipeline terminée pour le document {doc_id}.", "success")
    else:
        print("Pipeline terminée (doc_id non renseigné).")
        _send_log(context, "fin_pipeline", "Fin pipeline", "Pipeline terminée (doc_id non renseigné).", "success")


with DAG(
    dag_id="pipeline_documentaire",
    schedule=None,
    start_date=datetime(2025, 1, 1),
    catchup=False,
    default_args={"retries": 1, "retry_delay": timedelta(minutes=1)},
    tags=["hackathon", "pipeline"],
) as dag:
    t_backend = PythonOperator(task_id="verifier_backend", python_callable=verifier_backend)
    t_valid = PythonOperator(task_id="verifier_validations", python_callable=verifier_validations)
    t_data = PythonOperator(task_id="valider_donnees", python_callable=valider_donnees)
    t_coherence = PythonOperator(task_id="verifier_coherence", python_callable=verifier_coherence)
    t_fin = PythonOperator(task_id="fin_pipeline", python_callable=fin_pipeline)

    [t_backend, t_valid] >> t_data >> t_coherence >> t_fin