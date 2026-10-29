import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@workspace/ui/components/collapsible"
import { Badge } from "@workspace/ui/components/badge"
export function SchemaDisplay({
  name,
  children,
}: {
  name: string
  children: React.ReactNode
}) {
  return (
    <Collapsible>
      <CollapsibleTrigger className="flex items-center gap-2 text-xs">
        <Badge variant="outline">{name}</Badge>
      </CollapsibleTrigger>
      <CollapsibleContent className="mt-2 text-xs">
        {children}
      </CollapsibleContent>
    </Collapsible>
  )
}
