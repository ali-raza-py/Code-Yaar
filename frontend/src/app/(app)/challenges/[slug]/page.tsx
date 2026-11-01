"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  ArrowLeft, ChevronDown, Clock3, Lightbulb, Lock, Play,
  RotateCcw, Send, Sparkles, Trophy, CheckCircle2, AlertCircle,
} from "lucide-react";
import { challenges as challengesApi, ApiError } from "@/lib/api";
import type { ChallengeDetail, ChallengeRunResult, ChallengeSubmitResult } from "@/types";
import { useAuth } from "@/hooks/use-auth";
import CodeEditor from "@/components/learning/workspace/code-editor";
import { TestResults } from "@/components/challenges/test-results";

const DIFFICULTY_STYLES: Record<string, string> = {
  beginner: "bg-difficulty-easy-soft text-difficulty-easy",
  intermediate: "bg-difficulty-medium-soft text-difficulty-medium",
  advanced: "bg-difficulty-hard-soft text-difficulty-hard",
};

const LANG_LABELS: Record<string, string> = { python: "Python", cpp: "C++" };

function starterForLanguage(detail: ChallengeDetail, language: string): string {
  return (language === "cpp" ? detail.starter_code_cpp || detail.starter_code : detail.starter_code) ?? "";
}

function codeStorageKey(slug: string, language: string) {
  return `cy-challenge:${slug}:${language}`;
}

function readSavedCode(slug: string, language: string): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(codeStorageKey(slug, language));
}

/**
 * Guarantee the list/array fields the workspace renders are always present, so
 * a partial or stale API payload can never crash the page (e.g. a server that
 * predates the detail-serializer expansion returns no `requirements`).
 */
function normalizeDetail(data: ChallengeDetail): ChallengeDetail {
  return {
    ...data,
    languages: data.languages?.length ? data.languages : ["python"],
    requirements: data.requirements ?? [],
    constraints: data.constraints ?? [],
    examples: data.examples ?? [],
    hints: data.hints ?? [],
    sample_tests: data.sample_tests ?? [],
    attempts: data.attempts ?? 0,
    solved: Boolean(data.solved),
  };
}

export default function ChallengeWorkspacePage() {
  const params = useParams<{ slug: string }>();
  const slug = params?.slug ?? "";
  const { isAuthenticated, emailVerified, refresh } = useAuth();

  const [detail, setDetail] = useState<ChallengeDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<null | "network" | "notfound">(null);

  const [language, setLanguage] = useState("python");
  const [code, setCode] = useState("");
  const [running, setRunning] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [runResult, setRunResult] = useState<ChallengeRunResult | null>(null);
  const [submitResult, setSubmitResult] = useState<ChallengeSubmitResult | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [hintsRevealed, setHintsRevealed] = useState(0);
  const [showSolution, setShowSolution] = useState(false);
  const [solved, setSolved] = useState(false);
  // Set when the challenge loads (see `load`); 0 until then to keep render pure.
  const startedAt = useRef<number>(0);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = normalizeDetail(await challengesApi.detail(slug));
      setDetail(data);
      setSolved(Boolean(data.solved));
      const initialLang = data.languages[0] ?? "python";
      setLanguage(initialLang);
      // Restore any in-progress code, otherwise start from the scaffold.
      setCode(readSavedCode(slug, initialLang) ?? starterForLanguage(data, initialLang));
      startedAt.current = Date.now();
    } catch (caught) {
      if (caught instanceof ApiError && caught.status === 404) setError("notfound");
      else if (caught instanceof ApiError && caught.status === 0) setError("network");
      else setError("network");
    } finally {
      setLoading(false);
    }
  }, [slug]);

  useEffect(() => {
    (async () => { await load(); })();
  }, [load]);

  // Persist the working copy as it changes so refresh / back / forward keep it.
  useEffect(() => {
    if (!detail || typeof window === "undefined") return;
    window.localStorage.setItem(codeStorageKey(slug, language), code);
  }, [code, detail, language, slug]);

  const switchLanguage = (next: string) => {
    if (next === language || !detail) return;
    setLanguage(next);
    setCode(readSavedCode(slug, next) ?? starterForLanguage(detail, next));
    setRunResult(null);
    setSubmitResult(null);
    setActionError(null);
  };

  const resetCode = () => {
    if (!detail) return;
    const fresh = starterForLanguage(detail, language);
    setCode(fresh);
    window.localStorage.removeItem(codeStorageKey(slug, language));
    setRunResult(null);
    setSubmitResult(null);
    setActionError(null);
  };

  const handleRun = async () => {
    if (!isAuthenticated) { setActionError("Sign in to run your code against the sample tests."); return; }
    setRunning(true);
    setActionError(null);
    try {
      const result = await challengesApi.run(slug, { code, language });
      setRunResult(result);
    } catch (caught) {
      setActionError(caught instanceof ApiError ? caught.message : "The run could not be completed. Try again.");
    } finally {
      setRunning(false);
    }
  };

  const handleSubmit = async () => {
    if (!isAuthenticated) { setActionError("Sign in to submit your solution and earn XP."); return; }
    if (!emailVerified) { setActionError("Please verify your email before submitting solutions."); return; }
    setSubmitting(true);
    setActionError(null);
    try {
      const result = await challengesApi.submit(slug, {
        code,
        language,
        submission_id: typeof crypto !== "undefined" && crypto.randomUUID ? crypto.randomUUID() : undefined,
        time_spent_seconds: Math.max(0, Math.round((Date.now() - startedAt.current) / 1000)),
      });
      setSubmitResult(result);
      if (result.solved && !solved) {
        setSolved(true);
        await refresh(); // surface the newly awarded XP in the shell/dashboard
      }
    } catch (caught) {
      setActionError(caught instanceof ApiError ? caught.message : "Your submission could not be processed. Try again.");
    } finally {
      setSubmitting(false);
    }
  };

  const difficultyClass = detail ? DIFFICULTY_STYLES[detail.difficulty] : "";
  const sampleInputs = useMemo(() => detail?.examples ?? [], [detail]);

  return (
    <main className="min-h-full bg-[var(--challenge-bg)] text-[var(--challenge-text)]">
      <div className="mx-auto max-w-[1400px] px-4 py-6 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="flex flex-col gap-4 border-b border-[var(--challenge-border)] pb-5 lg:flex-row lg:items-center lg:justify-between">
          <div className="min-w-0">
            <Link href="/challenges" className="inline-flex items-center gap-1.5 text-sm font-semibold text-[var(--challenge-accent-strong)] hover:underline">
              <ArrowLeft aria-hidden="true" className="h-4 w-4" /> Back to Practice
            </Link>
            <h1 className="mt-2 truncate text-2xl font-semibold tracking-[-0.03em]">{detail?.title ?? "Challenge"}</h1>
            {detail && (
              <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1.5 text-xs">
                <span className={`rounded-pill px-2.5 py-1 font-bold capitalize ${difficultyClass}`}>{detail.difficulty}</span>
                <span className="rounded-md bg-[var(--challenge-surface-muted)] px-2 py-1 font-semibold text-[var(--challenge-text-soft)]">{detail.topic}</span>
                <span className="inline-flex items-center gap-1 text-[var(--challenge-muted)]"><Clock3 aria-hidden="true" className="h-3.5 w-3.5" />{detail.estimated_minutes} min</span>
                <span className="font-semibold text-success">+{detail.xp_reward} XP</span>
              </div>
            )}
          </div>
          <div className="shrink-0">
            {loading ? (
              <span className="text-xs text-[var(--challenge-muted)]">Loading…</span>
            ) : solved ? (
              <span className="inline-flex items-center gap-1.5 rounded-pill bg-success/12 px-3 py-1.5 text-sm font-bold text-success"><CheckCircle2 aria-hidden="true" className="h-4 w-4" /> Completed</span>
            ) : (
              <span className="inline-flex items-center gap-1.5 rounded-pill bg-[var(--challenge-surface-muted)] px-3 py-1.5 text-sm font-semibold text-[var(--challenge-muted)]"><Sparkles aria-hidden="true" className="h-4 w-4" /> Not yet solved</span>
            )}
          </div>
        </div>

        {/* Loading */}
        {loading && (
          <div className="mt-6 grid animate-pulse gap-4 lg:grid-cols-12">
            <div className="space-y-3 lg:col-span-5"><div className="h-6 w-2/3 rounded bg-[var(--challenge-surface-muted)]" /><div className="h-40 rounded-card bg-[var(--challenge-surface-muted)]" /><div className="h-24 rounded-card bg-[var(--challenge-surface-muted)]" /></div>
            <div className="h-[420px] rounded-card bg-[var(--challenge-surface-muted)] lg:col-span-7" />
          </div>
        )}

        {/* Not found */}
        {!loading && error === "notfound" && (
          <div className="mt-10 rounded-card border border-[var(--challenge-border)] bg-[var(--challenge-surface)] p-8 text-center shadow-[var(--challenge-shadow)]">
            <h2 className="text-xl font-bold">We couldn&apos;t find that challenge</h2>
            <p className="mt-2 text-sm text-[var(--challenge-muted)]">The challenge “{slug}” doesn&apos;t exist or is no longer available.</p>
            <Link href="/challenges" className="focus-ring mt-5 inline-flex items-center gap-2 rounded-md bg-[var(--challenge-accent)] px-4 py-2 text-sm font-bold text-white hover:opacity-90">
              <ArrowLeft aria-hidden="true" className="h-4 w-4" /> Browse all challenges
            </Link>
          </div>
        )}

        {/* Network error */}
        {!loading && error === "network" && (
          <div role="alert" className="mt-6 flex items-center justify-between gap-4 rounded-card border border-danger/30 bg-danger/10 px-4 py-3 text-sm text-danger">
            <span className="inline-flex items-center gap-2"><AlertCircle aria-hidden="true" className="h-4 w-4" /> Could not load this challenge. The API may be offline.</span>
            <button type="button" onClick={() => void load()} className="focus-ring rounded font-bold underline underline-offset-2">Try again</button>
          </div>
        )}

        {/* Workspace */}
        {!loading && !error && detail && (
          <div className="mt-6 grid gap-6 lg:grid-cols-12">
            {/* Problem statement */}
            <section aria-label="Problem" className="space-y-5 lg:col-span-5">
              <div className="rounded-card border border-[var(--challenge-border)] bg-[var(--challenge-surface)] p-5 shadow-[var(--challenge-shadow)]">
                <p className="whitespace-pre-line text-sm leading-7 text-[var(--challenge-text-soft)]">{detail.problem_statement || detail.description}</p>
              </div>

              {detail.requirements.length > 0 && (
                <div>
                  <h2 className="text-sm font-bold uppercase tracking-wide text-[var(--challenge-accent-strong)]">Requirements</h2>
                  <ul className="mt-2 space-y-1.5">
                    {detail.requirements.map((req, i) => (
                      <li key={i} className="flex gap-2 text-sm text-[var(--challenge-text-soft)]"><span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-[var(--challenge-accent)]" />{req}</li>
                    ))}
                  </ul>
                </div>
              )}

              {(detail.input_description || detail.output_description) && (
                <div className="grid gap-4 sm:grid-cols-2">
                  {detail.input_description && (<div className="rounded-card border border-[var(--challenge-border)] p-4"><h3 className="text-xs font-bold uppercase tracking-wide text-[var(--challenge-muted)]">Input</h3><p className="mt-1.5 whitespace-pre-line text-sm text-[var(--challenge-text-soft)]">{detail.input_description}</p></div>)}
                  {detail.output_description && (<div className="rounded-card border border-[var(--challenge-border)] p-4"><h3 className="text-xs font-bold uppercase tracking-wide text-[var(--challenge-muted)]">Output</h3><p className="mt-1.5 whitespace-pre-line text-sm text-[var(--challenge-text-soft)]">{detail.output_description}</p></div>)}
                </div>
              )}

              {sampleInputs.length > 0 && (
                <div className="space-y-2">
                  <h2 className="text-sm font-bold uppercase tracking-wide text-[var(--challenge-accent-strong)]">Examples</h2>
                  {sampleInputs.map((ex, i) => (
                    <details key={i} open={i === 0} className="group rounded-card border border-[var(--challenge-border)] bg-[var(--challenge-surface)]">
                      <summary className="flex cursor-pointer list-none items-center justify-between px-4 py-3 text-sm font-semibold">
                        Example {i + 1}
                        <ChevronDown aria-hidden="true" className="h-4 w-4 text-[var(--challenge-muted)] transition-transform group-open:rotate-180" />
                      </summary>
                      <div className="space-y-3 border-t border-[var(--challenge-border)] px-4 py-3">
                        {ex.explanation && <p className="text-sm text-[var(--challenge-muted)]">{ex.explanation}</p>}
                        <div><p className="text-[11px] font-bold uppercase tracking-wide text-[var(--challenge-muted)]">Input</p><pre className="mt-1 overflow-auto rounded bg-[var(--editor-bg)] p-2.5 font-mono text-xs text-[var(--editor-text)]">{ex.input || "(empty)"}</pre></div>
                        <div><p className="text-[11px] font-bold uppercase tracking-wide text-[var(--challenge-muted)]">Output</p><pre className="mt-1 overflow-auto rounded bg-[var(--editor-bg)] p-2.5 font-mono text-xs text-[var(--syn-string)]">{ex.output || "(empty)"}</pre></div>
                      </div>
                    </details>
                  ))}
                </div>
              )}

              {detail.constraints.length > 0 && (
                <div><h2 className="text-sm font-bold uppercase tracking-wide text-[var(--challenge-accent-strong)]">Constraints</h2><ul className="mt-2 space-y-1">{detail.constraints.map((c, i) => (<li key={i} className="font-mono text-xs text-[var(--challenge-text-soft)]">• {c}</li>))}</ul></div>
              )}

              {detail.hints.length > 0 && (
                <div className="rounded-card border border-[var(--challenge-border)] bg-[var(--challenge-surface)] p-4">
                  <div className="flex items-center justify-between">
                    <h2 className="inline-flex items-center gap-1.5 text-sm font-bold text-[var(--challenge-accent-strong)]"><Lightbulb aria-hidden="true" className="h-4 w-4" /> Hints</h2>
                    <span className="text-[11px] text-[var(--challenge-muted)]">{hintsRevealed}/{detail.hints.length} revealed</span>
                  </div>
                  <ul className="mt-3 space-y-2">
                    {detail.hints.slice(0, hintsRevealed).map((hint, i) => (
                      <li key={i} className="rounded-md bg-[var(--challenge-surface-muted)] p-3 text-sm text-[var(--challenge-text-soft)]">{hint}</li>
                    ))}
                  </ul>
                  {hintsRevealed < detail.hints.length ? (
                    <button type="button" onClick={() => setHintsRevealed((n) => n + 1)} className="focus-ring mt-3 rounded-md border border-[var(--challenge-border)] px-3 py-1.5 text-xs font-bold text-[var(--challenge-accent-strong)] hover:bg-[var(--challenge-accent-soft)]">
                      {hintsRevealed === 0 ? "Show a hint" : "Reveal next hint"}
                    </button>
                  ) : (<p className="mt-3 text-xs text-[var(--challenge-muted)]">You&apos;ve reached the last hint.</p>)}
                </div>
              )}
            </section>

            {/* Code + results */}
            <section aria-label="Workspace" className="space-y-4 lg:col-span-7">
              <div className="flex flex-wrap items-center gap-2">
                <label htmlFor="challenge-language" className="text-xs font-semibold text-[var(--challenge-muted)]">Language</label>
                <select id="challenge-language" value={language} onChange={(e) => switchLanguage(e.target.value)} className="focus-ring rounded-md border border-[var(--challenge-border)] bg-[var(--challenge-surface)] px-2.5 py-1.5 text-sm font-semibold">
                  {(detail.languages?.length ? detail.languages : ["python"]).map((lang) => (<option key={lang} value={lang}>{LANG_LABELS[lang] ?? lang}</option>))}
                </select>
                {detail.attempts > 0 && <span className="ml-auto text-xs text-[var(--challenge-muted)]">{detail.attempts} previous attempt{detail.attempts === 1 ? "" : "s"}</span>}
              </div>

              {!isAuthenticated && (
                <div className="flex items-center gap-2 rounded-md border border-[var(--challenge-border)] bg-[var(--challenge-surface)] px-3 py-2 text-xs text-[var(--challenge-muted)]">
                  <Lock aria-hidden="true" className="h-3.5 w-3.5" />
                  You can read this challenge, but <Link href="/sign-in" className="font-bold text-[var(--challenge-accent-strong)] hover:underline">sign in</Link> to run code and earn XP.
                </div>
              )}

              <div className="overflow-hidden rounded-card border border-[var(--challenge-border)] shadow-[var(--challenge-shadow)]">
                <div className="h-[360px] sm:h-[440px]">
                  <CodeEditor code={code} onChange={setCode} language={language} fileName={language === "cpp" ? "solution.cpp" : "solution.py"} onRun={() => void handleRun()} onSubmit={() => void handleSubmit()} />
                </div>
              </div>

              <div className="flex flex-wrap items-center gap-2">
                <button type="button" onClick={() => void handleRun()} disabled={running || submitting} className="focus-ring inline-flex items-center gap-2 rounded-md border border-[var(--challenge-border)] bg-[var(--challenge-surface)] px-4 py-2 text-sm font-bold text-[var(--challenge-text)] hover:bg-[var(--challenge-surface-muted)] disabled:opacity-60">
                  <Play aria-hidden="true" className="h-4 w-4" /> {running ? "Running…" : "Run Code"}
                </button>
                <button type="button" onClick={() => void handleSubmit()} disabled={running || submitting} className="focus-ring inline-flex items-center gap-2 rounded-md bg-[var(--challenge-accent)] px-4 py-2 text-sm font-bold text-white hover:opacity-90 disabled:opacity-60">
                  <Send aria-hidden="true" className="h-4 w-4" /> {submitting ? "Submitting…" : "Submit Solution"}
                </button>
                <button type="button" onClick={resetCode} className="focus-ring inline-flex items-center gap-1.5 rounded-md px-3 py-2 text-sm font-semibold text-[var(--challenge-muted)] hover:text-[var(--challenge-text)]">
                  <RotateCcw aria-hidden="true" className="h-4 w-4" /> Reset
                </button>
              </div>

              {actionError && (
                <div role="alert" className="flex items-center gap-2 rounded-md border border-warning/30 bg-warning/10 px-3 py-2 text-sm text-tone-amber-fg">
                  <AlertCircle aria-hidden="true" className="h-4 w-4 shrink-0" />
                  <span>{actionError}</span>
                  {actionError.startsWith("Sign in") && <Link href="/sign-in" className="ml-auto shrink-0 font-bold underline underline-offset-2">Sign in</Link>}
                  {actionError.startsWith("Please verify") && <Link href="/verify-email" className="ml-auto shrink-0 font-bold underline underline-offset-2">Verify email</Link>}
                </div>
              )}

              {/* XP toast */}
              {submitResult && submitResult.xp_earned > 0 && (
                <div className="flex items-center gap-2 rounded-card border border-success/30 bg-success/12 px-4 py-3 text-sm font-bold text-success">
                  <Trophy aria-hidden="true" className="h-5 w-5" /> Challenge solved! +{submitResult.xp_earned} XP awarded
                </div>
              )}

              {/* Feedback banner */}
              {submitResult && (
                <div className={`rounded-card border p-4 ${submitResult.solved ? "border-success/30 bg-success/10" : "border-[var(--challenge-border)] bg-[var(--challenge-surface)]"}`}>
                  <p className={`text-sm font-bold ${submitResult.solved ? "text-success" : "text-[var(--challenge-text)]"}`}>{submitResult.solved ? "All tests passed" : "Not solved yet"}</p>
                  <p className="mt-1 text-sm text-[var(--challenge-text-soft)]">{submitResult.feedback}</p>
                  <div className="mt-3"><TestResults results={submitResult.test_results} /></div>
                  {submitResult.solved && (submitResult.solution_explanation || submitResult.reference_solution) && (
                    <div className="mt-4 border-t border-[var(--challenge-border)] pt-4">
                      <button type="button" onClick={() => setShowSolution((v) => !v)} className="focus-ring inline-flex items-center gap-1.5 text-sm font-bold text-[var(--challenge-accent-strong)]">
                        <ChevronDown aria-hidden="true" className={`h-4 w-4 transition-transform ${showSolution ? "rotate-180" : ""}`} /> {showSolution ? "Hide" : "View"} model solution
                      </button>
                      {showSolution && (
                        <div className="mt-3 space-y-3">
                          {submitResult.solution_explanation && <p className="whitespace-pre-line text-sm leading-7 text-[var(--challenge-text-soft)]">{submitResult.solution_explanation}</p>}
                          <div className="flex flex-wrap gap-4 text-xs">
                            {submitResult.time_complexity && <p className="text-[var(--challenge-muted)]"><span className="font-bold text-[var(--challenge-text)]">Time:</span> {submitResult.time_complexity}</p>}
                            {submitResult.space_complexity && <p className="text-[var(--challenge-muted)]"><span className="font-bold text-[var(--challenge-text)]">Space:</span> {submitResult.space_complexity}</p>}
                          </div>
                          {submitResult.reference_solution && (
                            <div><p className="text-[11px] font-bold uppercase tracking-wide text-[var(--challenge-muted)]">Reference ({LANG_LABELS[language] ?? language})</p><pre className="mt-1 overflow-auto rounded bg-[var(--editor-bg)] p-3 font-mono text-xs text-[var(--editor-text)]">{submitResult.reference_solution}</pre></div>
                          )}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}

              {/* Run results (sample tests) */}
              {runResult && !submitResult && (
                <div className="rounded-card border border-[var(--challenge-border)] bg-[var(--challenge-surface)] p-4">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-bold">Sample test results</p>
                    {runResult.summary && <p className="text-xs text-[var(--challenge-muted)]">{runResult.summary}</p>}
                  </div>
                  <div className="mt-3"><TestResults results={runResult.test_results} /></div>
                </div>
              )}
            </section>
          </div>
        )}
      </div>
    </main>
  );
}
