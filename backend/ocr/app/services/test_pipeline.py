# on va  tester ner_extractor.py avec un texte fictif, sans avoir besoin d'un vrai PDF

import json                                    
from ner_extractor import extraire_entites     # On importe uniquement la fonction à teser 


# TEXTE FICTIF qui simule ce que l'OCR aurait lu sur une vraie facture
texte_facture = """
FACTURE N°
FAC-2026-0001
Date : 15/03/2026
Fournisseur : ACME Corp
SIRET : 625 098 876 00018
FACTURÉ À
Client : Pichon
SIRET : 501 357 107 00025
IBAN : FR76 1234 5678 9012 3456 7890 123

Montant HT : 1000,00
TVA : 200,00
Montant TTC : 1200,00
Échéance : 23/03/2026
Mode de règlement : Carte bancaire
"""

texte_devis = """
DEVIS N° D-2026-007
Date : 01/03/2026
Fournisseur : BuildPro SARL
SIRET : 98765432109876
Montant HT : 5000,00
TVA : 1000,00
Montant TTC : 6000,00
Valable jusqu : 31/03/2026
"""

texte_fiche_paie = """
BULLETIN DE SALAIRE
Période : mars 2026
Employeur : Société Exemple SAS
SIRET : 11122233344455
Salaire brut : 3000,00
Salaire net : 2400,00
"""

texte_rib = """
RELEVÉ BANCAIRE
Titulaire : Jean Dupont
IBAN : FR76 3000 4000 0100 0000 0000 000
"""

texte_avis_imposition = """
AVIS D'IMPOSITION 2025
Numéro fiscal : 1234567890123
Revenu fiscal : 35000,00
Montant impôt : 2500,00
Date : 01/09/2025
"""

# LISTE DE TOUS LES TEXTES À TESTER 
textes = [
    ("Facture",          texte_facture),
    ("Devis",            texte_devis),
    ("Fiche de paie",    texte_fiche_paie),
    ("RIB",              texte_rib),
    ("Avis imposition",  texte_avis_imposition),
]



#  LANCEMENT DES TESTS 
for nom, texte in textes:                                     # Parcourt chaque texte fictif
    print(f"\n{'='*50}")                                      # Séparateur visuel
    print(f"TEST : {nom}")                                    # Affiche le nom du test
    print('='*50)
    resultat = extraire_entites(texte)                        # Appelle la fonction à tester
    print(json.dumps(resultat, indent=2, ensure_ascii=False)) # Affiche le JSON produit

    # Validation minimale : le texte fictif "Devis" doit contenir un numéro de devis détecté
    if nom == "Devis":
        assert (
            resultat.get("numero_devis") == "D-2026-007"
        ), f'numero_devis inattendu: {resultat.get("numero_devis")}'
