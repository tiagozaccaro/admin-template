import type { Metadata } from "next"

import { AuditClient } from "./audit-client"

export const metadata: Metadata = {
  title: "Audit log | Admin Template",
  description: "Review agent tool invocation audit log",
}

export default function AuditPage() {
  return <AuditClient />
}
