import { Button } from "@workspace/ui/components/button"
export function Suggestion({
  label,
  onClick,
}: {
  label: string
  onClick?: () => void
}) {
  return (
    <Button variant="outline" size="sm" onClick={onClick}>
      {label}
    </Button>
  )
}
