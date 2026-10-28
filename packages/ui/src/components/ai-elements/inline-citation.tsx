import {
  HoverCard,
  HoverCardContent,
  HoverCardTrigger,
} from "@workspace/ui/components/hover-card"
export function InlineCitation({
  label,
  detail,
}: {
  label: string
  detail: React.ReactNode
}) {
  return (
    <HoverCard>
      <HoverCardTrigger>
        <span className="cursor-help underline decoration-dotted">{label}</span>
      </HoverCardTrigger>
      <HoverCardContent className="text-sm">{detail}</HoverCardContent>
    </HoverCard>
  )
}
