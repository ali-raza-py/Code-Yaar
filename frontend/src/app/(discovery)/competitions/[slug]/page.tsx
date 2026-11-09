"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowLeft, CalendarDays, Trophy, Users } from "lucide-react";
import { ApiError, competitions as competitionsApi } from "@/lib/api";
import type { CompetitionDetail, CompetitionResult, CompetitionSubmission } from "@/types";
import { useAuth } from "@/hooks/use-auth";

function dateLabel(value: string | null) {
  return value ? new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" }).format(new Date(value)) : "To be announced";
}

export default function CompetitionDetailPage({ params }: { params: Promise<{ slug: string }> }) {
  const { isAuthenticated } = useAuth();
  const [slug, setSlug] = useState("");
  const [detail, setDetail] = useState<CompetitionDetail | null>(null);
  const [results, setResults] = useState<CompetitionResult[]>([]);
  const [submission, setSubmission] = useState<CompetitionSubmission | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    params.then(({ slug: value }) => setSlug(value));
  }, [params]);

  useEffect(() => {
    if (!slug) return;
    let active = true;
    Promise.all([competitionsApi.detail(slug), competitionsApi.leaderboard(slug)]).then(([competition, leaderboard]) => {
      if (!active) return;
      setDetail(competition);
      setResults(leaderboard);
      if (competition.registration_status) {
        competitionsApi.submission(slug).then(setSubmission).catch(() => undefined);
      }
    }).catch((requestError) => active && setError(requestError instanceof ApiError ? requestError.message : "Competition could not be loaded.")).finally(() => active && setLoading(false));
    return () => { active = false; };
  }, [slug]);

  async function saveSubmission(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    try {
      const saved = await competitionsApi.saveSubmission(slug, {
        project_title: String(form.get("project_title") || ""),
        description: String(form.get("description") || ""),
        github_url: String(form.get("github_url") || ""),
        demo_url: String(form.get("demo_url") || ""),
        submit: form.get("submit") === "true",
      });
      setSubmission(saved);
      setMessage(saved.status === "submitted" ? "Submission sent for review." : "Draft saved.");
    } catch (requestError) {
      setError(requestError instanceof ApiError ? requestError.message : "Submission could not be saved.");
    }
  }

  if (loading) return <main className="min-h-full bg-background p-10 text-center text-sm text-muted-foreground">Loading competition…</main>;
  if (error && !detail) return <main className="min-h-full bg-background p-10 text-center text-sm text-red-600">{error}</main>;
  if (!detail) return null;

  const canRegister = isAuthenticated && !detail.registration_status && ["registration_open", "registration_closing_soon"].includes(detail.status);
  const joinHref = `/sign-in?next=${encodeURIComponent(`/competitions/${slug}`)}`;

  return (
    <main className="min-h-full bg-background text-foreground">
      <div className="mx-auto max-w-5xl px-4 py-8 sm:px-6 lg:px-8">
        <Link href="/competitions" className="inline-flex items-center gap-2 text-sm font-semibold text-muted-foreground hover:text-foreground"><ArrowLeft className="h-4 w-4" /> All competitions</Link>
        <header className="mt-8 border-b border-border pb-8">
          <p className="text-xs font-bold uppercase tracking-[0.16em] text-emerald-600 dark:text-emerald-400">{detail.category} · {detail.difficulty}</p>
          <div className="mt-3 flex flex-col justify-between gap-6 md:flex-row md:items-end">
            <div><h1 className="text-4xl font-semibold tracking-tight">{detail.title}</h1><p className="mt-3 max-w-2xl text-muted-foreground">{detail.short_description}</p></div>
            <div className="shrink-0">
              {canRegister && <Link href={`/hackathons/${slug}/register`} className="inline-block rounded-lg bg-emerald-600 px-5 py-3 text-sm font-semibold text-white hover:bg-emerald-500">Register now</Link>}
              {!isAuthenticated && <Link href={joinHref} className="inline-block rounded-lg bg-emerald-600 px-5 py-3 text-sm font-semibold text-white hover:bg-emerald-500">Sign in to register</Link>}
              {detail.registration_status && <span className="rounded-lg bg-emerald-500/10 px-4 py-3 text-sm font-semibold text-emerald-700 dark:text-emerald-300">You’re registered</span>}
            </div>
          </div>
          {message && <p role="status" className="mt-4 text-sm text-emerald-600">{message}</p>}
          {error && <p role="alert" className="mt-4 text-sm text-red-600">{error}</p>}
        </header>

        <div className="mt-8 grid gap-8 lg:grid-cols-[1fr_280px]">
          <div className="space-y-8">
            <section><h2 className="text-xl font-semibold">Overview</h2><p className="mt-3 whitespace-pre-line text-sm leading-7 text-muted-foreground">{detail.description}</p></section>
            {detail.problem_statement && <section><h2 className="text-xl font-semibold">Problem statement</h2><p className="mt-3 whitespace-pre-line text-sm leading-7 text-muted-foreground">{detail.problem_statement}</p></section>}
            {detail.eligibility_rules.length > 0 && <section><h2 className="text-xl font-semibold">Eligibility</h2><ul className="mt-3 list-disc space-y-2 pl-5 text-sm text-muted-foreground">{detail.eligibility_rules.map((rule) => <li key={rule}>{rule}</li>)}</ul></section>}
            {detail.competition_rules.length > 0 && <section><h2 className="text-xl font-semibold">Rules</h2><ul className="mt-3 list-disc space-y-2 pl-5 text-sm text-muted-foreground">{detail.competition_rules.map((rule) => <li key={rule}>{rule}</li>)}</ul></section>}

            {detail.registration_status && <section className="rounded-xl border border-border p-5"><h2 className="text-xl font-semibold">Your submission</h2><form onSubmit={saveSubmission} className="mt-4 space-y-4"><input name="project_title" defaultValue={submission?.project_title} required placeholder="Project title" className="h-10 w-full rounded-lg border border-border bg-background px-3 text-sm" /><textarea name="description" defaultValue={submission?.description} required placeholder="Describe what you built" rows={5} className="w-full rounded-lg border border-border bg-background p-3 text-sm" /><input name="github_url" defaultValue={submission?.github_url} type="url" placeholder="GitHub repository URL" className="h-10 w-full rounded-lg border border-border bg-background px-3 text-sm" /><input name="demo_url" defaultValue={submission?.demo_url} type="url" placeholder="Live demo URL" className="h-10 w-full rounded-lg border border-border bg-background px-3 text-sm" /><div className="flex gap-3"><button name="submit" value="false" className="rounded-lg border border-border px-4 py-2 text-sm font-semibold">Save draft</button><button name="submit" value="true" className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white">Submit work</button></div></form></section>}
          </div>

          <aside className="space-y-4">
            <section className="rounded-xl border border-border p-5"><h2 className="font-semibold">Timeline</h2><dl className="mt-4 space-y-4 text-sm"><div><dt className="text-muted-foreground">Registration closes</dt><dd className="mt-1 font-medium">{dateLabel(detail.registration_deadline)}</dd></div><div><dt className="text-muted-foreground">Competition starts</dt><dd className="mt-1 font-medium">{dateLabel(detail.competition_start)}</dd></div><div><dt className="text-muted-foreground">Submit by</dt><dd className="mt-1 font-medium">{dateLabel(detail.submission_deadline)}</dd></div><div><dt className="text-muted-foreground">Results</dt><dd className="mt-1 font-medium">{dateLabel(detail.results_announcement)}</dd></div></dl></section>
            <section className="rounded-xl border border-border p-5 text-sm text-muted-foreground"><p className="inline-flex items-center gap-2"><Users className="h-4 w-4" /> {detail.participant_count}{detail.participant_limit ? ` / ${detail.participant_limit}` : ""} participants</p><p className="mt-3 inline-flex items-center gap-2"><CalendarDays className="h-4 w-4" /> {detail.format} · {detail.delivery_mode}</p>{detail.prize_information && <p className="mt-3 inline-flex items-center gap-2"><Trophy className="h-4 w-4" /> {detail.prize_information}</p>}</section>
          </aside>
        </div>

        {results.length > 0 && <section className="mt-12 border-t border-border pt-8"><h2 className="text-xl font-semibold">Published results</h2><div className="mt-4 overflow-x-auto rounded-xl border border-border"><table className="w-full text-left text-sm"><thead className="bg-muted/40 text-muted-foreground"><tr><th className="px-4 py-3">Rank</th><th className="px-4 py-3">Participant</th><th className="px-4 py-3">Project</th><th className="px-4 py-3">Score</th></tr></thead><tbody>{results.map((result) => <tr key={`${result.rank}-${result.participant_name}`} className="border-t border-border"><td className="px-4 py-3 font-semibold">{result.rank}</td><td className="px-4 py-3">{result.participant_name}</td><td className="px-4 py-3 text-muted-foreground">{result.project_title || "—"}</td><td className="px-4 py-3">{result.final_score}</td></tr>)}</tbody></table></div></section>}
      </div>
    </main>
  );
}
