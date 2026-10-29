export function Queue({
  items,
}: {
  items: { title: string; done?: boolean }[]
}) {
  return (
    <ul className="space-y-1 text-sm">
      {items.map((i, idx) => (
        <li
          key={idx}
          className={i.done ? "text-muted-foreground line-through" : ""}
        >
          {i.title}
        </li>
      ))}
    </ul>
  )
}
