import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

// Session cookie issued by the backend on successful authentication.
const SESSION_COOKIE = "admin_template_session"

export function proxy(request: NextRequest) {
  const hasSession = request.cookies.has(SESSION_COOKIE)

  const { pathname } = request.nextUrl

  if (pathname === "/login") {
    if (hasSession) {
      return NextResponse.redirect(new URL("/dashboard", request.url))
    }
    return NextResponse.next()
  }

  if (pathname === "/") {
    if (hasSession) {
      return NextResponse.redirect(new URL("/dashboard", request.url))
    }
    return NextResponse.redirect(new URL("/login", request.url))
  }

  if (
    !hasSession &&
    (pathname.startsWith("/dashboard") || pathname.startsWith("/chat"))
  ) {
    return NextResponse.redirect(new URL("/login", request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
}
