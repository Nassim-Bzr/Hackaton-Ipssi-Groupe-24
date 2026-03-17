import React from "react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import type { UploadState } from "@/types/upload-state.type"

type DevisFormProps = {
  fileName: string
  idValue: string
  nomValue: string
  dateEmission?: string
  dateExpiration?: string
  siret?: string
  siren?: string
  montantTtc?: number
  montantHt?: number
  tva?: number
  uploadState: UploadState
  message: string | null
  isUploadingAll: boolean
  onChangeId: (value: string) => void
  onChangeNom: (value: string) => void
  onChangeDateEmission: (value: string) => void
  onChangeDateExpiration: (value: string) => void
  onChangeSiret: (value: string) => void
  onChangeSiren: (value: string) => void
  onChangeMontantTtc: (value: number | undefined) => void
  onChangeMontantHt: (value: number | undefined) => void
  onChangeTva: (value: number | undefined) => void
  onUpload: () => void
}

export function DevisForm({
  fileName,
  idValue,
  nomValue,
  dateEmission,
  dateExpiration,
  siret,
  siren,
  montantTtc,
  montantHt,
  tva,
  uploadState,
  message,
  isUploadingAll,
  onChangeId,
  onChangeNom,
  onChangeDateEmission,
  onChangeDateExpiration,
  onChangeSiret,
  onChangeSiren,
  onChangeMontantTtc,
  onChangeMontantHt,
  onChangeTva,
  onUpload,
}: DevisFormProps) {
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

        <div className="flex flex-col gap-1">
          <label className="text-xs">
            Date d&apos;émission
            <Input
              type="date"
              value={dateEmission ?? ""}
              onChange={(event: React.ChangeEvent<HTMLInputElement>) => onChangeDateEmission(event.target.value)}
              className="mt-1 h-8 text-xs"
            />
          </label>
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-xs">
            Date d&apos;expiration
            <Input
              type="date"
              value={dateExpiration ?? ""}
              onChange={(event: React.ChangeEvent<HTMLInputElement>) => onChangeDateExpiration(event.target.value)}
              className="mt-1 h-8 text-xs"
            />
          </label>
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-xs">
            SIRET
            <Input
              value={siret ?? ""}
              onChange={(event: React.ChangeEvent<HTMLInputElement>) => onChangeSiret(event.target.value)}
              className="mt-1 h-8 text-xs"
            />
          </label>
        </div>

        <div className="flex flex-col gap-1">
          <label>
            SIREN
            <Input
              value={siren ?? ""}
              onChange={(event: React.ChangeEvent<HTMLInputElement>) => onChangeSiren(event.target.value)}
              className="mt-1 h-8 text-xs"
            />
          </label>
        </div>

        <div className="flex flex-col gap-1">
          <label>
            Montant TTC
            <Input
              type="number"
              value={Number.isFinite(montantTtc ?? NaN) ? String(montantTtc) : ""}
              onChange={(event: React.ChangeEvent<HTMLInputElement>) => {
                const value = event.target.value
                const parsed = value === "" ? undefined : Number.parseFloat(value)
                onChangeMontantTtc(Number.isNaN(parsed as number) ? undefined : (parsed as number | undefined))
              }}
              className="mt-1 h-8 text-xs"
            />
          </label>
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-xs">
            Montant HT
            <Input
              type="number"
              value={Number.isFinite(montantHt ?? NaN) ? String(montantHt) : ""}
              onChange={(event: React.ChangeEvent<HTMLInputElement>) => {
                const value = event.target.value
                const parsed = value === "" ? undefined : Number.parseFloat(value)
                onChangeMontantHt(Number.isNaN(parsed as number) ? undefined : (parsed as number | undefined))
              }}
              className="mt-1 h-8 text-xs"
            />
          </label>
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-xs">
            TVA
            <Input
              type="number"
              value={Number.isFinite(tva ?? NaN) ? String(tva) : ""}
              onChange={(event: React.ChangeEvent<HTMLInputElement>) => {
                const value = event.target.value
                const parsed = value === "" ? undefined : Number.parseFloat(value)
                onChangeTva(Number.isNaN(parsed as number) ? undefined : (parsed as number | undefined))
              }}
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
          {uploadState === "uploading" ? "Envoi en cours..." : "Uploader ce devis"}
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

