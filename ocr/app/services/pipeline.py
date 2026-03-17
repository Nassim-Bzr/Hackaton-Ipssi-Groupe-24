import json
import os
import uuid

from document_classifier import classify_image, load_classifier
from ner_extractor import extraire_entites
from ocr_engine import extraire_texte
from preprocess import preprocess


MODEL_PATH = os.path.join(os.path.dirname(__file__), "model_classifier.keras")

try:
    CLASSIFIER_MODEL = load_classifier(MODEL_PATH)
except Exception:
    CLASSIFIER_MODEL = None


def traiter_document(chemin_fichier):
    image = preprocess(chemin_fichier)

    if CLASSIFIER_MODEL is not None:
        classification = classify_image(image, CLASSIFIER_MODEL)
        type_from_model = classification["document_type"]
        classification_confidence = classification["classification_confidence"]
    else:
        type_from_model = "inconnu"
        classification_confidence = None

    texte, score_ocr = extraire_texte(image)
    entites = extraire_entites(texte)

    type_from_ner = entites.pop("document_type", "inconnu")
    document_type = type_from_model if type_from_model != "inconnu" else type_from_ner

    nom_fichier = os.path.basename(chemin_fichier)

    return {
        "doc_id": str(uuid.uuid4()),
        "document_type": document_type,
        "classification_confidence": classification_confidence,
        "metadata": {
            "ocr_confidence_score": score_ocr,
            "engine": "PaddleOCR",
            "source_file": nom_fichier,
        },
        "entities": entites,
    }


if __name__ == "__main__":
    fichier_test = "exemple_facture.pdf"
    print(f"Traitement du fichier : {fichier_test}")

    try:
        resultat = traiter_document(fichier_test)
        print(json.dumps(resultat, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Erreur lors du traitement : {e}")
