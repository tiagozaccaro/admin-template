import { Item, ItemContent, ItemTitle } from "@workspace/ui/components/item"
import { Badge } from "@workspace/ui/components/badge"
export function EnvironmentVariables({
  name,
  value,
}: {
  name: string
  value: string
}) {
  return (
    <Item>
      <ItemContent>
        <ItemTitle className="flex items-center justify-between">
          <span>{name}</span>
          <Badge variant="secondary">{value}</Badge>
        </ItemTitle>
      </ItemContent>
    </Item>
  )
}
