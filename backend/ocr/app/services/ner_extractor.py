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

    lignes = [l.strip() for l in texte.splitlines() if l.strip()]
    if not lignes:
        return None

    # 1) Devis : ton OCR a toujours `À l'attention de : ...`.
    # Le nom de l'entreprise du client est la ligne juste avant cette mention.
    attention_re = re.compile(r"À\s*l'attention\s*de\s*[:\-]?", re.IGNORECASE)
    for idx, l in enumerate(lignes):
        if attention_re.search(l):
            # Remonte jusqu'à trouver la première ligne "significative" avant l'attention.
            j = idx - 1
            while j >= 0 and not lignes[j].strip():
                j -= 1
            if j < 0:
                break

            candidat = lignes[j].strip()
            # Si l'OCR encode "Client : X", on extrait X
            m = re.match(r"^(?:Facturé\s*À|Client|Destinataire)\s*[:\-]?\s*(.+?)\s*$", candidat, re.IGNORECASE)
            return (m.group(1).strip() if m else candidat) or None

    # 2) Facture : extraction à partir de `Facturé à : <Nom>`
    facture_re = re.compile(r"FACTUR[ÉE]\s+À\s*[:\-]?\s*(.+)$", re.IGNORECASE)
    for l in lignes:
        m = facture_re.search(l)
        if m:
            candidat = m.group(1).strip()
            if candidat:
                return candidat

    # 3) Fallback (ancien comportement) : `FACTURÉ À`/`FACTURE A` ou `ADRESSÉ A`
    marker_facture_ancien = re.search(r"FACTUR[ÉE]\s+À|FACTURE\s+A|FACTURE\s+À", texte, re.IGNORECASE)
    marker_adresse_ancien = re.search(
        r"ADRESS(?:[ÉE]{0,2})\s*[:\-]?\s*A|ADRESS(?:[ÉE]{0,2})\s*[:\-]?\s*À",
        texte,
        re.IGNORECASE,
    )
    marker = marker_facture_ancien or marker_adresse_ancien
    if not marker:
        return None

    apres = texte[marker.end() :]

    skip_re = re.compile(
        r"^(?:SIRET|SIREN|IBAN|TVA|MONTANT|DATE|(?:[ÉE]CH[ÉE]ANCE|ECHEANCE)|MODE|TAUX|NUM(?:[ÉE]RO|ERO))",
        re.IGNORECASE,
    )

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
        m = re.match(r"^(?:Client|Destinataire)\s*[:\-]?\s*(.+?)\s*$", l, re.IGNORECASE)
        if m:
            return m.group(1).strip() or None
        cut = cut_apres_re.search(l)
        if cut:
            return l[: cut.start()].strip() or None
        return l

    return None


def extraire_nom_client_contact(texte: str) -> str | None:
    """
    Extrait le nom réel (personne/contacts) du client depuis l'OCR.

    Hypothèse métier :
    - Le nom apparaît après le marqueur `À l'attention de :`.
    - Le nom est généralement sur la même ligne, sinon sur la ligne suivante.
    """
    if not texte:
        return None

    lines = [l.strip() for l in texte.splitlines()]
    if not lines:
        return None

    attention_line_re = re.compile(
        r"À\s*l'attention\s*de\s*[:\-]?\s*(.*)$",
        re.IGNORECASE,
    )

    for i, line in enumerate(lines):
        if not line:
            continue

        m = attention_line_re.search(line)
        if not m:
            continue

        # Cas "À l'attention de : Tom" (nom sur la même ligne)
        same_line = (m.group(1) or "").strip()
        if same_line:
            if "@" in same_line:
                same_line = same_line.split("@", 1)[0].strip()
            return same_line or None

        # Cas "À l'attention de :" puis nom sur la ligne suivante
        for j in range(i + 1, len(lines)):
            candidate = lines[j].strip()
            if not candidate:
                continue
            if "@" in candidate:
                break
            if re.match(
                r"^(?:SIRET|SIREN|IBAN|TVA|MONTANT|DATE|MODE|TAUX|NUM(?:[ÉE]RO|ERO)|"
                r"FACTUR[ÉE]|DEVIS|ADRESS(?:[ÉE]{0,2})|FOURNISSEUR|EMETTEUR|CLIENT|DESTINATAIRE)",
                candidate,
                re.IGNORECASE,
            ):
                break
            return candidate

    return None


def extraire_adresse_client_adress_zip_city(texte: str) -> dict[str, str | None]:
    """
    Découpe une adresse client OCR en :
    - adresse_client_adress : lignes "rue / complément" (sans code postal + ville)
    - adresse_client_zip : code postal (5 chiffres)
    - adresse_client_city : ville

    Hypothèse OCR (devis) : l'adresse suit la ligne `À l'attention de : ...`.
    """
    if not texte:
        return {
            "adresse_client_adress": None,
            "adresse_client_zip": None,
            "adresse_client_city": None,
        }

    raw_lines = texte.splitlines()
    # Trouver la ligne qui contient `À l'attention de :`
    attention_re = re.compile(r"À\s*l'attention\s*de\s*[:\-]?", re.IGNORECASE)
    attention_idx = None
    for idx, raw in enumerate(raw_lines):
        if attention_re.search(raw):
            attention_idx = idx
            break

    start_idx = None
    if attention_idx is not None:
        # On démarre juste après la ligne d'attention.
        start_idx = attention_idx + 1
    else:
        # Fallback facture : on tente après une ligne `Facturé à : ...`
        facture_line_re = re.compile(r"FACTUR[ÉE]\s+À\s*[:\-]?", re.IGNORECASE)
        for idx, raw in enumerate(raw_lines):
            if facture_line_re.search(raw):
                start_idx = idx + 1
                break

    if start_idx is None:
        return {
            "adresse_client_adress": None,
            "adresse_client_zip": None,
            "adresse_client_city": None,
        }

    stop_re = re.compile(
        r"^(?:SIRET|SIREN|IBAN|TVA|MONTANT|DATE|(?:[ÉE]CH[ÉE]ANCE|ECHEANCE)|MODE|TAUX|NUM(?:[ÉE]RO|ERO)|"
        r"FACTUR[ÉE]\s*[:\-]?|DEVIS|ADRESS(?:[ÉE]{0,2})|FOURNISSEUR|EMETTEUR|CLIENT|DESTINATAIRE|TAUX|@)",
        re.IGNORECASE,
    )

    collected: list[str] = []
    for raw in raw_lines[start_idx:]:
        l = raw.strip()
        if not l:
            continue

        if "@" in l:
            break
        if stop_re.match(l):
            break

        collected.append(l)
        if len(collected) >= 8:
            break

    if not collected:
        return {
            "adresse_client_adress": None,
            "adresse_client_zip": None,
            "adresse_client_city": None,
        }

    zip_city_re = re.compile(
        r"\b(\d{5})\b\s*([A-Za-zÀ-ÖØ-öø-ÿ'’\- ]+?)\s*$",
        re.IGNORECASE,
    )

    last = collected[-1]
    m = zip_city_re.search(last)
    if not m:
        return {
            "adresse_client_adress": "\n".join(collected).strip() or None,
            "adresse_client_zip": None,
            "adresse_client_city": None,
        }

    zip_code = m.group(1)
    city = m.group(2).strip()

    # Préserver la partie "rue" qui peut être sur la même ligne que le zip.
    before_zip = last[: m.start(1)].strip().rstrip(" ,")
    adress_lines = collected[:-1]
    if before_zip:
        adress_lines = [*adress_lines, before_zip]

    address_adress = "\n".join(adress_lines).strip() or None
    return {
        "adresse_client_adress": address_adress,
        "adresse_client_zip": zip_code,
        "adresse_client_city": city,
    }


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


def extraire_adresse_fournisseur(texte: str) -> str | None:
    """
    Extrait l'adresse du fournisseur en considérant que :
    - le nom du fournisseur est sur la ligne après un label (ex: "Fournisseur : X")
    - l'adresse est juste en dessous (plusieurs lignes possibles)
    """
    if not texte:
        return None

    lignes = [l.strip() for l in texte.splitlines()]

    # Stop si on détecte un nouveau label de champs.
    # On ancre au début de ligne car on veut éviter de couper au milieu d'une adresse.
    stop_re = re.compile(
        r"^(?:"
        r"SIRET|SIREN|IBAN|TVA|MONTANT|DATE|MODE|TAUX|NUM(?:[ÉE]RO|ERO)|"
        r"FACTUR[ÉE]\s*[:\-]?|ADRESS(?:[ÉE]{0,2})\s*[:\-]?|CLIENT|DESTINATAIRE|"
        r"FOURNISSEUR|EMETTEUR|EMPLOYEUR|TITULAIRE"
        r")\b",
        re.IGNORECASE,
    )

    # On cherche la première occurrence d'un label fournisseur.
    fournisseur_label_re = re.compile(
        r"^(?:Fournisseur|Émetteur|Employeur|Titulaire)\s*[:\-]?\s*(.*)$",
        re.IGNORECASE,
    )

    for i, ligne in enumerate(lignes):
        if not ligne:
            continue
        m = fournisseur_label_re.match(ligne)
        if not m:
            continue

        # Si le label contient déjà le nom, on commence l'adresse sur la ligne suivante.
        # Sinon (rare), on prend la première ligne non vide comme nom, puis on commence juste après.
        nom_sur_ligne = (m.group(1) or "").strip()
        start_j = i + 1
        if not nom_sur_ligne:
            # Cas où le label est seul sur sa ligne.
            for j in range(i + 1, min(i + 4, len(lignes))):
                if lignes[j].strip():
                    start_j = j + 1
                    break

        adresse_lignes: list[str] = []
        started = False

        for j in range(start_j, min(start_j + 12, len(lignes))):
            l = lignes[j].strip()
            if not l:
                if started:
                    break
                continue

            if stop_re.match(l):
                break

            adresse_lignes.append(l)
            started = True

        adresse = "\n".join(adresse_lignes).strip()
        if adresse:
            return adresse

    # Fallback : certains documents (ex: devis) n'ont pas de label explicite du type
    # "Fournisseur : ...". Dans ce cas, on considère que l'adresse est en dessous
    # de la première ligne non vide (souvent la ligne contenant le nom + le numéro).
    for i0 in range(len(lignes)):
        if lignes[i0].strip():
            start_j = None
            # Cherche la prochaine ligne non vide.
            for j0 in range(i0 + 1, min(i0 + 6, len(lignes))):
                if lignes[j0].strip():
                    start_j = j0
                    break
            if start_j is None:
                return None

            adresse_lignes: list[str] = []
            started = False
            for j in range(start_j, min(start_j + 12, len(lignes))):
                l = lignes[j].strip()
                if not l:
                    if started:
                        break
                    continue

                if stop_re.match(l):
                    break

                adresse_lignes.append(l)
                started = True

            adresse = "\n".join(adresse_lignes).strip()
            if adresse:
                return adresse
            return None

    return None


def extraire_adresse_fournisseur_adress_zip_city(texte: str) -> dict[str, str | None]:
    """
    Découpe une adresse fournisseur OCR en :
    - adress : lignes "rue / complément" (sans code postal + ville)
    - zip : code postal (5 chiffres)
    - city : ville
    """
    adresse_block = extraire_adresse_fournisseur(texte)
    if not adresse_block:
        return {
            "adresse_fournisseur_adress": None,
            "adresse_fournisseur_zip": None,
            "adresse_fournisseur_city": None,
        }

    lignes = [l.strip() for l in adresse_block.splitlines() if l.strip()]
    if not lignes:
        return {
            "adresse_fournisseur_adress": None,
            "adresse_fournisseur_zip": None,
            "adresse_fournisseur_city": None,
        }

    # On tente en priorité de trouver un couple "zip + ville" dans la dernière ligne.
    # Ex: "75001 PARIS", "69001 LYON", etc.
    # La dernière ligne de l'adresse peut contenir "Date : ..." juste après la ville
    # (ex: "25120 Sainte Élise-les-Bains Date : 25/02/2026").
    # On capture donc le city avant un prochain champ typique.
    zip_city_re = re.compile(
        r"\b(\d{5})\b\s*([A-Za-zÀ-ÖØ-öø-ÿ'’\- ]+?)\s*"
        r"(?=\s*(?:Date\s*:|Valable\s+jusqu|TVA\s*:|SIRET|SIREN|IBAN|MONTANT|MODE|TAUX|"
        r"FACTUR[ÉE]\s*[:\-]?|DEVIS|ADRESS(?:[ÉE]{0,2})\s*[:\-]?|$))",
        re.IGNORECASE,
    )

    zip_code: str | None = None
    city: str | None = None
    zip_line_idx: int | None = None
    zip_match_start: int | None = None
    zip_line_text: str | None = None

    for idx in range(len(lignes) - 1, -1, -1):
        m = zip_city_re.search(lignes[idx])
        if m:
            zip_code = m.group(1)
            city = m.group(2).strip()
            zip_line_idx = idx
            zip_match_start = m.start(1)
            zip_line_text = lignes[idx]
            break

    if zip_line_idx is None:
        # Fall back : pas de code postal détecté, on renvoie tout en "adress".
        return {
            "adresse_fournisseur_adress": "\n".join(lignes).strip() or None,
            "adresse_fournisseur_zip": None,
            "adresse_fournisseur_city": None,
        }

    # Rue/complement : on prend les lignes avant le code postal,
    # puis on ajoute éventuellement la partie avant le zip sur la ligne du zip.
    adress_lignes = lignes[:zip_line_idx]
    if zip_match_start is not None and zip_line_text:
        avant_zip = zip_line_text[:zip_match_start].strip().rstrip(" ,")
        if avant_zip:
            adress_lignes = [*adress_lignes, avant_zip] if adress_lignes else [avant_zip]

    adress = "\n".join(adress_lignes).strip() or None

    return {
        "adresse_fournisseur_adress": adress,
        "adresse_fournisseur_zip": zip_code,
        "adresse_fournisseur_city": city,
    }


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
            **extraire_adresse_fournisseur_adress_zip_city(texte),
            # nom_client = nom réel (personne/contact), nom_entreprise_client = nom entreprise
            "nom_client": extraire_nom_client_contact(texte) or extraire_client(texte),
            "nom_entreprise_client": extraire_client(texte),
            **extraire_adresse_client_adress_zip_city(texte),
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
            **extraire_adresse_fournisseur_adress_zip_city(texte),
            # nom_client = nom réel (personne/contact), nom_entreprise_client = nom entreprise
            "nom_client": extraire_nom_client_contact(texte) or extraire_client(texte),
            "nom_entreprise_client": extraire_client(texte),
            **extraire_adresse_client_adress_zip_city(texte),
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
