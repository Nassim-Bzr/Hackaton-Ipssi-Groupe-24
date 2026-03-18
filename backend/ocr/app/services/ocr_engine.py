from __future__ import annotations

from typing import Optional

import cv2  # type: ignore[import-not-found]
import numpy as np  # type: ignore[import-not-found]
from paddleocr import PaddleOCR  # type: ignore[import-not-found]
from pdf2image import convert_from_path  # type: ignore[import-not-found]

_ocr: Optional[PaddleOCR] = None


def _get_ocr() -> PaddleOCR:
    global _ocr
    if _ocr is None:
        # Chargement coûteux: on garde une instance globale.
        # Réglages "léger": moins de post-traitements pour limiter RAM/CPU.
        _ocr = PaddleOCR(use_textline_orientation=False, lang="fr")
    return _ocr


def extraire_texte(chemin_pdf: str) -> tuple[str, float]:
    """
    Extrait le texte d'un PDF via OCR (PaddleOCR).
    Retourne (texte_complet, score_confiance) où le score est la moyenne des
    confiances des lignes reconnues (0.0 si rien n'est détecté).
    """
    ocr = _get_ocr()

    textes: list[str] = []
    scores: list[float] = []

    # DPI plus bas pour éviter les OOM sur des PDF lourds.
    pages = convert_from_path(chemin_pdf, dpi=120)

    for page_img in pages:
        # Réduction de taille (garde le ratio) pour limiter l'empreinte mémoire.
        max_w = 1600
        if page_img.width > max_w:
            new_h = int(page_img.height * (max_w / page_img.width))
            page_img = page_img.resize((max_w, new_h))

        rgb = np.array(page_img)
        bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

        resultat = (
            ocr.predict(
                bgr,
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,
            )
            or []
        )

        # PaddleOCR v3 renvoie une liste de dicts contenant `rec_texts` / `rec_scores`.
        for page_res in resultat:
            if isinstance(page_res, dict):
                rec_texts = page_res.get("rec_texts") or []
                rec_scores = page_res.get("rec_scores") or []
                for t in rec_texts:
                    if t:
                        textes.append(str(t))
                for s in rec_scores:
                    try:
                        scores.append(float(s))
                    except (TypeError, ValueError):
                        pass
                continue

            # Compat ancien format (liste de tuples/structures).
            if isinstance(page_res, (list, tuple)) and len(page_res) >= 2:
                maybe = page_res[1]
                if isinstance(maybe, (list, tuple)) and len(maybe) >= 2:
                    texte, score = maybe[0], maybe[1]
                    if texte:
                        textes.append(str(texte))
                        try:
                            scores.append(float(score))
                        except (TypeError, ValueError):
                            pass

    texte_complet = "\n".join(textes).strip()
    score_global = float(np.mean(scores)) if scores else 0.0

    return texte_complet, score_global
