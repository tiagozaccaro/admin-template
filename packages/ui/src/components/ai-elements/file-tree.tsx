export function FileTree({ files }: { files: string[] }) {
  return (
    <ul className="font-mono text-xs">
      {files.map((f) => (
        <li key={f}>{f}</li>
      ))}
    </ul>
  )
}
