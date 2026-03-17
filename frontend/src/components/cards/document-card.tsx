export interface DocumentCardBaseProps {
  id: number
  nom: string
  documentType: string
  date: string
  siret: string
  siren: string
  montantHt: number
  montantTtc: number
  tva: number
}

export interface DocumentCardProps extends DocumentCardBaseProps {
  iban?: string
}

export function DocumentCard(props: DocumentCardProps) {
  const {
    id,
    nom,
    documentType,
    date,
    siret,
    siren,
    montantHt,
    montantTtc,
    tva,
    iban,
  } = props

  return (
    <article
      key={id}
      className="border bg-muted/60 px-4 py-3 text-sm shadow-sm"
    >
      <p>
        <span className="font-semibold">ID :</span> {id}
      </p>
      <p>
        <span className="font-semibold">Nom :</span> {nom}
      </p>
      <p>
        <span className="font-semibold">Date :</span> {date}
      </p>
      <p>
        <span className="font-semibold">Type de fichier :</span> {documentType}
      </p>
      <p>
        <span className="font-semibold">Siret :</span> {siret}
      </p>
      <p>
        <span className="font-semibold">Siren :</span> {siren}
      </p>
      <p>
        <span className="font-semibold">Montant HT :</span> {montantHt}
      </p>
      <p>
        <span className="font-semibold">Montant TTC :</span> {montantTtc}
      </p>
      <p>
        <span className="font-semibold">TVA :</span> {tva}
      </p>
      {documentType === "facture" && iban && (
        <p>
          <span className="font-semibold">IBAN :</span> {iban}
        </p>
      )}
    </article>
  )
}

