import type { DocumentItem } from "@/types/documents.type"

export interface FactureCardProps {
  document: DocumentItem
}

export function FactureCard(props: FactureCardProps) {
  const { document } = props

  return (
    <article className="border bg-muted/60 px-4 py-3 text-sm shadow-sm">
      <h3 className="mb-2 font-bold text-lg underline underline-offset-4">Facture</h3>
      <p>
        <span className="font-semibold">Numéro :</span> {document.entities.numero_facture}
      </p>
      <p>
        <span className="font-semibold">ID :</span> {document.id}
      </p>
      <p>
        <span className="font-semibold">Nom :</span> {document.nom}
      </p>
      <p>
        <span className="font-semibold">Date :</span> {document.date}
      </p>
      <p>
        <span className="font-semibold">Type de fichier :</span> {document.document_type}
      </p>
      <p>
        <span className="font-semibold">Siret :</span> {document.entities.siret}
      </p>
      <p>
        <span className="font-semibold">Siren :</span> {document.entities.siren}
      </p>
      <p>
        <span className="font-semibold">Montant HT :</span> {document.entities.montant_ht}
      </p>
      <p>
        <span className="font-semibold">Montant TTC :</span> {document.entities.montant_ttc}
      </p>
      <p>
        <span className="font-semibold">TVA :</span> {document.entities.tva}
      </p>
      {document.entities.iban ? (
        <p>
          <span className="font-semibold">IBAN :</span> {document.entities.iban}
        </p>
      ) : null}
    </article>
  )
}
