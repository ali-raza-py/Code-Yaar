"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useCallback } from "react";
import { cn } from "@/lib/utils";
import { ProfileOverviewBody } from "@/components/profile/profile-overview";
import { PortfolioDashboard } from "@/components/portfolio/portfolio-dashboard";

// The tab query param keeps deep links shareable (e.g. /profile?tab=portfolio)
// while every tab stays under the single protected My Profile destination.
const TABS = [
  { key: "overview", label: "Overview" },
  { key: "portfolio", label: "Portfolio" },
] as const;

type TabKey = (typeof TABS)[number]["key"];

function tabFromParam(value: string | null): TabKey {
  return TABS.some((tab) => tab.key === value) ? (value as TabKey) : "overview";
}

/**
 * Unified My Profile destination: account identity and the public-portfolio
 * manager as tabs over one route. Each tab body owns its own API calls and
 * mounts only while active, and the standalone /profile/portfolio route keeps
 * working for bookmarks and project edit/new sub-pages.
 */
export default function ProfilePage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const activeTab = tabFromParam(searchParams.get("tab"));

  const selectTab = useCallback(
    (key: TabKey) => {
      router.push(key === "overview" ? "/profile" : `/profile?tab=${key}`, { scroll: true });
    },
    [router],
  );

  return (
    <div>
      <div
        role="tablist"
        aria-label="My profile sections"
        className="mx-auto flex max-w-4xl px-4 pt-6 sm:px-6 lg:px-8"
      >
        <div className="inline-flex rounded-pill border border-border bg-muted/30 p-1">
          {TABS.map((tab) => (
            <button
              key={tab.key}
              type="button"
              role="tab"
              aria-selected={activeTab === tab.key}
              onClick={() => selectTab(tab.key)}
              className={cn(
                "rounded-pill px-4 py-1.5 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
                activeTab === tab.key
                  ? "bg-background text-foreground shadow-sm"
                  : "text-muted-foreground hover:text-foreground",
              )}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      <div role="tabpanel" aria-label={TABS.find((tab) => tab.key === activeTab)?.label}>
        {activeTab === "overview" && <ProfileOverviewBody />}
        {activeTab === "portfolio" && <PortfolioDashboard compact />}
      </div>
    </div>
  );
}
