"""
generate_silver.py

Transforme les fichiers bronze (PDF / images) en données silver (JSON structuré).

Le script parcourt data/bronze/, applique le pipeline complet
(classification Keras + OCR + extraction d'entités) et écrit les résultats
dans data/silver/ sous forme de fichiers JSON.

Usage :
    python generate_silver.py
    python generate_silver.py --bronze chemin/bronze --silver chemin/silver
"""

import argparse
import importlib.util
import json
import os
import sys

# -------------------------------------------------------------------
# Rend les modules du dossier services/ importables depuis data/
# -------------------------------------------------------------------
SERVICES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "services")
sys.path.insert(0, SERVICES_DIR)


def _load_traiter_document():
    pipeline_path = os.path.join(SERVICES_DIR, "pipeline.py")
    spec = importlib.util.spec_from_file_location("pipeline", pipeline_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Impossible de charger pipeline.py depuis {pipeline_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.traiter_document


traiter_document = _load_traiter_document()

# -------------------------------------------------------------------
# Constantes
# -------------------------------------------------------------------
SUPPORTED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp"}

DEFAULT_BRONZE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bronze")
DEFAULT_SILVER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "silver")


# -------------------------------------------------------------------
# Logique principale
# -------------------------------------------------------------------

def generate_silver(
    bronze_dir: str = DEFAULT_BRONZE,
    silver_dir: str = DEFAULT_SILVER,
) -> None:
    """
    Parcourt bronze_dir, traite chaque document via le pipeline complet
    et écrit les données silver (JSON) dans silver_dir.

    Flux par fichier :
        bronze (PDF/image)
        → preprocess  (image propre)
        → classify_image (Keras : facture | devis)   ← EN PREMIER
        → extraire_texte (PaddleOCR)
        → extraire_entites (regex NER)
        → silver JSON sauvegardé dans silver_dir/

    Args:
        bronze_dir : dossier contenant les fichiers bruts
        silver_dir : dossier de sortie pour les JSON silver
    """
    if not os.path.isdir(bronze_dir):
        print(f"[ERREUR] Dossier bronze introuvable : {bronze_dir}")
        return

    os.makedirs(silver_dir, exist_ok=True)

    fichiers = sorted(
        f for f in os.listdir(bronze_dir)
        if os.path.splitext(f)[1].lower() in SUPPORTED_EXTENSIONS
    )

    if not fichiers:
        print(f"Aucun fichier compatible trouvé dans : {bronze_dir}")
        print(f"Extensions acceptées : {', '.join(sorted(SUPPORTED_EXTENSIONS))}")
        return

    total = len(fichiers)
    print(f"Traitement de {total} fichier(s) bronze...\n")

    success, errors = 0, 0

    for fichier in fichiers:
        chemin_bronze = os.path.join(bronze_dir, fichier)
        print(f"  [{success + errors + 1}/{total}] {fichier}")

        try:
            silver_data = traiter_document(chemin_bronze)

            nom_sortie = os.path.splitext(fichier)[0] + "_silver.json"
            chemin_silver = os.path.join(silver_dir, nom_sortie)

            with open(chemin_silver, "w", encoding="utf-8") as f:
                json.dump(silver_data, f, ensure_ascii=False, indent=2)

            conf = silver_data.get("classification_confidence")
            conf_str = f"{conf:.4f}" if conf is not None else "N/A (modèle absent)"
            print(
                f"  → Silver : {nom_sortie}  "
                f"[type={silver_data['document_type']}, confiance={conf_str}]"
            )
            success += 1

        except Exception as exc:
            print(f"  [ERREUR] {fichier} : {exc}")
            errors += 1

    print(f"\nRésultat : {success} silver générés, {errors} erreur(s).")


# -------------------------------------------------------------------
# Point d'entrée CLI
# -------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Génération des données silver depuis le dossier bronze"
    )
    parser.add_argument(
        "--bronze",
        default=DEFAULT_BRONZE,
        help="Dossier des fichiers bronze (défaut : data/bronze/)",
    )
    parser.add_argument(
        "--silver",
        default=DEFAULT_SILVER,
        help="Dossier de sortie silver (défaut : data/silver/)",
    )
    args = parser.parse_args()

    generate_silver(bronze_dir=args.bronze, silver_dir=args.silver)
