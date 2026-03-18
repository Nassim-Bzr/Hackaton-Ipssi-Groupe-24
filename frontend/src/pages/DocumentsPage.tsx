import { DevisCard } from "@/components/cards/devis-card"
import { FactureCard } from "@/components/cards/facture-card"
import { useGetDocuments } from "@/hooks/use-get-documents"

export function DocumentsPage() {

  const { documents, isPending } = useGetDocuments()

  if (isPending) {
    return (
      <main className="mt-14">
        <div className="flex w-full flex-col gap-6">
          <header className="space-y-2">
            <h1 className="text-2xl font-semibold tracking-tight">Tous les documents</h1>
            <p className="text-sm text-muted-foreground">Chargement des documents en cours...</p>
          </header>
        </div>
      </main>
    )
  }

  // Pour éviter de faire documents.documents on transforme le type DocumentResponse en DocumentItem[]
  const documentsArray = Array.isArray(documents?.documents) ? documents!.documents : []

  // Si aucun document trouvé, on affiche un message
  if (documentsArray.length === 0) {
    return (
      <main className="mt-14">
        <div className="flex w-full flex-col gap-6">
          <header className="space-y-2">
            <h1 className="text-2xl font-semibold tracking-tight">Tous les documents</h1>
            <p className="text-sm text-muted-foreground">Aucun document trouvé dans la base de données.</p>
          </header>
        </div>
      </main>
    )
  }

  // Si des documents sont trouvés, on affiche la liste des documents
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
          {documentsArray.map((document) => {
            if (document.document_type === "facture") {
              return <FactureCard key={document.id} document={document} />
            }

            return <DevisCard key={document.id} document={document} />
          })}
        </section>
      </div>
    </main>
  )
}

