"""
Génération du dataset synthétique pour le hackathon IPSSI.
Produit des PDFs dans data/bronze/ : factures, devis, attestations URSSAF.
Scénarios : clean, falsified (SIRET/TVA incohérent), expired (date dépassée).

Champs extraits par l'OCR  :
  siret, siren, montant_ht, montant_ttc, tva, date_emission,
  date_expiration, nom_fournisseur, document_type, iban

Dépendances : pip install faker fpdf2
"""

import random
from pathlib import Path
from datetime import date, timedelta

from faker import Faker
from fpdf import FPDF

fake = Faker("fr_FR")
BRONZE = Path(__file__).parent.parent / "bronze"


# --- Helpers ---

def gen_siret():
    return "".join([str(random.randint(0, 9)) for _ in range(14)])

def siren_from(siret):
    return siret[:9]

def tva_intra(siret):
    cle = (12 + 3 * (int(siret[:9]) % 97)) % 97
    return f"FR{cle:02d}{siret[:9]}"

def montants():
    ht = round(random.uniform(500, 10000), 2)
    tva = round(ht * 0.20, 2)
    return ht, tva, round(ht + tva, 2)


# --- PDF générique ---

def make_pdf(titre, lignes_texte, output_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 12, titre, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=11)
    for ligne in lignes_texte:
        pdf.cell(0, 8, ligne, new_x="LMARGIN", new_y="NEXT")
    pdf.output(str(output_path))


# --- Générateurs ---

def gen_facture(scenario="clean"):
    siret = gen_siret()
    ht, tva, ttc = montants()
    tva_num = tva_intra(siret) if scenario == "clean" else tva_intra(gen_siret())
    emission = date.today() - timedelta(days=random.randint(1, 180))
    expiration = emission + timedelta(days=30)
    iban = f"FR76 {random.randint(10000,99999)} {random.randint(10000,99999)} {random.randint(10000,99999)}"
    return [
        f"document_type     : FACTURE",
        f"Numero            : FAC-{random.randint(1000,9999)}-{emission.year}",
        f"nom_fournisseur   : {fake.company()}",
        f"siret             : {siret}",
        f"siren             : {siren_from(siret)}",
        f"TVA intracom.     : {tva_num}",
        f"Client            : {fake.company()}",
        f"Adresse           : {fake.address().replace(chr(10), ', ')}",
        "",
        f"date_emission     : {emission.strftime('%d/%m/%Y')}",
        f"date_expiration   : {expiration.strftime('%d/%m/%Y')}",
        "",
        f"montant_ht        : {ht} EUR",
        f"tva               : {tva} EUR",
        f"montant_ttc       : {ttc} EUR",
        f"iban              : {iban}",
    ]


def gen_devis(scenario="clean"):
    siret = gen_siret()
    ht, tva, ttc = montants()
    emission = date.today() - timedelta(days=random.randint(1, 90))
    if scenario == "expired":
        expiration = emission + timedelta(days=random.randint(5, 20))
    else:
        expiration = date.today() + timedelta(days=random.randint(15, 60))
    return [
        f"document_type     : DEVIS",
        f"Reference         : DEV-{random.randint(1000,9999)}-{emission.year}",
        f"nom_fournisseur   : {fake.company()}",
        f"siret             : {siret}",
        f"siren             : {siren_from(siret)}",
        f"Client            : {fake.company()}",
        "",
        f"date_emission     : {emission.strftime('%d/%m/%Y')}",
        f"date_expiration   : {expiration.strftime('%d/%m/%Y')}",
        "",
        f"montant_ht        : {ht} EUR",
        f"tva               : {tva} EUR",
        f"montant_ttc       : {ttc} EUR",
        f"Prestation        : {fake.bs().capitalize()}",
    ]


def gen_attestation(scenario="clean"):
    siret = gen_siret()
    emission = date.today() - timedelta(days=random.randint(1, 60))
    if scenario == "expired":
        expiration = emission + timedelta(days=random.randint(10, 30))
    else:
        expiration = date.today() + timedelta(days=random.randint(30, 180))
    return [
        f"document_type     : ATTESTATION_URSSAF",
        f"nom_fournisseur   : {fake.company()}",
        f"siret             : {siret}",
        f"siren             : {siren_from(siret)}",
        f"Adresse           : {fake.address().replace(chr(10), ', ')}",
        "",
        f"date_emission     : {emission.strftime('%d/%m/%Y')}",
        f"date_expiration   : {expiration.strftime('%d/%m/%Y')}",
        "",
        "Statut : A jour de ses obligations declaratives et de paiement.",
        f"Numero attestation : ATT-{random.randint(100000, 999999)}",
    ]


# --- Orchestration ---

DOCS = {
    "factures": [
        (20, "clean",     gen_facture,     "FACTURE"),
        (10, "falsified", gen_facture,     "FACTURE"),
    ],
    "devis": [
        (15, "clean",     gen_devis,       "DEVIS"),
        (5,  "expired",   gen_devis,       "DEVIS"),
    ],
    "attestations": [
        (15, "clean",     gen_attestation, "ATTESTATION URSSAF"),
        (5,  "expired",   gen_attestation, "ATTESTATION URSSAF"),
    ],
}

if __name__ == "__main__":
    total = 0
    for folder, scenarios in DOCS.items():
        out = BRONZE / folder
        out.mkdir(parents=True, exist_ok=True)
        for n, scenario, gen_fn, titre in scenarios:
            for i in range(n):
                lignes = gen_fn(scenario)
                path = out / f"{folder[:-1]}_{scenario}_{i+1:03d}.pdf"
                make_pdf(titre, lignes, path)
                total += 1
        print(f"[OK] {folder}")

    print(f"\n{total} documents generes dans {BRONZE}")
