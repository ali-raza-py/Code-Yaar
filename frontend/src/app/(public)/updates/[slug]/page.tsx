"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowLeft } from "lucide-react";
import { ApiError, platformUpdates as platformUpdatesApi } from "@/lib/api";
import type { PublicPlatformUpdate } from "@/lib/api";

function dateLabel(value: string | null) {
  return value
    ? new Intl.DateTimeFormat(undefined, { dateStyle: "long" }).format(new Date(value))
    : "";
}

export default function UpdateDetailPage({ params }: { params: Promise<{ slug: string }> }) {
  const [slug, setSlug] = useState("");
  const [update, setUpdate] = useState<PublicPlatformUpdate | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    params.then(({ slug: value }) => setSlug(value));
  }, [params]);

  useEffect(() => {
    if (!slug) return;
    let active = true;
    platformUpdatesApi
      .detail(slug)
      .then((item) => active && setUpdate(item))
      .catch((requestError) => {
        if (active) {
          setError(
            requestError instanceof ApiError && requestError.status === 404
              ? "This update is no longer available."
              : requestError instanceof ApiError
                ? requestError.message
                : "Update could not be loaded.",
          );
        }
      })
      .finally(() => active && setLoading(false));
    return () => { active = false; };
  }, [slug]);

  if (loading) return <main className="min-h-full bg-background p-10 text-center text-sm text-muted-foreground">Loading update…</main>;

  if (error || !update) {
    return (
      <main className="min-h-full bg-background text-foreground">
        <div className="mx-auto max-w-3xl px-4 py-16 text-center sm:px-6">
          <p role="alert" className="text-sm text-red-600">{error || "Update not found."}</p>
          <Link href="/updates" className="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-emerald-600 hover:text-emerald-500">
            <ArrowLeft className="h-4 w-4" /> Back to updates
          </Link>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-full bg-background text-foreground">
      <div className="mx-auto max-w-3xl px-4 py-10 sm:px-6 lg:px-8">
        <Link href="/updates" className="inline-flex items-center gap-2 text-sm font-semibold text-muted-foreground hover:text-foreground">
          <ArrowLeft className="h-4 w-4" /> All updates
        </Link>
        <header className="mt-6 border-b border-border pb-6">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-xs font-bold uppercase tracking-[0.16em] text-emerald-600 dark:text-emerald-400">{update.category_label}</span>
            {update.version && <span className="rounded-full bg-muted px-2.5 py-0.5 text-xs font-semibold">{update.version}</span>}
          </div>
          <h1 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">{update.title}</h1>
          <p className="mt-2 text-sm text-muted-foreground">{dateLabel(update.published_at)}</p>
        </header>
        {update.summary && (
          <p className="mt-6 rounded-lg bg-muted/60 p-4 text-sm font-medium leading-6 text-foreground">{update.summary}</p>
        )}
        {update.change_list.length > 0 && (
          <section className="mt-6">
            <h2 className="text-lg font-semibold">What changed</h2>
            <ul className="mt-3 list-disc space-y-2 pl-5 text-sm leading-6 text-muted-foreground">
              {update.change_list.map((change) => <li key={change}>{change}</li>)}
            </ul>
          </section>
        )}
        <article className="mt-6 whitespace-pre-line text-sm leading-7 text-muted-foreground sm:text-base sm:leading-8">
          {update.content}
        </article>
      </div>
    </main>
  );
}
