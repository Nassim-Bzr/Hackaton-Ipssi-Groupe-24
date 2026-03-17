import type { PdfForm } from "@/types/pdf-form.type"
import type { UploadState } from "@/types/upload-state.type"

type HandlePdfFilesOptions = {
  setForms: (forms: PdfForm[]) => void
  setGlobalMessage: (message: string | null) => void
  setGlobalStatus: (status: UploadState) => void
}

/**
 * Traite une liste de fichiers en ne conservant que les PDF,
 * appelle le backend pour analyser chaque document
 * et pré-remplit les formulaires avec les données retournées.
 *
 * Cette étape ne déclenche PAS d'enregistrement en base :
 * la BDD n'est mise à jour que via la route `/upload-to-bdd`
 * appelée au clic sur les boutons d'upload.
 */
export async function handlePdfFiles(
  fileList: FileList | null,
  options: HandlePdfFilesOptions
) {
  const { setForms, setGlobalMessage, setGlobalStatus } = options

  if (!fileList) return

  const selected = Array.from(fileList)
  const pdfFiles = selected.filter(
    (file) =>
      file.type === "application/pdf" ||
      file.name.toLowerCase().endsWith(".pdf")
  )

  if (pdfFiles.length === 0) {
    setForms([])
    setGlobalMessage("Veuillez sélectionner uniquement des fichiers PDF.")
    setGlobalStatus("error")
    return
  }

  // On initialise des formulaires vides pendant l'analyse
  const initialForms: PdfForm[] = pdfFiles.map((file) => ({
    file,
    id: "",
    nom: "",
    uploadState: "idle",
    message: "Analyse du document en cours...",
  }))

  setForms(initialForms)
  setGlobalMessage("Analyse des documents en cours...")
  setGlobalStatus("idle")

  try {
    const analyzedForms: PdfForm[] = await Promise.all(
      pdfFiles.map(async (file) => {
        const formData = new FormData()
        formData.append("file", file)
        // On envoie des valeurs techniques pour id/nom ; elles pourront
        // être écrasées ensuite par l'utilisateur dans le formulaire.
        formData.append("id", file.name)
        formData.append("nom", file.name.replace(/\.pdf$/i, ""))

        const response = await fetch("http://localhost:3000/upload", {
          method: "POST",
          body: formData,
        })

        if (!response.ok) {
          throw new Error("Réponse du serveur invalide lors de l'analyse du document.")
        }

        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        let data: any = {}
        try {
          data = await response.json()
          console.log("[UPLOAD /upload] Réponse backend (analyse) pour le document :", {
            fileName: file.name,
            backendResponse: data,
          })
        } catch {
          // Si la réponse n'est pas un JSON valide, on retombe sur un formulaire quasi-vide.
          console.warn(
            "[UPLOAD /upload] Impossible de parser la réponse JSON du backend (analyse)",
          )
        }

        const entities = (data && data.entities) || {}

        const inferredId: string =
          entities.siret ||
          data?.doc_id ||
          ""

        const inferredNom: string =
          entities.nom_fournisseur ||
          data?.nom ||
          ""

        const inferredDateEmission: string | undefined =
          entities.date_emission || data?.metadata?.date_emission

        const inferredDateExpiration: string | undefined =
          entities.date_expiration || data?.metadata?.date_expiration

        const inferredMontantTtcRaw: unknown =
          entities.montant_ttc ?? data?.metadata?.montant_ttc
        const inferredMontantTtc =
          typeof inferredMontantTtcRaw === "number"
            ? inferredMontantTtcRaw
            : typeof inferredMontantTtcRaw === "string"
              ? Number.parseFloat(inferredMontantTtcRaw)
              : undefined

        const inferredMontantHtRaw: unknown =
          entities.montant_ht ?? data?.metadata?.montant_ht
        const inferredMontantHt =
          typeof inferredMontantHtRaw === "number"
            ? inferredMontantHtRaw
            : typeof inferredMontantHtRaw === "string"
              ? Number.parseFloat(inferredMontantHtRaw)
              : undefined

        const inferredTvaRaw: unknown =
          entities.tva ?? data?.metadata?.tva
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

        const inferredNomFournisseur: string | undefined =
          (entities.nom_fournisseur as string | undefined) || undefined

        const inferredIban: string | undefined =
          (entities.iban as string | undefined) || undefined

        const inferredDocumentType: string | undefined =
          (data && (data.document_type as string)) || undefined

        return {
          file,
          id: inferredId,
          nom: inferredNom,
          dateEmission: inferredDateEmission,
          dateExpiration: inferredDateExpiration,
          montantTtc: inferredMontantTtc,
          montantHt: inferredMontantHt,
          tva: inferredTva,
          siret: inferredSiret,
          siren: inferredSiren,
          nomFournisseur: inferredNomFournisseur,
          iban: inferredIban,
          documentType: inferredDocumentType,
          uploadState: "idle",
          message: null,
        }
      }),
    )

    setForms(analyzedForms)
    setGlobalMessage(null)
    setGlobalStatus("success")
  } catch (error) {
    console.error("Erreur lors de l'analyse des PDFs côté backend :", error)
    setForms(
      pdfFiles.map((file) => ({
        file,
        id: "",
        nom: "",
        uploadState: "error",
        message:
          "Impossible d'analyser automatiquement ce document pour le moment. Vous pouvez renseigner les champs manuellement.",
      })),
    )
    setGlobalMessage(
      "Une erreur est survenue lors de l'analyse automatique des documents. Vous pouvez compléter les formulaires manuellement.",
    )
    setGlobalStatus("error")
  }
}
