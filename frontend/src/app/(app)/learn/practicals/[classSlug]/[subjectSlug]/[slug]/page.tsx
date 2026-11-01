"use client";

import Link from "next/link";
import { Bookmark, CheckCircle2, Circle, FlaskConical } from "lucide-react";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { practicals as practicalsApi } from "@/lib/api";
import type { PracticalDetail } from "@/types";

const sections: Array<[keyof PracticalDetail, string]> = [
  ["aim", "Objective / Aim"], ["apparatus", "Required apparatus"], ["theory", "Theory"],
  ["procedure", "Procedure / Method"], ["observations", "Observations"], ["calculations", "Calculations"],
  ["result", "Result / Conclusion"], ["precautions", "Precautions"],
];

export default function PracticalDetailPage() {
  const { classSlug, subjectSlug, slug } = useParams<{ classSlug: string; subjectSlug: string; slug: string }>();
  const [practical, setPractical] = useState<PracticalDetail | null>(null);
  const [state, setState] = useState<"loading" | "ready" | "error">("loading");
  useEffect(() => {
    let active = true;
    practicalsApi.detail(slug).then((data) => { if (active) { setPractical(data); setState("ready"); } }).catch(() => { if (active) setState("error"); });
    return () => { active = false; };
  }, [slug]);
  const update = async (field: "is_completed" | "is_bookmarked") => {
    if (!practical) return;
    const value = !practical[field];
    if (field === "is_completed") await practicalsApi.complete(slug, value);
    else await practicalsApi.bookmark(slug, value);
    setPractical({ ...practical, [field]: value });
  };
  if (state === "loading") return <main className="mx-auto max-w-4xl px-4 py-12"><div className="h-8 w-2/3 animate-pulse rounded bg-secondary" /><div className="mt-6 h-64 animate-pulse rounded-card bg-secondary" /></main>;
  if (state === "error" || !practical) return <main className="mx-auto max-w-4xl px-4 py-12"><div className="rounded-card border border-dashed p-10 text-center">This practical could not be loaded.</div></main>;
  return <main className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
    <nav className="mb-6 text-sm text-muted-foreground"><Link href="/learn/practicals" className="hover:text-foreground">Practicals</Link><span className="mx-2">/</span><Link href={`/learn/practicals/${classSlug}/${subjectSlug}`} className="hover:text-foreground">Back to practicals</Link></nav>
    <header className="rounded-card bg-[#0f1d32] p-7 text-white sm:p-9"><div className="flex items-start justify-between gap-4"><div><div className="flex items-center gap-2 text-sm text-white/70"><FlaskConical className="h-4 w-4 text-cta" />Practical {practical.practical_number} · {practical.class_title} · {practical.subject_title}</div><h1 className="mt-4 text-3xl font-bold">{practical.title}</h1>{practical.chapter_topic && <p className="mt-2 text-white/70">{practical.chapter_topic}</p>}</div><button type="button" onClick={() => update("is_bookmarked")} aria-label={practical.is_bookmarked ? "Remove bookmark" : "Bookmark practical"} className="rounded-lg p-2 text-white/70 hover:bg-white/10 hover:text-white"><Bookmark className={`h-5 w-5 ${practical.is_bookmarked ? "fill-current text-amber-300" : ""}`} /></button></div><button type="button" onClick={() => update("is_completed")} className="mt-6 inline-flex min-h-11 items-center gap-2 rounded-lg bg-cta px-4 py-2 text-sm font-bold text-white hover:opacity-90">{practical.is_completed ? <CheckCircle2 className="h-4 w-4" /> : <Circle className="h-4 w-4" />}{practical.is_completed ? "Completed" : "Mark as completed"}</button></header>
    <article className="mt-6 space-y-5">{sections.filter(([key]) => practical[key]).map(([key, title]) => <section key={key} className="rounded-card border border-[var(--color-section-border)] bg-white p-6"><h2 className="text-lg font-bold">{title}</h2><div className="mt-3 whitespace-pre-wrap text-sm leading-7 text-muted-foreground">{practical[key] as string}</div></section>)}{practical.diagrams?.length > 0 && <section className="rounded-card border border-[var(--color-section-border)] bg-white p-6"><h2 className="text-lg font-bold">Diagrams</h2><div className="mt-4 grid gap-5 sm:grid-cols-2">{practical.diagrams.map((diagram) => <figure key={diagram.url}>{/* eslint-disable-next-line @next/next/no-img-element */}<img src={diagram.url} alt={diagram.caption || practical.title} className="max-h-96 w-full rounded-lg object-contain" />{diagram.caption && <figcaption className="mt-2 text-center text-sm text-muted-foreground">{diagram.caption}</figcaption>}</figure>)}</div></section>}</article>
  </main>;
}
