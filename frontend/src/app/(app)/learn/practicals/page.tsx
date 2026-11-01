"use client";

import Link from "next/link";
import { FlaskConical, ArrowRight } from "lucide-react";
import { useEffect, useState } from "react";
import { practicals as practicalsApi } from "@/lib/api";
import { useAuth } from "@/hooks/use-auth";
import type { PracticalClass } from "@/types";

export default function PracticalsPage() {
  const { user } = useAuth();
  const [classes, setClasses] = useState<PracticalClass[]>([]);
  const [state, setState] = useState<"loading" | "ready" | "error">("loading");

  useEffect(() => {
    let active = true;
    practicalsApi.classes().then((data) => {
      if (active) { setClasses(data); setState("ready"); }
    }).catch(() => { if (active) setState("error"); });
    return () => { active = false; };
  }, []);

  return (
    <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <nav className="mb-6 text-sm text-muted-foreground"><Link href="/learn" className="hover:text-foreground">Learn</Link><span className="mx-2">/</span><span>Practicals</span></nav>
      {user?.role === "administrator" && <div className="mb-5 flex flex-wrap gap-2"><Link href="/learn/practicals/manage" className="rounded-lg bg-primary px-4 py-2 text-sm font-bold text-primary-foreground">Manage Courses</Link><Link href="/learn/practicals/manage?mode=subjects" className="rounded-lg border border-[var(--color-section-border)] bg-white px-4 py-2 text-sm font-bold">Add Subject</Link><Link href="/learn/practicals/manage?mode=practicals" className="rounded-lg border border-[var(--color-section-border)] bg-white px-4 py-2 text-sm font-bold">Add Practical</Link><Link href="/learn/practicals/manage?mode=classes" className="rounded-lg border border-[var(--color-section-border)] bg-white px-4 py-2 text-sm font-bold">Add Course</Link></div>}
      <section className="rounded-card bg-[#0f1d32] p-8 text-white sm:p-10">
        <div className="flex items-center gap-3"><FlaskConical className="h-8 w-8 text-cta" /><h1 className="text-3xl font-bold sm:text-4xl">Practicals</h1></div>
        <p className="mt-3 max-w-2xl text-white/70">Explore verified practical exercises organized by class and subject.</p>
      </section>
      {state === "loading" && <div className="mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">{[1, 2, 3, 4].map((item) => <div key={item} className="h-40 animate-pulse rounded-card bg-secondary" />)}</div>}
      {state === "error" && <div className="mt-8 rounded-card border border-dashed p-10 text-center"><h2 className="font-semibold">Practicals could not be loaded</h2><p className="mt-2 text-sm text-muted-foreground">Please try again in a moment.</p></div>}
      {state === "ready" && classes.length === 0 && <div className="mt-8 rounded-card border border-dashed p-10 text-center"><h2 className="font-semibold">No classes published yet</h2><p className="mt-2 text-sm text-muted-foreground">Verified practical content will appear here when it is published.</p></div>}
      {state === "ready" && classes.length > 0 && <div className="mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">{classes.map((schoolClass) => <Link key={schoolClass.id} href={`/learn/practicals/${schoolClass.slug}`} className="group rounded-card border border-[var(--color-section-border)] bg-white p-6 transition hover:border-[var(--primary)] hover:shadow-md"><div className="flex items-start justify-between"><span className="rounded-full bg-cta/10 px-3 py-1 text-xs font-bold text-cta">CLASS</span><ArrowRight className="h-5 w-5 text-muted-foreground transition group-hover:text-cta" /></div><h2 className="mt-8 text-xl font-bold group-hover:text-cta">{schoolClass.title} Practicals</h2><p className="mt-2 text-sm text-muted-foreground">{schoolClass.description || "Practical exercises for this class."}</p><p className="mt-5 text-xs font-semibold text-muted-foreground">{schoolClass.subject_count} subject{schoolClass.subject_count === 1 ? "" : "s"}</p></Link>)}</div>}
    </main>
  );
}
