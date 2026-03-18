import uuid
import os

from ocr.app.services.ocr_engine import extraire_texte
from ocr.app.services.ner_extractor import extraire_entites


def construire_prefill(doc_id: str, document_type: str, entities: dict) -> dict:
    """
    Construit un objet stable destiné au frontend pour pré-remplir les formulaires.
    Les valeurs peuvent être None si non détectées.
    """
    return {
        "doc_id": doc_id,
        "document_type": document_type,
        "numero_facture": entities.get("numero_facture"),
        "numero_devis": entities.get("numero_devis"),
        "nom_client": entities.get("nom_client"),
        "nom_entreprise_client": entities.get("nom_entreprise_client"),
        "date_emission": entities.get("date_emission"),
        "date_echeance": entities.get("date_echeance"),
        "adresse_fournisseur_adress": entities.get("adresse_fournisseur_adress"),
        "adresse_fournisseur_zip": entities.get("adresse_fournisseur_zip"),
        "adresse_fournisseur_city": entities.get("adresse_fournisseur_city"),
        "adresse_client_adress": entities.get("adresse_client_adress"),
        "adresse_client_zip": entities.get("adresse_client_zip"),
        "adresse_client_city": entities.get("adresse_client_city"),
        "montant_ht": entities.get("montant_ht"),
        "tva": entities.get("tva"),
        "montant_ttc": entities.get("montant_ttc"),
        "iban": entities.get("iban"),
        "mode_paiement": entities.get("mode_paiement"),
        "siret_fournisseur": entities.get("siret_fournisseur"),
        "siret_client": entities.get("siret_client"),
        "sirets": entities.get("sirets", []),
    }


def traiter_document(chemin_fichier: str, doc_id: str | None = None) -> dict:
    """Reçoit un chemin de fichier PDF et retourne le dict d'extraction complet."""
    texte, score = extraire_texte(chemin_fichier)
    entites = extraire_entites(texte)

    nom_fichier = os.path.basename(chemin_fichier)
    type_doc = entites.pop("document_type", "inconnu")
    resolved_doc_id = doc_id or str(uuid.uuid4())

    return {
        "doc_id": resolved_doc_id,
        "document_type": type_doc,
        "ocr_text": texte,
        "metadata": {
            "confidence_score": score,
            "engine": "pdfplumber",
            "source_file": nom_fichier,
        },
        "entities": entites,
        "prefill": construire_prefill(resolved_doc_id, type_doc, entites),
    }
