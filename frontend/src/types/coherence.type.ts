/**
 * Types alignés sur l'API POST /coherence-check du service validations.
 */

export type DocumentCoherencePayload = {
  document_type: string
  siret?: string | null
  montant_ht?: number | null
  tva?: number | null
  montant_ttc?: number | null
  date_echeance?: string | null
}

export type CoherenceInput = {
  documents: DocumentCoherencePayload[]
}

export type AnomalieResult = {
  verification: string
  valide: boolean
  message: string
}

export type CoherenceResponse = {
  coherent: boolean
  anomalies: AnomalieResult[]
}
