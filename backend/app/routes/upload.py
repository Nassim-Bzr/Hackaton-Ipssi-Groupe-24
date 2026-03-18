import os
import uuid

import requests
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.services.data_lake_service import (
    save_clean_text,
    save_curated_record,
    save_raw_document,
)
from app.services.pipeline import traiter_document
from config.settings import UPLOAD_DIR, VALIDATION_SERVICE_URL

router = APIRouter()


""" Route utilisée pour sauvegarder un formulaire validé par l'utilisateur en base """
@router.post("/upload-to-bdd", status_code=201)
async def upload_to_bdd(
    file: UploadFile = File(...),
    id: str = Form(...),
    nom: str = Form(...),
    siret: str = Form(None),
    siren: str = Form(None),
    date_emission: str = Form(None),
    date_echeance: str = Form(None),
    date_expiration: str = Form(None),
    numero_facture: str = Form(None),
    mode_paiement: str = Form(None),
    montant_ht: float = Form(None),
    montant_ttc: float = Form(None),
    tva: float = Form(None),
    nom_fournisseur: str = Form(None),
    iban: str = Form(None),
    siret_client: str = Form(None),
    siret_fournisseur: str = Form(None),
):
    doc_id = str(uuid.uuid4())
    file_bytes = await file.read()

    entities = {k: v for k, v in {
        "siret": siret,
        "siren": siren,
        "date_emission": date_emission,
        "date_echeance": date_echeance,
        "date_expiration": date_expiration,
        "numero_facture": numero_facture,
        "mode_paiement": mode_paiement,
        "montant_ht": montant_ht,
        "montant_ttc": montant_ttc,
        "tva": tva,
        "nom_fournisseur": nom_fournisseur,
        "iban": iban,
        "siret_client": siret_client,
        "siret_fournisseur": siret_fournisseur,
    }.items() if v is not None}

    from app.services.mongo_service import save_document
    save_document({
        "doc_id": doc_id,
        "id": id,
        "nom": nom,
        "filename": file.filename,
        "entities": entities,
    })

    return {
        "doc_id": doc_id,
        "id": id,
        "nom": nom,
        "entities": entities,
        "message": "Document sauvegardé avec succès.",
    }

""" Route utilisé pour analyser le document et pré-remplir les formulaires """
@router.post("/upload", status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    id: str = Form(...),
    nom: str = Form(...),
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Seuls les fichiers PDF sont acceptés.")

    doc_id = str(uuid.uuid4())
    file_bytes = await file.read()
    raw_uri = save_raw_document(file_bytes, file.filename, doc_id)

    # Sauvegarde temporaire du fichier
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    tmp_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(tmp_path, "wb") as f:
        f.write(file_bytes)

    try:
        # OCR + extraction des entités
        resultat = traiter_document(tmp_path, doc_id=doc_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur OCR : {e}")
    finally:
        os.remove(tmp_path)

    entities = resultat.get("entities", {})
    prefill = resultat.get("prefill", {})

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

    clean_uri = save_clean_text(
        doc_id=doc_id,
        source_filename=file.filename,
        ocr_text=resultat.get("ocr_text", ""),
        metadata={
            "confidence_score": resultat["metadata"].get("confidence_score"),
            "document_type": resultat.get("document_type"),
            "engine": resultat["metadata"].get("engine"),
        },
    )

    curated_payload = {
        "doc_id": doc_id,
        "id": id,
        "nom": nom,
        "document_type": resultat["document_type"],
        "entities": entities,
        "is_valid": is_valid,
        "validation_details": validation_details,
        "metadata": {
            **resultat["metadata"],
            "raw_uri": raw_uri,
            "clean_uri": clean_uri,
        },
    }
    curated_uri = save_curated_record(doc_id=doc_id, curated_payload=curated_payload)

    return {
        "doc_id": resultat["doc_id"],
        "id": id,
        "nom": nom,
        "document_type": resultat["document_type"],
        "metadata": resultat["metadata"],
        "entities": entities,
        "prefill": prefill,
        "is_valid": is_valid,
        "validation_details": validation_details,
        "confidence_score": resultat["metadata"]["confidence_score"],
        "data_lake": {
            "raw_uri": raw_uri,
            "clean_uri": clean_uri,
            "curated_uri": curated_uri,
        },
    }