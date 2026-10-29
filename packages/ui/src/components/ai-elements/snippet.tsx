import {
  InputGroup,
  InputGroupInput,
  InputGroupAddon,
} from "@workspace/ui/components/input-group"
export function Snippet({ value }: { value: string }) {
  return (
    <InputGroup>
      <InputGroupInput value={value} readOnly />
      <InputGroupAddon align="inline-end">Copy</InputGroupAddon>
    </InputGroup>
  )
}
