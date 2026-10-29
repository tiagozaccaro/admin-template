import { Progress } from "@workspace/ui/components/progress"
export function Context({ used, total }: { used: number; total: number }) {
  const pct = Math.min(100, Math.round((used / total) * 100))
  return (
    <div className="text-xs text-muted-foreground">
      <div>
        Context: {used}/{total} tokens
      </div>
      <Progress value={pct} className="mt-1 h-1" />
    </div>
  )
}
