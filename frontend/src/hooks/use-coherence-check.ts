import type { DocumentItem } from "@/types/documents.type"
import type {
  CoherenceInput,
  CoherenceResponse,
  DocumentCoherencePayload,
} from "@/types/coherence.type"
import { useQuery } from "@tanstack/react-query"

const COHERENCE_CHECK_URL = "http://localhost:8000/coherence-check"

/**
 * Mappe la liste des documents (facture / devis) vers le format attendu par l'API coherence-check.
 */
function mapDocumentsToCoherencePayload(
  documents: DocumentItem[]
): DocumentCoherencePayload[] {
  return documents.map((doc) => {
    const { document_type, entities } = doc
    const siret =
      "siret_fournisseur" in entities
        ? entities.siret_fournisseur ?? entities.siret ?? null
        : entities.siret ?? null

    if (document_type === "facture") {
      return {
        document_type: "facture",
        siret: siret ?? undefined,
        montant_ht: entities.montant_ht ?? null,
        tva: entities.tva ?? null,
        montant_ttc: entities.montant_ttc ?? null,
        date_echeance: entities.date_echeance ?? null,
      }
    }

    // devis
    return {
      document_type: "devis",
      siret: siret ?? undefined,
      montant_ht: entities.montant_ht ?? null,
      tva: entities.tva ?? null,
      montant_ttc: entities.montant_ttc ?? null,
      date_echeance: null,
    }
  })
}

async function fetchCoherenceCheck(
  payload: CoherenceInput
): Promise<CoherenceResponse> {
  const response = await fetch(COHERENCE_CHECK_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    throw new Error(
      `Impossible de vérifier la cohérence (${response.status})`
    )
  }

  return (await response.json()) as CoherenceResponse
}

/**
 * Hook TanStack Query pour appeler POST /coherence-check sur le service validations.
 * La requête ne part que lorsqu'il y a au moins un document (enabled).
 */
export function useCoherenceCheck(documents: DocumentItem[] | undefined) {
  const queryKey = [
    "coherence",
    documents?.map((d) => d.id).sort().join(",") ?? "",
  ] as const

  const {
    data,
    isPending,
    error,
    refetch,
  } = useQuery<CoherenceResponse>({
    queryKey,
    queryFn: () => {
      const payload: CoherenceInput = {
        documents: mapDocumentsToCoherencePayload(documents!),
      }
      return fetchCoherenceCheck(payload)
    },
    enabled: (documents?.length ?? 0) > 0,
  })

  return {
    coherent: data?.coherent ?? false,
    anomalies: data?.anomalies ?? [],
    isPending,
    error,
    refetch,
  }
}
