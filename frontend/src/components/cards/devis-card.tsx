import type { DocumentItem } from "@/types/documents.type";

export interface DevisCardProps {
  document: Extract<DocumentItem, { document_type: "devis" }>
}

export function DevisCard(props: DevisCardProps) {
  const { document } = props
  const { entities } = document

  const formatValue = (value: unknown) => {
    if (value === null || value === undefined || value === "") return "—"
    return String(value)
  }

  const formatTva = () => {
    const tva = entities.tva
    if (tva === null || tva === undefined) return "—"
    return `${tva}%`
  }

  return (
    <article className="rounded-md border bg-background p-4 space-y-4 text-sm">
      <header className="mb-1">
        <h2 className="text-sm font-semibold">Devis</h2>
        <p className="text-xs text-muted-foreground">
          ID : {document.id} · Nom : {document.nom}
        </p>
      </header>

      <section className="space-y-2">
        <h2 className="text-muted-foreground">INFORMATION DU FOURNISSEUR</h2>

        <article className="grid grid-cols-2 gap-3">
          <div className="space-y-1">
            <p className="text-xs font-medium">NOM</p>
            <p className="text-sm">{formatValue(entities.nom_fournisseur)}</p>
          </div>

          <div className="space-y-1">
            <p className="text-xs font-medium">SIRET</p>
            <p className="text-sm">{formatValue(entities.siret_fournisseur ?? entities.siret)}</p>
          </div>

          <div className="space-y-1 sm:col-span-2">
            <p className="text-xs font-medium">ADRESSE</p>
            <p className="text-sm whitespace-pre-line">{formatValue(entities.adresse_fournisseur_adress)}</p>
          </div>

          <div className="space-y-1">
            <p className="text-xs font-medium">VILLE</p>
            <p className="text-sm">{formatValue(entities.adresse_fournisseur_city)}</p>
          </div>

          <div className="space-y-1">
            <p className="text-xs font-medium">CODE POSTAL</p>
            <p className="text-sm">{formatValue(entities.adresse_fournisseur_zip)}</p>
          </div>

          <div className="space-y-1">
            <p className="text-xs font-medium">SIREN</p>
            <p className="text-sm">{formatValue(entities.siren)}</p>
          </div>

          <div className="space-y-1">
            <p className="text-xs font-medium">SIRETS (DÉTECTÉS)</p>
            <p className="text-sm">
              {Array.isArray(entities.sirets) && entities.sirets.length > 0 ? entities.sirets.join(", ") : "—"}
            </p>
          </div>
        </article>
      </section>

      <section className="space-y-2">
        <h2 className="text-muted-foreground">INFORMATION DU DEVIS</h2>

        <article className="grid grid-cols-2 gap-3">
          <div className="space-y-1">
            <p className="text-xs font-medium">NUMÉRO DE DEVIS</p>
            <p className="text-sm">{formatValue(entities.numero_devis)}</p>
          </div>

          <div className="space-y-1">
            <p className="text-xs font-medium">DATE D'ÉMISSION</p>
            <p className="text-sm">{formatValue(entities.date_emission)}</p>
          </div>

          <div className="space-y-1">
            <p className="text-xs font-medium">DATE D'EXPIRATION</p>
            <p className="text-sm">{formatValue(entities.date_expiration)}</p>
          </div>

          <div className="space-y-1">
            <p className="text-xs font-medium">MONTANT HT</p>
            <p className="text-sm">{formatValue(entities.montant_ht)}</p>
          </div>

          <div className="space-y-1">
            <p className="text-xs font-medium">MONTANT TTC</p>
            <p className="text-sm">{formatValue(entities.montant_ttc)}</p>
          </div>

          <div className="space-y-1 sm:col-span-2">
            <p className="text-xs font-medium">TVA</p>
            <p className="text-sm">{formatTva()}</p>
          </div>
        </article>
      </section>

      <section className="space-y-2">
        <h2 className="text-muted-foreground">INFORMATION DU CLIENT</h2>

        <article className="grid grid-cols-2 gap-3">
          <div className="space-y-1 sm:col-span-2">
            <p className="text-xs font-medium">NOM</p>
            <p className="text-sm">{formatValue(entities.nom_client)}</p>
          </div>

          <div className="space-y-1">
            <p className="text-xs font-medium">SIRET CLIENT</p>
            <p className="text-sm">{formatValue(entities.siret_client)}</p>
          </div>

          <div className="space-y-1">
            <p className="text-xs font-medium">SIRET FOURNISSEUR</p>
            <p className="text-sm">{formatValue(entities.siret_fournisseur ?? entities.siret)}</p>
          </div>
        </article>
      </section>
    </article>
  )
}
