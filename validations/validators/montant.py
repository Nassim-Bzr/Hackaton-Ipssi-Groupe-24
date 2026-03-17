"""Validation du montant."""

from typing import Optional, Union

Number = Union[int, float]


def is_valid_montant(montant: Number) -> bool:
    """Vérifie qu'un montant est numérique et >= 0."""
    try:
        value = float(montant)
    except (TypeError, ValueError):
        return False
    return value >= 0


def montant_error_message(montant: Optional[Number]) -> Optional[str]:
    """Retourne un message d'erreur en français si le montant est invalide."""
    if montant is None:
        return "Le montant est requis."
    try:
        value = float(montant)
    except (TypeError, ValueError):
        return "Le montant doit être un nombre."
    if value < 0:
        return "Le montant doit être supérieur ou égal à 0."
    return None

