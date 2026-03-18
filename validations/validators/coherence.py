# coherence.py - Vérification de cohérence entre plusieurs documents

from datetime import datetime
from typing import Optional


def verifier_siret_coherent(siret_facture: Optional[str], siret_attestation: Optional[str]) -> dict:
    """Vérifie que le SIRET de la facture correspond à celui de l'attestation."""
    if not siret_facture or not siret_attestation:
        return {
            "valide": True,
            "message": "SIRET non disponible dans un ou plusieurs documents — vérification ignorée"
        }
    if siret_facture != siret_attestation:
        return {
            "valide": False,
            "message": f"Incohérence SIRET : facture ({siret_facture}) ≠ attestation ({siret_attestation})"
        }
    return {"valide": True, "message": "SIRET cohérent entre les documents"}


def verifier_date_expiration(date_str: Optional[str]) -> dict:
    """Vérifie que la date d'expiration de l'attestation n'est pas dépassée."""
    if not date_str:
        return {
            "valide": True,
            "message": "Date d'expiration non trouvée — vérification ignorée"
        }
    # Formats acceptés : JJ/MM/AAAA ou AAAA-MM-JJ
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            date_expiration = datetime.strptime(date_str.strip(), fmt)
            if date_expiration < datetime.now():
                return {
                    "valide": False,
                    "message": f"Attestation expirée depuis le {date_str}"
                }
            return {"valide": True, "message": f"Attestation valide jusqu'au {date_str}"}
        except ValueError:
            continue
    return {
        "valide": True,
        "message": f"Format de date non reconnu ({date_str}) — vérification ignorée"
    }


def verifier_tva_coherente(montant_ht: Optional[float], tva: Optional[float], montant_ttc: Optional[float]) -> dict:
    """Vérifie que HT + TVA ≈ TTC (tolérance de 0.05€ pour les arrondis)."""
    if montant_ht is None or tva is None or montant_ttc is None:
        return {
            "valide": True,
            "message": "Montants incomplets — vérification TVA ignorée"
        }
    ttc_calcule = round(montant_ht + tva, 2)
    ecart = abs(ttc_calcule - montant_ttc)
    if ecart > 0.05:
        return {
            "valide": False,
            "message": f"TVA incohérente : {montant_ht} HT + {tva} TVA = {ttc_calcule} ≠ {montant_ttc} TTC (écart: {round(ecart, 2)}€)"
        }
    return {"valide": True, "message": f"TVA cohérente : {montant_ht} + {tva} = {montant_ttc}"}
