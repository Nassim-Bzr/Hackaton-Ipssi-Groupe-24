export interface Devis {
  document_type: "devis"
  entities: {
    date_emission: string
    date_expiration: string
    montant_ht: number
    montant_ttc: number
    tva: number
    nom_fournisseur: string
    adresse_fournisseur_adress?: string
    adresse_fournisseur_zip?: string
    adresse_fournisseur_city?: string
    nom_client: string
    numero_devis: string
    siren: string
    siret: string
  }
}
