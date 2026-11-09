"use client";

import { useCallback, Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { adminApi, downloadRegistrationsCsv } from "@/lib/admin-api";
import type {
  CompetitionAdmin,
  CompetitionRegistrationAdmin,
  RegistrationStatsAdmin,
} from "@/lib/admin-api";
import { NetworkError } from "@/components/learning/workspace/error-states";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { ChevronDown, ChevronRight, Download, Search } from "lucide-react";

const STATUS_LABELS: Record<string, string> = {
  registered: "Pending",
  approved: "Approved",
  rejected: "Rejected",
  waitlisted: "Waitlisted",
  withdrawn: "Withdrawn",
  disqualified: "Disqualified",
};

const STATUS_BADGE: Record<string, "default" | "secondary" | "outline" | "destructive"> = {
  registered: "outline",
  approved: "default",
  rejected: "destructive",
  waitlisted: "secondary",
  withdrawn: "secondary",
  disqualified: "destructive",
};

function ApplicationsContent() {
  const searchParams = useSearchParams();
  const [competitions, setCompetitions] = useState<CompetitionAdmin[]>([]);
  const [registrations, setRegistrations] = useState<CompetitionRegistrationAdmin[]>([]);
  const [stats, setStats] = useState<RegistrationStatsAdmin | null>(null);
  const [competition, setCompetition] = useState(searchParams.get("competition") || "");
  const [status, setStatus] = useState("");
  const [searchInput, setSearchInput] = useState("");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(false);
  const [expanded, setExpanded] = useState<number | null>(null);
  const [busyId, setBusyId] = useState<number | null>(null);
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");
  const [exporting, setExporting] = useState(false);

  const load = useCallback(async () => {
    try {
      const [list, statsData] = await Promise.all([
        adminApi.listRegistrations({
          competition: competition ? Number(competition) : undefined,
          status: status || undefined,
          search: search || undefined,
          page_size: 100,
        }),
        adminApi.registrationStats(competition ? { competition: Number(competition) } : undefined),
      ]);
      setRegistrations(list.results);
      setStats(statsData);
      setLoadError(false);
    } catch {
      setLoadError(true);
    } finally {
      setLoading(false);
    }
  }, [competition, status, search]);

  useEffect(() => {
    (async () => {
      try {
        const data = await adminApi.listCompetitions({ page_size: 100 });
        setCompetitions(data.results);
      } catch {
        // The selector just stays empty; the list itself still loads.
      }
      await load();
    })();
  }, [load]);

  async function decide(registration: CompetitionRegistrationAdmin, nextStatus: string) {
    const labels: Record<string, string> = {
      approved: "Approve",
      rejected: "Reject",
      waitlisted: "Waitlist",
    };
    const confirmMessage =
      `${labels[nextStatus]} "${registration.participant_name}" for "${registration.competition_title}"? ` +
      `The participant will be notified by email about this decision.`;
    if (!confirm(confirmMessage)) return;
    setBusyId(registration.id);
    setError("");
    setNotice("");
    try {
      await adminApi.updateRegistrationStatus(registration.id, nextStatus);
      setNotice(`${registration.participant_name} marked ${STATUS_LABELS[nextStatus].toLowerCase()}. Confirmation email queued.`);
      await load();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "The decision did not save.");
    } finally {
      setBusyId(null);
    }
  }

  async function exportCsv() {
    setExporting(true);
    setError("");
    try {
      await downloadRegistrationsCsv({
        competition: competition ? Number(competition) : undefined,
        status: status || undefined,
        search: search || undefined,
      });
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "The CSV export could not be generated.");
    } finally {
      setExporting(false);
    }
  }

  if (loadError) return <NetworkError onRetry={load} />;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold">Hackathon Applications</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Review registration answers, decide applications, and export the list.
            Every decision sends the matching confirmation email.
          </p>
        </div>
        <Button variant="outline" size="sm" disabled={exporting || loading} onClick={exportCsv}>
          <Download className="mr-1 h-4 w-4" /> {exporting ? "Exporting..." : "Export CSV"}
        </Button>
      </div>

      {stats && (
        <div className="grid gap-3 sm:grid-cols-3 lg:grid-cols-6">
          {["total", "registered", "approved", "rejected", "waitlisted", "withdrawn"].map((key) => (
            <Card key={key}>
              <CardContent className="py-3">
                <p className="text-xs uppercase tracking-wide text-muted-foreground">
                  {key === "total" ? "Total" : STATUS_LABELS[key] || key}
                </p>
                <p className="text-xl font-bold">
                  {key === "total" ? stats.total : stats.by_status[key] ?? 0}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Filters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap items-center gap-3">
            <select
              value={competition}
              onChange={(e) => setCompetition(e.target.value)}
              className="rounded-md border bg-background px-3 py-2 text-sm"
            >
              <option value="">All hackathons</option>
              {competitions.map((c) => (
                <option key={c.id} value={c.id}>{c.title}</option>
              ))}
            </select>
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              className="rounded-md border bg-background px-3 py-2 text-sm"
            >
              <option value="">All statuses</option>
              {Object.entries(STATUS_LABELS).map(([value, label]) => (
                <option key={value} value={value}>{label}</option>
              ))}
            </select>
            <form
              className="flex items-center gap-2"
              onSubmit={(e) => {
                e.preventDefault();
                setSearch(searchInput.trim());
              }}
            >
              <div className="relative">
                <Search className="absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <input
                  value={searchInput}
                  onChange={(e) => setSearchInput(e.target.value)}
                  placeholder="Name, email, reference…"
                  className="rounded-md border bg-background py-2 pl-8 pr-3 text-sm"
                />
              </div>
              <Button type="submit" size="sm" variant="outline">Search</Button>
            </form>
          </div>
        </CardContent>
      </Card>

      {notice && (
        <p className="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-2 text-sm text-emerald-800 dark:border-emerald-800 dark:bg-emerald-950 dark:text-emerald-200">
          {notice}
        </p>
      )}
      {error && (
        <p role="alert" className="rounded-md border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700 dark:border-red-800 dark:bg-red-950 dark:text-red-200">
          {error}
        </p>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Applications ({registrations.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="animate-pulse space-y-3">
              {[0, 1, 2].map((i) => <Skeleton key={i} className="h-16" />)}
            </div>
          ) : registrations.length === 0 ? (
            <p className="text-sm text-muted-foreground">No applications match these filters yet.</p>
          ) : (
            <div className="space-y-3">
              {registrations.map((registration) => {
                const isOpen = expanded === registration.id;
                const busy = busyId === registration.id;
                return (
                  <div key={registration.id} className="rounded-lg border">
                    <button
                      type="button"
                      onClick={() => setExpanded(isOpen ? null : registration.id)}
                      className="flex w-full flex-wrap items-center justify-between gap-2 px-4 py-3 text-left"
                    >
                      <div className="flex flex-wrap items-center gap-2">
                        {isOpen ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                        <span className="font-medium">{registration.participant_name}</span>
                        <span className="text-sm text-muted-foreground">{registration.participant_email}</span>
                        <Badge variant={STATUS_BADGE[registration.registration_status] || "secondary"}>
                          {STATUS_LABELS[registration.registration_status] || registration.registration_status}
                        </Badge>
                      </div>
                      <div className="text-right text-xs text-muted-foreground">
                        <p>{registration.competition_title}</p>
                        <p>{registration.reference} · {new Date(registration.registered_at).toLocaleString()}</p>
                      </div>
                    </button>
                    {isOpen && (
                      <div className="border-t px-4 py-4">
                        <p className="mb-2 text-xs font-bold uppercase tracking-wider text-muted-foreground">
                          Registration answers
                        </p>
                        {Object.keys(registration.registration_data).length === 0 ? (
                          <p className="text-sm text-muted-foreground">No stored answers for this registration.</p>
                        ) : (
                          <dl className="space-y-2 text-sm">
                            {Object.entries(registration.registration_data).map(([key, value]) => (
                              <div key={key}>
                                <dt className="font-medium text-muted-foreground">{key.replace(/_/g, " ")}</dt>
                                <dd className="whitespace-pre-wrap">{Array.isArray(value) ? value.join(", ") : String(value)}</dd>
                              </div>
                            ))}
                          </dl>
                        )}
                        <div className="mt-4 flex flex-wrap gap-2">
                          {registration.registration_status !== "approved" && (
                            <Button size="sm" disabled={busy} onClick={() => decide(registration, "approved")}>
                              {busy ? "Working..." : "Approve"}
                            </Button>
                          )}
                          {registration.registration_status !== "waitlisted" && (
                            <Button size="sm" variant="outline" disabled={busy} onClick={() => decide(registration, "waitlisted")}>
                              Waitlist
                            </Button>
                          )}
                          {registration.registration_status !== "rejected" && (
                            <Button size="sm" variant="outline" disabled={busy} onClick={() => decide(registration, "rejected")}>
                              Reject
                            </Button>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

export default function ApplicationsPage() {
  return (
    <Suspense
      fallback={
        <div className="animate-pulse space-y-4">
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-24" />
        </div>
      }
    >
      <ApplicationsContent />
    </Suspense>
  );
}
