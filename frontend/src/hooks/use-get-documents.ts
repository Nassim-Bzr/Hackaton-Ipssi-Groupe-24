import type { DocumentResponse } from "@/types/documents.type"
import { useQuery } from "@tanstack/react-query"

export function useGetDocuments() {
  const { data: documents, isPending } = useQuery<DocumentResponse>({
    queryKey: ["documents"],
    queryFn: async () => {
      const response = await fetch("http://localhost:3000/documents")

      if (!response.ok) {
        throw new Error(
          `Erreur lors de la récupération des documents (${response.status})`
        )
      }

      return (await response.json()) as DocumentResponse
    },
  })
  return { documents, isPending }
}
