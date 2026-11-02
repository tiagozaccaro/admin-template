import type { Metadata } from "next"

import { AgentsClient } from "./agents-client"

export const metadata: Metadata = {
  title: "Agents | Admin Template",
  description: "Manage standalone machine admin agents",
}

export default function AgentsPage() {
  return <AgentsClient />
}
