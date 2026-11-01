"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowRight, Medal } from "lucide-react";
import { leaderboard as leaderboardApi, type LeaderboardEntry } from "@/lib/api";

/**
 * Leaderboard preview sourced from GET /api/leaderboard/ (top 5 real
 * rankings). Shown on the homepage as a live community teaser; the full
 * board lives at /leaderboard. Renders an honest quiet state when there is
 * no XP data yet — no invented names.
 */
export function LeaderboardPreview() {
  const [entries, setEntries] = useState<LeaderboardEntry[] | null>(null);

  useEffect(() => {
    let cancelled = false;
    leaderboardApi.list({ limit: 5 })
      .then((data) => { if (!cancelled) setEntries(data.entries); })
      .catch(() => { if (!cancelled) setEntries([]); });
    return () => { cancelled = true; };
  }, []);

  if (entries === null) {
    return (
      <div className="space-y-2">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-12 animate-pulse rounded-md border border-forest-border bg-white/60" />
        ))}
      </div>
    );
  }

  if (entries.length === 0) {
    return (
      <div className="rounded-[var(--radius-card)] border border-forest-border bg-white p-5 text-sm text-forest-muted">
        <span className="inline-flex items-center gap-1.5 font-semibold text-forest-accent"><Medal className="h-4 w-4" /> The rankings open with the first XP earned.</span>
        <p className="mt-2">Complete a lesson and you could hold the top spot.</p>
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-[var(--radius-card)] border border-forest-border bg-white">
      <ul className="divide-y divide-forest-border">
        {entries.map((entry) => (
          <li key={entry.user_id} className="flex items-center gap-3 px-4 py-3">
            <span className={`grid h-7 w-7 shrink-0 place-items-center rounded-full text-xs font-bold ${entry.rank <= 3 ? "bg-forest-deep text-mint" : "bg-forest-bg text-forest-muted"}`}>
              {entry.rank}
            </span>
            <span className="grid h-7 w-7 shrink-0 place-items-center rounded-full bg-forest-accent/10 text-xs font-bold text-forest-accent">
              {entry.username.charAt(0).toUpperCase()}
            </span>
            <span className="min-w-0 flex-1 truncate text-sm font-semibold text-forest-ink">{entry.username}</span>
            <span className="font-mono text-xs text-forest-muted">{entry.xp_points.toLocaleString()} XP</span>
          </li>
        ))}
      </ul>
      <div className="border-t border-forest-border px-4 py-3">
        <Link href="/leaderboard" className="focus-ring inline-flex items-center gap-1 text-sm font-semibold text-forest-accent">
          See the full board <ArrowRight className="h-4 w-4" />
        </Link>
      </div>
    </div>
  );
}
