from typing import Optional, Dict, Any, List

import requests
from fastapi import FastAPI
from pydantic import BaseModel, Field

from validators.siret import is_valid_siret, siret_error_message
from validators.montant import is_valid_montant, montant_error_message
from validators.coherence import verifier_siret_coherent, verifier_date_expiration, verifier_tva_coherente


class ValidationInput(BaseModel):
    """Modèle des données reçues pour validation."""

    siret: str = Field(..., description="Numéro SIRET à 14 chiffres")
    montant: float = Field(..., description="Montant à valider (>= 0)")


class FieldValidationResult(BaseModel):
    """Résultat détaillé de la validation d'un champ."""

    field: str
    valid: bool
    message: Optional[str] = None


class ValidationResponse(BaseModel):
    """Réponse renvoyée par l'API de validation."""

    isValid: bool
    details: Dict[str, FieldValidationResult]
    callbackSent: bool


app = FastAPI(title="Validations service", version="1.0.0")


# ─── Modèles pour la vérification inter-documents ───────────────────────────

class DocumentCoherence(BaseModel):
    """Un document avec ses champs extraits par l'OCR."""
    document_type: str = Field(..., description="Type : facture, attestation, devis...")
    siret: Optional[str] = None
    montant_ht: Optional[float] = None
    tva: Optional[float] = None
    montant_ttc: Optional[float] = None
    date_echeance: Optional[str] = None   # date d'expiration pour attestation URSSAF


class CoherenceInput(BaseModel):
    """Liste de documents à vérifier ensemble."""
    documents: List[DocumentCoherence]


class AnomalieResult(BaseModel):
    """Résultat d'une vérification."""
    verification: str
    valide: bool
    message: str


class CoherenceResponse(BaseModel):
    """Réponse globale de la vérification inter-documents."""
    coherent: bool
    anomalies: List[AnomalieResult]


@app.post("/data-validation", response_model=ValidationResponse)
def data_validation(payload: ValidationInput) -> ValidationResponse:
    """Réceptionne les données à valider et notifie un autre service avec le résultat global."""
    siret_ok = is_valid_siret(payload.siret)
    montant_ok = is_valid_montant(payload.montant)

    is_valid_global = siret_ok and montant_ok

    details = {
        "siret": FieldValidationResult(
            field="siret",
            valid=siret_ok,
            message=None if siret_ok else siret_error_message(payload.siret),
        ),
        "montant": FieldValidationResult(
            field="montant",
            valid=montant_ok,
            message=None if montant_ok else montant_error_message(payload.montant),
        ),
    }

    callback_sent = False
    try:
        # Envoie d'une requête HTTP au service externe pour lui communiquer le résultat global.
        response = requests.post(
            "http://localhost:3000",
            json={"isValid": is_valid_global},
            timeout=5,
        )
        callback_sent = response.ok
    except requests.RequestException:
        callback_sent = False

    return ValidationResponse(
        isValid=is_valid_global,
        details=details,
        callbackSent=callback_sent,
    )


@app.post("/coherence-check", response_model=CoherenceResponse)
def coherence_check(payload: CoherenceInput) -> CoherenceResponse:
    """Vérifie la cohérence entre plusieurs documents (facture, attestation, devis...)."""
    anomalies = []

    # Récupère les données par type de document
    facture = next((d for d in payload.documents if d.document_type == "facture"), None)
    attestation = next((d for d in payload.documents if "attestation" in d.document_type), None)

    # 1. Vérification SIRET cohérent entre facture et attestation
    if facture and attestation:
        resultat = verifier_siret_coherent(facture.siret, attestation.siret)
        anomalies.append(AnomalieResult(
            verification="siret_inter_documents",
            valide=resultat["valide"],
            message=resultat["message"]
        ))

    # 2. Vérification date expiration attestation URSSAF
    if attestation:
        resultat = verifier_date_expiration(attestation.date_echeance)
        anomalies.append(AnomalieResult(
            verification="date_expiration_attestation",
            valide=resultat["valide"],
            message=resultat["message"]
        ))

    # 3. Vérification cohérence TVA sur la facture
    if facture:
        resultat = verifier_tva_coherente(facture.montant_ht, facture.tva, facture.montant_ttc)
        anomalies.append(AnomalieResult(
            verification="tva_coherente",
            valide=resultat["valide"],
            message=resultat["message"]
        ))

    coherent = all(a.valide for a in anomalies)
    return CoherenceResponse(coherent=coherent, anomalies=anomalies)

