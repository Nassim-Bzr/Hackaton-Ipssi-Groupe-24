type TypeFichier = "facture" | "devis"

interface DocumentItem {
  id: number
  nom: string
  date: string
  type: TypeFichier
}

const documentsMock: DocumentItem[] = [
  { id: 1, nom: "Facture Janvier", date: "2024-01-15", type: "facture" },
  { id: 2, nom: "Devis Projet Alpha", date: "2024-02-02", type: "devis" },
  { id: 3, nom: "Facture Février", date: "2024-02-20", type: "facture" },
]

export function DocumentsPage() {
  return (
    <main className="mt-14">
      <div className="flex w-full flex-col gap-6">
        <header className="space-y-2">
          <h1 className="text-2xl font-semibold tracking-tight">Tous les documents</h1>
          <p className="max-w-xl text-sm text-muted-foreground">
            Liste des documents disponibles avec leur identifiant, nom, date et type de fichier (facture ou
            devis).
          </p>
        </header>

        <section className="grid gap-4 md:grid-cols-3">
          {documentsMock.map((document) => (
            <article
              key={document.id}
              className="border bg-muted/60 px-4 py-3 text-sm shadow-sm"
            >
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
                <span className="font-semibold">Type de fichier :</span> {document.type}
              </p>
            </article>
          ))}
        </section>
      </div>
    </main>
  )
}

