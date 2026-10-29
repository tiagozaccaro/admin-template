export function StackTrace({
  error,
  frames,
}: {
  error: string
  frames?: string[]
}) {
  return (
    <div className="rounded-md border p-3 text-xs">
      <div className="font-medium text-destructive">{error}</div>
      {frames && (
        <pre className="mt-2 overflow-auto text-muted-foreground">
          {frames.join("\n")}
        </pre>
      )}
    </div>
  )
}
