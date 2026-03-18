# ner_extractor.py fichier qui  extraire les informations clés d'un texte brut avec des expressions régulières (RegEx)

import re  # Bibliothèque pour les expressions régulières


def _normaliser_siret(valeur: str) -> str:
    return re.sub(r"\D", "", valeur or "")


def extraire_tous_les_siret(texte: str) -> list[str]:
    
    #Retourne tous les SIRET trouvés dans le texte en acceptant les espaces.
    
    if not texte:
        return []
    candidates = re.findall(r"\b\d{3}[\s.]?\d{3}[\s.]?\d{3}[\s.]?\d{5}\b", texte)
    sirets: list[str] = []
    seen = set()
    for c in candidates:
        s = _normaliser_siret(c)
        if len(s) == 14 and s not in seen:
            sirets.append(s)
            seen.add(s)
    return sirets


def extraire_siret(texte):
    # Cherche le premier SIRET 
    sirets = extraire_tous_les_siret(texte)
    return sirets[0] if sirets else None


def extraire_siren(texte):
    # Cherche un SIREN : 9 chiffres NON suivis d'autres chiffres pour eviter de le confondre avec un SIRET
    match = re.search(r'\b\d{9}\b(?!\d)', texte)
    return match.group() if match else None


def extraire_iban(texte):
    # Cherche un IBAN français  FR+25caracteres
    match = re.search(r'\bFR\d{2}[\s]?(\d{4}[\s]?){5}\d{3}\b', texte, re.IGNORECASE)
    if match:
        return match.group().replace(" ", "")  
    return None


def extraire_montant(texte, mot_cle):
    # Cherche un montant associé aux mots clés : "HT", "TTC", "TVA", "brut", "net"
    # [^\S\n]* = espaces mais PAS saut de ligne → évite que "1000,00\nTVA" matche faussement
    pattern = rf'(\d+[.,]\d{{2}})[^\S\n]*€?[^\S\n]*{mot_cle}|{mot_cle}[^\n]*?(\d+[.,]\d{{2}})[^\S\n]*€?'
    match = re.search(pattern, texte, re.IGNORECASE)
    if match:
        valeur = match.group(1) or match.group(2)           
        valeur = valeur.replace(" ", "").replace(",", ".")  
        return float(valeur)                             
    return None


def extraire_taux_tva(texte: str) -> float | None:
    """
    Extrait un taux de TVA sous la forme "TVA : 20%" (ou "taux TVA 20 %").
    Retourne un float (ex: 20.0) ou None si non trouvé.
    """
    if not texte:
        return None

    # On capture le nombre avant le caractère '%'.
    # - accepte "20%", "20 %", "20,0%", "20.0%"
    pattern = r"(?:taux\s+)?TVA\s*[:\-]?\s*(\d+(?:[.,]\d+)?)\s*%"
    match = re.search(pattern, texte, re.IGNORECASE)
    if not match:
        return None

    valeur = match.group(1).replace(" ", "").replace(",", ".")
    try:
        return float(valeur)
    except ValueError:
        return None


def extraire_date(texte, mots_cles):
    # Cherche une date au format JJ/MM/AAAA ou AAAA-MM-JJ près d'un mot clé
    for mot in mots_cles:
        pattern = rf'{mot}.*?(\d{{2}}/\d{{2}}/\d{{4}}|\d{{4}}-\d{{2}}-\d{{2}})'
        match = re.search(pattern, texte, re.IGNORECASE)
        if match:
            return match.group(1)  
    return None


def extraire_numero_facture(texte: str) -> str | None:
    """
    pour extraire un numéro de facture pres de \"FACTURE\" / \"Facture N°\".
    et accepte les retours à la ligne (ex: \"FACTURE N°\\nFAC-2026-0001\").
    """
    if not texte:
        return None
    match = re.search(
        r"(?:FACTURE)\s*(?:N[°o]|No|#)?\s*[:\-]?\s*([A-Z0-9][A-Z0-9-]{3,})",
        texte,
        re.IGNORECASE,
    )
    if not match:
        return None
    numero = match.group(1).strip()
    return numero or None


def extraire_numero_devis(texte: str) -> str | None:
    """
    Pour extraire un numéro de devis près de "DEVIS" / "Devis N°" / "Devis No".
    Accepte les retours à la ligne (ex: "DEVIS N°\\nD-2026-007").
    """
    if not texte:
        return None

    match = re.search(
        r"(?:DEVIS)\s*(?:N[°o]|No|#)?\s*[:\-]?\s*([A-Z0-9][A-Z0-9-]{3,})",
        texte,
        re.IGNORECASE,
    )
    if not match:
        return None

    numero = match.group(1).strip()
    return numero or None


def extraire_mode_paiement(texte: str) -> str | None:
    # pour extraire le mode de règlement  si il se trouve dans la facture 
    if not texte:
        return None
    match = re.search(
        r"(?:Mode\s+de\s+r[èeé]glement)\s*[:\-]?\s*([^\n\r]+)",
        texte,
        re.IGNORECASE,
    )
    if match:
        valeur = match.group(1).strip()
        return valeur or None
    return None


def extraire_date_echeance(texte: str) -> str | None:
    # pour extraire la date d'échéance si présente 
    return extraire_date(texte, ["échéance", "echeance", "à régler avant le", "a regler avant le"])


def extraire_siret_fournisseur_client(texte: str) -> dict:
    """
    on essaie d'attribuer un SIRET au fournisseur et au client
    : séparation par la section \"FACTURÉ À\" (ou variantes).
    """
    sirets = extraire_tous_les_siret(texte)
    if not sirets:
        return {"siret_fournisseur": None, "siret_client": None, "sirets": []}

    marker = re.search(r"FACTUR[ÉE]\s+À|FACTURE\s+A|FACTURE\s+À", texte, re.IGNORECASE)
    if marker:
        avant = texte[: marker.start()]
        apres = texte[marker.end() :]
        siret_f = extraire_siret(avant) or (sirets[0] if sirets else None)
        siret_c = extraire_siret(apres)
        return {"siret_fournisseur": siret_f, "siret_client": siret_c, "sirets": sirets}

    siret_f = sirets[0] if len(sirets) >= 1 else None
    siret_c = sirets[1] if len(sirets) >= 2 else None
    return {"siret_fournisseur": siret_f, "siret_client": siret_c, "sirets": sirets}


def extraire_client(texte: str) -> str | None:
    """
    Extrait le nom du client depuis la zone située après "FACTURÉ À"/"FACTURE A"
    (ou variantes comme "ADRESSE A"/"ADRESSÉ A" selon le format OCR).
    """
    if not texte:
        return None

    # On priorise "FACTURÉ À"/"FACTURE A" car c'est le label le plus spécifique.
    marker_facture = re.search(r"FACTUR[ÉE]\s+À|FACTURE\s+A|FACTURE\s+À", texte, re.IGNORECASE)
    # Pour les devis, l'OCR renvoie souvent "ADRESSÉ A" (avec accent variable),
    # parfois sans espace ou avec une variante (ADRESSE/ADRESSÉ/ADRESSÉE...).
    marker_adresse = re.search(
        r"ADRESS(?:[ÉE]{0,2})\s*[:\-]?\s*A|ADRESS(?:[ÉE]{0,2})\s*[:\-]?\s*À",
        texte,
        re.IGNORECASE,
    )
    marker = marker_facture or marker_adresse
    if not marker:
        return None

    apres = texte[marker.end() :]

    # On prend la première ligne "significative" après le marqueur.
    # Si une ligne est sous la forme "Client : X", on capture directement X.
    # Les lignes qu'on ne veut presque jamais confondre avec un "nom".
    # On utilise une regex pour gérer correctement les accents OCR.
    skip_re = re.compile(
        r"^(?:SIRET|SIREN|IBAN|TVA|MONTANT|DATE|(?:[ÉE]CH[ÉE]ANCE|ECHEANCE)|MODE|TAUX|NUM(?:[ÉE]RO|ERO))",
        re.IGNORECASE,
    )

    # Si le nom client est sur la même ligne que d'autres champs (rare mais déjà vu OCR),
    # on coupe avant les prochains labels typiques.
    cut_apres_re = re.compile(
        r"\b(?:SIRET|SIREN|IBAN|TVA|MONTANT|DATE|MODE|TAUX|NUM(?:[ÉE]RO|ERO)|(?:[ÉE]CH[ÉE]ANCE|ECHEANCE))\b",
        re.IGNORECASE,
    )

    for ligne in apres.splitlines():
        l = ligne.strip()
        if not l:
            continue

        if skip_re.match(l):
            continue

        # Cas le plus fréquent dans vos tests OCR: "Client : Pichon"
        m = re.match(r"^(?:Client|Destinataire)\s*[:\-]?\s*(.+?)\s*$", l, re.IGNORECASE)
        if m:
            nom = m.group(1).strip()
            return nom or None

        # Fallback: si c'est une autre ligne texte (souvent le bloc commence par le nom),
        # on retourne le texte avant d'éventuels autres labels.
        cut = cut_apres_re.search(l)
        if cut:
            candidat = l[: cut.start()].strip()
            return candidat or None
        return l

    return None


def extraire_fournisseur(texte):
    # Cherche la ligne qui suit un mot clé connu (Fournisseur, Émetteur, etc.)
    match = re.search(r'(?:Fournisseur|Émetteur|Employeur|Titulaire)\s*[:\-]?\s*(.+)', texte, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    
    # Fallback : prend uniquement le premier mot de la première ligne non vide
   
    for ligne in texte.split('\n'):
        ligne = ligne.strip()
        if ligne and len(ligne) > 1 and not re.match(r'^\d', ligne):
            premier_mot = ligne.split()[0]  # Prend uniquement le premier mot
            return premier_mot
    return None


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
    attribution_siret = extraire_siret_fournisseur_client(texte)
    base = {
        "document_type": type_doc,
        "siret":         extraire_siret(texte),
        "sirets":        attribution_siret.get("sirets", []),
        "siret_fournisseur": attribution_siret.get("siret_fournisseur"),
        "siret_client":  attribution_siret.get("siret_client"),
        "siren":         extraire_siren(texte),
        "date_emission": extraire_date(texte, ["date", "émis", "emission", "le"]),
    }

    if type_doc == "facture":                          # Champs spécifiques à une facture
        montant_ht = extraire_montant(texte, "HT")
        montant_ttc = extraire_montant(texte, "TTC")

        # Priorité à l'extraction explicite du taux en %.
        tva_taux = extraire_taux_tva(texte)

        # Fallback: si le PDF ne contient que le montant de TVA (pas de "%"),
        # on calcule le taux à partir de HT et du montant TVA.
        if tva_taux is None and montant_ht:
            tva_montant = extraire_montant(texte, "TVA")
            if tva_montant is not None and montant_ht != 0:
                tva_taux = round((tva_montant / montant_ht) * 100, 2)

        base.update({
            "nom_fournisseur": extraire_fournisseur(texte),
            "nom_client": extraire_client(texte),
            "numero_facture":  extraire_numero_facture(texte),
            "date_echeance":   extraire_date_echeance(texte),
            "montant_ht":      montant_ht,
            "montant_ttc":     montant_ttc,
            "tva":             tva_taux,
            "iban":            extraire_iban(texte),
            "mode_paiement":   extraire_mode_paiement(texte),
        })

    elif type_doc == "devis":                          # Champs spécifiques à un devis
        montant_ht = extraire_montant(texte, "HT")
        montant_ttc = extraire_montant(texte, "TTC")

        tva_taux = extraire_taux_tva(texte)
        if tva_taux is None and montant_ht:
            tva_montant = extraire_montant(texte, "TVA")
            if tva_montant is not None and montant_ht != 0:
                tva_taux = round((tva_montant / montant_ht) * 100, 2)

        base.update({
            "nom_fournisseur": extraire_fournisseur(texte),
            "nom_client": extraire_client(texte),
            "numero_devis": extraire_numero_devis(texte),
            "montant_ht":      montant_ht,
            "montant_ttc":     montant_ttc,
            "tva":             tva_taux,
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
