"use client"

import { Card } from "@workspace/ui/components/card"

export function Tool({
  name,
  input,
  output,
}: {
  name: string
  input?: unknown
  output?: unknown
}) {
  return (
    <Card className="p-3 text-xs">
      <div className="font-medium">{name}</div>
      {input !== undefined && (
        <pre className="mt-2 overflow-auto">
          {JSON.stringify(input, null, 2)}
        </pre>
      )}
      {output !== undefined && (
        <pre className="mt-2 overflow-auto text-muted-foreground">
          {JSON.stringify(output, null, 2)}
        </pre>
      )}
    </Card>
  )
}
