"use client";

import Link from "next/link";
import { ArrowRight, BookOpen } from "lucide-react";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { practicals as practicalsApi } from "@/lib/api";
import type { PracticalSubject } from "@/types";

export default function PracticalSubjectsPage() {
  const { classSlug } = useParams<{ classSlug: string }>();
  const [subjects, setSubjects] = useState<PracticalSubject[]>([]);
  const [state, setState] = useState<"loading" | "ready" | "error">("loading");
  useEffect(() => {
    let active = true;
    practicalsApi.subjects(classSlug).then((data) => { if (active) { setSubjects(data); setState("ready"); } }).catch(() => { if (active) setState("error"); });
    return () => { active = false; };
  }, [classSlug]);
  return <main className="mx-auto max-w-5xl px-4 py-8 sm:px-6 lg:px-8">
    <nav className="mb-6 text-sm text-muted-foreground"><Link href="/learn" className="hover:text-foreground">Learn</Link><span className="mx-2">/</span><Link href="/learn/practicals" className="hover:text-foreground">Practicals</Link><span className="mx-2">/</span><span>{classSlug.replaceAll("-", " ")}</span></nav>
    <h1 className="text-3xl font-bold capitalize">Choose a subject</h1><p className="mt-2 text-muted-foreground">Select a subject to view its practical exercises.</p>
    {state === "loading" && <div className="mt-8 grid gap-4 sm:grid-cols-2">{[1, 2, 3, 4].map((item) => <div key={item} className="h-28 animate-pulse rounded-card bg-secondary" />)}</div>}
    {state === "error" && <div className="mt-8 rounded-card border border-dashed p-10 text-center">Subjects could not be loaded.</div>}
    {state === "ready" && subjects.length === 0 && <div className="mt-8 rounded-card border border-dashed p-10 text-center"><h2 className="font-semibold">No subjects published yet</h2><p className="mt-2 text-sm text-muted-foreground">Check back after content has been reviewed.</p></div>}
    {state === "ready" && subjects.length > 0 && <div className="mt-8 grid gap-4 sm:grid-cols-2">{subjects.map((subject) => <Link key={subject.id} href={`/learn/practicals/${classSlug}/${subject.slug}`} className="group flex items-center justify-between rounded-card border border-[var(--color-section-border)] bg-white p-6 hover:border-[var(--primary)] hover:shadow-md"><div className="flex items-center gap-4"><BookOpen className="h-7 w-7 text-cta" /><div><h2 className="font-bold group-hover:text-cta">{subject.title}</h2><p className="mt-1 text-sm text-muted-foreground">{subject.description || "Explore subject practicals."}</p><p className="mt-2 text-xs font-semibold text-muted-foreground">{subject.practical_count} practical{subject.practical_count === 1 ? "" : "s"}</p></div></div><ArrowRight className="h-5 w-5 text-muted-foreground" /></Link>)}</div>}
  </main>;
}
