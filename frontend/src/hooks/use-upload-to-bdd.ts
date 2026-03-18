import type { Devis } from "@/types/devis.type"
import type { Facture } from "@/types/facture.type"
import { useMutation } from "@tanstack/react-query"

const UPLOAD_TO_BDD_URL = "http://localhost:3000/upload-to-bdd"

type FactureEntities = Facture["entities"]
type DevisEntities = Devis["entities"]

/** Payload pour l’upload : entités facture ou devis (snake_case comme les types). */
type UploadEntities = FactureEntities | DevisEntities

export type UploadToBddVariables = {
  index: number
  file: File
  id: string
  nom: string
  entities: UploadEntities
  documentType: "facture" | "devis"
}

/** Réponse du backend POST /upload-to-bdd */
export type UploadToBddResponse = {
  doc_id: string
  document_type: string
  is_valid: boolean
  confidence_score?: number
  entities: Record<string, unknown>
  prefill?: Record<string, unknown>
  data_lake?: { raw_uri: string; clean_uri: string; curated_uri: string }
}

function appendIfPresent(
  formData: FormData,
  key: string,
  value: string | number | undefined
): void {
  if (value === undefined || value === null) return
  if (typeof value === "number") {
    if (Number.isFinite(value)) formData.append(key, String(value))
    return
  }
  const s = String(value).trim()
  if (s !== "") formData.append(key, s)
}

/**
 * Construit le FormData pour POST /upload-to-bdd à partir des entités
 * (facture ou devis) en snake_case.
 */
function buildUploadFormData(variables: UploadToBddVariables): FormData {
  const { file, id, nom, entities, documentType } = variables
  const formData = new FormData()
  formData.append("file", file)
  formData.append("id", id)
  formData.append("nom", nom)

  // Champs communs
  appendIfPresent(formData, "siret", (entities as { siret?: string }).siret)
  appendIfPresent(formData, "siren", (entities as { siren?: string }).siren)
  appendIfPresent(formData, "date_emission", (entities as { date_emission?: string }).date_emission)
  appendIfPresent(formData, "nom_fournisseur", (entities as { nom_fournisseur?: string }).nom_fournisseur)
  appendIfPresent(
    formData,
    "adresse_fournisseur_adress",
    (entities as { adresse_fournisseur_adress?: string }).adresse_fournisseur_adress,
  )
  appendIfPresent(
    formData,
    "adresse_fournisseur_zip",
    (entities as { adresse_fournisseur_zip?: string }).adresse_fournisseur_zip,
  )
  appendIfPresent(
    formData,
    "adresse_fournisseur_city",
    (entities as { adresse_fournisseur_city?: string }).adresse_fournisseur_city,
  )
  appendIfPresent(formData, "iban", (entities as { iban?: string }).iban)
  appendIfPresent(formData, "montant_ht", (entities as { montant_ht?: number }).montant_ht)
  appendIfPresent(formData, "montant_ttc", (entities as { montant_ttc?: number }).montant_ttc)

  if (documentType === "facture") {
    const e = entities as FactureEntities
    appendIfPresent(formData, "date_echeance", e.date_echeance)
    appendIfPresent(formData, "numero_facture", e.numero_facture)
    appendIfPresent(formData, "siret_client", e.siret_client)
    appendIfPresent(formData, "mode_paiement", e.mode_paiement)
  } else {
    const e = entities as DevisEntities
    appendIfPresent(formData, "date_expiration", e.date_expiration)
    appendIfPresent(formData, "numero_devis", e.numero_devis)
    appendIfPresent(formData, "tva", e.tva)
  }

  return formData
}

async function uploadToBdd(variables: UploadToBddVariables): Promise<UploadToBddResponse> {
  if (!variables.id.trim() || !variables.nom.trim()) {
    throw new Error("Veuillez renseigner l'ID et le nom avant l'envoi.")
  }
  const formData = buildUploadFormData(variables)
  const response = await fetch(UPLOAD_TO_BDD_URL, {
    method: "POST",
    body: formData,
  })
  if (!response.ok) {
    throw new Error("Réponse du serveur invalide")
  }
  return response.json() as Promise<UploadToBddResponse>
}

/**
 * Hook TanStack Query pour envoyer un formulaire (facture ou devis) vers le backend
 * et enregistrer le document en base.
 */
export function useUploadToBdd() {
  return useMutation({
    mutationKey: ["upload-to-bdd"],
    mutationFn: uploadToBdd,
  })
}
