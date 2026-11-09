"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { adminApi } from "@/lib/admin-api";
import type { CompetitionAdmin } from "@/lib/admin-api";
import { useAuth } from "@/hooks/use-auth";
import { NetworkError } from "@/components/learning/workspace/error-states";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  EMPTY_HACKATHON_FORM,
  HackathonForm,
  hackathonFromAdmin,
  hackathonToPayload,
  type HackathonFormValues,
} from "../hackathon-form";

export default function EditHackathonPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();
  const [competition, setCompetition] = useState<CompetitionAdmin | null>(null);
  const [values, setValues] = useState<HackathonFormValues>(EMPTY_HACKATHON_FORM);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [saving, setSaving] = useState(false);
  const [notice, setNotice] = useState("");
  const [actionError, setActionError] = useState("");

  const id = Number(params.id);

  const load = useCallback(async () => {
    if (!user) return;
    try {
      const data = await adminApi.getCompetition(id);
      setCompetition(data);
      setValues(hackathonFromAdmin(data));
      setError(false);
    } catch {
      setError(true);
    } finally {
      setLoading(false);
    }
  }, [user, id]);

  useEffect(() => {
    (async () => { await load(); })();
  }, [load]);

  async function handleSubmit() {
    setSaving(true);
    setActionError("");
    setNotice("");
    try {
      await adminApi.updateCompetition(id, hackathonToPayload(values));
      setNotice("Changes saved.");
      await load();
    } catch (caught) {
      setActionError(caught instanceof Error ? caught.message : "The hackathon could not be saved.");
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

  if (error || !competition) {
    return <NetworkError onRetry={load} />;
  }

  const publishable = competition.status !== "archived";

  return (
    <div className="space-y-6">
      <Card className="mx-auto max-w-4xl">
        <CardHeader>
          <div className="flex flex-wrap items-center justify-between gap-3">
            <CardTitle>Edit Hackathon</CardTitle>
            <div className="flex items-center gap-2">
              <Badge variant="outline">{competition.status.replace(/_/g, " ")}</Badge>
              <Badge variant={competition.is_published ? "default" : "secondary"}>
                {competition.is_published ? "Published" : "Not published"}
              </Badge>
              {competition.is_archived && <Badge variant="secondary">Archived</Badge>}
            </div>
          </div>
          <p className="mt-1 text-sm text-muted-foreground">
            Saving edits never changes visibility. Statuses below always follow
            the event dates; archiving takes the event out of public listings
            while keeping every application and submission record.
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

          <div className="flex flex-wrap gap-2">
            {!competition.is_published && publishable && (
              <Button
                size="sm"
                disabled={saving}
                onClick={() =>
                  confirm(`Publish "${competition.title}"? It becomes visible to everyone immediately — no email is sent.`) &&
                  runStatusAction(() => adminApi.publishCompetition(competition.id), "Hackathon published.")
                }
              >
                Publish
              </Button>
            )}
            {competition.is_published && (
              <Button
                size="sm"
                variant="outline"
                disabled={saving}
                onClick={() =>
                  confirm(`Unpublish "${competition.title}"?`) &&
                  runStatusAction(() => adminApi.unpublishCompetition(competition.id), "Hackathon unpublished.")
                }
              >
                Unpublish
              </Button>
            )}
            {!competition.is_archived ? (
              <Button
                size="sm"
                variant="outline"
                disabled={saving}
                onClick={() =>
                  confirm(`Archive "${competition.title}"? It leaves public listings; applications stay recorded.`) &&
                  runStatusAction(() => adminApi.archiveCompetition(competition.id), "Hackathon archived.")
                }
              >
                Archive
              </Button>
            ) : (
              <Button
                size="sm"
                variant="outline"
                disabled={saving}
                onClick={() =>
                  runStatusAction(() => adminApi.unarchiveCompetition(competition.id), "Hackathon unarchived.")
                }
              >
                Unarchive
              </Button>
            )}
            <Link href={`/admin/competitions/${competition.id}/form-builder`}>
              <Button size="sm" variant="outline">Registration form builder</Button>
            </Link>
            <Link href={`/admin/applications?competition=${competition.id}`}>
              <Button size="sm" variant="outline">
                Applications ({competition.participant_count})
              </Button>
            </Link>
          </div>

          <HackathonForm
            values={values}
            onChange={setValues}
            submitLabel="Save Changes"
            saving={saving}
            disabled={saving}
            onSubmit={handleSubmit}
            onCancel={() => router.push("/admin/competitions")}
          />
        </CardContent>
      </Card>
    </div>
  );
}
