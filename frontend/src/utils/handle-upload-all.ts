import type React from "react"

import type { PdfForm } from "@/types/pdf-form.type"
import type { UploadState } from "@/types/upload-state.type"

type HandleUploadAllOptions = {
  isUploadingAll: boolean
  setIsUploadingAll: (value: boolean) => void
  setGlobalMessage: (message: string | null) => void
  setGlobalStatus: (status: UploadState) => void
  inputRef: React.RefObject<HTMLInputElement | null>
  uploadSingleForm: (index: number) => Promise<boolean>
}

/**
 * Gère l'envoi de tous les formulaires présents dans la liste.
 */
export async function handleUploadAll(
  forms: PdfForm[],
  {
    isUploadingAll,
    setIsUploadingAll,
    setGlobalMessage,
    setGlobalStatus,
    inputRef,
    uploadSingleForm,
  }: HandleUploadAllOptions
) {
  if (!forms.length || isUploadingAll) {
    return
  }

  setIsUploadingAll(true)
  setGlobalMessage(null)
  setGlobalStatus("idle")

  let hadError = false

  for (let index = 0; index < forms.length; index++) {
    const form = forms[index]
    if (!form) continue
    if (form.uploadState === "success") continue

    const success = await uploadSingleForm(index)
    if (!success) {
      hadError = true
    }
  }

  setIsUploadingAll(false)

  if (hadError) {
    setGlobalStatus("error")
    setGlobalMessage("Certains formulaires n'ont pas pu être envoyés.")
  } else {
    setGlobalStatus("success")
    setGlobalMessage("Tous les formulaires ont été envoyés avec succès.")
    setIsUploadingAll(false)
    if (inputRef.current) {
      inputRef.current.value = ""
    }
  }
}
