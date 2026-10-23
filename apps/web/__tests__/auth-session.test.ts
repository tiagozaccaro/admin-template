import { describe, it, expect } from "vitest"
import { clearSessionCookie, sessionCookieName } from "@/lib/auth/session"

describe("session", () => {
  it("exports cookie name", () => {
    expect(sessionCookieName).toBe("admin_template_session")
  })

  it("clearSessionCookie clears cookie", () => {
    document.cookie = "admin_template_session=abc; path=/"
    clearSessionCookie()
    expect(document.cookie).not.toContain("admin_template_session=abc")
  })
})
