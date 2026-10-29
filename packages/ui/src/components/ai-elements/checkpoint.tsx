import { Separator } from "@workspace/ui/components/separator"
export function Checkpoint({ label }: { label: string }) {
  return (
    <div className="my-4 flex items-center gap-2 text-xs text-muted-foreground">
      <Separator className="flex-1" />
      <span>{label}</span>
      <Separator className="flex-1" />
    </div>
  )
}
