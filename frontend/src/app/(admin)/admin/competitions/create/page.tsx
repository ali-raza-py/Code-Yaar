"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { adminApi } from "@/lib/admin-api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  EMPTY_HACKATHON_FORM,
  HackathonForm,
  hackathonToPayload,
  type HackathonFormValues,
} from "../hackathon-form";

export default function CreateHackathonPage() {
  const router = useRouter();
  const [values, setValues] = useState<HackathonFormValues>(EMPTY_HACKATHON_FORM);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit() {
    setSaving(true);
    setError("");
    try {
      const created = await adminApi.createCompetition(hackathonToPayload(values));
      // New events always start unpublished with the standard registration
      // form already seeded; go straight to the form builder for review.
      router.push(`/admin/competitions/${created.id}`);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "The hackathon could not be created.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <Card className="mx-auto max-w-4xl">
      <CardHeader>
        <CardTitle>Create Hackathon</CardTitle>
        <p className="mt-1 text-sm text-muted-foreground">
          New events are saved unpublished and always get the standard
          registration form, which you can customize afterwards in the form
          builder. Publishing is a separate action.
        </p>
      </CardHeader>
      <CardContent>
        {error && (
          <p role="alert" className="mb-4 rounded-md border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700 dark:border-red-800 dark:bg-red-950 dark:text-red-200">
            {error}
          </p>
        )}
        <HackathonForm
          values={values}
          onChange={setValues}
          submitLabel="Create Hackathon"
          saving={saving}
          disabled={saving}
          onSubmit={handleSubmit}
          onCancel={() => router.back()}
        />
      </CardContent>
    </Card>
  );
}
