"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { CalendarDays, Search, Users } from "lucide-react";
import { competitions as competitionsApi, ApiError } from "@/lib/api";
import type { Competition } from "@/types";

const tabs = [
  ["", "Discover"],
  ["mine", "My Competitions"],
  ["completed", "Past Competitions"],
];

function dateLabel(value: string) {
  return new Intl.DateTimeFormat(undefined, { dateStyle: "medium" }).format(new Date(value));
}

export default function CompetitionsPage() {
  const [competitions, setCompetitions] = useState<Competition[]>([]);
  const [tab, setTab] = useState("");
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    const load = tab === "mine"
      ? competitionsApi.mine()
      : competitionsApi.list({ status: tab || undefined, search: search || undefined, category: category || undefined });
    load.then((items) => {
      if (active) setCompetitions(items);
    }).catch((requestError) => {
      if (active) setError(requestError instanceof ApiError ? requestError.message : "Competitions could not be loaded.");
    }).finally(() => active && setLoading(false));
    return () => { active = false; };
  }, [category, search, tab]);

  const categories = useMemo(() => Array.from(new Set(competitions.map((item) => item.category))).sort(), [competitions]);

  return (
    <main className="min-h-full bg-background text-foreground">
      <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8">
        <header className="flex flex-col justify-between gap-6 border-b border-border pb-8 md:flex-row md:items-end">
          <div>
            <p className="mb-3 text-xs font-bold uppercase tracking-[0.16em] text-emerald-600 dark:text-emerald-400">Apply your skills</p>
            <h1 className="text-4xl font-semibold tracking-tight">Competitions</h1>
            <p className="mt-3 max-w-2xl text-muted-foreground">Challenge your skills, build real projects, and compete with learners.</p>
          </div>
          <a href="#how-it-works" className="text-sm font-semibold text-emerald-600 hover:text-emerald-500">How it works</a>
        </header>

        <nav aria-label="Competition sections" className="mt-6 flex gap-2 overflow-x-auto border-b border-border">
          {tabs.map(([value, label]) => (
            <button key={value} type="button" onClick={() => setTab(value)} className={`whitespace-nowrap border-b-2 px-3 py-3 text-sm font-semibold ${tab === value ? "border-emerald-500 text-emerald-600" : "border-transparent text-muted-foreground hover:text-foreground"}`}>
              {label}
            </button>
          ))}
        </nav>

        <section aria-label="Competition filters" className="mt-6 flex flex-col gap-3 sm:flex-row">
          <label className="relative flex-1">
            <Search aria-hidden="true" className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
            <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search competitions or organizers" className="h-10 w-full rounded-lg border border-border bg-background pl-9 pr-3 text-sm outline-none ring-emerald-500 focus:ring-2" />
          </label>
          <select value={category} onChange={(event) => setCategory(event.target.value)} className="h-10 rounded-lg border border-border bg-background px-3 text-sm outline-none focus:ring-2 focus:ring-emerald-500">
            <option value="">All categories</option>
            {categories.map((item) => <option key={item} value={item}>{item}</option>)}
          </select>
        </section>

        {error && <p role="alert" className="mt-8 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700 dark:border-red-900 dark:bg-red-950/30 dark:text-red-300">{error}</p>}
        {loading ? <p className="mt-12 text-center text-sm text-muted-foreground">Loading competitions…</p> : competitions.length === 0 ? (
          <section className="mt-12 rounded-xl border border-dashed border-border px-6 py-14 text-center">
            <h2 className="text-lg font-semibold">No competitions available right now.</h2>
            <p className="mx-auto mt-2 max-w-md text-sm text-muted-foreground">New challenges are on their way. Check back soon for your next opportunity to build something great.</p>
          </section>
        ) : (
          <div className="mt-8 grid gap-5 md:grid-cols-2">
            {competitions.map((competition) => (
              <article key={competition.id} className="flex flex-col rounded-xl border border-border bg-card p-5 shadow-sm">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="text-xs font-bold uppercase tracking-wide text-emerald-600 dark:text-emerald-400">{competition.category}</p>
                    <h2 className="mt-2 text-xl font-semibold">{competition.title}</h2>
                  </div>
                  <span className="rounded-full bg-emerald-500/10 px-2.5 py-1 text-xs font-semibold capitalize text-emerald-700 dark:text-emerald-300">{competition.status.replaceAll("_", " ")}</span>
                </div>
                <p className="mt-3 line-clamp-2 text-sm leading-6 text-muted-foreground">{competition.short_description}</p>
                <div className="mt-5 grid gap-2 text-xs text-muted-foreground sm:grid-cols-2">
                  <span className="inline-flex items-center gap-2"><CalendarDays className="h-4 w-4" /> Closes {dateLabel(competition.registration_deadline)}</span>
                  <span className="inline-flex items-center gap-2"><Users className="h-4 w-4" /> {competition.participant_count}{competition.participant_limit ? ` / ${competition.participant_limit}` : ""} participants</span>
                </div>
                <div className="mt-6 flex items-center justify-between border-t border-border pt-4">
                  <span className="text-xs text-muted-foreground">By {competition.organizer_name || "Code Yaar"}</span>
                  <Link href={`/competitions/${competition.slug}`} className="text-sm font-semibold text-emerald-600 hover:text-emerald-500">View details →</Link>
                </div>
              </article>
            ))}
          </div>
        )}

        <section id="how-it-works" className="mt-16 border-t border-border pt-10">
          <h2 className="text-xl font-semibold">How competitions work</h2>
          <p className="mt-2 text-sm text-muted-foreground">Choose a challenge, register before the deadline, submit your work, and track published results in one place.</p>
        </section>
      </div>
    </main>
  );
}
