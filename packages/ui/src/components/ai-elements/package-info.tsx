import {
  Item,
  ItemContent,
  ItemTitle,
  ItemDescription,
} from "@workspace/ui/components/item"
import { Badge } from "@workspace/ui/components/badge"
export function PackageInfo({
  name,
  version,
}: {
  name: string
  version: string
}) {
  return (
    <Item>
      <ItemContent>
        <ItemTitle>{name}</ItemTitle>
        <ItemDescription>
          <Badge variant="secondary">{version}</Badge>
        </ItemDescription>
      </ItemContent>
    </Item>
  )
}
