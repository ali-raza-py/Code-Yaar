'use client';

import Link from 'next/link';
import { useEffect, useMemo, useState } from 'react';
import { ArrowRight, Clock, Layers, Search, Target } from 'lucide-react';
import { tracks as tracksApi, type TrackCategory, type TrackSummary } from '@/lib/api';
import { NetworkError } from '@/components/learning/workspace/error-states';
import { trackDifficultyTone } from '@/components/learning/tracks/shared';

/**
 * LEARN > Tracks: the discovery layer of the platform. Everything on this
 * page is served by GET /api/tracks/ — published tracks with at least one
 * published course — so nothing here is hardcoded and empty shelves (like a
 * track awaiting its first course) never surface.
 */

const CATEGORY_LABELS: Record<TrackCategory, string> = {
  school_board: 'School & Board Education',
  programming: 'Programming',
  web: 'Web Development',
  ai: 'Artificial Intelligence',
  other: 'Other',
};

function TrackCard({ track }: { track: TrackSummary }) {
  return (
    <Link
      href={`/learn/tracks/${track.slug}`}
      className="group flex flex-col overflow-hidden rounded-card border border-border bg-card transition-all hover:border-primary/50 hover:shadow-[var(--shadow-2)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
    >
      {/* Cover: admin-uploaded artwork when set, a calm navy panel otherwise. */}
      <div className="relative h-32 shrink-0 overflow-hidden bg-hero-navy">
        {track.cover_url ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={track.cover_url} alt="" className="h-full w-full object-cover" />
        ) : (
          <div className="flex h-full items-end justify-between p-4">
            <span className="rounded-pill bg-white/10 px-2.5 py-1 text-[11px] font-bold uppercase tracking-wider text-white/80">
              {CATEGORY_LABELS[track.category] ?? track.category_display}
            </span>
            <Layers aria-hidden="true" className="h-6 w-6 text-white/25" />
          </div>
        )}
      </div>

      <div className="flex min-h-0 flex-1 flex-col p-5">
        <div className="flex items-center gap-2 text-[11px] font-semibold uppercase tracking-wider">
          <span className={`rounded-pill px-2 py-0.5 ${trackDifficultyTone(track.difficulty)}`}>
            {track.difficulty}
          </span>
          <span className="text-muted-foreground">
            {track.course_count} course{track.course_count === 1 ? '' : 's'}
          </span>
          {track.estimated_hours > 0 && (
            <span className="ml-auto inline-flex items-center gap-1 text-muted-foreground">
              <Clock aria-hidden="true" className="h-3.5 w-3.5" />
              {track.estimated_hours}h
            </span>
          )}
        </div>

        <h2 className="mt-3 text-lg font-bold text-foreground group-hover:text-primary">{track.title}</h2>
        <p className="mt-2 line-clamp-2 text-sm text-muted-foreground">{track.description}</p>

        {track.learning_objectives.length > 0 && (
          <p className="mt-3 flex items-start gap-1.5 text-xs text-muted-foreground">
            <Target aria-hidden="true" className="mt-0.5 h-3.5 w-3.5 shrink-0 text-primary" />
            <span className="line-clamp-1">
              {track.learning_objectives.length} learning objective{track.learning_objectives.length === 1 ? '' : 's'}
            </span>
          </p>
        )}

        {track.enrolled && (
          <div className="mt-4">
            <div className="flex items-center justify-between text-xs font-medium">
              <span className="text-muted-foreground">Your progress</span>
              <span className="text-foreground">{track.progress_percentage}%</span>
            </div>
            <div className="mt-1.5 h-1.5 overflow-hidden rounded-full bg-muted">
              <div
                className="h-full rounded-full bg-cta transition-[width] duration-300"
                style={{ width: `${Math.max(track.progress_percentage, 2)}%` }}
              />
            </div>
          </div>
        )}

        <div className="mt-auto flex items-center justify-between pt-5 text-xs">
          <span className="font-semibold text-muted-foreground">
            {track.total_xp > 0 ? `${track.total_xp} XP available` : ' '}
          </span>
          <span className="font-semibold text-primary">
            {track.enrolled ? 'Continue learning' : 'Explore track'}
            <ArrowRight aria-hidden="true" className="ml-1 inline h-3.5 w-3.5" />
          </span>
        </div>
      </div>
    </Link>
  );
}

export default function TracksPage() {
  const [tracks, setTracks] = useState<TrackSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [category, setCategory] = useState<TrackCategory | 'all'>('all');
  const [search, setSearch] = useState('');

  const load = async () => {
    try {
      const data = await tracksApi.list();
      setTracks(data);
      setError(false);
    } catch {
      setError(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Deferred via await so the effect never sets state synchronously.
    (async () => { await load(); })();
  }, []);

  // Only categories that actually have published tracks get a chip.
  const categories = useMemo(
    () => Array.from(new Set(tracks.map((track) => track.category))),
    [tracks],
  );

  const filtered = useMemo(() => {
    const query = search.trim().toLowerCase();
    return tracks.filter((track) => {
      const matchesCategory = category === 'all' || track.category === category;
      const matchesSearch =
        !query ||
        `${track.title} ${track.description} ${CATEGORY_LABELS[track.category] ?? ''}`
          .toLowerCase()
          .includes(query);
      return matchesCategory && matchesSearch;
    });
  }, [category, search, tracks]);

  return (
    <div className="mx-auto max-w-6xl px-4 py-6 sm:px-6 lg:px-8">
      <header className="mb-6 overflow-hidden rounded-card bg-hero-navy p-8 text-white sm:p-10">
        <p className="text-xs font-bold uppercase tracking-[0.14em] text-white/60">Learn</p>
        <h1 className="mt-2 text-2xl font-bold sm:text-3xl">Learning Tracks</h1>
        <p className="mt-3 max-w-2xl text-sm text-white/70 sm:text-base">
          Structured paths that group related courses in the right order — pick a track
          and follow it from first lesson to certificate.
        </p>
      </header>

      <div className="mb-4 flex flex-wrap items-center gap-2" role="group" aria-label="Filter tracks by category">
        <button
          type="button"
          onClick={() => setCategory('all')}
          className={`rounded-pill px-4 py-2 text-sm font-medium transition-colors ${
            category === 'all'
              ? 'bg-hero-navy text-white'
              : 'border border-border bg-card text-foreground hover:bg-muted'
          }`}
        >
          All Tracks
        </button>
        {categories.map((slug) => (
          <button
            key={slug}
            type="button"
            onClick={() => setCategory(slug)}
            className={`rounded-pill px-4 py-2 text-sm font-medium transition-colors ${
              category === slug
                ? 'bg-hero-navy text-white'
                : 'border border-border bg-card text-foreground hover:bg-muted'
            }`}
          >
            {CATEGORY_LABELS[slug]}
          </button>
        ))}
        <label className="relative ml-auto block w-full sm:w-72">
          <span className="sr-only">Search tracks</span>
          <Search aria-hidden="true" className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <input
            type="search"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search tracks..."
            className="w-full rounded-pill border border-border bg-card py-2 pl-9 pr-4 text-sm outline-none transition-colors focus:border-primary"
          />
        </label>
      </div>

      {error ? (
        <NetworkError onRetry={load} />
      ) : loading ? (
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map((item) => (
            <div key={item} className="h-72 animate-pulse rounded-card border border-border bg-card" />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <div className="rounded-card border border-dashed border-border bg-card p-12 text-center">
          <h2 className="font-semibold">No tracks match your search</h2>
          <p className="mt-2 text-sm text-muted-foreground">
            Try another keyword or switch back to “All Tracks”.
          </p>
        </div>
      ) : (
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((track) => (
            <TrackCard key={track.id} track={track} />
          ))}
        </div>
      )}
    </div>
  );
}
