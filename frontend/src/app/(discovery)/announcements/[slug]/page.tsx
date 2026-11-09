"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowLeft, CalendarDays } from "lucide-react";
import { ApiError, announcements as announcementsApi } from "@/lib/api";
import type { PublicAnnouncement } from "@/lib/api";

function dateLabel(value: string | null) {
  return value
    ? new Intl.DateTimeFormat(undefined, { dateStyle: "long" }).format(new Date(value))
    : "";
}

function priorityClass(priority: string) {
  if (priority === "urgent") return "bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-300";
  if (priority === "important") return "bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300";
  return "bg-emerald-500/10 text-emerald-700 dark:text-emerald-300";
}

export default function AnnouncementDetailPage({ params }: { params: Promise<{ slug: string }> }) {
  const [slug, setSlug] = useState("");
  const [announcement, setAnnouncement] = useState<PublicAnnouncement | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    params.then(({ slug: value }) => setSlug(value));
  }, [params]);

  useEffect(() => {
    if (!slug) return;
    let active = true;
    announcementsApi
      .detail(slug)
      .then((item) => active && setAnnouncement(item))
      .catch((requestError) => {
        if (active) {
          setError(
            requestError instanceof ApiError && requestError.status === 404
              ? "This announcement is no longer available."
              : requestError instanceof ApiError
                ? requestError.message
                : "Announcement could not be loaded.",
          );
        }
      })
      .finally(() => active && setLoading(false));
    return () => { active = false; };
  }, [slug]);

  if (loading) return <main className="min-h-full bg-background p-10 text-center text-sm text-muted-foreground">Loading announcement…</main>;

  if (error || !announcement) {
    return (
      <main className="min-h-full bg-background text-foreground">
        <div className="mx-auto max-w-3xl px-4 py-16 text-center sm:px-6">
          <p role="alert" className="text-sm text-red-600">{error || "Announcement not found."}</p>
          <Link href="/announcements" className="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-emerald-600 hover:text-emerald-500">
            <ArrowLeft className="h-4 w-4" /> Back to announcements
          </Link>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-full bg-background text-foreground">
      <div className="mx-auto max-w-3xl px-4 py-10 sm:px-6 lg:px-8">
        <Link href="/announcements" className="inline-flex items-center gap-2 text-sm font-semibold text-muted-foreground hover:text-foreground">
          <ArrowLeft className="h-4 w-4" /> All announcements
        </Link>
        <header className="mt-6 border-b border-border pb-6">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-xs font-bold uppercase tracking-[0.16em] text-emerald-600 dark:text-emerald-400">{announcement.category_label}</span>
            {announcement.priority !== "normal" && (
              <span className={`rounded px-2 py-0.5 text-[10px] font-bold uppercase ${priorityClass(announcement.priority)}`}>
                {announcement.priority_label}
              </span>
            )}
          </div>
          <h1 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">{announcement.title}</h1>
          <p className="mt-3 inline-flex items-center gap-2 text-sm text-muted-foreground">
            <CalendarDays className="h-4 w-4" />
            {dateLabel(announcement.published_at || announcement.created_at)}
          </p>
        </header>
        {announcement.cover_image && (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={announcement.cover_image} alt="" className="mt-6 w-full rounded-xl border border-border object-cover" />
        )}
        <article className="mt-6 whitespace-pre-line text-sm leading-7 text-muted-foreground sm:text-base sm:leading-8">
          {announcement.body}
        </article>
      </div>
    </main>
  );
}
