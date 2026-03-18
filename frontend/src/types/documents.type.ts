export type DevisEntities = {
  adresse_fournisseur_adress: string
  adresse_fournisseur_city: string
  adresse_fournisseur_zip: string
  date_emission: string
  date_expiration: string
  montant_ht: number
  montant_ttc: number
  nom_client: string | null
  nom_entreprise_client: string | null
  nom_fournisseur: string
  numero_devis: string
  tva: number

  adresse_client_adress: string | null
  adresse_client_zip: string | null
  adresse_client_city: string | null

  // D'après tes exemples, certains champs peuvent être `null` (ex: siren).
  siren: string | null
  siret: string | null
  siret_fournisseur: string | null
  siret_client: string | null
  sirets: string[] | null
}

export type FactureEntities = {
  adresse_fournisseur_adress: string
  adresse_fournisseur_city: string
  adresse_fournisseur_zip: string
  date_echeance: string
  date_emission: string
  iban: string
  mode_paiement: string
  montant_ht: number
  montant_ttc: number
  nom_client: string | null
  nom_entreprise_client: string | null
  nom_fournisseur: string
  numero_facture: string
  tva: number

  adresse_client_adress: string | null
  adresse_client_zip: string | null
  adresse_client_city: string | null

  siren: string | null
  siret: string
  siret_fournisseur: string
  siret_client: string | null
  sirets: string[] | null
}

/**
 * Objet retourné par l'API `/documents`.
 *
 * Note: les champs d'entités diffèrent entre `devis` et `facture`, d'où le typage discriminé.
 */
export type DocumentItem =
  | {
      doc_id: string
      id: string
      nom: string
      document_type: "devis"
      entities: DevisEntities
      metadata?: Record<string, unknown>
      is_valid?: boolean
      validation_details?: Record<string, unknown>
    }
  | {
      doc_id: string
      id: string
      nom: string
      document_type: "facture"
      entities: FactureEntities
      metadata?: Record<string, unknown>
      is_valid?: boolean
      validation_details?: Record<string, unknown>
    }

export interface DocumentResponse {
  documents: DocumentItem[]
  total: number
}
