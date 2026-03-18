export interface Facture {
  document_type: "facture"
  entities: {
    date_emission: string
    date_echeance: string
    iban: string
    montant_ht: number
    montant_ttc: number
    nom_fournisseur: string
    adresse_fournisseur_adress?: string
    adresse_fournisseur_zip?: string
    adresse_fournisseur_city?: string
    nom_client?: string
    numero_facture: string
    siren: string
    siret: string
    siret_client: string
    mode_paiement: string
    tva: number
  }
}
