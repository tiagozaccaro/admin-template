import { render, screen, waitFor } from "@testing-library/react"
import { describe, it, expect, vi, beforeEach } from "vitest"

beforeEach(() => {
  if (!window.matchMedia) {
    // @ts-ignore
    window.matchMedia = () => ({
      matches: false,
      addEventListener: () => {},
      removeEventListener: () => {},
    })
  }
})

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
}))
vi.mock("@/lib/auth/google", () => ({ startGoogleSignIn: vi.fn() }))

import DashboardPage from "../app/dashboard/page"
import LoginPage from "../app/login/page"
import SignupPage from "../app/signup/page"
import AccountPage from "../app/account/page"

describe("more pages", () => {
  beforeEach(() => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        id: "1",
        keycloak_sub: "s",
        email: "a@b.com",
        display_name: "Alice",
      }),
    }) as any
  })

  it("dashboard renders", () => {
    render(<DashboardPage />)
    // just no crash
    expect(true).toBe(true)
  })

  it("login renders", () => {
    render(<LoginPage />)
    expect(true).toBe(true)
  })

  it("signup renders", () => {
    render(<SignupPage />)
    expect(true).toBe(true)
  })

  it("account renders after fetch", async () => {
    render(<AccountPage />)
    await waitFor(() => expect(screen.getByText("a@b.com")).toBeTruthy())
  })
})
