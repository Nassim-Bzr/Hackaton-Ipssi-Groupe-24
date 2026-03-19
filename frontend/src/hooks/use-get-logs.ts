import type { LogsResponse } from "@/types/logs.type"
import { useQuery } from "@tanstack/react-query"

const PIPELINE_LOGS_URL = "http://localhost:3000/pipeline/logs"

export function useGetLogs() {
  const { data, isPending, refetch, isFetching } = useQuery<LogsResponse>({
    queryKey: ["pipeline-logs"],
    queryFn: async () => {
      const response = await fetch(PIPELINE_LOGS_URL)

      if (!response.ok) {
        throw new Error(
          `Erreur lors de la récupération des logs (${response.status})`
        )
      }

      return (await response.json()) as LogsResponse
    },
  })
  return { logs: data?.logs ?? [], total: data?.total ?? 0, isPending, refetch, isFetching }
}
