import type { DocumentCardBaseProps } from "@/components/cards/document-card"
import { DocumentCard } from "@/components/cards/document-card"

export type DevisCardProps = DocumentCardBaseProps

export function DevisCard(props: DevisCardProps) {
  return <DocumentCard {...props} />
}
