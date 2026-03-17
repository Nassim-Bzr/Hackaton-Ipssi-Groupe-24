import type { UploadState } from "./upload-state.type"

export type PdfForm = {
  file: File
  id: string
  nom: string
  uploadState: UploadState
  message: string | null
}
