/**
 * Web OIDC client placeholder (Authorization Code + PKCE).
 *
 * Placeholder for the web authentication client per T018. Talks to the
 * Keycloak realm `contentforge` (client `contentforge-web`, PKCE,
 * redirect http://localhost:3000/auth/callback). Tokens are held in
 * memory only -- no app-issued long-lived tokens are persisted
 * (constitution VI / AGENTS.md security).
 *
 * Configure `ISSUER` (Keycloak issuer URL) before use in production.
 */

export const OIDC_CONFIG = {
  // Keycloak realm issuer. Set to the deployed Keycloak issuer, e.g.
  // https://auth.contentforge.local/realms/contentforge
  issuer: "http://localhost:8080/realms/contentforge",
  clientId: "contentforge-web",
  redirectUri: "http://localhost:3000/auth/callback",
  scope: "openid profile email",
} as const

export const AUTHORIZATION_ENDPOINT = `${OIDC_CONFIG.issuer}/protocol/openid-connect/auth`
export const TOKEN_ENDPOINT = `${OIDC_CONFIG.issuer}/protocol/openid-connect/token`

const CODE_VERIFIER_KEY = "contentforge_pkce_verifier"
const CODE_STATE_KEY = "contentforge_pkce_state"

interface TokenSet {
  accessToken: string
  idToken: string | null
  refreshToken: string | null
  expiresAt: number | null
}

let tokenStore: TokenSet | null = null

/** Cryptographically random PKCE code verifier (43-128 chars). */
export function generateCodeVerifier(): string {
  const bytes = new Uint8Array(32)
  crypto.getRandomValues(bytes)
  return base64UrlEncode(bytes).replace(/=+$/, "")
}

/** SHA-256 digest of the verifier, base64url-encoded (no padding). */
export async function codeChallenge(verifier: string): Promise<string> {
  const digest = await crypto.subtle.digest(
    "SHA-256",
    new TextEncoder().encode(verifier)
  )
  return base64UrlEncode(new Uint8Array(digest)).replace(/=+$/, "")
}

function base64UrlEncode(data: Uint8Array): string {
  let binary = ""
  for (const byte of data) {
    binary += String.fromCharCode(byte)
  }
  return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "")
}

/** Build the Keycloak authorization URL with PKCE. */
export async function buildAuthorizationUrl(state: string): Promise<URL> {
  const verifier = generateCodeVerifier()
  sessionStorage.setItem(CODE_VERIFIER_KEY, verifier)
  sessionStorage.setItem(CODE_STATE_KEY, state)
  const challenge = await codeChallenge(verifier)
  const url = new URL(AUTHORIZATION_ENDPOINT)
  url.searchParams.set("client_id", OIDC_CONFIG.clientId)
  url.searchParams.set("response_type", "code")
  url.searchParams.set("scope", OIDC_CONFIG.scope)
  url.searchParams.set("redirect_uri", OIDC_CONFIG.redirectUri)
  url.searchParams.set("code_challenge", challenge)
  url.searchParams.set("code_challenge_method", "S256")
  url.searchParams.set("state", state)
  return url
}

/** Start the authorization code flow (redirects to Keycloak). */
export async function startLogin(state: string): Promise<void> {
  const url = await buildAuthorizationUrl(state)
  window.location.assign(url.toString())
}

/** Exchange the authorization code for tokens (held in memory only). */
export async function handleCallback(
  code: string,
  state: string
): Promise<TokenSet> {
  const expectedState = sessionStorage.getItem(CODE_STATE_KEY)
  if (expectedState === null || expectedState !== state) {
    throw new Error("OIDC state mismatch")
  }
  const verifier = sessionStorage.getItem(CODE_VERIFIER_KEY)
  if (verifier === null) {
    throw new Error("OIDC code verifier missing")
  }

  const response = await fetch(TOKEN_ENDPOINT, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      grant_type: "authorization_code",
      code,
      redirect_uri: OIDC_CONFIG.redirectUri,
      client_id: OIDC_CONFIG.clientId,
      code_verifier: verifier,
    }).toString(),
  })
  if (!response.ok) {
    throw new Error(`Token exchange failed: ${response.status}`)
  }
  const payload = (await response.json()) as {
    access_token: string
    id_token?: string | null
    refresh_token?: string | null
    expires_in?: number | null
  }

  const now = Date.now()
  tokenStore = {
    accessToken: payload.access_token,
    idToken: payload.id_token ?? null,
    refreshToken: payload.refresh_token ?? null,
    expiresAt:
      payload.expires_in !== null && payload.expires_in !== undefined
        ? now + payload.expires_in * 1000
        : null,
  }
  sessionStorage.removeItem(CODE_VERIFIER_KEY)
  sessionStorage.removeItem(CODE_STATE_KEY)
  return tokenStore
}

/** Access token held in memory (null when unauthenticated/expired). */
export function getAccessToken(): string | null {
  if (tokenStore === null) {
    return null
  }
  if (tokenStore.expiresAt !== null && Date.now() >= tokenStore.expiresAt) {
    return null
  }
  return tokenStore.accessToken
}

/** Whether a valid access token is held in memory. */
export function isAuthenticated(): boolean {
  return getAccessToken() !== null
}

/** Clear the in-memory token store (logout). */
export function logout(): void {
  tokenStore = null
}
