"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { GitBranch } from "lucide-react";
import { tracks as tracksApi } from "@/lib/api";
import type { TrackSummary } from "@/lib/api";

/**
 * Career tracks sourced from GET /api/tracks/ (real records, managed in Django admin).
 */
export function TracksStrip() {
  const [tracks, setTracks] = useState<TrackSummary[] | null>(null);

  useEffect(() => {
    let cancelled = false;
    tracksApi.list()
      .then((data) => { if (!cancelled) setTracks(data); })
      .catch(() => { if (!cancelled) setTracks([]); });
    return () => { cancelled = true; };
  }, []);

  if (tracks === null) {
    return (
      <div className="grid gap-3 sm:grid-cols-2">
        {[1, 2].map((i) => (
          <div key={i} className="h-32 animate-pulse rounded-[var(--radius-card)] border border-forest-border bg-white/60" />
        ))}
      </div>
    );
  }

  if (tracks.length === 0) {
    return (
      <div className="rounded-[var(--radius-card)] border border-forest-border bg-white p-5 text-sm text-forest-muted">
        Career tracks are being prepared. Meanwhile, the{' '}
        <Link href="/learn" className="focus-ring rounded font-semibold text-forest-accent">course catalog</Link>{' '}
        is open.
      </div>
    );
  }

  return (
    <div className="grid gap-3 sm:grid-cols-2">
      {tracks.slice(0, 4).map((track) => (
        <Link key={track.slug} href={`/learn?track=${track.slug}`} className="focus-ring group rounded-[var(--radius-card)] border border-forest-border bg-white p-5 hover:border-forest-border-hover">
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="font-mono text-[10px] uppercase tracking-wider text-forest-line-soft">
                {track.difficulty} · {track.estimated_hours} hours · {track.course_count} {track.course_count === 1 ? 'course' : 'courses'}
              </p>
              <h3 className="mt-2 font-bold group-hover:text-forest-accent">{track.title}</h3>
            </div>
            <GitBranch className="h-5 w-5 text-forest-line-soft" />
          </div>
          <p className="mt-3 line-clamp-2 text-sm text-forest-muted">{track.description}</p>
        </Link>
      ))}
    </div>
  );
}
