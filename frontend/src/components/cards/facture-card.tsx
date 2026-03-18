import type { DocumentItem } from "@/types/documents.type";

export interface FactureCardProps {
  document: Extract<DocumentItem, { document_type: "facture" }>
}

export function FactureCard(props: FactureCardProps) {
  const { document } = props
  const { entities } = document
  console.log(entities);

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
        <h2 className="text-sm font-semibold">Facture</h2>
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

        </article>
      </section>

      <section className="space-y-2">
        <h2 className="text-muted-foreground">INFORMATION DE LA FACTURE</h2>

        <article className="grid grid-cols-2 gap-3">
          <div className="space-y-1">
            <p className="text-xs font-medium">NUMÉRO DE FACTURE</p>
            <p className="text-sm">{formatValue(entities.numero_facture)}</p>
          </div>

          <div className="space-y-1">
            <p className="text-xs font-medium">DATE D'ÉMISSION</p>
            <p className="text-sm">{formatValue(entities.date_emission)}</p>
          </div>

          <div className="space-y-1">
            <p className="text-xs font-medium">DATE D'ÉCHÉANCE</p>
            <p className="text-sm">{formatValue(entities.date_echeance)}</p>
          </div>

          <div className="space-y-1">
            <p className="text-xs font-medium">MODE DE PAIEMENT</p>
            <p className="text-sm">{formatValue(entities.mode_paiement)}</p>
          </div>

          <div className="space-y-1 sm:col-span-2">
            <p className="text-xs font-medium">IBAN</p>
            <p className="text-sm">{formatValue(entities.iban)}</p>
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
          <div className="space-y-1">
            <p className="text-xs font-medium">NOM</p>
            <p className="text-sm">{formatValue(entities.nom_client)}</p>
          </div>

          <div className="space-y-1">
            <p className="text-xs font-medium">NOM ENTREPRISE</p>
            <p className="text-sm">{formatValue(entities.nom_entreprise_client)}</p>
          </div>

          <div className="space-y-1">
            <p className="text-xs font-medium">ADRESSE</p>
            <p className="text-sm whitespace-pre-line">{formatValue(entities.adresse_client_adress)}</p>
          </div>

          <div className="space-y-1">
            <p className="text-xs font-medium">CODE POSTAL</p>
            <p className="text-sm">{formatValue(entities.adresse_client_zip)}</p>
          </div>

          <div className="space-y-1">
            <p className="text-xs font-medium">VILLE</p>
            <p className="text-sm">{formatValue(entities.adresse_client_city)}</p>
          </div>

          <div className="space-y-1">
            <p className="text-xs font-medium">SIRET CLIENT</p>
            <p className="text-sm">{formatValue(entities.siret_client)}</p>
          </div>

        </article>
      </section>
    </article>
  )
}
