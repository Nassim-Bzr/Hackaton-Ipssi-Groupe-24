type TypeFichier = "facture" | "devis"

export interface DocumentItem {
  id: number
  nom: string
  date: string
  document_type: TypeFichier
  entities: {
    siret: string
    siren: string
    montant_ht: number
    montant_ttc: number
    numero_facture: string
    numero_devis: string
    tva: number
    date_emission: string
    date_echeance: string
    date_expiration: string
    nom_fournisseur: string
    adresse_fournisseur_adress?: string
    adresse_fournisseur_zip?: string
    adresse_fournisseur_city?: string
    nom_client?: string
    iban: string
  }
}

export interface DocumentResponse {
  documents: DocumentItem[]
  total: number
}
