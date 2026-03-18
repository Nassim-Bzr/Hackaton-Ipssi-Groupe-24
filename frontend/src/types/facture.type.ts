export interface Facture {
  document_type: "facture"
  entities: {
    date_emission: string
    date_echeance: string
    iban: string
    montant_ht: number
    montant_ttc: number
    nom_fournisseur: string
    numero_facture: string
    siren: string
    siret: string
    siret_client: string
    mode_paiement: string
  }
}
