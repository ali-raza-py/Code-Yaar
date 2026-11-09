"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Megaphone } from "lucide-react";
import { ApiError, announcements as announcementsApi } from "@/lib/api";
import type { PublicAnnouncement } from "@/lib/api";

const CATEGORIES = [
  ["", "All"],
  ["general", "General"],
  ["platform_updates", "Platform Updates"],
  ["hackathons", "Hackathons"],
  ["courses", "Courses"],
  ["competitions", "Competitions"],
  ["maintenance", "Maintenance"],
  ["important", "Important"],
];

function dateLabel(value: string | null) {
  return value
    ? new Intl.DateTimeFormat(undefined, { dateStyle: "medium" }).format(new Date(value))
    : "";
}

function priorityClass(priority: string) {
  if (priority === "urgent") return "bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-300";
  if (priority === "important") return "bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300";
  return "";
}

export default function AnnouncementsPage() {
  const [category, setCategory] = useState("");
  const [items, setItems] = useState<PublicAnnouncement[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    announcementsApi
      .list(category ? { category } : undefined)
      .then((list) => active && setItems(list))
      .catch((requestError) => {
        if (active) setError(requestError instanceof ApiError ? requestError.message : "Announcements could not be loaded.");
      })
      .finally(() => active && setLoading(false));
    return () => { active = false; };
  }, [category]);

  // Switching tabs shows the spinner from the click handler rather than from
  // the effect body, which React reserves for synchronizing with external systems.
  function selectCategory(value: string) {
    if (value === category) return;
    setLoading(true);
    setError(null);
    setCategory(value);
  }

  return (
    <main className="min-h-full bg-background text-foreground">
      <div className="mx-auto max-w-4xl px-4 py-10 sm:px-6 lg:px-8">
        <header className="border-b border-border pb-8">
          <p className="mb-3 text-xs font-bold uppercase tracking-[0.16em] text-emerald-600 dark:text-emerald-400">Notice board</p>
          <h1 className="text-4xl font-semibold tracking-tight">Announcements</h1>
          <p className="mt-3 max-w-2xl text-muted-foreground">
            What&rsquo;s happening on Code Yaar — events, course news, and maintenance notices.
          </p>
        </header>

        <nav aria-label="Announcement categories" className="mt-6 flex gap-2 overflow-x-auto border-b border-border">
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
          <p className="mt-12 text-center text-sm text-muted-foreground">Loading announcements…</p>
        ) : items.length === 0 ? (
          <section className="mt-12 rounded-xl border border-dashed border-border px-6 py-14 text-center">
            <Megaphone className="mx-auto h-8 w-8 text-muted-foreground" />
            <h2 className="mt-3 text-lg font-semibold">Nothing on the board right now.</h2>
            <p className="mx-auto mt-2 max-w-md text-sm text-muted-foreground">New announcements appear here the moment they are published.</p>
          </section>
        ) : (
          <div className="mt-8 space-y-4">
            {items.map((item) => (
              <article key={item.id} className="rounded-xl border border-border bg-card p-5 shadow-sm">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-xs font-bold uppercase tracking-wide text-emerald-600 dark:text-emerald-400">{item.category_label}</span>
                  {item.priority !== "normal" && (
                    <span className={`rounded px-1.5 py-0.5 text-[10px] font-bold uppercase ${priorityClass(item.priority)}`}>
                      {item.priority_label}
                    </span>
                  )}
                  <span className="ml-auto text-xs text-muted-foreground">{dateLabel(item.published_at || item.created_at)}</span>
                </div>
                <h2 className="mt-2 text-xl font-semibold">{item.title}</h2>
                <p className="mt-2 line-clamp-3 text-sm leading-6 text-muted-foreground">{item.short_description || item.body}</p>
                {item.slug && (
                  <Link href={`/announcements/${item.slug}`} className="mt-3 inline-block text-sm font-semibold text-emerald-600 hover:text-emerald-500">
                    Read more →
                  </Link>
                )}
              </article>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
