export function WebPreview({ url }: { url: string }) {
  return (
    <iframe
      src={url}
      className="h-64 w-full rounded-md border"
      title="preview"
    />
  )
}
