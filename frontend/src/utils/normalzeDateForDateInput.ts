export function normalizeDateForDateInput(value: unknown): string {
  if (typeof value !== "string") return ""
  const trimmed = value.trim()
  if (!trimmed) return ""

  if (/^\d{4}-\d{2}-\d{2}$/.test(trimmed)) return trimmed

  const match = /^(\d{2})\/(\d{2})\/(\d{4})$/.exec(trimmed)
  if (!match) return trimmed
  const [, dd, mm, yyyy] = match
  return `${yyyy}-${mm}-${dd}`
}
