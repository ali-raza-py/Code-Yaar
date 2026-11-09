"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useCallback } from "react";
import { cn } from "@/lib/utils";
import { ProgressOverviewBody } from "@/components/progress/progress-overview";
import { AchievementsTabBody } from "@/components/progress/achievements-tab";
import { CertificatesTabBody } from "@/components/progress/certificates-tab";

// The tab query param keeps deep links shareable (e.g. /progress?tab=certificates)
// while every tab stays under the single protected My Progress destination.
const TABS = [
  { key: "overview", label: "Overview" },
  { key: "achievements", label: "Achievements" },
  { key: "certificates", label: "Certificates" },
] as const;

type TabKey = (typeof TABS)[number]["key"];

function tabFromParam(value: string | null): TabKey {
  return TABS.some((tab) => tab.key === value) ? (value as TabKey) : "overview";
}

/**
 * Unified My Progress destination: learning statistics, badges and
 * certificates as tabs over one route. Each tab body owns its own API calls
 * and mounts only while active, so no data is fetched twice and the
 * standalone /achievements and /certificates routes keep working unchanged.
 */
export default function ProgressPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const activeTab = tabFromParam(searchParams.get("tab"));

  const selectTab = useCallback(
    (key: TabKey) => {
      router.push(key === "overview" ? "/progress" : `/progress?tab=${key}`, { scroll: true });
    },
    [router],
  );

  return (
    <div>
      <div
        role="tablist"
        aria-label="My progress sections"
        className="mx-auto flex max-w-7xl px-4 pt-6 sm:px-6 lg:px-8"
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
        {activeTab === "overview" && <ProgressOverviewBody />}
        {activeTab === "achievements" && (
          <AchievementsTabBody
            compact
            overviewHref="/progress"
            certificatesHref="/progress?tab=certificates"
          />
        )}
        {activeTab === "certificates" && (
          <CertificatesTabBody
            compact
            overviewHref="/progress"
            achievementsHref="/progress?tab=achievements"
          />
        )}
      </div>
    </div>
  );
}
