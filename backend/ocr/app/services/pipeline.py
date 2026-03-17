# pipeline.py pour  orchestrer toutes les étapes dans l'ordre et produire le JSON final

import uuid                          
import json                          
import os                           



from preprocess import preprocess           
from ocr_engine import extraire_texte       
from ner_extractor import extraire_entites   


def traiter_document(chemin_fichier):
    # Fonction principale qui reçoit un fichier et retourne le JSON final

    image = preprocess(chemin_fichier)               
    texte, score = extraire_texte(image)             
    entites = extraire_entites(texte)                

    nom_fichier = os.path.basename(chemin_fichier)   
    type_doc = entites.pop("document_type", "inconnu")  

    resultat = {
        "doc_id":        str(uuid.uuid4()),          
        "document_type": type_doc,                   
        "metadata": {
            "confidence_score": score,               
            "engine":           "PaddleOCR",        
            "source_file":      nom_fichier,         
        },
        "entities": entites,                         # dictionnaire des champs extraits 
    }

    return resultat  # Retourne le dictionnaire Python (pas encore du JSON )







# --- EXEMPLE DE TEST (s'exécute uniquement si on lance ce fichier directement) ---
if __name__ == "__main__":
    # Simule le traitement d'un fichier fictif pour tester le pipeline
    fichier_test = "exemple_facture.pdf"             # Nom du fichier fictif à tester

    print(f"Traitement du fichier : {fichier_test}")

    try:
        resultat = traiter_document(fichier_test)              # Lance le pipeline complet
        print(json.dumps(resultat, indent=2, ensure_ascii=False))  # Affiche le JSON formaté
    except Exception as e:
        print(f"Erreur lors du traitement : {e}")              # Affiche l'erreur si ça plante
