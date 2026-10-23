"use client"

export function LoadingState({ label = "Loading..." }: { label?: string }) {
  return (
    <div className="flex items-center justify-center p-8 text-muted-foreground">
      <span className="mr-2 inline-block h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
      <span>{label}</span>
    </div>
  )
}

export function ErrorState({
  message = "Something went wrong.",
}: {
  message?: string
}) {
  return (
    <div className="rounded-md border border-destructive/50 bg-destructive/10 p-4 text-destructive">
      {message}
    </div>
  )
}

export function EmptyState({
  title = "Nothing here yet",
  description,
}: {
  title?: string
  description?: string
}) {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center text-muted-foreground">
      <p className="font-medium">{title}</p>
      {description && <p className="text-sm">{description}</p>}
    </div>
  )
}
