"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { AlertCircle, Check, RotateCcw } from "lucide-react";
import { challenges as challengesApi, ApiError } from "@/lib/api";
import { demoChallenges } from "@/data/challenges";
import type { Challenge } from "@/types";
import { ChallengeCard } from "@/components/challenges/challenge-card";
import { ChallengeSkeleton } from "@/components/challenges/challenge-skeleton";
import { EmptyState } from "@/components/challenges/empty-state";
import { FilterBar, type SortOrder } from "@/components/challenges/filter-bar";
import { TopicChips } from "@/components/challenges/topic-chips";
import { DifficultyTabs, type Difficulty } from "@/components/challenges/difficulty-tabs";

const baseTopics = ["Arrays", "Strings", "Data Structures", "Algorithms", "Trees", "Graphs", "System Design", "Dynamic Programming", "Stacks", "Linked Lists"];

export default function ChallengesPage() {
  const router = useRouter();
  const pathname = usePathname();
  const params = useSearchParams();
  const mode = params.get("mode");
  const initialDifficulty = params.get("difficulty") as Difficulty;
  const initialSort = params.get("sort") as SortOrder;
  const [challenges, setChallenges] = useState<Challenge[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [usingDemoData, setUsingDemoData] = useState(false);
  const [difficulty, setDifficulty] = useState<Difficulty>(["all", "beginner", "intermediate", "advanced"].includes(initialDifficulty) ? initialDifficulty : "all");
  const [topic, setTopic] = useState(params.get("topic") || "All");
  const [sort, setSort] = useState<SortOrder>(["newest", "difficulty", "solved"].includes(initialSort) ? initialSort : "newest");
  const [searchInput, setSearchInput] = useState(params.get("search") || "");
  const [search, setSearch] = useState(params.get("search") || "");
  const [showAllTopics, setShowAllTopics] = useState(false);
  const [filtersOpen, setFiltersOpen] = useState(false);

  const loadChallenges = useCallback(async () => {
    try {
      setLoading(true);
      const liveChallenges = await challengesApi.list();
      const shouldUseDemo = liveChallenges.length === 0 && process.env.NODE_ENV === "development";
      setChallenges(shouldUseDemo ? demoChallenges : liveChallenges);
      setUsingDemoData(shouldUseDemo);
      setError(null);
    } catch (requestError) {
      setError(requestError instanceof ApiError && requestError.status === 401 ? "auth" : "network");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadChallenges(); }, [loadChallenges]);

  useEffect(() => {
    const timeout = window.setTimeout(() => setSearch(searchInput.trim()), 250);
    return () => window.clearTimeout(timeout);
  }, [searchInput]);

  useEffect(() => {
    const query = new URLSearchParams();
    if (search) query.set("search", search);
    if (difficulty !== "all") query.set("difficulty", difficulty);
    if (topic !== "All") query.set("topic", topic);
    if (sort !== "newest") query.set("sort", sort);
    if (mode) query.set("mode", mode);
    const queryString = query.toString();
    router.replace(`${pathname}${queryString ? `?${queryString}` : ""}`, { scroll: false });
  }, [difficulty, mode, pathname, router, search, sort, topic]);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      const target = event.target as HTMLElement;
      if (event.key === "/" && target.tagName !== "INPUT" && target.tagName !== "TEXTAREA") {
        event.preventDefault();
        document.querySelector<HTMLInputElement>("[aria-label='Search challenges']")?.focus();
      }
      if (event.key === "Escape" && searchInput) setSearchInput("");
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [searchInput]);

  const topics = useMemo(() => ["All", ...Array.from(new Set([...baseTopics, ...challenges.map((challenge) => challenge.topic)]))], [challenges]);
  const filtered = useMemo(() => {
    const result = challenges.filter((challenge) => {
      if (difficulty !== "all" && challenge.difficulty !== difficulty) return false;
      if (topic !== "All" && challenge.topic !== topic) return false;
      if (search && !`${challenge.title} ${challenge.description} ${challenge.topic}`.toLowerCase().includes(search.toLowerCase())) return false;
      return true;
    });
    return result.sort((left, right) => sort === "difficulty" ? left.difficulty.localeCompare(right.difficulty) : sort === "solved" ? right.xp_reward - left.xp_reward : right.id - left.id);
  }, [challenges, difficulty, search, sort, topic]);

  const hasFilters = Boolean(search || difficulty !== "all" || topic !== "All");
  const clearFilters = () => {
    setSearchInput("");
    setSearch("");
    setDifficulty("all");
    setTopic("All");
    setSort("newest");
  };

  return (
    <main className="min-h-full bg-[var(--challenge-bg)] text-[var(--challenge-text)]">
      <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6 sm:py-10 lg:px-8">
        <header className="flex flex-col justify-between gap-8 border-b border-[var(--challenge-border)] pb-8 md:flex-row md:items-end">
          <div>
            <p className="mb-3 text-xs font-bold uppercase tracking-[0.16em] text-[var(--challenge-accent-strong)]">Practice library</p>
            <h1 className="text-3xl font-semibold tracking-[-0.035em] text-[var(--challenge-text)] sm:text-4xl">Coding Challenges</h1>
            <p className="mt-3 max-w-[60ch] text-[15px] leading-7 text-[var(--challenge-muted)]">Focused problems for building sharper technical instincts, one concept at a time.</p>
          </div>
          <div className="w-full max-w-[220px] md:pb-1">
            <div className="flex items-baseline justify-between text-xs font-semibold"><span className="text-[var(--challenge-muted)]">Progress</span><span className="text-[var(--challenge-text)]">0 / 120 solved</span></div>
            <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-[var(--challenge-surface-muted)]"><div className="h-full w-0 rounded-full bg-[var(--challenge-accent)]" /></div>
          </div>
        </header>

        <section aria-label="Challenge filters" className="mt-6 space-y-5">
          <FilterBar search={searchInput} difficulty={difficulty} sort={sort} onSearchChange={setSearchInput} onDifficultyChange={setDifficulty} onSortChange={setSort} onClearSearch={() => setSearchInput("")} onOpenFilters={() => setFiltersOpen(true)} />
          <TopicChips topics={topics} value={topic} showAll={showAllTopics} onChange={setTopic} onToggleShowAll={() => setShowAllTopics((value) => !value)} />
        </section>

        {filtersOpen && <div className="fixed inset-0 z-50 flex items-end bg-slate-950/35 lg:hidden" role="presentation" onClick={() => setFiltersOpen(false)}>
          <section role="dialog" aria-modal="true" aria-labelledby="mobile-filter-title" onClick={(event) => event.stopPropagation()} className="w-full rounded-t-2xl border-t border-[var(--challenge-border)] bg-[var(--challenge-surface)] p-5 shadow-2xl">
            <div className="flex items-center justify-between"><h2 id="mobile-filter-title" className="text-lg font-bold text-[var(--challenge-text)]">Filters</h2><button type="button" onClick={() => setFiltersOpen(false)} className="min-h-10 rounded-md px-3 text-sm font-semibold text-[var(--challenge-accent-strong)]">Done</button></div>
            <div className="mt-5"><DifficultyTabs value={difficulty} onChange={setDifficulty} /></div>
            <div className="mt-5"><TopicChips topics={topics} value={topic} showAll={true} onChange={setTopic} onToggleShowAll={() => undefined} /></div>
          </section>
        </div>}

        <div className="mt-6 flex min-h-8 flex-wrap items-center justify-between gap-3" aria-live="polite">
          <div className="flex flex-wrap items-center gap-2">
            {hasFilters && <span className="text-xs font-semibold text-[var(--challenge-muted)]">Active:</span>}
            {search && <button type="button" onClick={() => setSearchInput("")} className="rounded-full bg-[var(--challenge-accent-soft)] px-2.5 py-1 text-xs font-semibold text-[var(--challenge-accent-strong)]">Search: {search} ×</button>}
            {difficulty !== "all" && <button type="button" onClick={() => setDifficulty("all")} className="rounded-full bg-[var(--challenge-accent-soft)] px-2.5 py-1 text-xs font-semibold capitalize text-[var(--challenge-accent-strong)]">{difficulty} ×</button>}
            {topic !== "All" && <button type="button" onClick={() => setTopic("All")} className="rounded-full bg-[var(--challenge-accent-soft)] px-2.5 py-1 text-xs font-semibold text-[var(--challenge-accent-strong)]">{topic} ×</button>}
            {hasFilters && <button type="button" onClick={clearFilters} className="inline-flex items-center gap-1 px-1 text-xs font-semibold text-[var(--challenge-muted)] hover:text-[var(--challenge-text)]"><RotateCcw aria-hidden="true" className="h-3.5 w-3.5" />Clear all</button>}
          </div>
          <p className="text-sm font-semibold text-[var(--challenge-muted)]">{loading ? "Loading challenges..." : `${filtered.length} challenge${filtered.length === 1 ? "" : "s"}`}</p>
        </div>

        {usingDemoData && <p className="mt-3 text-xs text-[var(--challenge-muted)]"><Check aria-hidden="true" className="mr-1 inline h-3.5 w-3.5 text-emerald-600" />Development preview using local examples while the API library is empty.</p>}

        <section className="mt-5" aria-label="Challenge results">
          {error === "network" && <div className="flex items-center justify-between gap-4 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800"><span className="inline-flex items-center gap-2"><AlertCircle aria-hidden="true" className="h-4 w-4" />Could not load the challenge library.</span><button type="button" onClick={loadChallenges} className="font-bold underline underline-offset-2">Try again</button></div>}
          {error === "auth" && <div className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">Sign in to view your challenge progress.</div>}
          {loading ? <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">{Array.from({ length: 6 }).map((_, index) => <ChallengeSkeleton key={index} />)}</div> : !error && filtered.length === 0 ? <EmptyState filtered={hasFilters} onClear={clearFilters} /> : !error && <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">{filtered.map((challenge) => <ChallengeCard key={challenge.id} challenge={challenge} acceptanceRate={Math.max(54, 92 - challenge.id * 5)} />)}</div>}
        </section>
      </div>
    </main>
  );
}