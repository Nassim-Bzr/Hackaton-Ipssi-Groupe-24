import type { DocumentItem } from "@/types/documents.type";

export interface DevisCardProps {
  document: DocumentItem
}

export function DevisCard(props: DevisCardProps) {
  const { document } = props

  return (
    <article className="border bg-muted/60 px-4 py-3 text-sm shadow-sm">
      <h3 className="mb-2 font-bold text-lg underline underline-offset-4">Devis</h3>
      <div className="grid grid-cols-2 gap-2">
        <p className="font-semibold">Numéro :</p>
        <p>{document.entities.numero_devis}</p>
      </div>
      <div className="grid grid-cols-2 gap-2">
        <p className="font-semibold">ID :</p>
        <p>{document.id}</p>
      </div>
      <div className="grid grid-cols-2 gap-2">
        <p className="font-semibold">Nom :</p>
        <p>{document.nom}</p>
      </div>
      <div className="grid grid-cols-2 gap-2">
        <p className="font-semibold">Date expiration :</p>
        <p>{document.entities.date_expiration}</p>
      </div>
      <div className="grid grid-cols-2 gap-2">
        <p className="font-semibold">Date émission :</p>
        <p>{document.entities.date_emission}</p>
      </div>
      <div className="grid grid-cols-2 gap-2">
        <p className="font-semibold">Type de fichier :</p>
        <p>{document.document_type}</p>
      </div>
      <div className="grid grid-cols-2 gap-2">
        <p className="font-semibold">Siret :</p>
        <p>{document.entities.siret}</p>
      </div>
      <div className="grid grid-cols-2 gap-2">
        <p className="font-semibold">Siren :</p>
        <p>{document.entities.siren}</p>
      </div>
      <div className="grid grid-cols-2 gap-2">
        <p className="font-semibold">Montant HT :</p>
        <p>{document.entities.montant_ht}</p>
      </div>
      <div className="grid grid-cols-2 gap-2">
        <p className="font-semibold">Montant TTC :</p>
        <p>{document.entities.montant_ttc}</p>
      </div>
      <div className="grid grid-cols-2 gap-2">
        <p className="font-semibold">TVA :</p>
        <p>{document.entities.tva != null ? `${document.entities.tva}%` : ""}</p>
      </div>
    </article>
  )
}
