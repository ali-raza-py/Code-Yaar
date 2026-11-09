"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { History } from "lucide-react";
import { ApiError, platformUpdates as platformUpdatesApi } from "@/lib/api";
import type { PublicPlatformUpdate } from "@/lib/api";

const CATEGORIES = [
  ["", "All"],
  ["feature", "New Features"],
  ["course", "Courses & Tracks"],
  ["improvement", "Improvements"],
  ["bug_fix", "Bug Fixes"],
  ["performance", "Performance"],
  ["certificate", "Certificates"],
  ["other", "Other"],
];

function dateLabel(value: string | null) {
  return value
    ? new Intl.DateTimeFormat(undefined, { dateStyle: "long" }).format(new Date(value))
    : "";
}

export default function UpdatesPage() {
  const [category, setCategory] = useState("");
  const [items, setItems] = useState<PublicPlatformUpdate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    platformUpdatesApi
      .list(category ? { category } : undefined)
      .then((list) => active && setItems(list))
      .catch((requestError) => {
        if (active) setError(requestError instanceof ApiError ? requestError.message : "Updates could not be loaded.");
      })
      .finally(() => active && setLoading(false));
    return () => { active = false; };
  }, [category]);

  // The spinner is raised from the click handler instead of the effect body,
  // which React reserves for synchronizing with external systems.
  function selectCategory(value: string) {
    if (value === category) return;
    setLoading(true);
    setError(null);
    setCategory(value);
  }

  return (
    <main className="min-h-full bg-background text-foreground">
      <div className="mx-auto max-w-3xl px-4 py-10 sm:px-6 lg:px-8">
        <header className="border-b border-border pb-8">
          <p className="mb-3 text-xs font-bold uppercase tracking-[0.16em] text-emerald-600 dark:text-emerald-400">Changelog</p>
          <h1 className="text-4xl font-semibold tracking-tight">Updates</h1>
          <p className="mt-3 max-w-2xl text-muted-foreground">
            The permanent record of what changed on Code Yaar — newest first.
          </p>
        </header>

        <nav aria-label="Update categories" className="mt-6 flex gap-2 overflow-x-auto border-b border-border">
          {CATEGORIES.map(([value, label]) => (
            <button
              key={value}
              type="button"
              onClick={() => selectCategory(value)}
              className={`whitespace-nowrap border-b-2 px-3 py-3 text-sm font-semibold ${category === value ? "border-emerald-500 text-emerald-600" : "border-transparent text-muted-foreground hover:text-foreground"}`}
            >
              {label}
            </button>
          ))}
        </nav>

        {error && <p role="alert" className="mt-8 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700 dark:border-red-900 dark:bg-red-950/30 dark:text-red-300">{error}</p>}
        {loading ? (
          <p className="mt-12 text-center text-sm text-muted-foreground">Loading updates…</p>
        ) : items.length === 0 ? (
          <section className="mt-12 rounded-xl border border-dashed border-border px-6 py-14 text-center">
            <History className="mx-auto h-8 w-8 text-muted-foreground" />
            <h2 className="mt-3 text-lg font-semibold">No updates in this category yet.</h2>
            <p className="mx-auto mt-2 max-w-md text-sm text-muted-foreground">Every published change to the platform shows up here.</p>
          </section>
        ) : (
          <ol className="mt-10 space-y-10">
            {items.map((item) => (
              <li key={item.id} className="relative border-l-2 border-emerald-500/40 pl-6">
                <span className="absolute -left-[7px] top-1.5 h-3 w-3 rounded-full bg-emerald-500" />
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-xs font-bold uppercase tracking-wide text-emerald-600 dark:text-emerald-400">{item.category_label}</span>
                  {item.version && <span className="rounded-full bg-muted px-2 py-0.5 text-xs font-semibold">{item.version}</span>}
                  <span className="text-xs text-muted-foreground">{dateLabel(item.published_at)}</span>
                </div>
                <h2 className="mt-2 text-xl font-semibold">
                  {item.slug ? (
                    <Link href={`/updates/${item.slug}`} className="hover:text-emerald-600">{item.title}</Link>
                  ) : (
                    item.title
                  )}
                </h2>
                {item.summary && <p className="mt-2 text-sm leading-6 text-muted-foreground">{item.summary}</p>}
                {item.change_list.length > 0 && (
                  <ul className="mt-3 list-disc space-y-1 pl-5 text-sm text-muted-foreground">
                    {item.change_list.slice(0, 5).map((change) => <li key={change}>{change}</li>)}
                  </ul>
                )}
                {item.slug && (
                  <Link href={`/updates/${item.slug}`} className="mt-3 inline-block text-sm font-semibold text-emerald-600 hover:text-emerald-500">
                    Full details →
                  </Link>
                )}
              </li>
            ))}
          </ol>
        )}
      </div>
    </main>
  );
}
