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

    const response = await fetch("http://localhost:3000/upload", {
      method: "POST",
      body: formData,
    })

    if (!response.ok) {
      throw new Error("Réponse du serveur invalide")
    }

    success = true

    updateFormAtIndex(index, (form) => ({
      ...form,
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
