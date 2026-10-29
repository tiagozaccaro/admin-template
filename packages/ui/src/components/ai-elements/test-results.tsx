export function TestResults({
  passed,
  failed,
  total,
}: {
  passed: number
  failed: number
  total: number
}) {
  return (
    <div className="text-sm">
      Tests: {passed} passed, {failed} failed, {total} total
    </div>
  )
}
