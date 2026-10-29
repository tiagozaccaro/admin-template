"use client"

import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@workspace/ui/components/collapsible"

export function Reasoning({ children }: { children: React.ReactNode }) {
  return (
    <Collapsible>
      <CollapsibleTrigger className="text-xs text-muted-foreground">
        Reasoning
      </CollapsibleTrigger>
      <CollapsibleContent className="mt-2 text-sm">
        {children}
      </CollapsibleContent>
    </Collapsible>
  )
}
