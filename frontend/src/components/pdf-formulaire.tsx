import React from "react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import type { UploadState } from "@/types/upload-state.type"

export type PdfFormulaireProps = {
  fileName: string
  idValue: string
  nomValue: string
  uploadState: UploadState
  message: string | null
  isUploadingAll: boolean
  onChangeId: (value: string) => void
  onChangeNom: (value: string) => void
  onUpload: () => void
}

export function PdfFormulaire({
  fileName,
  idValue,
  nomValue,
  uploadState,
  message,
  isUploadingAll,
  onChangeId,
  onChangeNom,
  onUpload,
}: PdfFormulaireProps) {
  return (
    <article className="space-y-2 border bg-background p-3 text-xs">
      <p className="font-medium break-all">{fileName}</p>

      <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
        <div className="flex flex-col gap-1">
          <label className="text-xs">
            ID
            <Input
              value={idValue}
              onChange={(event: React.ChangeEvent<HTMLInputElement>) => onChangeId(event.target.value)}
              className="mt-1 h-8 text-xs"
            />
          </label>
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-xs">
            Nom
            <Input
              value={nomValue}
              onChange={(event: React.ChangeEvent<HTMLInputElement>) => onChangeNom(event.target.value)}
              className="mt-1 h-8 text-xs"
            />
          </label>
        </div>
      </div>

      <div className="flex items-center justify-between gap-2">
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={onUpload}
          disabled={uploadState === "uploading" || isUploadingAll}
        >
          {uploadState === "uploading" ? "Envoi en cours..." : "Uploader ce formulaire"}
        </Button>

        {uploadState === "success" && (
          <span className="text-xs text-emerald-600 dark:text-emerald-400">Envoyé</span>
        )}
        {uploadState === "error" && message && <span className="text-xs text-destructive">Erreur</span>}
      </div>

      {message && (
        <p
          className={[
            "border px-2 py-1",
            uploadState === "error"
              ? "border-destructive/40 bg-destructive/5 text-destructive"
              : "border-emerald-500/40 bg-emerald-500/5 text-emerald-600 dark:text-emerald-400",
          ].join(" ")}
        >
          {message}
        </p>
      )}
    </article>
  )
}

