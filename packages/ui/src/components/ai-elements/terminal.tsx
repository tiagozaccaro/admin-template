export function Terminal({
  command,
  output,
}: {
  command: string
  output?: string
}) {
  return (
    <div className="rounded-md bg-black p-3 font-mono text-xs text-green-400">
      <div>$ {command}</div>
      {output && <pre className="mt-2 whitespace-pre-wrap">{output}</pre>}
    </div>
  )
}
