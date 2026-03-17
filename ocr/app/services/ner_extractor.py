# ner_extractor.py fichier qui  extraire les informations clés d'un texte brut avec des expressions régulières (RegEx)

import re  # Bibliothèque pour les expressions régulières


def extraire_siret(texte):
    # Cherche un SIRET : exactement 14 chiffres consécutifs dans le texte
    match = re.search(r'\b\d{14}\b', texte)
    return match.group() if match else None


def extraire_siren(texte):
    # Cherche un SIREN : 9 chiffres NON suivis d'autres chiffres (évite de confondre avec un SIRET)
    match = re.search(r'\b\d{9}\b(?!\d)', texte)
    return match.group() if match else None


def extraire_iban(texte):
    # Cherche un IBAN français : commence par FR suivi de 25 chiffres/lettres
    match = re.search(r'\bFR\d{2}[\s]?(\d{4}[\s]?){5}\d{3}\b', texte, re.IGNORECASE)
    if match:
        return match.group().replace(" ", "")  
    return None


def extraire_montant(texte, mot_cle):
    # Cherche un montant associé à un mot clé (ex: "HT", "TTC", "TVA", "brut", "net")
    # [^\S\n]* = espaces mais PAS de saut de ligne (évite de prendre le montant de la ligne d'avant)
    # [^\d\n]* = tout sauf chiffre et saut de ligne (permet de passer " : " entre le mot clé et le nombre)
    pattern = rf'(\d[\d\s]*[.,]\d{{2}})[^\S\n]*{mot_cle}|{mot_cle}[^\d\n]*(\d[\d\s]*[.,]\d{{2}})'
    match = re.search(pattern, texte, re.IGNORECASE)
    if match:
        valeur = match.group(1) or match.group(2)           # Prend le groupe qui a matché
        valeur = valeur.replace(" ", "").replace(",", ".")  # Nettoie le nombre
        return float(valeur)                                # Convertit en décimal
    return None


def extraire_date(texte, mots_cles):
    # Cherche une date au format JJ/MM/AAAA ou AAAA-MM-JJ près d'un mot clé
    for mot in mots_cles:
        pattern = rf'{mot}.*?(\d{{2}}/\d{{2}}/\d{{4}}|\d{{4}}-\d{{2}}-\d{{2}})'
        match = re.search(pattern, texte, re.IGNORECASE)
        if match:
            return match.group(1)  
    return None


def extraire_fournisseur(texte):
    # Cherche la ligne qui suit le mot "Fournisseur", "Émetteur", "Employeur" ou "Titulaire"
    match = re.search(r'(?:Fournisseur|Émetteur|Employeur|Titulaire)\s*[:\-]?\s*(.+)', texte, re.IGNORECASE)
    return match.group(1).strip() if match else None


def extraire_numero_fiscal(texte):
    # Cherche le numéro fiscal : 13 chiffres précédés de "fiscal" ou "SPI"
    match = re.search(r'(?:fiscal|SPI|numéro)[^\d]*(\d{13})', texte, re.IGNORECASE)
    return match.group(1) if match else None


def extraire_numero_allocataire(texte):
    # Cherche le numéro allocataire Pôle Emploi : 7 à 10 chiffres après "allocataire"
    match = re.search(r'(?:allocataire|identifiant)[^\d]*(\d{7,10})', texte, re.IGNORECASE)
    return match.group(1) if match else None


def extraire_periode(texte):
    # Cherche une période de type "mois/année" (comme "mars 2026" ou "03/2026")
    # On cherche directement après le séparateur ": " pour éviter de capturer un mot partiel
    match = re.search(r'(?:période|mois)\s*[:\-]?\s*([a-zA-Zéèêàù]+\s\d{4}|\d{2}/\d{4})', texte, re.IGNORECASE)
    return match.group(1) if match else None


def extraire_type_document(texte):
    # Détermine le type du document selon les mots présents dans le texte
    types = [
        "fiche de paie", "bulletin de salaire",  
        "facture", "devis", "attestation",
        "kbis", "rib", "relevé bancaire",
        "avis d'imposition", "france travail", "pôle emploi",
    ]
    for type_doc in types:                            
        if re.search(type_doc, texte, re.IGNORECASE):  
            return type_doc                           
    return "inconnu"                                   











def extraire_entites(texte):
    # Fonction principale : retourne des champs différents selon le type de document



    type_doc = extraire_type_document(texte)  # Détermine d'abord le type du document

    # Champs communs à tous les documents
    base = {
        "document_type": type_doc,
        "siret":         extraire_siret(texte),
        "siren":         extraire_siren(texte),
        "date_emission": extraire_date(texte, ["date", "émis", "emission", "le"]),
    }

    if type_doc == "facture":                          # Champs spécifiques à une facture
        base.update({
            "nom_fournisseur": extraire_fournisseur(texte),
            "montant_ht":      extraire_montant(texte, "HT"),
            "montant_ttc":     extraire_montant(texte, "TTC"),
            "tva":             extraire_montant(texte, "TVA"),
            "iban":            extraire_iban(texte),
        })

    elif type_doc == "devis":                          # Champs spécifiques à un devis
        base.update({
            "nom_fournisseur": extraire_fournisseur(texte),
            "montant_ht":      extraire_montant(texte, "HT"),
            "montant_ttc":     extraire_montant(texte, "TTC"),
            "tva":             extraire_montant(texte, "TVA"),
            "date_expiration": extraire_date(texte, ["expiration", "échéance", "valable jusqu"]),
        })

    elif type_doc in ["rib", "relevé bancaire"]:       # Champs spécifiques à un RIB
        base.update({
            "titulaire": extraire_fournisseur(texte),  
            "iban":      extraire_iban(texte),
        })

    elif type_doc in ["fiche de paie", "bulletin de salaire"]:  # Champs spécifiques à une fiche de paie
        base.update({
            "nom_employeur": extraire_fournisseur(texte),
            "salaire_brut":  extraire_montant(texte, "brut"),
            "salaire_net":   extraire_montant(texte, "net"),
            "periode":       extraire_periode(texte),
        })

    elif type_doc == "avis d'imposition":              # Champs spécifiques à un avis d'imposition
        base.update({
            "numero_fiscal":           extraire_numero_fiscal(texte),
            "revenu_fiscal_reference": extraire_montant(texte, "revenu fiscal"),
            "montant_impot":           extraire_montant(texte, "impôt"),
        })

    elif type_doc in ["france travail", "pôle emploi"]:  # Champs spécifiques à une attestation PE
        base.update({
            "numero_allocataire": extraire_numero_allocataire(texte),
            "montant_allocation": extraire_montant(texte, "allocation"),
            "date_fin":           extraire_date(texte, ["fin", "jusqu", "échéance"]),
        })

    return base  # Retourne le dictionnaire adapté au type de document
