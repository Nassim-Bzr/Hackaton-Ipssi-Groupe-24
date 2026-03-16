import { PdfUploader } from "@/components/pdf-uploader"

export function App() {
  return (
    <main className="flex min-h-svh items-center justify-center px-4 py-10">
      <div className="flex w-full max-w-2xl flex-col gap-6">
        <header className="space-y-2">
          <h1 className="text-2xl font-semibold tracking-tight">
            Import de documents PDF
          </h1>
          <p className="max-w-xl text-sm text-muted-foreground">
            Sélectionnez ou déposez plusieurs fichiers au format PDF. Ils seront
            envoyés à votre backend via une requête HTTP sur{" "}
            <code className="rounded bg-muted px-1 py-0.5 text-xs">
              POST http://localhost:3000/upload
            </code>
            .
          </p>
        </header>

        <PdfUploader />
      </div>
    </main>
  )
}

export default App
