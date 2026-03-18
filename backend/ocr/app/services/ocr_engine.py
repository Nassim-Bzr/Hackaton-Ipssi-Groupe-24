# ocr_engine.py fichier pour lire le texte d'un fichier PDF ou image
# Si le PDF contient du texte embarqué  on utilise  pdfplumber 
# Si c'est un scan ou une image on utilise  PaddleOCR (lecture par intelligence artificielle)

import pdfplumber
# PaddleOCR importé uniquement si nécessaire (évite les erreurs au démarrage Docker)

_ocr = None  # Moteur PaddleOCR chargé uniquement à la première utilisation


def _get_ocr():
    # Charge PaddleOCR une seule fois, uniquement quand on en a besoin
    global _ocr
    if _ocr is None:
        from paddleocr import PaddleOCR
        _ocr = PaddleOCR(use_angle_cls=True, lang="fr")
    return _ocr


def extraire_texte_pdf(chemin_pdf):
    # Lit le texte embarqué dans un PDF numérique avec pdfplumber
    pages_texte = []
    with pdfplumber.open(chemin_pdf) as pdf:
        for page in pdf.pages:
            texte = page.extract_text()
            if texte:
                pages_texte.append(texte)
    return "\n".join(pages_texte).strip()


def extraire_texte_image(image):
    # Lit le texte dans une image ou un scan avec PaddleOCR
    resultats = _get_ocr().predict(image)                      
    lignes_texte = []                                   
    scores = []                                         
    for bloc in resultats:                              
        for ligne in bloc.get("rec_texts", []):         
            lignes_texte.append(ligne)
        for score in bloc.get("rec_scores", []):        
            scores.append(score)
    texte = "\n".join(lignes_texte)                    
    score_moyen = sum(scores) / len(scores) if scores else 0.0  
    return texte, round(score_moyen, 2)                 


def extraire_texte(chemin_fichier):
    # Fonction principale : choisit automatiquement la bonne méthode selon le fichier
    # Retourne toujours (texte, score_confiance)

    if chemin_fichier.endswith(".pdf"):                 
        texte = extraire_texte_pdf(chemin_fichier)      # Essaie pdfplumber d'abord si c'est un pdf

        if texte:                                       # Si du texte a été trouvé dans le PDF
            return texte, 1.0                           # Score 1.0 = texte lu avec certitude

        # Si pdfplumber ne trouve rien alors  c'est un scan, on utilise PaddleOCR
        try:
            from preprocess import preprocess
        except ImportError:
            from ocr.app.services.preprocess import preprocess
        image = preprocess(chemin_fichier)
        return extraire_texte_image(image)

    else:
        try:
            from preprocess import preprocess
        except ImportError:
            from ocr.app.services.preprocess import preprocess
        image = preprocess(chemin_fichier)
        return extraire_texte_image(image)            
