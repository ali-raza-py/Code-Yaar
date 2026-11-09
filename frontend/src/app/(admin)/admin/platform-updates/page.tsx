"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { Plus, Edit, Trash2, Eye, EyeOff, Archive, Mail, ExternalLink } from "lucide-react";
import { adminApi } from "@/lib/admin-api";
import type { PlatformUpdateAdmin } from "@/lib/admin-api";
import { useAuth } from "@/hooks/use-auth";
import { NetworkError } from "@/components/learning/workspace/error-states";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

const STATUS_LABELS: Record<string, string> = {
  draft: "Draft",
  published: "Published",
  unpublished: "Unpublished",
  archived: "Archived",
};

const CATEGORY_LABELS: Record<string, string> = {
  feature: "New Feature",
  course: "Courses & Tracks",
  improvement: "Improvement",
  bug_fix: "Bug Fix",
  performance: "Performance",
  certificate: "Certificates",
  other: "Other",
};

export default function AdminPlatformUpdatesPage() {
  const { user, loading: authLoading } = useAuth();
  const [updates, setUpdates] = useState<PlatformUpdateAdmin[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [busy, setBusy] = useState<string | null>(null);
  const [notice, setNotice] = useState("");
  const [actionError, setActionError] = useState("");

  const load = useCallback(async () => {
    if (!user) return;
    try {
      const data = await adminApi.listPlatformUpdates({ page_size: 100 });
      setUpdates(data.results);
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

  const isSuperAdmin = Boolean(user?.is_super_admin);

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
          <h1 className="text-3xl font-bold tracking-tight text-foreground">Platform Updates</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            The public changelog. Updates describe what changed on the
            platform; announcing them by email is a separate, deliberate step.
          </p>
        </div>
        <Link href="/admin/platform-updates/create">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Create Update
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
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Version</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Category</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Status</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Published</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--color-section-border)]">
                {updates.length === 0 && (
                  <tr>
                    <td colSpan={6} className="px-4 py-8 text-center text-muted-foreground">
                      No platform updates yet. Write the first changelog entry.
                    </td>
                  </tr>
                )}
                {updates.map((update) => {
                  const rowKey = String(update.id);
                  const rowBusy = busy === rowKey;
                  return (
                    <tr key={update.id} className="hover:bg-[var(--color-section-light)]">
                      <td className="px-4 py-3 font-medium">{update.title}</td>
                      <td className="px-4 py-3 text-muted-foreground">{update.version || "—"}</td>
                      <td className="px-4 py-3">
                        <Badge variant="outline">{CATEGORY_LABELS[update.category] ?? update.category}</Badge>
                      </td>
                      <td className="px-4 py-3">
                        <Badge variant={update.status === "published" ? "default" : update.status === "archived" ? "secondary" : "outline"}>
                          {STATUS_LABELS[update.status] ?? update.status}
                        </Badge>
                      </td>
                      <td className="px-4 py-3 text-muted-foreground">
                        {update.published_at ? new Date(update.published_at).toLocaleString() : "—"}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-1">
                          <Link href={`/admin/platform-updates/${update.id}`} title="Edit">
                            <Button variant="ghost" size="sm" disabled={rowBusy}>
                              <Edit className="h-4 w-4" />
                            </Button>
                          </Link>
                          {isSuperAdmin && update.status !== "published" && update.status !== "archived" && (
                            <Button
                              variant="ghost"
                              size="sm"
                              disabled={rowBusy}
                              title="Publish"
                              onClick={() =>
                                runAction(
                                  rowKey,
                                  `Publish "${update.title}"? It appears on the public Updates page immediately — no email is sent.`,
                                  () => adminApi.publishPlatformUpdate(update.id),
                                  "Update published. It is live on the Updates page.",
                                )
                              }
                            >
                              {rowBusy ? <Skeleton className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                            </Button>
                          )}
                          {isSuperAdmin && update.status === "published" && (
                            <Button
                              variant="ghost"
                              size="sm"
                              disabled={rowBusy}
                              title="Unpublish"
                              onClick={() =>
                                runAction(
                                  rowKey,
                                  `Unpublish "${update.title}"?`,
                                  () => adminApi.unpublishPlatformUpdate(update.id),
                                  "Update unpublished.",
                                )
                              }
                            >
                              {rowBusy ? <Skeleton className="h-4 w-4" /> : <EyeOff className="h-4 w-4" />}
                            </Button>
                          )}
                          {isSuperAdmin && update.status !== "archived" && (
                            <Button
                              variant="ghost"
                              size="sm"
                              disabled={rowBusy}
                              title="Archive"
                              onClick={() =>
                                runAction(
                                  rowKey,
                                  `Archive "${update.title}"?`,
                                  () => adminApi.archivePlatformUpdate(update.id),
                                  "Update archived.",
                                )
                              }
                            >
                              {rowBusy ? <Skeleton className="h-4 w-4" /> : <Archive className="h-4 w-4" />}
                            </Button>
                          )}
                          {isSuperAdmin && (
                            <Button
                              variant="ghost"
                              size="sm"
                              disabled={rowBusy}
                              title="Create email draft (does not send anything yet)"
                              onClick={() =>
                                runAction(
                                  rowKey,
                                  `Stage an email draft for "${update.title}"? Nothing is sent — review it in Email Campaigns.`,
                                  () => adminApi.emailDraftPlatformUpdate(update.id),
                                  "Draft campaign created. Open Email Campaigns to preview, test, and send.",
                                )
                              }
                            >
                              {rowBusy ? <Skeleton className="h-4 w-4" /> : <Mail className="h-4 w-4" />}
                            </Button>
                          )}
                          {update.status === "published" && update.slug && (
                            <Link href={`/updates/${update.slug}`} title="View public page" target="_blank">
                              <Button variant="ghost" size="sm" disabled={rowBusy}>
                                <ExternalLink className="h-4 w-4" />
                              </Button>
                            </Link>
                          )}
                          <Button
                            variant="ghost"
                            size="sm"
                            disabled={rowBusy}
                            title="Delete"
                            onClick={() =>
                              runAction(
                                rowKey,
                                `Delete "${update.title}" permanently? Prefer Archive to keep the changelog record.`,
                                () => adminApi.deletePlatformUpdate(update.id),
                                "Update deleted.",
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
