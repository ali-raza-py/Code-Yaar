"use client";

import Link from "next/link";
import { Search, CheckCircle2, Bookmark } from "lucide-react";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { practicals as practicalsApi } from "@/lib/api";
import type { PracticalSummary } from "@/types";

export default function PracticalListPage() {
  const { classSlug, subjectSlug } = useParams<{ classSlug: string; subjectSlug: string }>();
  const [items, setItems] = useState<PracticalSummary[]>([]);
  const [search, setSearch] = useState("");
  const [state, setState] = useState<"loading" | "ready" | "error">("loading");
  useEffect(() => {
    let active = true;
    practicalsApi.list({ classSlug, subjectSlug, search: search || undefined }).then((data) => { if (active) { setItems(data); setState("ready"); } }).catch(() => { if (active) setState("error"); });
    return () => { active = false; };
  }, [classSlug, subjectSlug, search]);
  return <main className="mx-auto max-w-5xl px-4 py-8 sm:px-6 lg:px-8">
    <nav className="mb-6 text-sm text-muted-foreground"><Link href="/learn/practicals" className="hover:text-foreground">Practicals</Link><span className="mx-2">/</span><Link href={`/learn/practicals/${classSlug}`} className="hover:text-foreground">{classSlug.replaceAll("-", " ")}</Link><span className="mx-2">/</span><span>{subjectSlug.replaceAll("-", " ")}</span></nav>
    <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end"><div><h1 className="text-3xl font-bold capitalize">{subjectSlug.replaceAll("-", " ")} practicals</h1><p className="mt-2 text-muted-foreground">Read the complete method and record your progress.</p></div><label className="relative block w-full sm:w-72"><span className="sr-only">Search practicals</span><Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" /><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search practicals..." className="w-full rounded-lg border border-[var(--color-section-border)] bg-white px-4 py-2 pl-9 text-sm outline-none focus:border-[var(--primary)]" /></label></div>
    {state === "loading" && <div className="mt-8 space-y-3">{[1, 2, 3].map((item) => <div key={item} className="h-24 animate-pulse rounded-card bg-secondary" />)}</div>}
    {state === "error" && <div className="mt-8 rounded-card border border-dashed p-10 text-center">Practicals could not be loaded.</div>}
    {state === "ready" && items.length === 0 && <div className="mt-8 rounded-card border border-dashed p-10 text-center"><h2 className="font-semibold">No practicals found</h2><p className="mt-2 text-sm text-muted-foreground">Try a different search or check back later.</p></div>}
    {state === "ready" && items.length > 0 && <div className="mt-8 space-y-3">{items.map((item) => <Link key={item.id} href={`/learn/practicals/${classSlug}/${subjectSlug}/${item.slug}`} className="group flex items-center justify-between rounded-card border border-[var(--color-section-border)] bg-white p-5 hover:border-[var(--primary)] hover:shadow-md"><div><div className="flex items-center gap-2 text-xs font-semibold text-muted-foreground"><span>Practical {item.practical_number}</span>{item.chapter_topic && <><span>·</span><span>{item.chapter_topic}</span></>}</div><h2 className="mt-2 font-bold group-hover:text-cta">{item.title}</h2>{item.description && <p className="mt-1 text-sm text-muted-foreground">{item.description}</p>}</div><div className="flex items-center gap-3 text-muted-foreground">{item.is_completed && <CheckCircle2 className="h-5 w-5 text-cta" aria-label="Completed" />}{item.is_bookmarked && <Bookmark className="h-5 w-5 fill-current text-amber-500" aria-label="Bookmarked" />}<span className="text-sm">Read</span></div></Link>)}</div>}
  </main>;
}
