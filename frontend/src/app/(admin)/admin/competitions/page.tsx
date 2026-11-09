"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { Plus, Edit, Trash2, Eye, EyeOff, Archive, ClipboardList } from "lucide-react";
import { adminApi } from "@/lib/admin-api";
import type { CompetitionAdmin } from "@/lib/admin-api";
import { useAuth } from "@/hooks/use-auth";
import { NetworkError } from "@/components/learning/workspace/error-states";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

export default function AdminHackathonsPage() {
  const { user, loading: authLoading } = useAuth();
  const [competitions, setCompetitions] = useState<CompetitionAdmin[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [busy, setBusy] = useState<string | null>(null);
  const [notice, setNotice] = useState("");
  const [actionError, setActionError] = useState("");

  const load = useCallback(async () => {
    if (!user) return;
    try {
      const data = await adminApi.listCompetitions({ page_size: 100 });
      setCompetitions(data.results);
      setError(false);
    } catch {
      setError(true);
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    (async () => { await load(); })();
  }, [load]);

  async function runAction(
    key: string,
    confirmMessage: string | null,
    action: () => Promise<unknown>,
    successMessage: string,
  ) {
    if (confirmMessage && !confirm(confirmMessage)) return;
    setBusy(key);
    setNotice("");
    setActionError("");
    try {
      await action();
      setNotice(successMessage);
      await load();
    } catch (caught) {
      setActionError(
        caught instanceof Error ? caught.message : "That action did not complete. Try again.",
      );
    } finally {
      setBusy(null);
    }
  }

  if (authLoading || (loading && user)) {
    return (
      <div className="animate-pulse space-y-4">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-64" />
      </div>
    );
  }

  if (error) return <NetworkError onRetry={load} />;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">Hackathons</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Manage hackathons and competitions. Publishing is separate from
            emailing, and statuses always follow the event dates.
          </p>
        </div>
        <Link href="/admin/competitions/create">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Create Hackathon
          </Button>
        </Link>
      </div>

      {notice && (
        <p className="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-2 text-sm text-emerald-800 dark:border-emerald-800 dark:bg-emerald-950 dark:text-emerald-200">
          {notice}
        </p>
      )}
      {actionError && (
        <p role="alert" className="rounded-md border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700 dark:border-red-800 dark:bg-red-950 dark:text-red-200">
          {actionError}
        </p>
      )}

      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[var(--color-section-border)]">
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Title</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Category</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Registrations</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Status</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Published</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--color-section-border)]">
                {competitions.map((comp) => {
                  const rowKey = String(comp.id);
                  const rowBusy = busy === rowKey;
                  return (
                    <tr key={comp.id} className="hover:bg-[var(--color-section-light)]">
                      <td className="px-4 py-3 font-medium">{comp.title}</td>
                      <td className="px-4 py-3">{comp.category}</td>
                      <td className="px-4 py-3">{comp.participant_count}</td>
                      <td className="px-4 py-3">
                        <Badge variant={comp.is_archived ? "secondary" : "outline"}>
                          {comp.status.replace(/_/g, " ")}
                        </Badge>
                      </td>
                      <td className="px-4 py-3">
                        <Badge variant={comp.is_published ? "default" : "secondary"}>
                          {comp.is_published ? "Published" : "Draft"}
                        </Badge>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-1">
                          <Link href={`/admin/competitions/${comp.id}`} title="Edit">
                            <Button variant="ghost" size="sm" disabled={rowBusy}>
                              <Edit className="h-4 w-4" />
                            </Button>
                          </Link>
                          <Link href={`/admin/competitions/${comp.id}/form-builder`} title="Registration form builder">
                            <Button variant="ghost" size="sm" disabled={rowBusy}>
                              <ClipboardList className="h-4 w-4" />
                            </Button>
                          </Link>
                          {!comp.is_published && !comp.is_archived && (
                            <Button
                              variant="ghost"
                              size="sm"
                              disabled={rowBusy}
                              title="Publish"
                              onClick={() =>
                                runAction(
                                  rowKey,
                                  `Publish "${comp.title}"? It becomes visible to everyone — no email is sent.`,
                                  () => adminApi.publishCompetition(comp.id),
                                  "Hackathon published.",
                                )
                              }
                            >
                              {rowBusy ? <Skeleton className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                            </Button>
                          )}
                          {comp.is_published && (
                            <Button
                              variant="ghost"
                              size="sm"
                              disabled={rowBusy}
                              title="Unpublish"
                              onClick={() =>
                                runAction(
                                  rowKey,
                                  `Unpublish "${comp.title}"?`,
                                  () => adminApi.unpublishCompetition(comp.id),
                                  "Hackathon unpublished.",
                                )
                              }
                            >
                              {rowBusy ? <Skeleton className="h-4 w-4" /> : <EyeOff className="h-4 w-4" />}
                            </Button>
                          )}
                          {!comp.is_archived && (
                            <Button
                              variant="ghost"
                              size="sm"
                              disabled={rowBusy}
                              title="Archive"
                              onClick={() =>
                                runAction(
                                  rowKey,
                                  `Archive "${comp.title}"? Applications and submissions stay recorded.`,
                                  () => adminApi.archiveCompetition(comp.id),
                                  "Hackathon archived.",
                                )
                              }
                            >
                              {rowBusy ? <Skeleton className="h-4 w-4" /> : <Archive className="h-4 w-4" />}
                            </Button>
                          )}
                          {comp.is_archived && (
                            <Button
                              variant="ghost"
                              size="sm"
                              disabled={rowBusy}
                              title="Unarchive"
                              onClick={() =>
                                runAction(
                                  rowKey,
                                  null,
                                  () => adminApi.unarchiveCompetition(comp.id),
                                  "Hackathon unarchived.",
                                )
                              }
                            >
                              {rowBusy ? <Skeleton className="h-4 w-4" /> : <Archive className="h-4 w-4 rotate-180" />}
                            </Button>
                          )}
                          <Button
                            variant="ghost"
                            size="sm"
                            disabled={rowBusy}
                            title="Delete"
                            onClick={() =>
                              runAction(
                                rowKey,
                                `Delete "${comp.title}" and all of its registrations permanently?`,
                                () => adminApi.deleteCompetition(comp.id),
                                "Hackathon deleted.",
                              )
                            }
                          >
                            <Trash2 className="h-4 w-4 text-red-500" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
