import { Button } from "@workspace/ui/components/button"
export function Confirmation({
  message,
  onConfirm,
  onDeny,
}: {
  message: string
  onConfirm: () => void
  onDeny: () => void
}) {
  return (
    <div className="rounded-md border p-3 text-sm">
      <div>{message}</div>
      <div className="mt-2 flex gap-2">
        <Button size="sm" onClick={onConfirm}>
          Approve
        </Button>
        <Button size="sm" variant="outline" onClick={onDeny}>
          Deny
        </Button>
      </div>
    </div>
  )
}
