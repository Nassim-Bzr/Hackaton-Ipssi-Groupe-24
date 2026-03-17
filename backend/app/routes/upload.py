import os
import shutil

import requests
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.services.pipeline import traiter_document
from app.services.mongo_service import save_document
from config.settings import UPLOAD_DIR, VALIDATION_SERVICE_URL

router = APIRouter()

""" Route utilisé pour analyser le document et pré-remplir les formulaires """
@router.post("/upload", status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    id: str = Form(...),
    nom: str = Form(...),
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Seuls les fichiers PDF sont acceptés.")

    # Sauvegarde temporaire du fichier
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    tmp_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(tmp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        # OCR + extraction des entités
        resultat = traiter_document(tmp_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur OCR : {e}")
    finally:
        os.remove(tmp_path)

    entities = resultat.get("entities", {})

    # Appel au service de validation
    siret = entities.get("siret") or ""
    montant = entities.get("montant_ttc") or 0.0
    is_valid = False
    validation_details = {}

    try:
        resp = requests.post(
            VALIDATION_SERVICE_URL,
            json={"siret": siret, "montant": montant},
            timeout=5,
        )
        if resp.ok:
            data = resp.json()
            is_valid = data.get("isValid", False)
            validation_details = data.get("details", {})
    except requests.RequestException:
        pass  # La validation est best-effort

    return {
        "doc_id": resultat["doc_id"],
        "id": id,
        "nom": nom,
        "document_type": resultat["document_type"],
        "metadata": resultat["metadata"],
        "entities": entities,
        "is_valid": is_valid,
        "validation_details": validation_details,
        "confidence_score": resultat["metadata"]["confidence_score"],
    }