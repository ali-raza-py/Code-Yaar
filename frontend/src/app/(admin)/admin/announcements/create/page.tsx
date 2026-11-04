"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { adminApi } from "@/lib/admin-api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  AnnouncementForm,
  EMPTY_ANNOUNCEMENT_FORM,
  type AnnouncementFormValues,
} from "../announcement-form";

export default function CreateAnnouncementPage() {
  const router = useRouter();
  const [values, setValues] = useState<AnnouncementFormValues>(EMPTY_ANNOUNCEMENT_FORM);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  async function handleSubmit() {
    setSaving(true);
    setError("");
    setFieldErrors({});
    try {
      await adminApi.createAnnouncement({
        title: values.title,
        body: values.body,
        short_description: values.short_description,
        category: values.category,
        priority: values.priority,
        target_audience: values.target_audience,
        scheduled_at: values.scheduled_at ? new Date(values.scheduled_at).toISOString() : null,
        expires_at: values.expires_at ? new Date(values.expires_at).toISOString() : null,
      });
      router.push("/admin/announcements");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "The announcement could not be created.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <Card className="mx-auto max-w-3xl">
      <CardHeader>
        <CardTitle>Create Announcement</CardTitle>
        <p className="mt-1 text-sm text-muted-foreground">
          New announcements are saved as drafts. Use Publish from the
          announcements list when it is ready to go live.
        </p>
      </CardHeader>
      <CardContent>
        {error && (
          <p role="alert" className="mb-4 rounded-md border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700 dark:border-red-800 dark:bg-red-950 dark:text-red-200">
            {error}
          </p>
        )}
        <AnnouncementForm
          values={values}
          onChange={setValues}
          fieldErrors={fieldErrors}
          submitLabel="Save as Draft"
          saving={saving}
          disabled={saving}
          onSubmit={handleSubmit}
          onCancel={() => router.back()}
        />
      </CardContent>
    </Card>
  );
}
