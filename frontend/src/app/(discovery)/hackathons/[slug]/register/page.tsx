"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowLeft, ArrowRight, CalendarClock, CheckCircle2 } from "lucide-react";
import { ApiError, competitions as competitionsApi } from "@/lib/api";
import type { RegistrationFormFieldPublic } from "@/lib/api";
import type { CompetitionDetail } from "@/types";
import { useAuth } from "@/hooks/use-auth";

const inputClass =
  "mt-1 w-full rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none ring-emerald-500 focus:ring-2";

const OPEN_STATUSES = ["registration_open", "registration_closing_soon"];

function dateLabel(value: string | null) {
  return value
    ? new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" }).format(new Date(value))
    : "To be announced";
}

export default function HackathonRegisterPage({ params }: { params: Promise<{ slug: string }> }) {
  const { user, loading: authLoading } = useAuth();
  const [slug, setSlug] = useState("");
  const [competition, setCompetition] = useState<CompetitionDetail | null>(null);
  const [fields, setFields] = useState<RegistrationFormFieldPublic[]>([]);
  const [answers, setAnswers] = useState<Record<string, string | string[]>>({});
  const [teamName, setTeamName] = useState("");
  const [rulesAccepted, setRulesAccepted] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [pageError, setPageError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [reference, setReference] = useState<string | null>(null);

  useEffect(() => {
    params.then(({ slug: value }) => setSlug(value));
  }, [params]);

  useEffect(() => {
    if (!slug) return;
    let active = true;
    Promise.all([competitionsApi.detail(slug), competitionsApi.registrationForm(slug)])
      .then(([competitionData, formFields]) => {
        if (!active) return;
        setCompetition(competitionData);
        setFields(formFields);
      })
      .catch((requestError) => {
        if (active) {
          setPageError(
            requestError instanceof ApiError && requestError.status === 404
              ? "This hackathon doesn’t exist or is no longer published."
              : requestError instanceof ApiError
                ? requestError.message
                : "The registration form could not be loaded.",
          );
        }
      });
    return () => { active = false; };
  }, [slug]);

  function setAnswer(key: string, value: string | string[]) {
    setAnswers((prev) => ({ ...prev, [key]: value }));
    setFieldErrors((prev) => {
      if (!prev[key]) return prev;
      const next = { ...prev };
      delete next[key];
      return next;
    });
  }

  function toggleCheckboxValue(key: string, option: string) {
    setAnswers((prev) => {
      const current = Array.isArray(prev[key]) ? (prev[key] as string[]) : [];
      const next = current.includes(option)
        ? current.filter((value) => value !== option)
        : [...current, option];
      return { ...prev, [key]: next };
    });
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!competition) return;
    setSubmitting(true);
    setPageError(null);
    const errors: Record<string, string> = {};
    for (const field of fields) {
      if (!field.required) continue;
      const value = answers[field.field_key];
      const empty =
        value === undefined ||
        value === "" ||
        (Array.isArray(value) && value.length === 0);
      if (empty) errors[field.field_key] = "This question is required.";
    }
    if (Object.keys(errors).length) {
      setFieldErrors(errors);
      setSubmitting(false);
      return;
    }
    try {
      const registration = await competitionsApi.register(slug, {
        rules_accepted: competition.competition_rules.length === 0 || rulesAccepted,
        registration_data: answers,
        ...(teamName.trim() ? { team_name: teamName.trim() } : {}),
      });
      setReference(registration.reference || "");
    } catch (requestError) {
      if (requestError instanceof ApiError) {
        const mapped: Record<string, string> = {};
        Object.entries(requestError.fieldErrors || {}).forEach(([key, messages]) => {
          if (key !== "detail" && key !== "non_field_errors") mapped[key] = messages[0];
        });
        setFieldErrors(mapped);
        setPageError(requestError.message);
      } else {
        setPageError("Registration could not be submitted. Check your connection and try again.");
      }
    } finally {
      setSubmitting(false);
    }
  }

  if (!authLoading && !user) {
    return (
      <main className="min-h-full bg-background text-foreground">
        <div className="mx-auto max-w-xl px-4 py-16 text-center sm:px-6">
          <h1 className="text-2xl font-semibold">Sign in to register</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Hackathon registrations are tied to your Code Yaar account so your
            application and submission stay with you.
          </p>
          <Link
            href={`/sign-in?next=${encodeURIComponent(`/hackathons/${slug}/register`)}`}
            className="mt-6 inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-5 py-3 text-sm font-semibold text-white hover:bg-emerald-500"
          >
            Sign in <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </main>
    );
  }

  if (pageError && !competition) {
    return (
      <main className="min-h-full bg-background text-foreground">
        <div className="mx-auto max-w-xl px-4 py-16 text-center sm:px-6">
          <p role="alert" className="text-sm text-red-600">{pageError}</p>
          <Link href="/competitions" className="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-emerald-600 hover:text-emerald-500">
            <ArrowLeft className="h-4 w-4" /> Back to hackathons
          </Link>
        </div>
      </main>
    );
  }

  if (!competition) {
    return <main className="min-h-full bg-background p-10 text-center text-sm text-muted-foreground">Loading registration form…</main>;
  }

  if (reference !== null) {
    return (
      <main className="min-h-full bg-background text-foreground">
        <div className="mx-auto max-w-xl px-4 py-16 text-center sm:px-6">
          <CheckCircle2 className="mx-auto h-12 w-12 text-emerald-600" />
          <h1 className="mt-4 text-2xl font-semibold">You’re registered!</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Your registration reference is <span className="font-bold text-foreground">{reference || "—"}</span>.
            Keep it handy — organizers use it to identify your application. A
            confirmation email is on its way if the server’s mail settings allow it.
          </p>
          <div className="mt-6 flex justify-center gap-3">
            <Link href={`/competitions/${slug}`} className="rounded-lg border border-border px-4 py-2 text-sm font-semibold hover:bg-muted">
              View hackathon
            </Link>
            <Link href="/dashboard" className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-500">
              Go to dashboard
            </Link>
          </div>
        </div>
      </main>
    );
  }

  const alreadyRegistered = Boolean(competition.registration_status);
  const registrationOpen = OPEN_STATUSES.includes(competition.status);
  const teamAllowed = competition.format === "team" || competition.format === "both";

  return (
    <main className="min-h-full bg-background text-foreground">
      <div className="mx-auto max-w-2xl px-4 py-10 sm:px-6 lg:px-8">
        <Link href={`/competitions/${slug}`} className="inline-flex items-center gap-2 text-sm font-semibold text-muted-foreground hover:text-foreground">
          <ArrowLeft className="h-4 w-4" /> About this hackathon
        </Link>
        <header className="mt-6 border-b border-border pb-6">
          <p className="text-xs font-bold uppercase tracking-[0.16em] text-emerald-600 dark:text-emerald-400">Registration</p>
          <h1 className="mt-2 text-3xl font-semibold tracking-tight">{competition.title}</h1>
          <p className="mt-2 inline-flex items-center gap-2 text-sm text-muted-foreground">
            <CalendarClock className="h-4 w-4" />
            Registration closes {dateLabel(competition.registration_deadline)}
          </p>
        </header>

        {alreadyRegistered ? (
          <section className="mt-8 rounded-xl border border-emerald-200 bg-emerald-50 p-6 text-center dark:border-emerald-900 dark:bg-emerald-950/30">
            <CheckCircle2 className="mx-auto h-8 w-8 text-emerald-600" />
            <h2 className="mt-2 font-semibold text-emerald-800 dark:text-emerald-200">
              You already have a registration for this event.
            </h2>
            <p className="mt-1 text-sm text-emerald-700 dark:text-emerald-300">
              Status: <span className="font-bold capitalize">{competition.registration_status}</span>. Manage your
              submission from the hackathon page.
            </p>
          </section>
        ) : !registrationOpen ? (
          <section className="mt-8 rounded-xl border border-amber-200 bg-amber-50 p-6 text-center dark:border-amber-900 dark:bg-amber-950/30">
            <h2 className="font-semibold text-amber-800 dark:text-amber-200">Registration isn’t open right now.</h2>
            <p className="mt-1 text-sm text-amber-700 dark:text-amber-300">
              Status: <span className="font-bold capitalize">{competition.status.replaceAll("_", " ")}</span>. Check the
              timeline on the hackathon page and come back when registration opens.
            </p>
          </section>
        ) : (
          <form onSubmit={handleSubmit} className="mt-8 space-y-6">
            {pageError && (
              <p role="alert" className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700 dark:border-red-900 dark:bg-red-950/30 dark:text-red-300">
                {pageError}
              </p>
            )}

            {competition.eligibility_rules.length > 0 && (
              <section className="rounded-xl border border-border p-4 text-sm text-muted-foreground">
                <h2 className="font-semibold text-foreground">Eligibility</h2>
                <ul className="mt-2 list-disc space-y-1 pl-5">
                  {competition.eligibility_rules.map((rule) => <li key={rule}>{rule}</li>)}
                </ul>
              </section>
            )}

            {fields.map((field) => {
              const error = fieldErrors[field.field_key];
              return (
                <div key={field.id}>
                  <label className="block text-sm font-semibold text-foreground">
                    {field.label}
                    {field.required ? <span className="ml-1 text-red-500">*</span> : <span className="ml-1 text-xs font-normal text-muted-foreground">(optional)</span>}
                    {field.description && (
                      <span className="mt-1 block text-xs font-normal text-muted-foreground">{field.description}</span>
                    )}
                    {field.field_type === "short_text" && (
                      <input
                        type="text"
                        value={(answers[field.field_key] as string) ?? ""}
                        maxLength={field.validation.max_length}
                        minLength={field.validation.min_length}
                        placeholder={field.placeholder}
                        onChange={(e) => setAnswer(field.field_key, e.target.value)}
                        className={inputClass}
                      />
                    )}
                    {field.field_type === "long_text" && (
                      <textarea
                        rows={4}
                        value={(answers[field.field_key] as string) ?? ""}
                        maxLength={field.validation.max_length}
                        minLength={field.validation.min_length}
                        placeholder={field.placeholder}
                        onChange={(e) => setAnswer(field.field_key, e.target.value)}
                        className={inputClass}
                      />
                    )}
                    {(field.field_type === "email" || field.field_type === "url" || field.field_type === "date") && (
                      <input
                        type={field.field_type === "url" ? "url" : field.field_type}
                        value={(answers[field.field_key] as string) ?? ""}
                        placeholder={field.placeholder}
                        onChange={(e) => setAnswer(field.field_key, e.target.value)}
                        className={inputClass}
                      />
                    )}
                    {field.field_type === "phone" && (
                      <input
                        type="tel"
                        value={(answers[field.field_key] as string) ?? ""}
                        placeholder={field.placeholder || "+92 300 1234567"}
                        onChange={(e) => setAnswer(field.field_key, e.target.value)}
                        className={inputClass}
                      />
                    )}
                    {field.field_type === "number" && (
                      <input
                        type="number"
                        value={(answers[field.field_key] as string) ?? ""}
                        min={field.validation.min}
                        max={field.validation.max}
                        placeholder={field.placeholder}
                        onChange={(e) => setAnswer(field.field_key, e.target.value)}
                        className={inputClass}
                      />
                    )}
                    {field.field_type === "dropdown" && (
                      <select
                        value={(answers[field.field_key] as string) ?? ""}
                        onChange={(e) => setAnswer(field.field_key, e.target.value)}
                        className={inputClass}
                      >
                        <option value="">{field.placeholder || "Choose one…"}</option>
                        {field.options.map((option) => (
                          <option key={String(option)} value={String(option)}>{String(option)}</option>
                        ))}
                      </select>
                    )}
                    {field.field_type === "multiple_choice" && (
                      <div className="mt-2 space-y-2">
                        {field.options.map((option) => (
                          <label key={String(option)} className="flex items-center gap-2 text-sm">
                            <input
                              type="radio"
                              name={field.field_key}
                              value={String(option)}
                              checked={answers[field.field_key] === String(option)}
                              onChange={() => setAnswer(field.field_key, String(option))}
                            />
                            {String(option)}
                          </label>
                        ))}
                      </div>
                    )}
                    {field.field_type === "checkboxes" && (
                      <div className="mt-2 space-y-2">
                        {field.options.map((option) => (
                          <label key={String(option)} className="flex items-center gap-2 text-sm">
                            <input
                              type="checkbox"
                              checked={((answers[field.field_key] as string[]) ?? []).includes(String(option))}
                              onChange={() => toggleCheckboxValue(field.field_key, String(option))}
                            />
                            {String(option)}
                          </label>
                        ))}
                      </div>
                    )}
                  </label>
                  {error && <p role="alert" className="mt-1 text-xs font-medium text-red-600">{error}</p>}
                </div>
              );
            })}

            {teamAllowed && (
              <div>
                <label className="block text-sm font-semibold text-foreground">
                  Team name
                  {competition.format === "team" && <span className="ml-1 text-red-500">*</span>}
                  <span className="mt-1 block text-xs font-normal text-muted-foreground">
                    You’ll lead this team. Members can be invited after registering.
                  </span>
                  <input
                    type="text"
                    value={teamName}
                    onChange={(e) => setTeamName(e.target.value)}
                    placeholder="e.g. Binary Builders"
                    className={inputClass}
                  />
                </label>
                {fieldErrors.team_name && (
                  <p role="alert" className="mt-1 text-xs font-medium text-red-600">{fieldErrors.team_name}</p>
                )}
              </div>
            )}

            {competition.competition_rules.length > 0 && (
              <section className="rounded-xl border border-border p-4">
                <h2 className="text-sm font-semibold text-foreground">Rules</h2>
                <ul className="mt-2 max-h-40 space-y-1 overflow-y-auto pl-5 text-xs text-muted-foreground">
                  {competition.competition_rules.map((rule) => <li key={rule}>• {rule}</li>)}
                </ul>
                <label className="mt-3 flex items-start gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={rulesAccepted}
                    onChange={(e) => setRulesAccepted(e.target.checked)}
                    className="mt-1"
                  />
                  I have read and accept the hackathon rules.
                </label>
                {fieldErrors.rules_accepted && (
                  <p role="alert" className="mt-1 text-xs font-medium text-red-600">{fieldErrors.rules_accepted}</p>
                )}
              </section>
            )}

            <button
              type="submit"
              disabled={submitting}
              className="w-full rounded-lg bg-emerald-600 px-5 py-3 text-sm font-semibold text-white hover:bg-emerald-500 disabled:opacity-60"
            >
              {submitting ? "Submitting…" : "Submit registration"}
            </button>
            <p className="text-center text-xs text-muted-foreground">
              Answers are validated on the server before your spot is saved. You
              can’t register twice for the same event.
            </p>
          </form>
        )}
      </div>
    </main>
  );
}
