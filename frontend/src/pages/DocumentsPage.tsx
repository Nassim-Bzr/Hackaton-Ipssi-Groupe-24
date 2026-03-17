import { DocumentCard } from "@/components/cards/document-card"
import type { DocumentResponse } from "@/types/documents.type"
import { useEffect, useState } from "react"

export function DocumentsPage() {
  const [documents, setDocuments] = useState<DocumentResponse>()
  const [loading, setLoading] = useState<boolean>(true)

  useEffect(() => {
    const fetchDocuments = async () => {
      setLoading(true)
      try {
        const response = await fetch("http://localhost:3000/documents")

        if (!response.ok) {
          throw new Error(`Erreur lors de la récupération des documents (${response.status})`)
        }

        const data: DocumentResponse = await response.json()
        console.log(data)
        setDocuments(data)
      } catch (err) {
        console.error(err)
      } finally {
        setLoading(false)
      }
    }

    fetchDocuments()
  }, [])

  // Pendant le chargement, on affiche un état de chargement
  if (loading) {
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

  const documentsArray = Array.isArray(documents?.documents) ? documents!.documents : []

  // Si aucun document trouvé, on affiche un message
  if (!loading && documentsArray.length === 0) {
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
          {documentsArray.map((document) => (
            <DocumentCard
              key={document.id}
              id={document.id}
              nom={document.nom}
              documentType={document.document_type}
              date={document.date}
              siret={document.entities.siret}
              siren={document.entities.siren}
              montantHt={document.entities.montant_ht}
              montantTtc={document.entities.montant_ttc}
              tva={document.entities.tva}
              iban={document.entities.iban}
            />
          ))}
        </section>
      </div>
    </main>
  )
}

