import React, { useCallback, useRef, useState } from "react"

import { Button } from "@/components/ui/button"

type UploadState = "idle" | "uploading" | "success" | "error"

export function PdfUploader() {
  const [files, setFiles] = useState<File[]>([])
  const [isDragging, setIsDragging] = useState(false)
  const [uploadState, setUploadState] = useState<UploadState>("idle")
  const [message, setMessage] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement | null>(null)

  const handleFiles = useCallback((fileList: FileList | null) => {
    if (!fileList) return

    const selected = Array.from(fileList)
    const pdfFiles = selected.filter(
      (file) => file.type === "application/pdf" || file.name.toLowerCase().endsWith(".pdf"),
    )

    if (pdfFiles.length === 0) {
      setMessage("Veuillez sélectionner uniquement des fichiers PDF.")
      setUploadState("error")
      return
    }

    setFiles(pdfFiles)
    setMessage(null)
    setUploadState("idle")
  }, [])

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

  const handleUpload = async () => {
    if (!files.length || uploadState === "uploading") {
      return
    }

    setUploadState("uploading")
    setMessage(null)

    try {
      const formData = new FormData()
      // Ajout de chaque PDF sous la même clé pour un traitement côté backend.
      files.forEach((file) => {
        formData.append("files", file)
      })

      const response = await fetch("http://localhost:3000/upload", {
        method: "POST",
        body: formData,
      })

      if (!response.ok) {
        throw new Error("Réponse du serveur invalide")
      }

      setUploadState("success")
      setMessage("Les fichiers PDF ont été envoyés avec succès.")
      setFiles([])
      if (inputRef.current) {
        inputRef.current.value = ""
      }
    } catch (error) {
      console.error(error)
      setUploadState("error")
      setMessage(
        "Une erreur est survenue lors de l'envoi des fichiers. Veuillez vérifier que le serveur est accessible.",
      )
    } finally {
      setUploadState((current) => (current === "uploading" ? "idle" : current))
    }
  }

  const hasFiles = files.length > 0
  const isUploading = uploadState === "uploading"

  return (
    <section className="flex w-full max-w-xl flex-col gap-4">
      <article
        onDrop={onDrop}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        className={[
          "flex min-h-40 w-full cursor-pointer flex-col items-center justify-center rounded-md border border-dashed bg-muted/40 p-6 text-center text-sm transition-colors",
          isDragging ? "border-primary bg-primary/5" : "border-border",
          isUploading ? "opacity-70" : "",
        ].join(" ")}
        onClick={triggerFileDialog}
      >
        <input
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
            {files.length} fichier{files.length > 1 ? "s" : ""} sélectionné
            {files.length > 1 ? "s" : ""}.
          </p>
        ) : (
          <p className="text-xs text-muted-foreground">
            Aucun fichier sélectionné pour le moment.
          </p>
        )}
      </article>

      {hasFiles && (
        <ul className="max-h-32 list-disc space-y-1 overflow-auto pl-5 text-xs text-muted-foreground">
          {files.map((file) => (
            <li key={file.name}>{file.name}</li>
          ))}
        </ul>
      )}

      <article className="flex items-center gap-2">
        <Button
          type="button"
          variant="default"
          size="sm"
          onClick={handleUpload}
          disabled={!hasFiles || isUploading}
        >
          {isUploading ? "Envoi en cours..." : "Envoyer les PDF"}
        </Button>
      </article>

      {message && (
        <article
          className={[
            "rounded-md border px-3 py-2 text-xs",
            uploadState === "error"
              ? "border-destructive/40 bg-destructive/5 text-destructive"
              : "border-emerald-500/40 bg-emerald-500/5 text-emerald-600 dark:text-emerald-400",
          ].join(" ")}
        >
          {message}
        </article>
      )}
    </section>
  )
}

