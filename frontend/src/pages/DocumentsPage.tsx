import { DevisCard } from "@/components/cards/devis-card"
import { FactureCard } from "@/components/cards/facture-card"
import { useCoherenceCheck } from "@/hooks/use-coherence-check"
import { useGetDocuments } from "@/hooks/use-get-documents"

export function DocumentsPage() {
  const { documents, isPending } = useGetDocuments()
  const documentsArray = Array.isArray(documents?.documents) ? documents!.documents : []
  const { coherent, anomalies, isPending: isCoherencePending, error: coherenceError } = useCoherenceCheck(documentsArray)

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

  // Si des documents sont trouvés, on affiche la liste des documents + statut de cohérence
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

        {/* Bloc statut cohérence : affiché uniquement quand il y a des documents */}
        <section className="rounded-lg border p-4" aria-live="polite">
          {isCoherencePending && (
            <p className="text-sm text-muted-foreground">Vérification de cohérence en cours…</p>
          )}
          {coherenceError && (
            <p className="text-sm text-destructive">
              Impossible de vérifier la cohérence. Vérifiez que le service validations (port 8000) est démarré.
            </p>
          )}
          {!isCoherencePending && !coherenceError && (
            <>
              {coherent ? (
                <p className="text-sm font-medium text-green-700 dark:text-green-400">
                  Documents valide
                </p>
              ) : (
                <div className="space-y-2">
                  <p className="text-sm font-medium text-destructive">Documents incohérents</p>
                  <ul className="list-inside list-disc space-y-1 text-sm text-muted-foreground">
                    {anomalies.map((a) => (
                      <li key={a.verification}>{a.message}</li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          )}
        </section>

        <section className="grid gap-4 md:grid-cols-2">
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

