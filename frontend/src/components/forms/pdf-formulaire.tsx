import { DevisForm } from "@/components/forms/devis-form"
import { FactureForm } from "@/components/forms/facture-form"
import type { PdfForm } from "@/types/pdf-form.type"
import type { UploadState } from "@/types/upload-state.type"

export type PdfFormulaireProps = {
  form: PdfForm
  uploadState: UploadState
  message: string | null
  isUploadingAll: boolean
  onChange: (updater: (current: PdfForm) => PdfForm) => void
  onUpload: () => void
}

export function PdfFormulaire({
  form,
  uploadState,
  message,
  isUploadingAll,
  onChange,
  onUpload,
}: PdfFormulaireProps) {
  const commonProps = {
    fileName: form.file.name,
    idValue: form.id,
    nomValue: form.nom,
    dateEmission: form.dateEmission,
    montantTtc: form.montantTtc,
    uploadState,
    message,
    isUploadingAll,
    onChangeId: (value: string) =>
      onChange((current) => ({
        ...current,
        id: value,
      })),
    onChangeNom: (value: string) =>
      onChange((current) => ({
        ...current,
        nom: value,
      })),
    onChangeDateEmission: (value: string) =>
      onChange((current) => ({
        ...current,
        dateEmission: value,
      })),
    onChangeMontantTtc: (value: number | undefined) =>
      onChange((current) => ({
        ...current,
        montantTtc: value,
      })),
    onUpload,
  }

  if (form.documentType === "facture") {
    return (
      <FactureForm
        {...commonProps}
        siret={form.siret}
        siren={form.siren}
        montantHt={form.montantHt}
        tva={form.tva}
        nomFournisseur={form.nomFournisseur}
        iban={form.iban}
        onChangeSiret={(value: string) =>
          onChange((current) => ({
            ...current,
            siret: value,
          }))
        }
        onChangeSiren={(value: string) =>
          onChange((current) => ({
            ...current,
            siren: value,
          }))
        }
        onChangeMontantHt={(value: number | undefined) =>
          onChange((current) => ({
            ...current,
            montantHt: value,
          }))
        }
        onChangeTva={(value: number | undefined) =>
          onChange((current) => ({
            ...current,
            tva: value,
          }))
        }
        onChangeNomFournisseur={(value: string) =>
          onChange((current) => ({
            ...current,
            nomFournisseur: value,
          }))
        }
        onChangeIban={(value: string) =>
          onChange((current) => ({
            ...current,
            iban: value,
          }))
        }
      />
    )
  }

  if (form.documentType === "devis") {
    return (
      <DevisForm
        {...commonProps}
        dateExpiration={form.dateExpiration}
        siret={form.siret}
        siren={form.siren}
        montantHt={form.montantHt}
        tva={form.tva}
        onChangeDateExpiration={(value: string) =>
          onChange((current) => ({
            ...current,
            dateExpiration: value,
          }))
        }
        onChangeSiret={(value: string) =>
          onChange((current) => ({
            ...current,
            siret: value,
          }))
        }
        onChangeSiren={(value: string) =>
          onChange((current) => ({
            ...current,
            siren: value,
          }))
        }
        onChangeMontantHt={(value: number | undefined) =>
          onChange((current) => ({
            ...current,
            montantHt: value,
          }))
        }
        onChangeTva={(value: number | undefined) =>
          onChange((current) => ({
            ...current,
            tva: value,
          }))
        }
      />
    )
  }

  // Fallback générique si le type de document n'est pas encore connu
  return (
    <FactureForm
      {...commonProps}
      siret={form.siret}
      siren={form.siren}
      montantHt={form.montantHt}
      tva={form.tva}
      nomFournisseur={form.nomFournisseur}
      iban={form.iban}
      onChangeSiret={(value: string) =>
        onChange((current) => ({
          ...current,
          siret: value,
        }))
      }
      onChangeSiren={(value: string) =>
        onChange((current) => ({
          ...current,
          siren: value,
        }))
      }
      onChangeMontantHt={(value: number | undefined) =>
        onChange((current) => ({
          ...current,
          montantHt: value,
        }))
      }
      onChangeTva={(value: number | undefined) =>
        onChange((current) => ({
          ...current,
          tva: value,
        }))
      }
      onChangeNomFournisseur={(value: string) =>
        onChange((current) => ({
          ...current,
          nomFournisseur: value,
        }))
      }
      onChangeIban={(value: string) =>
        onChange((current) => ({
          ...current,
          iban: value,
        }))
      }
    />
  )
}

