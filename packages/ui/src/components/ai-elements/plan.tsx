export function Plan({
  steps,
}: {
  steps: { title: string; done?: boolean }[]
}) {
  return (
    <ol className="list-decimal space-y-1 pl-5 text-sm">
      {steps.map((s, i) => (
        <li
          key={i}
          className={s.done ? "text-muted-foreground line-through" : ""}
        >
          {s.title}
        </li>
      ))}
    </ol>
  )
}
