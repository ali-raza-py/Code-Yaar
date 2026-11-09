"use client";

import { AppShell } from "@/components/layout/app-shell";
import { RequireAuth } from "@/components/auth/require-auth";

/**
 * The authenticated student shell. Everything in this route group requires a
 * session — no browse-mode exceptions. Public discovery (courses, tracks,
 * challenges viewing, leaderboard) lives in the (public) group, where pages
 * render for visitors and students alike; the API is the real security
 * boundary and RequireAuth only keeps empty chrome away from signed-out
 * visitors (see components/auth/require-auth.tsx).
 */
export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <RequireAuth>
      <AppShell>{children}</AppShell>
    </RequireAuth>
  );
}
