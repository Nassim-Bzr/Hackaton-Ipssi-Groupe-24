import type { UploadState } from "./upload-state.type"

export type PdfForm = {
  file: File
  id: string
  nom: string
  /**
   * Type de document renvoyé par le backend (ex: "facture", "devis").
   */
  documentType?: string
  /**
   * Champs dérivés des entités extraites par le backend.
   * Ils sont optionnels et ne sont remplis qu'après un appel réussi à /upload.
   */
  dateEmission?: string
  dateExpiration?: string
  montantTtc?: number
  montantHt?: number
  tva?: number
  siret?: string
  siren?: string
  nomFournisseur?: string
  iban?: string
  uploadState: UploadState
  message: string | null
}
