import { type NextRequest, NextResponse } from "next/server";

/**
 * Route protection deliberately lives on the client, not here.
 *
 * The refresh token is an HttpOnly cookie scoped to the API origin, so a proxy
 * running on the frontend origin can never read it — any redirect decision
 * made here would be guesswork. `(app)/layout.tsx` guards the authenticated
 * shell with `RequireAuth`, and the API rejects unauthenticated requests
 * regardless of what the browser renders.
 */
export async function proxy(request: NextRequest) {
  return NextResponse.next({ request });
}

export const config = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};
