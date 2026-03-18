import type { UploadState } from "./upload-state.type"
import type { Facture } from "./facture.type"
import type { Devis } from "./devis.type"

export type PdfForm = {
  file: File
  id: string
  nom: string
  /**
   * Réponse brute renvoyée par le backend lors de l'analyse (/upload).
   * Permet de la transmettre telle quelle aux composants enfants si besoin.
   */
  facture?: Facture
  /**
   * Réponse brute renvoyée par le backend lors de l'analyse (/upload) pour un devis.
   */
  devis?: Devis
  /**
   * Type de document renvoyé par le backend (ex: "facture", "devis").
   */
  documentType?: string
  /**
   * Champs dérivés des entités extraites par le backend.
   * Ils sont optionnels et ne sont remplis qu'après un appel réussi à /upload.
   */
  dateEmission?: string
  dateEcheance?: string
  dateExpiration?: string
  numeroFacture?: string
  modePaiement?: string
  montantTtc?: number
  montantHt?: number
  tva?: number
  siret?: string
  siretClient?: string
  siretFournisseur?: string
  siren?: string
  nomFournisseur?: string
  adresseFournisseur?: string
  codePostalFournisseur?: string
  villeFournisseur?: string
  nomClient?: string
  iban?: string
  uploadState: UploadState
  message: string | null
}
