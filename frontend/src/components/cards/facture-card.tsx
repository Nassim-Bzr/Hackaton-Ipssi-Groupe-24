import type { DocumentCardBaseProps } from "@/components/cards/document-card"
import { DocumentCard } from "@/components/cards/document-card"

export interface FactureCardProps extends DocumentCardBaseProps {
    iban: string
}

export function FactureCard(props: FactureCardProps) {
    return <DocumentCard {...props} />
}
