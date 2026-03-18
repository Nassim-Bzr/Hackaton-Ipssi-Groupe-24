import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import type { Facture } from "@/types/facture.type"
import { normalizeDateForDateInput } from "@/utils/normalzeDateForDateInput"
import { useEffect, useMemo, useState } from "react"

type FactureFormProps = {
  facture?: Facture
  onUpload?: (entities: Facture["entities"]) => void
  isUploading?: boolean
}

export function FactureForm({ facture, onUpload, isUploading }: FactureFormProps) {

  // Initialisation des entités
  const initialEntities = useMemo<Facture["entities"]>(() => {
    if (facture) {
      return {
        ...facture.entities,
        date_emission: normalizeDateForDateInput(facture.entities.date_emission),
        date_echeance: normalizeDateForDateInput(facture.entities.date_echeance),
      }
    }
    return {
      date_emission: "",
      date_echeance: "",
      iban: "",
      montant_ht: 0,
      montant_ttc: 0,
      nom_fournisseur: "",
      numero_facture: "",
      siren: "",
      siret: "",
      siret_client: "",
      mode_paiement: ""
    }
  }, [facture])
  const [entities, setEntities] = useState<Facture["entities"]>(initialEntities)

  // Mise à jour des entités
  useEffect(() => {
    setEntities(initialEntities)
  }, [initialEntities])

  // Affichage du formulaire
  if (!facture) return null

  return (
    <form className="rounded-md border bg-background p-4">
      <header className="mb-4">
        <h2 className="text-sm font-semibold">Facture</h2>
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
          <p className="text-xs font-medium">Numéro de facture</p>
          <Input
            value={entities.numero_facture ?? ""}
            onChange={(e) => setEntities((prev) => ({ ...prev, numero_facture: e.target.value }))}
            placeholder="Ex: F-2026-001"
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
          <p className="text-xs font-medium">Date d’échéance</p>
          <Input
            type="date"
            value={entities.date_echeance ?? ""}
            onChange={(e) => setEntities((prev) => ({ ...prev, date_echeance: e.target.value }))}
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
          <p className="text-xs font-medium">IBAN</p>
          <Input
            value={entities.iban ?? ""}
            onChange={(e) => setEntities((prev) => ({ ...prev, iban: e.target.value }))}
            placeholder="Ex: FR76..."
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

        <div className="space-y-1">
          <p className="text-xs font-medium">SIRET CLIENT</p>
          <Input
            value={entities.siret_client ?? ""}
            onChange={(e) => setEntities((prev) => ({ ...prev, siret_client: e.target.value }))}
            placeholder="14 chiffres"
          />
        </div>

        <div className="space-y-1">
          <p className="text-xs font-medium">MODE DE PAIEMENT</p>
          <Input
            value={entities.mode_paiement ?? ""}
            onChange={(e) => setEntities((prev) => ({ ...prev, mode_paiement: e.target.value }))}
            placeholder="Ex: Carte bancaire"
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
            {isUploading ? "Envoi en cours..." : "Envoyer formulaire"}
          </Button>
        </footer>
      )}
    </form>
  )
}