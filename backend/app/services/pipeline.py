import uuid
import os

from ocr.app.services.ocr_engine import extraire_texte
from ocr.app.services.ner_extractor import extraire_entites


def traiter_document(chemin_fichier: str) -> dict:
    """Reçoit un chemin de fichier PDF et retourne le dict d'extraction complet."""
    texte, score = extraire_texte(chemin_fichier)
    entites = extraire_entites(texte)

    nom_fichier = os.path.basename(chemin_fichier)
    type_doc = entites.pop("document_type", "inconnu")

    return {
        "doc_id": str(uuid.uuid4()),
        "document_type": type_doc,
        "metadata": {
            "confidence_score": score,
            "engine": "pdfplumber",
            "source_file": nom_fichier,
        },
        "entities": entites,
    }
