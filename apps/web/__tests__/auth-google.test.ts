import { describe, it, expect, vi, beforeEach } from "vitest"
import { getApiUrl, startGoogleSignIn } from "@/lib/auth/google"

describe("google auth", () => {
  beforeEach(() => {
    vi.unstubAllEnvs()
    vi.unstubAllGlobals()
  })

  it("getApiUrl defaults", () => {
    expect(getApiUrl()).toBe("http://localhost:8000")
  })

  it("startGoogleSignIn redirects", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        authorization_url: "https://accounts.google.com/o/oauth2/auth",
      }),
    })
    vi.stubGlobal("fetch", fetchMock)
    const loc = { href: "" }
    vi.stubGlobal("window", { location: loc })
    await startGoogleSignIn()
    expect(fetchMock).toHaveBeenCalled()
    expect(loc.href).toBe("https://accounts.google.com/o/oauth2/auth")
  })

  it("throws on failure", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false }))
    await expect(startGoogleSignIn()).rejects.toThrow(
      "Failed to start Google sign-in"
    )
  })
})
