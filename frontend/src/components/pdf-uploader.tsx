import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import type { UploadToBddResponse, UploadToBddVariables } from "@/hooks/use-upload-to-bdd"
import { useUploadToBdd } from "@/hooks/use-upload-to-bdd"
import type { Devis } from "@/types/devis.type"
import type { Facture } from "@/types/facture.type"
import type { PdfForm } from "@/types/pdf-form.type"
import type { UploadState } from "@/types/upload-state.type"
import {
  buildAnalyzeFormData,
  buildInitialForms,
  filterPdfFiles,
  mapBackendAnalysisToPdfForm,
} from "@/utils/handle-pdf-files"
import { handleUploadAll as handleUploadAllUtil } from "@/utils/handle-upload-all"
import { useMutation } from "@tanstack/react-query"
import React, { useCallback, useRef, useState } from "react"
import { DevisForm } from "./forms/devis-form"
import { FactureForm } from "./forms/facture-form"

export function PdfUploader() {
  const [forms, setForms] = useState<PdfForm[]>([])
  const [isDragging, setIsDragging] = useState(false)
  const [isUploadingAll, setIsUploadingAll] = useState(false)
  const [uploadingIndex, setUploadingIndex] = useState<number | null>(null)
  const [globalMessage, setGlobalMessage] = useState<string | null>(null)
  const [globalStatus, setGlobalStatus] = useState<UploadState>("idle")
  const inputRef = useRef<HTMLInputElement | null>(null)

  // Upload d’un formulaire vers la BDD (hook TanStack Query)
  const uploadToBddMutation = useUploadToBdd()

  // Requête à l'API pour analyser le document
  const analyzePdfMutation = useMutation({
    mutationKey: ["analyze-pdf"],
    mutationFn: async (file: File) => {
      const formData = buildAnalyzeFormData(file)
      const response = await fetch("http://localhost:3000/upload", {
        method: "POST",
        body: formData,
      })
      if (!response.ok) {
        throw new Error("Réponse du serveur invalide lors de l'analyse du document.")
      }

      const data: Facture | Devis = await response.json()
      return { file, data }
    },
  })

  console.log("analyzePdfMutation", analyzePdfMutation.data?.data.entities)

  /**
   * Gestion des fichiers sélectionnés
   * ça permet de pouvoir gérer les fichiers sélectionnés dans la zone glisser-déposer
   * si il n'y a pas de fichiers sélectionnés, on affiche un message
   */
  const handleFiles = useCallback(
    async (fileList: FileList | null) => {
      const pdfFiles = filterPdfFiles(fileList)
      setForms(buildInitialForms(pdfFiles))
      setGlobalMessage("Analyse des documents en cours...")
      setGlobalStatus("idle")
      try {
        const analyzedForms = await Promise.all(pdfFiles.map(async (file) => {
          const result = await analyzePdfMutation.mutateAsync(file)
          const mapped = mapBackendAnalysisToPdfForm(file, result.data)
          if (result.data.document_type === "devis") return { ...mapped, devis: result.data }
          return { ...mapped, facture: result.data }
        }))

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
    },
    [analyzePdfMutation, setForms, setGlobalMessage, setGlobalStatus],
  )

  const onInputChange = useCallback<React.ChangeEventHandler<HTMLInputElement>>(
    (event) => {
      void handleFiles(event.target.files)
    },
    [handleFiles],
  )

  /**
   * Gestion du glisser-déposer
   * Comportement de base : les fichiers vont s'ouvrir dans le navigateur
   * en faisant event.preventDefault() et event.stopPropagation()
   * on évite que le navigateur ouvre les fichiers dans le navigateur
   */
  const onDrop = useCallback<React.DragEventHandler<HTMLDivElement>>(
    (event) => {
      event.preventDefault()
      event.stopPropagation()
      setIsDragging(false)
      void handleFiles(event.dataTransfer.files)
    },
    [handleFiles],
  )

  /**
   * Gestion du glisser-déposer
   * Comportement de base : les fichiers vont s'ouvrir dans le navigateur
   * en faisant event.preventDefault() et event.stopPropagation()
   * on évite que le navigateur ouvre les fichiers dans le navigateur
   */
  const onDragOver = useCallback<React.DragEventHandler<HTMLDivElement>>((event) => {
    event.preventDefault()
    event.stopPropagation()
    setIsDragging(true)
  }, [])

  /**
   * La zone glisser-déposer est un input déguisé
   * cette fonction déclanche la modal d'ouverture de fichier
   */
  const triggerFileDialog = () => {
    inputRef.current?.click()
  }

  /**
   * Mise à jour du formulaire à l'index donné
   * avec la fonction updater passée en paramètre
   * ça sert surtout pour pouvoir gérer plusieurs formulaires en même temps
   */
  const updateFormAtIndex = useCallback(
    (index: number, updater: (form: PdfForm) => PdfForm) => {
      setForms((prev) => {
        if (!prev[index]) return prev
        const next = [...prev]
        next[index] = updater(next[index])
        return next
      })
    },
    [],
  )

  const triggerAirflowForUploadResult = useCallback(
    async (data: UploadToBddResponse, variables: UploadToBddVariables) => {
      const response = await fetch("http://localhost:3000/pipeline/trigger", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          doc_id: data.doc_id,
          document_type: data.document_type,
          is_valid: data.is_valid,
          id: variables.id,
          nom: variables.nom,
        }),
      })

      if (!response.ok) {
        throw new Error("Déclenchement Airflow impossible pour ce document.")
      }
    },
    [],
  )

  /**
   * Callback pour l’upload BDD (succès) par index
   * On met à jour le formulaire à l'index donné
   * avec la fonction updater passée en paramètre
   * ça sert surtout pour pouvoir gérer plusieurs formulaires en même temps
   * la fonction updater est une fonction qui prend un formulaire et renvoie un formulaire
   * on peut donc utiliser cette fonction pour mettre à jour le formulaire à l'index donné
   * avec les nouvelles valeurs
   */
  const onUploadToBddSuccess = useCallback(
    async (data: UploadToBddResponse, variables: UploadToBddVariables) => {
      setUploadingIndex(null)

      // Mise à jour de l'état du formulaire dans l'UI
      updateFormAtIndex(variables.index, (form) => ({
        ...form,
        uploadState: "success",
        message: "Ce formulaire a été envoyé avec succès.",
      }))

      // Déclenchement de la pipeline Airflow une fois le document enregistré en BDD.
      // Le flux unitaire et le flux global partagent cette même logique.
      try {
        await triggerAirflowForUploadResult(data, variables)
      } catch (error) {
        console.error("Erreur lors du déclenchement de la pipeline Airflow :", error)
        updateFormAtIndex(variables.index, (form) => ({
          ...form,
          message: "Document envoyé mais Airflow n'a pas pu être déclenché.",
        }))
      }
    },
    [triggerAirflowForUploadResult, updateFormAtIndex],
  )

  /**
   * Callback pour l’upload BDD (erreur) par index
   * On met à jour le formulaire à l'index donné
   * avec la fonction updater passée en paramètre
   * ça sert surtout pour pouvoir gérer plusieurs formulaires en même temps
   * la fonction updater est une fonction qui prend un formulaire et renvoie un formulaire
   * on peut donc utiliser cette fonction pour mettre à jour le formulaire à l'index donné
   * avec les nouvelles valeurs
   */
  const onUploadToBddError = useCallback(
    (error: Error, variables: UploadToBddVariables) => {
      setUploadingIndex(null)
      updateFormAtIndex(variables.index, (form) => ({
        ...form,
        uploadState: "error",
        message: error.message ?? "Une erreur est survenue lors de l'envoi de ce formulaire.",
      }))
    },
    [updateFormAtIndex],
  )

  /**
   * Envoie d'une facture précise en fonction de son index
   * ça permet de pouvoir uploader une facture sans tout uploader en même temps
   */
  const handleUploadFacture = useCallback(
    (index: number) => (entities: Facture["entities"]) => {
      const form = forms[index]
      if (!form) return
      setUploadingIndex(index)
      uploadToBddMutation.mutate({ index, file: form.file, id: form.id, nom: form.nom, entities, documentType: "facture" }, { onSuccess: onUploadToBddSuccess, onError: onUploadToBddError })
    },
    [forms, uploadToBddMutation, onUploadToBddSuccess, onUploadToBddError],
  )

  /**
   * Envoie d'un devis précis en fonction de son index
   * ça permet de pouvoir uploader un devis sans tout uploader en même temps
   */
  const handleUploadDevis = useCallback(
    (index: number) => (entities: Devis["entities"]) => {
      const form = forms[index]
      if (!form) return
      setUploadingIndex(index)
      uploadToBddMutation.mutate({ index, file: form.file, id: form.id, nom: form.nom, entities, documentType: "devis" }, { onSuccess: onUploadToBddSuccess, onError: onUploadToBddError })
    },
    [forms, uploadToBddMutation, onUploadToBddSuccess, onUploadToBddError],
  )

  /**
   * Fonction wrapper qui permet facilement d'identifier le formulaire à uploader
   */
  const uploadSingleForm = useCallback(
    async (index: number) => {
      const form = forms[index]
      if (!form) return false

      if (!form.id || !form.nom) {
        updateFormAtIndex(index, (current) => ({
          ...current,
          message: "Veuillez renseigner l'ID et le nom avant l'envoi.",
          uploadState: "error",
        }))
        return false
      }

      const isFacture = form.documentType === "facture"
      const documentType = isFacture ? "facture" : "devis"
      const entities = isFacture ? form.facture?.entities : form.devis?.entities

      if (!entities) {
        updateFormAtIndex(index, (current) => ({
          ...current,
          message: "Les données du document sont incomplètes pour l'envoi.",
          uploadState: "error",
        }))
        return false
      }

      setUploadingIndex(index)
      updateFormAtIndex(index, (current) => ({
        ...current,
        uploadState: "uploading",
        message: null,
      }))

      try {
        const data = await uploadToBddMutation.mutateAsync({
          index,
          file: form.file,
          id: form.id,
          nom: form.nom,
          entities,
          documentType,
        })
        await onUploadToBddSuccess(data, {
          index,
          file: form.file,
          id: form.id,
          nom: form.nom,
          entities,
          documentType,
        })
        return true
      } catch (error) {
        const uploadError = error instanceof Error ? error : new Error("Erreur inconnue")
        onUploadToBddError(uploadError, {
          index,
          file: form.file,
          id: form.id,
          nom: form.nom,
          entities,
          documentType,
        })
        return false
      }
    },
    [forms, onUploadToBddError, onUploadToBddSuccess, updateFormAtIndex, uploadToBddMutation],
  )

  /**
   * Envoie de tous les formulaires
   * ça permet de pouvoir uploader tous les formulaires en même temps
   */
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

  /**
   * Affichage des fichiers sélectionnés
   * ça permet de pouvoir afficher les fichiers sélectionnés dans la zone glisser-déposer
   * si il n'y a pas de fichiers sélectionnés, on affiche un message
   */
  const hasFiles = forms.length > 0

  return (
    <section className="flex w-full max-w-xl flex-col gap-4">
      <article
        onDrop={onDrop}
        onDragOver={onDragOver}
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
          {forms.map((form, index) => {
            if (form.documentType === "facture") {
              return (
                <div key={`${form.file.name}-${index}`} className="space-y-2">
                  <FactureForm
                    facture={form.facture}
                    onUpload={handleUploadFacture(index)}
                    isUploading={uploadingIndex === index}
                  />
                  {form.message != null && form.message !== "" && (
                    <p
                      className={
                        form.uploadState === "error"
                          ? "text-xs text-destructive"
                          : "text-xs text-emerald-600 dark:text-emerald-400"
                      }
                    >
                      {form.message}
                    </p>
                  )}
                </div>
              )
            }
            return (
              <div key={`${form.file.name}-${index}`} className="space-y-2">
                <DevisForm
                  devis={form.devis}
                  onUpload={handleUploadDevis(index)}
                  isUploading={uploadingIndex === index}
                />
                {form.message != null && form.message !== "" && (
                  <p
                    className={
                      form.uploadState === "error"
                        ? "text-xs text-destructive"
                        : "text-xs text-emerald-600 dark:text-emerald-400"
                    }
                  >
                    {form.message}
                  </p>
                )}
              </div>
            )
          })}
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

