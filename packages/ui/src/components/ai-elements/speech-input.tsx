import { Button } from "@workspace/ui/components/button"
export function SpeechInput({ listening }: { listening?: boolean }) {
  return (
    <Button variant="outline" size="icon">
      {listening ? "…" : "🎤"}
    </Button>
  )
}
