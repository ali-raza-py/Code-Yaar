"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { adminApi } from "@/lib/admin-api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  EMPTY_PLATFORM_UPDATE_FORM,
  PlatformUpdateForm,
  parseChangeList,
  type PlatformUpdateFormValues,
} from "../platform-update-form";

export default function CreatePlatformUpdatePage() {
  const router = useRouter();
  const [values, setValues] = useState<PlatformUpdateFormValues>(EMPTY_PLATFORM_UPDATE_FORM);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit() {
    setSaving(true);
    setError("");
    try {
      await adminApi.createPlatformUpdate({
        title: values.title,
        version: values.version,
        category: values.category,
        summary: values.summary,
        content: values.content,
        change_list: parseChangeList(values.changeListText),
        target_audience: values.target_audience,
      });
      router.push("/admin/platform-updates");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "The update could not be created.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <Card className="mx-auto max-w-3xl">
      <CardHeader>
        <CardTitle>Create Platform Update</CardTitle>
        <p className="mt-1 text-sm text-muted-foreground">
          Changelog entries are saved as drafts. Publishing puts them on the
          public Updates page; emailing them stays a separate action.
        </p>
      </CardHeader>
      <CardContent>
        {error && (
          <p role="alert" className="mb-4 rounded-md border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700 dark:border-red-800 dark:bg-red-950 dark:text-red-200">
            {error}
          </p>
        )}
        <PlatformUpdateForm
          values={values}
          onChange={setValues}
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
