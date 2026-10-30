"use client";

import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import Link from "next/link";
import { ShieldAlert } from "lucide-react";
import { useAuth } from "@/hooks/use-auth";
import type { UserRole } from "@/lib/api";

/**
 * Client-side route guard.
 *
 * This is a usability layer, not a security boundary: the API enforces
 * authentication and permissions on every request. Its job is to keep an
 * unauthenticated visitor from staring at empty dashboard chrome, and to
 * return them to the page they originally asked for after signing in.
 */

export function AuthGateLoader({ label = "Checking your session…" }: { label?: string }) {
  return (
    <div className="flex min-h-[60vh] items-center justify-center px-4">
      <div className="flex flex-col items-center gap-3 text-sm text-muted-foreground">
        <span
          aria-hidden="true"
          className="h-6 w-6 animate-spin rounded-full border-2 border-primary/25 border-t-primary"
        />
        <span role="status">{label}</span>
      </div>
    </div>
  );
}

function AccessDenied() {
  return (
    <div className="mx-auto max-w-md px-4 py-16 text-center">
      <div className="mx-auto grid h-12 w-12 place-items-center rounded-full border border-destructive/20 bg-destructive/[0.06]">
        <ShieldAlert className="h-6 w-6 text-destructive" aria-hidden="true" />
      </div>
      <h1 className="mt-5 text-xl font-bold tracking-tight text-foreground">No access</h1>
      <p className="mt-2 text-sm text-muted-foreground">
        Your account doesn&apos;t have permission to view this page.
      </p>
      <Link
        href="/dashboard"
        className="mt-6 inline-flex h-10 items-center rounded-lg bg-primary px-4 text-sm font-semibold text-primary-foreground transition-opacity hover:opacity-90"
      >
        Back to dashboard
      </Link>
    </div>
  );
}

export function RequireAuth({
  children,
  roles,
}: {
  children: React.ReactNode;
  /** When set, the signed-in user must hold one of these roles. */
  roles?: UserRole[];
}) {
  const { user, loading } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (loading || user) return;
    const target = pathname && pathname !== "/" ? pathname : "/dashboard";
    router.replace(`/sign-in?next=${encodeURIComponent(target)}`);
  }, [loading, user, pathname, router]);

  if (loading || !user) return <AuthGateLoader />;
  if (roles && !roles.includes(user.role)) return <AccessDenied />;
  return <>{children}</>;
}

/**
 * Keeps a signed-in visitor out of the sign-in / sign-up screens.
 * `next` is read from the URL at redirect time so it survives the round trip.
 */
export function RedirectIfAuthenticated({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (loading || !user) return;
    const params = new URLSearchParams(window.location.search);
    const next = params.get("next");
    router.replace(next && next.startsWith("/") ? next : "/dashboard");
  }, [loading, user, router]);

  if (loading) return <AuthGateLoader label="Restoring your session…" />;
  if (user) return <AuthGateLoader label="Redirecting…" />;
  return <>{children}</>;
}

/** Safe post-auth destination: relative paths only, never an absolute URL. */
export function readNextPath(fallback = "/dashboard"): string {
  if (typeof window === "undefined") return fallback;
  const next = new URLSearchParams(window.location.search).get("next");
  return next && next.startsWith("/") && !next.startsWith("//") ? next : fallback;
}
