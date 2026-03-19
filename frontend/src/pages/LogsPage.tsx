import { Button } from "@/components/ui/button"
import { useGetLogs } from "@/hooks/use-get-logs"

function formatTimestamp(ts: string) {
  try {
    const d = new Date(ts)
    return d.toLocaleString("fr-FR")
  } catch {
    return ts
  }
}

function levelBadgeClass(level: string) {
  switch (level) {
    case "success":
      return "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400"
    case "error":
      return "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400"
    default:
      return "bg-muted text-muted-foreground"
  }
}

export function LogsPage() {
  const { logs, total, isPending, refetch, isFetching } = useGetLogs()

  const headerContent =
    logs.length === 0 && !isPending ? (
      <p className="text-sm text-muted-foreground">Aucun log pour le moment. Les logs apparaîtront après l’exécution des tâches du pipeline.</p>
    ) : isPending && !isFetching ? (
      <p className="text-sm text-muted-foreground">Chargement des logs en cours...</p>
    ) : (
      <p className="max-w-xl text-sm text-muted-foreground">
        Liste des logs envoyés à chaque étape du pipeline documentaire ({total} entrée{total > 1 ? "s" : ""}).
      </p>
    )

  if (isPending && !isFetching) {
    return (
      <main className="mt-14">
        <div className="flex w-full flex-col gap-6">
          <header className="flex flex-wrap items-start justify-between gap-4">
            <div className="space-y-2">
              <h1 className="text-2xl font-semibold tracking-tight">Logs du pipeline</h1>
              {headerContent}
            </div>
            <Button variant="outline" size="sm" onClick={() => refetch()} disabled={isFetching}>
              {isFetching ? "Actualisation…" : "Actualiser"}
            </Button>
          </header>
        </div>
      </main>
    )
  }

  if (logs.length === 0) {
    return (
      <main className="mt-14">
        <div className="flex w-full flex-col gap-6">
          <header className="flex flex-wrap items-start justify-between gap-4">
            <div className="space-y-2">
              <h1 className="text-2xl font-semibold tracking-tight">Logs du pipeline</h1>
              {headerContent}
            </div>
            <Button variant="outline" size="sm" onClick={() => refetch()} disabled={isFetching}>
              {isFetching ? "Actualisation…" : "Actualiser"}
            </Button>
          </header>
        </div>
      </main>
    )
  }

  return (
    <main className="mt-14">
      <div className="flex w-full flex-col gap-6">
        <header className="flex flex-wrap items-start justify-between gap-4">
          <div className="space-y-2">
            <h1 className="text-2xl font-semibold tracking-tight">Logs du pipeline</h1>
            {headerContent}
          </div>
          <Button variant="outline" size="sm" onClick={() => refetch()} disabled={isFetching}>
            {isFetching ? "Actualisation…" : "Actualiser"}
          </Button>
        </header>

        <section className="rounded-lg border overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-muted/50">
                  <th className="px-4 py-3 text-left font-medium">Date / heure</th>
                  <th className="px-4 py-3 text-left font-medium">Étape</th>
                  <th className="px-4 py-3 text-left font-medium">Message</th>
                  <th className="px-4 py-3 text-left font-medium">Niveau</th>
                  <th className="px-4 py-3 text-left font-medium">Document</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log, index) => (
                  <tr key={index} className="border-b last:border-0">
                    <td className="px-4 py-3 text-muted-foreground whitespace-nowrap">
                      {formatTimestamp(log.timestamp)}
                    </td>
                    <td className="px-4 py-3 font-medium">{log.step_name}</td>
                    <td className="px-4 py-3">{log.message}</td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex rounded px-2 py-0.5 text-xs font-medium ${levelBadgeClass(log.level)}`}>
                        {log.level}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-muted-foreground">
                      {log.doc_id ?? "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </main>
  )
}
