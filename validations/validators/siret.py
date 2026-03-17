"""Validation du SIRET."""

from typing import Optional


def is_valid_siret(siret: str) -> bool:
    """Vérifie qu'un SIRET est composé de 14 chiffres.

    Règles simples :
    - non vide
    - uniquement des chiffres
    - longueur exacte de 14 caractères
    """
    if not isinstance(siret, str):
        return False
    siret_str = siret.strip()
    return len(siret_str) == 14 and siret_str.isdigit()


def siret_error_message(siret: Optional[str]) -> Optional[str]:
    """Retourne un message d'erreur en français si le SIRET est invalide."""
    if siret is None:
        return "Le SIRET est requis."
    siret_str = str(siret).strip()
    if not siret_str:
        return "Le SIRET ne doit pas être vide."
    if not siret_str.isdigit():
        return "Le SIRET doit contenir uniquement des chiffres."
    if len(siret_str) != 14:
        return "Le SIRET doit contenir exactement 14 chiffres."
    return None

