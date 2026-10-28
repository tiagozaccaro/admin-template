import { Card } from "@workspace/ui/components/card"
import { Button } from "@workspace/ui/components/button"
export function Artifact({
  title,
  children,
}: {
  title: string
  children: React.ReactNode
}) {
  return (
    <Card className="p-3">
      <div className="mb-2 flex items-center justify-between">
        <span className="text-sm font-medium">{title}</span>
        <Button size="sm" variant="ghost">
          Copy
        </Button>
      </div>
      {children}
    </Card>
  )
}
