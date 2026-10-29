import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@workspace/ui/components/collapsible"
export function Subagent({
  name,
  children,
}: {
  name: string
  children: React.ReactNode
}) {
  return (
    <Collapsible>
      <CollapsibleTrigger className="text-xs font-medium">
        Subagent: {name}
      </CollapsibleTrigger>
      <CollapsibleContent className="mt-2 pl-3 text-sm">
        {children}
      </CollapsibleContent>
    </Collapsible>
  )
}
