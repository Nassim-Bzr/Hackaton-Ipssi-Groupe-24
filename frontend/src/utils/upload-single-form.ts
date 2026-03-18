import type { PdfForm } from "@/types/pdf-form.type"

type UpdateFormAtIndexFn = (
  index: number,
  updater: (form: PdfForm) => PdfForm
) => void

/**
 * Envoie un formulaire PDF unique vers le backend.
 * Gère aussi la mise à jour de l'état du formulaire ciblé.
 */
export async function uploadSingleForm(
  index: number,
  forms: PdfForm[],
  updateFormAtIndex: UpdateFormAtIndexFn
): Promise<boolean> {
  const formToUpload = forms[index]

  if (!formToUpload) {
    return false
  }

  if (!formToUpload.id || !formToUpload.nom) {
    updateFormAtIndex(index, (form) => ({
      ...form,
      message: "Veuillez renseigner l'ID et le nom avant l'envoi.",
      uploadState: "error",
    }))
    return false
  }

  updateFormAtIndex(index, (form) => ({
    ...form,
    uploadState: "uploading",
    message: null,
  }))

  let success = false

  try {
    const formData = new FormData()
    formData.append("file", formToUpload.file)
    formData.append("id", formToUpload.id)
    formData.append("nom", formToUpload.nom)
    // Champs supplémentaires issus du formulaire pour surcharger les entités côté backend
    if (formToUpload.siret) {
      formData.append("siret", formToUpload.siret)
    }
    if (formToUpload.siren) {
      formData.append("siren", formToUpload.siren)
    }
    if (formToUpload.dateEmission) {
      formData.append("date_emission", formToUpload.dateEmission)
    }
    if (formToUpload.dateEcheance) {
      formData.append("date_echeance", formToUpload.dateEcheance)
    }
    if (formToUpload.dateExpiration) {
      formData.append("date_expiration", formToUpload.dateExpiration)
    }
    if (formToUpload.numeroFacture) {
      formData.append("numero_facture", formToUpload.numeroFacture)
    }
    if (formToUpload.modePaiement) {
      formData.append("mode_paiement", formToUpload.modePaiement)
    }
    if (typeof formToUpload.montantHt === "number") {
      formData.append("montant_ht", String(formToUpload.montantHt))
    }
    if (typeof formToUpload.montantTtc === "number") {
      formData.append("montant_ttc", String(formToUpload.montantTtc))
    }
    if (typeof formToUpload.tva === "number") {
      formData.append("tva", String(formToUpload.tva))
    }
    if (formToUpload.nomFournisseur) {
      formData.append("nom_fournisseur", formToUpload.nomFournisseur)
    }
    if (formToUpload.iban) {
      formData.append("iban", formToUpload.iban)
    }
    if (formToUpload.siretClient) {
      formData.append("siret_client", formToUpload.siretClient)
    }
    if (formToUpload.siretFournisseur) {
      formData.append("siret_fournisseur", formToUpload.siretFournisseur)
    }

    const response = await fetch("http://localhost:3000/upload-to-bdd", {
      method: "POST",
      body: formData,
    })

    if (!response.ok) {
      throw new Error("Réponse du serveur invalide")
    }

    // On lit la réponse du backend pour ce document et on pré-remplit
    // les champs du formulaire avec les données retournées.
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    let data: any = null
    try {
      data = await response.json()
      console.log("[UPLOAD /upload] Réponse backend pour le document :", {
        index,
        id: formToUpload.id,
        nom: formToUpload.nom,
        backendResponse: data,
      })
    } catch (e) {
      console.warn(
        "[UPLOAD /upload] Impossible de parser la réponse JSON du backend",
        e
      )
    }

    const entities = (data && data.entities) || {}

    // D'après `DocumentEntities` côté backend :
    // siret, montant_ht, montant_ttc, tva, date_emission, date_expiration, nom_fournisseur, iban.
    const inferredId: string =
      entities.siret ||
      data?.doc_id ||
      formToUpload.id

    const inferredNom: string =
      entities.nom_fournisseur ||
      formToUpload.nom

    const inferredDateEmission: string | undefined =
      entities.date_emission || data?.date_emission

    const inferredDateExpiration: string | undefined =
      entities.date_expiration || data?.date_expiration

    const inferredMontantTtcRaw: unknown =
      entities.montant_ttc ?? data?.montant_ttc
    const inferredMontantTtc =
      typeof inferredMontantTtcRaw === "number"
        ? inferredMontantTtcRaw
        : typeof inferredMontantTtcRaw === "string"
          ? Number.parseFloat(inferredMontantTtcRaw)
          : undefined

    const inferredMontantHtRaw: unknown =
      entities.montant_ht ?? data?.montant_ht
    const inferredMontantHt =
      typeof inferredMontantHtRaw === "number"
        ? inferredMontantHtRaw
        : typeof inferredMontantHtRaw === "string"
          ? Number.parseFloat(inferredMontantHtRaw)
          : undefined

    const inferredTvaRaw: unknown =
      entities.tva ?? data?.tva
    const inferredTva =
      typeof inferredTvaRaw === "number"
        ? inferredTvaRaw
        : typeof inferredTvaRaw === "string"
          ? Number.parseFloat(inferredTvaRaw)
          : undefined

    const inferredSiret: string | undefined =
      (entities.siret as string | undefined) || undefined

    const inferredSiren: string | undefined =
      (entities.siren as string | undefined) || undefined

    const inferredDocumentType: string | undefined =
      (data && (data.document_type as string)) || undefined

    success = true

    updateFormAtIndex(index, (form) => ({
      ...form,
      id: inferredId,
      nom: inferredNom,
      dateEmission: inferredDateEmission,
      dateExpiration: inferredDateExpiration,
      montantTtc: inferredMontantTtc,
      montantHt: inferredMontantHt,
      tva: inferredTva,
      siret: inferredSiret,
      siren: inferredSiren,
      documentType: inferredDocumentType,
      uploadState: "success",
      message: "Ce formulaire a été envoyé avec succès.",
    }))
  } catch (error) {
    console.error(error)
    updateFormAtIndex(index, (form) => ({
      ...form,
      uploadState: "error",
      message:
        "Une erreur est survenue lors de l'envoi de ce formulaire. Veuillez vérifier que le serveur est accessible.",
    }))
  } finally {
    updateFormAtIndex(index, (form) => ({
      ...form,
      uploadState: form.uploadState === "uploading" ? "idle" : form.uploadState,
    }))
  }

  return success
}
