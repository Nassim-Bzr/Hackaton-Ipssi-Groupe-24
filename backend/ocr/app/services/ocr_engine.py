import pdfplumber


def extraire_texte(chemin_pdf: str) -> tuple[str, float]:
    """
    Extrait le texte embarqué d'un PDF (fpdf, Word exporté, etc.).
    Retourne (texte_complet, score_confiance).
    Le score est 1.0 si du texte est trouvé, 0.0 sinon.
    """
    pages_texte = []

    with pdfplumber.open(chemin_pdf) as pdf:
        for page in pdf.pages:
            texte = page.extract_text()
            if texte:
                pages_texte.append(texte)

    texte_complet = "\n".join(pages_texte).strip()
    score = 1.0 if texte_complet else 0.0

    return texte_complet, score
