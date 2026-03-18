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
    nom_client?: string
    nom_entreprise_client: string
    adresse_client_adress?: string
    adresse_client_zip?: string
    adresse_client_city?: string
    numero_devis: string
    siren: string
    siret: string
  }
}
