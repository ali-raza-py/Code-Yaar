"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { Plus, Edit, Trash2, Eye, EyeOff, Archive, Mail, ExternalLink } from "lucide-react";
import { adminApi } from "@/lib/admin-api";
import type { AnnouncementAdmin } from "@/lib/admin-api";
import { useAuth } from "@/hooks/use-auth";
import { NetworkError } from "@/components/learning/workspace/error-states";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

const STATUS_LABELS: Record<AnnouncementAdmin["status"], string> = {
  draft: "Draft",
  published: "Published",
  unpublished: "Unpublished",
  archived: "Archived",
};

const CATEGORY_LABELS: Record<string, string> = {
  general: "General",
  platform_updates: "Platform Updates",
  hackathons: "Hackathons",
  courses: "Courses",
  competitions: "Competitions",
  maintenance: "Maintenance",
  important: "Important",
};

function statusBadgeVariant(status: AnnouncementAdmin["status"]) {
  switch (status) {
    case "published":
      return "default";
    case "archived":
      return "secondary";
    default:
      return "outline";
  }
}

export default function AdminAnnouncementsPage() {
  const { user, loading: authLoading } = useAuth();
  const [announcements, setAnnouncements] = useState<AnnouncementAdmin[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [busy, setBusy] = useState<string | null>(null);
  const [notice, setNotice] = useState("");
  const [actionError, setActionError] = useState("");

  const load = useCallback(async () => {
    if (!user) return;
    try {
      const data = await adminApi.listAnnouncements({ page_size: 100 });
      setAnnouncements(data.results);
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
          <h1 className="text-3xl font-bold tracking-tight text-foreground">Announcements</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Create, edit, and publish platform announcements. Publishing is a
            separate action from saving, and only Super Admins can publish.
          </p>
        </div>
        <Link href="/admin/announcements/create">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Create Announcement
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
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Priority</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Audience</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Status</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Published</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--color-section-border)]">
                {announcements.length === 0 && (
                  <tr>
                    <td colSpan={7} className="px-4 py-8 text-center text-muted-foreground">
                      No announcements yet. Create one to get started.
                    </td>
                  </tr>
                )}
                {announcements.map((announcement) => {
                  const rowKey = String(announcement.id);
                  const rowBusy = busy === rowKey;
                  return (
                    <tr key={announcement.id} className="hover:bg-[var(--color-section-light)]">
                      <td className="px-4 py-3 font-medium">{announcement.title}</td>
                      <td className="px-4 py-3">{CATEGORY_LABELS[announcement.category] ?? announcement.category}</td>
                      <td className="px-4 py-3">
                        <Badge variant={announcement.priority === "urgent" ? "default" : "outline"}>
                          {announcement.priority}
                        </Badge>
                      </td>
                      <td className="px-4 py-3">
                        <Badge variant="outline">{announcement.target_audience}</Badge>
                      </td>
                      <td className="px-4 py-3">
                        <Badge variant={statusBadgeVariant(announcement.status)}>
                          {STATUS_LABELS[announcement.status] ?? announcement.status}
                        </Badge>
                      </td>
                      <td className="px-4 py-3 text-muted-foreground">
                        {announcement.published_at
                          ? new Date(announcement.published_at).toLocaleString()
                          : "—"}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-1">
                          <Link href={`/admin/announcements/${announcement.id}`} title="Edit">
                            <Button variant="ghost" size="sm" disabled={rowBusy}>
                              <Edit className="h-4 w-4" />
                            </Button>
                          </Link>
                          {isSuperAdmin && announcement.status !== "published" && announcement.status !== "archived" && (
                            <Button
                              variant="ghost"
                              size="sm"
                              disabled={rowBusy}
                              title="Publish"
                              onClick={() =>
                                runAction(
                                  rowKey,
                                  `Publish "${announcement.title}"? It becomes visible to its audience immediately.`,
                                  () => adminApi.publishAnnouncement(announcement.id),
                                  "Announcement published.",
                                )
                              }
                            >
                              {rowBusy ? <Skeleton className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                            </Button>
                          )}
                          {isSuperAdmin && announcement.status === "published" && (
                            <Button
                              variant="ghost"
                              size="sm"
                              disabled={rowBusy}
                              title="Unpublish"
                              onClick={() =>
                                runAction(
                                  rowKey,
                                  `Unpublish "${announcement.title}"? Learners stop seeing it right away.`,
                                  () => adminApi.unpublishAnnouncement(announcement.id),
                                  "Announcement unpublished.",
                                )
                              }
                            >
                              {rowBusy ? <Skeleton className="h-4 w-4" /> : <EyeOff className="h-4 w-4" />}
                            </Button>
                          )}
                          {isSuperAdmin && announcement.status !== "archived" && (
                            <Button
                              variant="ghost"
                              size="sm"
                              disabled={rowBusy}
                              title="Archive"
                              onClick={() =>
                                runAction(
                                  rowKey,
                                  `Archive "${announcement.title}"? Archived announcements leave the public feed for good.`,
                                  () => adminApi.archiveAnnouncement(announcement.id),
                                  "Announcement archived.",
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
                                  `Stage an email draft from "${announcement.title}"? Nothing is sent — review and confirm it in Email Campaigns.`,
                                  () => adminApi.emailDraftAnnouncement(announcement.id),
                                  "Draft campaign created. Open Email Campaigns to preview, test, and send.",
                                )
                              }
                            >
                              {rowBusy ? <Skeleton className="h-4 w-4" /> : <Mail className="h-4 w-4" />}
                            </Button>
                          )}
                          {announcement.status === "published" && announcement.slug && (
                            <Link href={`/announcements/${announcement.slug}`} title="View public page" target="_blank">
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
                                `Delete "${announcement.title}" permanently? Prefer Archive if you want to keep the record.`,
                                () => adminApi.deleteAnnouncement(announcement.id),
                                "Announcement deleted.",
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
