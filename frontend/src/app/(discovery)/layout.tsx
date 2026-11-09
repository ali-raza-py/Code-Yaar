"use client";

import { PublicHeader } from "@/components/layout/public-header";
import { Footer } from "@/components/layout/footer";
import { AppShell } from "@/components/layout/app-shell";
import { PageTransition } from "@/components/layout/page-transition";
import { useAuth } from "@/hooks/use-auth";

/**
 * Shared discovery surfaces — Tracks, Challenges, Leaderboard — are readable
 * by visitors AND used day-to-day by signed-in students (they're linked from
 * the app sidebar). A single fixed chrome can't serve both: forcing these
 * pages through the public layout threw students out of the AppShell the
 * moment they clicked "Tracks".
 *
 * So the layout adapts to auth state instead of the route: students keep the
 * sidebar shell, visitors get the marketing header/footer, and the neutral
 * container while the session restores avoids a chrome flash on load.
 */
export default function DiscoveryLayout({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, loading } = useAuth();

  // Session still restoring: render content without committing to either
  // chrome, so a signed-in learner never sees the visitor header then the
  // sidebar snapping in.
  if (loading) {
    return <div className="min-h-dvh bg-background">{children}</div>;
  }

  if (isAuthenticated) {
    return <AppShell>{children}</AppShell>;
  }

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
