# ocr_engine.py fichier qui va permettre de lire le texte d'une image avec PaddleOCR et retourner le texte + score de confiance

from paddleocr import PaddleOCR  


# création du  moteur OCR une seule fois au démarrage pour éviter de le recharger à chaque appel
ocr = PaddleOCR(use_angle_cls=True, lang="fr")  


def extraire_texte(image):
    # Lit le texte présent dans l'image et retourne le texte brut + score de confiance
    resultats = ocr.predict(image)       

    lignes_texte = []    
    scores = []          

    for bloc in resultats:                       
        for ligne in bloc.get("rec_texts", []):   
            lignes_texte.append(ligne)            
        for score in bloc.get("rec_scores", []):  
            scores.append(score)                  

    texte_complet = "\n".join(lignes_texte)             
    score_moyen = sum(scores) / len(scores) if scores else 0.0  

    return texte_complet, round(score_moyen, 2)  
