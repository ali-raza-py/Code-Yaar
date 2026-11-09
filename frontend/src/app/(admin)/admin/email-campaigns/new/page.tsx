"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { adminApi } from "@/lib/admin-api";
import type { CompetitionAdmin } from "@/lib/admin-api";
import { useAuth } from "@/hooks/use-auth";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  CampaignForm,
  EMPTY_CAMPAIGN_FORM,
  campaignToPayload,
  type CampaignFormValues,
} from "../campaign-form";

export default function NewCampaignPage() {
  const router = useRouter();
  const { user } = useAuth();
  const [values, setValues] = useState<CampaignFormValues>(EMPTY_CAMPAIGN_FORM);
  const [competitions, setCompetitions] = useState<CompetitionAdmin[]>([]);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const data = await adminApi.listCompetitions({ page_size: 100 });
        setCompetitions(data.results);
      } catch {
        // Hackathon audiences just won't have options until the list loads.
      }
    })();
  }, [user]);

  async function handleSubmit() {
    setSaving(true);
    setError("");
    try {
      const created = await adminApi.createCampaign(campaignToPayload(values));
      router.push(`/admin/email-campaigns/${created.id}`);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "The campaign draft could not be created.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <Card className="mx-auto max-w-3xl">
      <CardHeader>
        <CardTitle>New Email Campaign</CardTitle>
        <p className="mt-1 text-sm text-muted-foreground">
          This only creates a draft — nobody receives anything yet. On the next
          screen you can check the audience size, preview the email, send
          yourself a test, and finally send for real.
        </p>
      </CardHeader>
      <CardContent>
        {error && (
          <p role="alert" className="mb-4 rounded-md border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700 dark:border-red-800 dark:bg-red-950 dark:text-red-200">
            {error}
          </p>
        )}
        <CampaignForm
          values={values}
          onChange={setValues}
          competitions={competitions.map((c) => ({ id: c.id, title: c.title }))}
          submitLabel="Create draft"
          saving={saving}
          disabled={saving}
          onSubmit={handleSubmit}
          onCancel={() => router.push("/admin/email-campaigns")}
        />
      </CardContent>
    </Card>
  );
}
