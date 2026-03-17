from typing import Optional, Dict, Any

import requests
from fastapi import FastAPI
from pydantic import BaseModel, Field

from validators.siret import is_valid_siret, siret_error_message
from validators.montant import is_valid_montant, montant_error_message


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

