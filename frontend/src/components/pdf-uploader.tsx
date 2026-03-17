import { PdfFormulaire } from "@/components/pdf-formulaire"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import type { PdfForm } from "@/types/pdf-form.type"
import type { UploadState } from "@/types/upload-state.type"
import { handlePdfFiles } from "@/utils/handle-pdf-files"
import { handleUploadAll as handleUploadAllUtil } from "@/utils/handle-upload-all"
import { uploadSingleForm as uploadSingleFormUtil } from "@/utils/upload-single-form"
import React, { useCallback, useRef, useState } from "react"

export function PdfUploader() {
  const [forms, setForms] = useState<PdfForm[]>([])
  const [isDragging, setIsDragging] = useState(false)
  const [isUploadingAll, setIsUploadingAll] = useState(false)
  const [globalMessage, setGlobalMessage] = useState<string | null>(null)
  const [globalStatus, setGlobalStatus] = useState<UploadState>("idle")
  const inputRef = useRef<HTMLInputElement | null>(null)

  const handleFiles = useCallback(
    (fileList: FileList | null) => {
      handlePdfFiles(fileList, {
        setForms,
        setGlobalMessage,
        setGlobalStatus,
      })
    },
    [setForms, setGlobalMessage, setGlobalStatus],
  )

  const onInputChange = useCallback<React.ChangeEventHandler<HTMLInputElement>>(
    (event) => {
      handleFiles(event.target.files)
    },
    [handleFiles],
  )

  const onDrop = useCallback<React.DragEventHandler<HTMLDivElement>>(
    (event) => {
      event.preventDefault()
      event.stopPropagation()
      setIsDragging(false)
      handleFiles(event.dataTransfer.files)
    },
    [handleFiles],
  )

  const onDragOver = useCallback<React.DragEventHandler<HTMLDivElement>>((event) => {
    event.preventDefault()
    event.stopPropagation()
    setIsDragging(true)
  }, [])

  const onDragLeave = useCallback<React.DragEventHandler<HTMLDivElement>>((event) => {
    event.preventDefault()
    event.stopPropagation()
    setIsDragging(false)
  }, [])

  const triggerFileDialog = () => {
    inputRef.current?.click()
  }

  const updateFormAtIndex = useCallback(
    (index: number, updater: (form: PdfForm) => PdfForm) => {
      setForms((prev) => {
        if (!prev[index]) return prev
        const next = [...prev]
        next[index] = updater(next[index])
        return next
      })
    },
    [setForms],
  )

  const uploadSingleForm = useCallback(
    (index: number) => uploadSingleFormUtil(index, forms, updateFormAtIndex),
    [forms, updateFormAtIndex],
  )

  const handleUploadAll = useCallback(
    () =>
      handleUploadAllUtil(forms, {
        isUploadingAll,
        setIsUploadingAll,
        setGlobalMessage,
        setGlobalStatus,
        inputRef,
        uploadSingleForm,
      }),
    [forms, isUploadingAll, setIsUploadingAll, setGlobalMessage, setGlobalStatus, inputRef, uploadSingleForm],
  )

  const hasFiles = forms.length > 0

  return (
    <section className="flex w-full max-w-xl flex-col gap-4">
      <article
        onDrop={onDrop}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        className={[
          "flex min-h-40 w-full cursor-pointer flex-col items-center justify-center border border-dashed bg-muted/40 p-6 text-center text-sm transition-colors",
          isDragging ? "border-primary bg-primary/5" : "border-border",
          isUploadingAll ? "opacity-70" : "",
        ].join(" ")}
        onClick={triggerFileDialog}
      >
        <Input
          ref={inputRef}
          type="file"
          accept="application/pdf"
          multiple
          className="hidden"
          onChange={onInputChange}
        />
        <p className="mb-2 font-medium">Déposez vos fichiers PDF ici</p>
        <p className="mb-4 text-xs text-muted-foreground">
          ou cliquez pour sélectionner plusieurs fichiers au format PDF.
        </p>
        {hasFiles ? (
          <p className="text-xs text-foreground">
            {forms.length} fichier{forms.length > 1 ? "s" : ""} sélectionné
            {forms.length > 1 ? "s" : ""}.
          </p>
        ) : (
          <p className="text-xs text-muted-foreground">
            Aucun fichier sélectionné pour le moment.
          </p>
        )}
      </article>

      {hasFiles && (
        <section className="flex flex-col gap-3">
          {forms.map((form, index) => (
            <PdfFormulaire
              key={`${form.file.name}-${index}`}
              fileName={form.file.name}
              idValue={form.id}
              nomValue={form.nom}
              uploadState={form.uploadState}
              message={form.message}
              isUploadingAll={isUploadingAll}
              onChangeId={(value) =>
                updateFormAtIndex(index, (current) => ({
                  ...current,
                  id: value,
                }))
              }
              onChangeNom={(value) =>
                updateFormAtIndex(index, (current) => ({
                  ...current,
                  nom: value,
                }))
              }
              onUpload={() => uploadSingleForm(index)}
            />
          ))}
        </section>
      )}

      <article className="flex items-center gap-2">
        <Button
          type="button"
          variant="default"
          size="sm"
          onClick={handleUploadAll}
          disabled={!hasFiles || isUploadingAll}
        >
          {isUploadingAll ? "Envoi de tous les formulaires..." : "Uploader tous les formulaires"}
        </Button>
      </article>

      {globalMessage && (
        <article
          className={[
            "border px-3 py-2 text-xs",
            globalStatus === "error"
              ? "border-destructive/40 bg-destructive/5 text-destructive"
              : "border-emerald-500/40 bg-emerald-500/5 text-emerald-600 dark:text-emerald-400",
          ].join(" ")}
        >
          {globalMessage}
        </article>
      )}
    </section>
  )
}

