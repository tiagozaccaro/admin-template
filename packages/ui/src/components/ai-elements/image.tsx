export function AIImage({ src, alt }: { src: string; alt?: string }) {
  return <img src={src} alt={alt ?? ""} className="max-w-full rounded-md" />
}
