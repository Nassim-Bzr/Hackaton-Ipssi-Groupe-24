import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import type { Devis } from "@/types/devis.type"
import { normalizeDateForDateInput } from "@/utils/normalzeDateForDateInput"
import { useEffect, useMemo, useState } from "react"

type DevisFormProps = {
  devis?: Devis
  onUpload?: (entities: Devis["entities"]) => void
  isUploading?: boolean
}

export function DevisForm({ devis, onUpload, isUploading }: DevisFormProps) {
  const initialEntities = useMemo<Devis["entities"]>(() => {
    if (devis) {
      return {
        ...devis.entities,
        date_emission: normalizeDateForDateInput(devis.entities.date_emission),
        date_expiration: normalizeDateForDateInput(devis.entities.date_expiration),
      }
    }
    return {
      date_emission: "",
      date_expiration: "",
      montant_ht: 0,
      montant_ttc: 0,
      tva: 0,
      nom_fournisseur: "",
      numero_devis: "",
      siren: "",
      siret: "",
    }
  }, [devis])

  const [entities, setEntities] = useState<Devis["entities"]>(initialEntities)

  useEffect(() => {
    setEntities(initialEntities)
  }, [initialEntities])

  if (!devis) return null

  return (
    <form className="rounded-md border bg-background p-4">
      <header className="mb-4">
        <h2 className="text-sm font-semibold">Devis</h2>
        <p className="text-xs text-muted-foreground">
          Champs pré-remplis automatiquement. Vous pouvez les modifier si nécessaire.
        </p>
      </header>

      <section className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <div className="space-y-1">
          <p className="text-xs font-medium">Nom fournisseur</p>
          <Input
            value={entities.nom_fournisseur ?? ""}
            onChange={(e) => setEntities((prev) => ({ ...prev, nom_fournisseur: e.target.value }))}
            placeholder="Ex: ACME SAS"
          />
        </div>

        <div className="space-y-1">
          <p className="text-xs font-medium">Numéro de devis</p>
          <Input
            value={entities.numero_devis ?? ""}
            onChange={(e) => setEntities((prev) => ({ ...prev, numero_devis: e.target.value }))}
            placeholder="Ex: D-2026-001"
          />
        </div>

        <div className="space-y-1">
          <p className="text-xs font-medium">Date d’émission</p>
          <Input
            type="date"
            value={entities.date_emission ?? ""}
            onChange={(e) => setEntities((prev) => ({ ...prev, date_emission: e.target.value }))}
          />
        </div>

        <div className="space-y-1">
          <p className="text-xs font-medium">Date d’expiration</p>
          <Input
            type="date"
            value={entities.date_expiration ?? ""}
            onChange={(e) => setEntities((prev) => ({ ...prev, date_expiration: e.target.value }))}
          />
        </div>

        <div className="space-y-1">
          <p className="text-xs font-medium">Montant HT</p>
          <Input
            inputMode="decimal"
            value={Number.isFinite(entities.montant_ht) ? String(entities.montant_ht) : ""}
            onChange={(e) =>
              setEntities((prev) => ({
                ...prev,
                montant_ht: e.target.value === "" ? 0 : Number.parseFloat(e.target.value),
              }))
            }
            placeholder="0.00"
          />
        </div>

        <div className="space-y-1">
          <p className="text-xs font-medium">Montant TTC</p>
          <Input
            inputMode="decimal"
            value={Number.isFinite(entities.montant_ttc) ? String(entities.montant_ttc) : ""}
            onChange={(e) =>
              setEntities((prev) => ({
                ...prev,
                montant_ttc: e.target.value === "" ? 0 : Number.parseFloat(e.target.value),
              }))
            }
            placeholder="0.00"
          />
        </div>

        <div className="space-y-1 sm:col-span-2">
          <p className="text-xs font-medium">TVA</p>
          <Input
            inputMode="decimal"
            value={Number.isFinite(entities.tva) ? String(entities.tva) : ""}
            onChange={(e) =>
              setEntities((prev) => ({
                ...prev,
                tva: e.target.value === "" ? 0 : Number.parseFloat(e.target.value),
              }))
            }
            placeholder="0.00"
          />
        </div>

        <div className="space-y-1">
          <p className="text-xs font-medium">SIREN</p>
          <Input
            value={entities.siren ?? ""}
            onChange={(e) => setEntities((prev) => ({ ...prev, siren: e.target.value }))}
            placeholder="9 chiffres"
          />
        </div>

        <div className="space-y-1">
          <p className="text-xs font-medium">SIRET</p>
          <Input
            value={entities.siret ?? ""}
            onChange={(e) => setEntities((prev) => ({ ...prev, siret: e.target.value }))}
            placeholder="14 chiffres"
          />
        </div>
      </section>

      {onUpload && (
        <footer className="mt-4 flex justify-end">
          <Button
            type="button"
            variant="default"
            size="sm"
            disabled={isUploading}
            onClick={() => onUpload(entities)}
          >
            {isUploading ? "Envoi en cours..." : "Envoyer devis"}
          </Button>
        </footer>
      )}
    </form>
  )
}