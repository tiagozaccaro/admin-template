import { cn } from "cn"

export function Sources({
  items,
}: {
  items: { title: string; url: string }[]
}) {
  return (
    <div className={cn("mt-2 flex flex-wrap gap-2 text-xs")}>
      {items.map((s) => (
        <a
          key={s.url}
          href={s.url}
          className="text-muted-foreground underline"
          target="_blank"
          rel="noreferrer"
        >
          {s.title}
        </a>
      ))}
    </div>
  )
}
