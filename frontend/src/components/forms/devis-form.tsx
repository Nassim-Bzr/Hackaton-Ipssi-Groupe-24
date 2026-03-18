import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import type { Devis } from "@/types/devis.type"
import { normalizeDateForDateInput } from "@/utils/normalzeDateForDateInput"
import { useEffect, useMemo, useState } from "react"
import { Label } from "../ui/label"

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
      adresse_fournisseur_adress: "",
      adresse_fournisseur_zip: "",
      adresse_fournisseur_city: "",
      nom_entreprise_client: "",
      adresse_client_adress: "",
      adresse_client_zip: "",
      adresse_client_city: "",
      nom_client: "",
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
    <form className="rounded-md border bg-background p-4 space-y-4">
      <header className="mb-4">
        <h2 className="text-sm font-semibold">Devis</h2>
        <p className="text-xs text-muted-foreground">
          Champs pré-remplis automatiquement. Vous pouvez les modifier si nécessaire.
        </p>
      </header>

      <section className="space-y-2">
        <h2 className="text-muted-foreground">INFORMATION DU FOURNISSEUR</h2>

        <article className="grid grid-cols-2 gap-3">
          <div className="space-y-1">
            <Label className="text-xs font-medium">NOM</Label>
            <Input
              value={entities.nom_fournisseur ?? ""}
              onChange={(e) => setEntities((prev) => ({ ...prev, nom_fournisseur: e.target.value }))}
              placeholder="Ex: ACME SAS"
            />
          </div>

          <div className="space-y-1">
            <Label className="text-xs font-medium">ADRESSE</Label>
            <Input
              value={entities.adresse_fournisseur_adress ?? ""}
              onChange={(e) => setEntities((prev) => ({ ...prev, adresse_fournisseur_adress: e.target.value }))}
              placeholder="Ex: 123 Main St, Anytown, USA"
            />
          </div>

          <div className="space-y-1">
            <Label className="text-xs font-medium">VILLE</Label>
            <Input
              value={entities.adresse_fournisseur_city ?? ""}
              onChange={(e) => setEntities((prev) => ({ ...prev, adresse_fournisseur_city: e.target.value }))}
              placeholder="Ex: Paris"
            />
          </div>

          <div className="space-y-1">
            <Label className="text-xs font-medium">CODE POSTAL</Label>
            <Input
              value={entities.adresse_fournisseur_zip ?? ""}
              onChange={(e) => setEntities((prev) => ({ ...prev, adresse_fournisseur_zip: e.target.value }))}
              placeholder="Ex: 75001"
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
        </article>
      </section>

      <section className="space-y-2">
        <h2 className="text-muted-foreground">INFORMATION DU DEVIS</h2>

        <article className="grid grid-cols-2 gap-3">
          <div className="space-y-1">
            <Label className="text-xs font-medium">NUMÉRO DE DEVIS</Label>
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

          <div className="space-y-1">
            <p className="text-xs font-medium">TVA</p>
            <Input
              inputMode="decimal"
              value={Number.isFinite(entities.tva) ? String(entities.tva) : ""}
              onChange={(e) => setEntities((prev) => ({ ...prev, tva: Number.parseFloat(e.target.value) }))}
              placeholder="0.00"
            />
          </div>
        </article>
      </section>

      <section className="space-y-2">
        <h2 className="text-muted-foreground">INFORMATION DU CLIENT</h2>

        <article className="grid grid-cols-2 gap-3">
          <div className="space-y-1">
            <Label className="text-xs font-medium">NOM</Label>
            <Input
              value={entities.nom_client ?? ""}
              onChange={(e) =>
                setEntities((prev) => ({ ...prev, nom_client: e.target.value }))
              }
              placeholder="Ex: John Doe"
            />
          </div>

          <div className="space-y-1">
            <Label className="text-xs font-medium">NOM ENTREPRISE</Label>
            <Input
              value={entities.nom_entreprise_client ?? ""}
              onChange={(e) => setEntities((prev) => ({ ...prev, nom_entreprise_client: e.target.value }))}
              placeholder="Ex: John Doe"
            />
          </div>

          <div className="space-y-1">
            <Label className="text-xs font-medium">ADRESSE</Label>
            <Input
              value={entities.adresse_client_adress ?? ""}
              onChange={(e) => setEntities((prev) => ({ ...prev, adresse_client_adress: e.target.value }))}
              placeholder="Ex: 29, avenue de Georges"
            />
          </div>

          <div className="space-y-1">
            <Label className="text-xs font-medium">CODE POSTAL</Label>
            <Input
              value={entities.adresse_client_zip ?? ""}
              onChange={(e) => setEntities((prev) => ({ ...prev, adresse_client_zip: e.target.value }))}
              placeholder="Ex: 37647"
            />
          </div>

          <div className="space-y-1">
            <Label className="text-xs font-medium">VILLE</Label>
            <Input
              value={entities.adresse_client_city ?? ""}
              onChange={(e) => setEntities((prev) => ({ ...prev, adresse_client_city: e.target.value }))}
              placeholder="Ex: Benard"
            />
          </div>
        </article>
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