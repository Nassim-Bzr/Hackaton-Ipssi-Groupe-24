/** Un log renvoyé par l'API `/pipeline/logs`. */
export interface PipelineLog {
  doc_id?: string
  dag_run_id: string
  task_id: string
  step_name: string
  message: string
  level: string
  timestamp: string
}

export interface LogsResponse {
  logs: PipelineLog[]
  total: number
}
