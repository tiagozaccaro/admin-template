import { render, screen } from "@testing-library/react"
import { describe, it, expect, vi } from "vitest"

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
}))
vi.mock("@/lib/auth/google", () => ({ startGoogleSignIn: vi.fn() }))

import ItemsPage from "../app/items/page"
import TenantsPage from "../src/app/(app)/tenants/page"

describe("pages", () => {
  it("items", () => {
    render(<ItemsPage />)
    expect(screen.getByText("Items")).toBeTruthy()
  })
  it("tenants", () => {
    render(<TenantsPage />)
    expect(screen.getByText("Tenants")).toBeTruthy()
  })
})
