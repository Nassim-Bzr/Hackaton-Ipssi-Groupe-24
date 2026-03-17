import type { PdfForm } from "@/types/pdf-form.type"
import type { UploadState } from "@/types/upload-state.type"

type HandlePdfFilesOptions = {
  setForms: (forms: PdfForm[]) => void
  setGlobalMessage: (message: string | null) => void
  setGlobalStatus: (status: UploadState) => void
}

/**
 * Traite une liste de fichiers en ne conservant que les PDF,
 * déclenche l'envoi automatique vers le backend
 * et met à jour l'état global via les callbacks fournis.
 */
export function handlePdfFiles(
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

  // Envoi automatique des fichiers PDF sélectionnés vers le backend
  // sans nécessiter de clic sur un bouton.
  pdfFiles.forEach(async (file) => {
    try {
      const formData = new FormData()
      formData.append("file", file)

      await fetch("http://localhost:3000", {
        method: "POST",
        body: formData,
      })
    } catch (error) {
      console.error(
        "Erreur lors de la requête automatique vers le backend",
        error
      )
    }
  })

  const newForms: PdfForm[] = pdfFiles.map((file) => ({
    file,
    id: "",
    nom: file.name.replace(/\.pdf$/i, ""),
    uploadState: "idle",
    message: null,
  }))

  setForms(newForms)
  setGlobalMessage(null)
  setGlobalStatus("idle")
}
