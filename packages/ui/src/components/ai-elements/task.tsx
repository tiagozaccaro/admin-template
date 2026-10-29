export function Task({
  title,
  status,
}: {
  title: string
  status: "pending" | "running" | "done" | "error"
}) {
  return (
    <div className="flex items-center gap-2 text-sm">
      <span className="text-muted-foreground">[{status}]</span>
      <span>{title}</span>
    </div>
  )
}
