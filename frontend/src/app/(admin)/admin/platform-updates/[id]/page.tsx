"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { adminApi } from "@/lib/admin-api";
import type { PlatformUpdateAdmin } from "@/lib/admin-api";
import { useAuth } from "@/hooks/use-auth";
import { NetworkError } from "@/components/learning/workspace/error-states";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  EMPTY_PLATFORM_UPDATE_FORM,
  PlatformUpdateForm,
  parseChangeList,
  type PlatformUpdateFormValues,
} from "../platform-update-form";

export default function EditPlatformUpdatePage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();
  const [update, setUpdate] = useState<PlatformUpdateAdmin | null>(null);
  const [values, setValues] = useState<PlatformUpdateFormValues>(EMPTY_PLATFORM_UPDATE_FORM);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [saving, setSaving] = useState(false);
  const [notice, setNotice] = useState("");
  const [actionError, setActionError] = useState("");

  const load = useCallback(async () => {
    if (!user) return;
    try {
      const data = await adminApi.getPlatformUpdate(Number(params.id));
      setUpdate(data);
      setValues({
        title: data.title,
        version: data.version,
        category: data.category,
        summary: data.summary,
        content: data.content,
        changeListText: (data.change_list || []).join("\n"),
        target_audience: data.target_audience,
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
      await adminApi.updatePlatformUpdate(Number(params.id), {
        title: values.title,
        version: values.version,
        category: values.category,
        summary: values.summary,
        content: values.content,
        change_list: parseChangeList(values.changeListText),
        target_audience: values.target_audience,
      });
      setNotice("Changes saved.");
      await load();
    } catch (caught) {
      setActionError(caught instanceof Error ? caught.message : "The update could not be saved.");
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

  if (error || !update) {
    return <NetworkError onRetry={load} />;
  }

  const isSuperAdmin = Boolean(user?.is_super_admin);

  return (
    <Card className="mx-auto max-w-3xl">
      <CardHeader>
        <div className="flex items-center justify-between gap-4">
          <CardTitle>Edit Platform Update</CardTitle>
          <Badge variant={update.status === "published" ? "default" : "outline"}>{update.status}</Badge>
        </div>
        <p className="mt-1 text-sm text-muted-foreground">
          Saving edits never changes visibility. Publish from the buttons below
          or the updates list.
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
            {update.status !== "published" && update.status !== "archived" && (
              <Button
                size="sm"
                disabled={saving}
                onClick={() =>
                  confirm(`Publish "${update.title}"? No email is sent — publishing only updates the public changelog.`) &&
                  runStatusAction(() => adminApi.publishPlatformUpdate(update.id), "Update published.")
                }
              >
                Publish
              </Button>
            )}
            {update.status === "published" && (
              <Button
                size="sm"
                variant="outline"
                disabled={saving}
                onClick={() =>
                  confirm(`Unpublish "${update.title}"?`) &&
                  runStatusAction(() => adminApi.unpublishPlatformUpdate(update.id), "Update unpublished.")
                }
              >
                Unpublish
              </Button>
            )}
            {update.status !== "archived" && (
              <Button
                size="sm"
                variant="outline"
                disabled={saving}
                onClick={() =>
                  confirm(`Archive "${update.title}"?`) &&
                  runStatusAction(() => adminApi.archivePlatformUpdate(update.id), "Update archived.")
                }
              >
                Archive
              </Button>
            )}
          </div>
        )}

        <PlatformUpdateForm
          values={values}
          onChange={setValues}
          submitLabel="Save Changes"
          saving={saving}
          disabled={saving}
          onSubmit={handleSubmit}
          onCancel={() => router.push("/admin/platform-updates")}
        />
      </CardContent>
    </Card>
  );
}
