import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@workspace/ui/components/collapsible"
export function ChainOfThought({
  summary,
  children,
}: {
  summary: string
  children: React.ReactNode
}) {
  return (
    <Collapsible>
      <CollapsibleTrigger className="text-xs font-medium">
        {summary}
      </CollapsibleTrigger>
      <CollapsibleContent className="mt-2 text-sm">
        {children}
      </CollapsibleContent>
    </Collapsible>
  )
}
