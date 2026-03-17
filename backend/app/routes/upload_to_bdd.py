import os
import shutil

import requests
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.services.pipeline import traiter_document
from app.services.mongo_service import save_document
from config.settings import UPLOAD_DIR, VALIDATION_SERVICE_URL

router = APIRouter()

""" Route utilisé pour enregistré le document en base de données """

@router.post("/upload-to-bdd", status_code=201)
async def upload_document_to_bdd(
    file: UploadFile = File(...),
    id: str = Form(...),
    nom: str = Form(...),
    siret: str | None = Form(default=None),
    siren: str | None = Form(default=None),
    date_emission: str | None = Form(default=None),
    date_expiration: str | None = Form(default=None),
    montant_ht: str | None = Form(default=None),
    montant_ttc: str | None = Form(default=None),
    tva: str | None = Form(default=None),
    nom_fournisseur: str | None = Form(default=None),
    iban: str | None = Form(default=None),
):
    """
    Effectue l'analyse complète puis enregistre le document en base.
    Utilisé lorsque l'utilisateur valide explicitement l'envoi (clic sur un bouton).
    """
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

    entities = resultat.get("entities", {}) or {}

    # Champs simples (sans conversion)
    champs_simples = [
        ("siret", siret),
        ("siren", siren),
        ("date_emission", date_emission),
        ("date_expiration", date_expiration),
        ("nom_fournisseur", nom_fournisseur),
        ("iban", iban),
    ]
    for cle, valeur in champs_simples:
        if valeur:
            entities[cle] = valeur

    # Champs numériques (avec conversion float)
    champs_numeriques = [
        ("montant_ht", montant_ht),
        ("montant_ttc", montant_ttc),
        ("tva", tva),
    ]
    for cle, valeur in champs_numeriques:
        if valeur:
            try:
                entities[cle] = float(valeur)
            except ValueError:
                pass

    # Appel au service de validation
    siret_for_validation = entities.get("siret") or ""
    montant_for_validation = entities.get("montant_ttc") or 0.0
    is_valid = False
    validation_details = {}

    try:
        resp = requests.post(
            VALIDATION_SERVICE_URL,
            json={"siret": siret_for_validation, "montant": montant_for_validation},
            timeout=5,
        )
        if resp.ok:
            data = resp.json()
            is_valid = data.get("isValid", False)
            validation_details = data.get("details", {})
    except requests.RequestException:
        pass  # La validation est best-effort

    document = {
        "doc_id": resultat["doc_id"],
        "id": id,
        "nom": nom,
        "document_type": resultat["document_type"],
        "metadata": resultat["metadata"],
        "entities": entities,
        "is_valid": is_valid,
        "validation_details": validation_details,
    }

    save_document(document)

    return {
        "doc_id": document["doc_id"],
        "document_type": document["document_type"],
        "is_valid": is_valid,
        "confidence_score": resultat["metadata"]["confidence_score"],
        "entities": entities,
    }

