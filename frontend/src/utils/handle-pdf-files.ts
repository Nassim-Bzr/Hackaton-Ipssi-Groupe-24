import type { PdfForm } from "@/types/pdf-form.type"

/**
 * Helpers de pré-traitement/mapping pour l'upload/analyse PDF.
 */
export function filterPdfFiles(fileList: FileList | null): File[] {
  if (!fileList) return []
  const selected = Array.from(fileList)
  return selected.filter(
    (file) => file.type === "application/pdf" || file.name.toLowerCase().endsWith(".pdf"),
  )
}

export function buildInitialForms(pdfFiles: File[]): PdfForm[] {
  return pdfFiles.map((file) => ({
    file,
    id: "",
    nom: "",
    uploadState: "idle",
    message: "Analyse du document en cours...",
  }))
}

export function buildAnalyzeFormData(file: File): FormData {
  const formData = new FormData()
  formData.append("file", file)
  // Valeurs techniques pour id/nom ; elles pourront être écrasées ensuite.
  formData.append("id", file.name)
  formData.append("nom", file.name.replace(/\.pdf$/i, ""))
  return formData
}

function normalizeDateForDateInput(value: unknown): string | undefined {
  if (typeof value !== "string") return undefined
  const trimmed = value.trim()
  if (!trimmed) return undefined

  // Déjà au format attendu par <input type="date">.
  if (/^\d{4}-\d{2}-\d{2}$/.test(trimmed)) return trimmed

  // Backends/NER renvoient souvent jj/mm/aaaa.
  const match = /^(\d{2})\/(\d{2})\/(\d{4})$/.exec(trimmed)
  if (!match) return trimmed
  const [, dd, mm, yyyy] = match
  return `${yyyy}-${mm}-${dd}`
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function extractPayload(data: any): any {
  // On tolère plusieurs formats: {entities}, {data:{entities}}, {data:{data:{entities}}}, etc.
  return data?.data?.data ?? data?.data ?? data
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function mapBackendAnalysisToPdfForm(file: File, data: any): PdfForm {
  const payload = extractPayload(data)
  const prefill = (payload && payload.prefill) || {}
  const entities = (payload && payload.entities) || {}

  const inferredId: string =
    prefill.siret_fournisseur ||
    entities.siret_fournisseur ||
    entities.siret ||
    payload?.doc_id ||
    payload?.nom ||
    ""

  const inferredNom: string = entities.nom_fournisseur || payload?.nom || ""
  const inferredNomClient: string | undefined =
    (prefill.nom_client as string | undefined) ||
    (entities.nom_client as string | undefined) ||
    undefined

  const inferredDateEmissionRaw: unknown = prefill.date_emission ?? entities.date_emission
  const inferredDateEmission: string | undefined = normalizeDateForDateInput(inferredDateEmissionRaw)

  const inferredDateEcheanceRaw: unknown =
    prefill.date_echeance ?? entities.date_echeance
  const inferredDateEcheance: string | undefined = normalizeDateForDateInput(inferredDateEcheanceRaw)

  const inferredDateExpiration: string | undefined = entities.date_expiration

  const inferredNumeroFacture: string | undefined =
    (entities.numero_facture as string | undefined) || undefined

  const inferredModePaiement: string | undefined =
    (entities.mode_paiement as string | undefined) || undefined

  const inferredMontantTtcRaw: unknown = prefill.montant_ttc ?? entities.montant_ttc
  const inferredMontantTtc =
    typeof inferredMontantTtcRaw === "number"
      ? inferredMontantTtcRaw
      : typeof inferredMontantTtcRaw === "string"
        ? Number.parseFloat(inferredMontantTtcRaw)
        : undefined

  const inferredMontantHtRaw: unknown = prefill.montant_ht ?? entities.montant_ht
  const inferredMontantHt =
    typeof inferredMontantHtRaw === "number"
      ? inferredMontantHtRaw
      : typeof inferredMontantHtRaw === "string"
        ? Number.parseFloat(inferredMontantHtRaw)
        : undefined

  const inferredTvaRaw: unknown = prefill.tva ?? entities.tva
  const inferredTva =
    typeof inferredTvaRaw === "number"
      ? inferredTvaRaw
      : typeof inferredTvaRaw === "string"
        ? Number.parseFloat(inferredTvaRaw)
        : undefined

  const inferredSiretFournisseur: string | undefined =
    (prefill.siret_fournisseur as string | undefined) ||
    (entities.siret_fournisseur as string | undefined) ||
    (entities.siret as string | undefined) ||
    undefined

  const inferredSiretClient: string | undefined =
    (entities.siret_client as string | undefined) || undefined

  const inferredSiret: string | undefined =
    inferredSiretFournisseur || inferredSiretClient || undefined

  const inferredSiren: string | undefined = (entities.siren as string | undefined) || undefined
  const inferredNomFournisseur: string | undefined =
    (entities.nom_fournisseur as string | undefined) || undefined
  const inferredIban: string | undefined =
    (prefill.iban as string | undefined) || (entities.iban as string | undefined) || undefined

  const inferredDocumentType: string | undefined =
    (payload && (payload.document_type as string)) || undefined

  return {
    file,
    id: inferredId,
    nom: inferredNom,
    nomClient: inferredNomClient,
    dateEmission: inferredDateEmission,
    dateEcheance: inferredDateEcheance,
    dateExpiration: inferredDateExpiration,
    numeroFacture: inferredNumeroFacture,
    modePaiement: inferredModePaiement,
    montantTtc: inferredMontantTtc,
    montantHt: inferredMontantHt,
    tva: inferredTva,
    siret: inferredSiret,
    siretClient: inferredSiretClient,
    siretFournisseur: inferredSiretFournisseur,
    siren: inferredSiren,
    nomFournisseur: inferredNomFournisseur,
    iban: inferredIban,
    documentType: inferredDocumentType,
    uploadState: "idle",
    message: null,
  }
}
