"use client";

import { usePathname } from "next/navigation";
import { AppShell } from "@/components/layout/app-shell";
import { PublicHeader } from "@/components/layout/public-header";
import { Footer } from "@/components/layout/footer";
import { PageTransition } from "@/components/layout/page-transition";
import { RequireAuth } from "@/components/auth/require-auth";
import { useAuth } from "@/hooks/use-auth";

/**
 * Catalogue routes the public header links to. Their APIs already answer
 * anonymous reads, so a signed-out visitor should browse them instead of
 * being detoured through the sign-in screen. Every other (app) route — and
 * every action like enrolling or completing a lesson — stays guarded.
 */
const BROWSE_ROUTES = ["/learn", "/projects", "/challenges", "/leaderboard"];

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { user, loading } = useAuth();

  // Signed in (or still restoring the session): the dashboard shell exactly
  // as it always was. Rendering RequireAuth while loading also means a
  // returning learner never flashes the public chrome, and a visitor whose
  // session check comes back empty unmounts RequireAuth before its redirect
  // effect can fire.
  if (!BROWSE_ROUTES.includes(pathname) || loading || user) {
    return (
      <RequireAuth>
        <AppShell>{children}</AppShell>
      </RequireAuth>
    );
  }

  // Signed-out visitor on a browse-only route: the same page, framed by the
  // public header and footer used by the rest of the public site.
  return (
    <>
      <PublicHeader />
      <main className="flex-1">
        <PageTransition>{children}</PageTransition>
      </main>
      <Footer />
    </>
  );
}
