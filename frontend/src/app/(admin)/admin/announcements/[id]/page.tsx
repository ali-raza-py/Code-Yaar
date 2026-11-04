"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { adminApi } from "@/lib/admin-api";
import type { AnnouncementAdmin } from "@/lib/admin-api";
import { useAuth } from "@/hooks/use-auth";
import { NetworkError } from "@/components/learning/workspace/error-states";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  AnnouncementForm,
  EMPTY_ANNOUNCEMENT_FORM,
  toLocalInputValue,
  type AnnouncementFormValues,
} from "../announcement-form";

export default function EditAnnouncementPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();
  const [announcement, setAnnouncement] = useState<AnnouncementAdmin | null>(null);
  const [values, setValues] = useState<AnnouncementFormValues>(EMPTY_ANNOUNCEMENT_FORM);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [saving, setSaving] = useState(false);
  const [notice, setNotice] = useState("");
  const [actionError, setActionError] = useState("");

  const load = useCallback(async () => {
    if (!user) return;
    try {
      const data = await adminApi.getAnnouncement(Number(params.id));
      setAnnouncement(data);
      setValues({
        title: data.title,
        short_description: data.short_description,
        body: data.body,
        category: data.category,
        priority: data.priority,
        target_audience: data.target_audience,
        scheduled_at: toLocalInputValue(data.scheduled_at),
        expires_at: toLocalInputValue(data.expires_at),
      });
      setError(false);
    } catch {
      setError(true);
    } finally {
      setLoading(false);
    }
  }, [user, params.id]);

  useEffect(() => {
    (async () => { await load(); })();
  }, [load]);

  async function handleSubmit() {
    setSaving(true);
    setActionError("");
    setNotice("");
    try {
      await adminApi.updateAnnouncement(Number(params.id), {
        title: values.title,
        body: values.body,
        short_description: values.short_description,
        category: values.category,
        priority: values.priority,
        target_audience: values.target_audience,
        scheduled_at: values.scheduled_at ? new Date(values.scheduled_at).toISOString() : null,
        expires_at: values.expires_at ? new Date(values.expires_at).toISOString() : null,
      });
      setNotice("Changes saved.");
      await load();
    } catch (caught) {
      setActionError(caught instanceof Error ? caught.message : "The announcement could not be saved.");
    } finally {
      setSaving(false);
    }
  }

  async function runStatusAction(action: () => Promise<unknown>, message: string) {
    setSaving(true);
    setActionError("");
    try {
      await action();
      setNotice(message);
      await load();
    } catch (caught) {
      setActionError(caught instanceof Error ? caught.message : "That action did not complete.");
    } finally {
      setSaving(false);
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

  if (error || !announcement) {
    return <NetworkError onRetry={load} />;
  }

  const isSuperAdmin = Boolean(user?.is_super_admin);

  return (
    <Card className="mx-auto max-w-3xl">
      <CardHeader>
        <div className="flex items-center justify-between gap-4">
          <CardTitle>Edit Announcement</CardTitle>
          <Badge variant={announcement.is_published ? "default" : "outline"}>
            {announcement.status}
          </Badge>
        </div>
        <p className="mt-1 text-sm text-muted-foreground">
          Saving edits never changes visibility. Use the buttons below to move
          it through the publishing workflow.
        </p>
      </CardHeader>
      <CardContent className="space-y-5">
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

        {isSuperAdmin && (
          <div className="flex flex-wrap gap-2">
            {announcement.status !== "published" && announcement.status !== "archived" && (
              <Button
                size="sm"
                disabled={saving}
                onClick={() =>
                  confirm(`Publish "${announcement.title}"?`) &&
                  runStatusAction(() => adminApi.publishAnnouncement(announcement.id), "Announcement published.")
                }
              >
                Publish
              </Button>
            )}
            {announcement.status === "published" && (
              <Button
                size="sm"
                variant="outline"
                disabled={saving}
                onClick={() =>
                  confirm(`Unpublish "${announcement.title}"?`) &&
                  runStatusAction(() => adminApi.unpublishAnnouncement(announcement.id), "Announcement unpublished.")
                }
              >
                Unpublish
              </Button>
            )}
            {announcement.status !== "archived" && (
              <Button
                size="sm"
                variant="outline"
                disabled={saving}
                onClick={() =>
                  confirm(`Archive "${announcement.title}"?`) &&
                  runStatusAction(() => adminApi.archiveAnnouncement(announcement.id), "Announcement archived.")
                }
              >
                Archive
              </Button>
            )}
          </div>
        )}

        <AnnouncementForm
          values={values}
          onChange={setValues}
          submitLabel="Save Changes"
          saving={saving}
          disabled={saving}
          onSubmit={handleSubmit}
          onCancel={() => router.push("/admin/announcements")}
        />
      </CardContent>
    </Card>
  );
}
