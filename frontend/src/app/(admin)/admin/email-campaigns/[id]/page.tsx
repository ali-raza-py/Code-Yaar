"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { adminApi } from "@/lib/admin-api";
import type {
  CompetitionAdmin,
  EmailCampaignAdmin,
  EmailCampaignRecipientAdmin,
} from "@/lib/admin-api";
import { NetworkError } from "@/components/learning/workspace/error-states";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  CampaignForm,
  EMPTY_CAMPAIGN_FORM,
  campaignFromAdmin,
  campaignToPayload,
  type CampaignFormValues,
} from "../campaign-form";

const STATUS_BADGE: Record<EmailCampaignAdmin["status"], "default" | "secondary" | "outline" | "destructive"> = {
  draft: "outline",
  queued: "secondary",
  sending: "secondary",
  sent: "default",
  partial: "destructive",
  failed: "destructive",
};

const RECIPIENT_BADGE: Record<EmailCampaignRecipientAdmin["status"], "default" | "secondary" | "outline" | "destructive"> = {
  pending: "outline",
  sent: "default",
  render_only: "secondary",
  skipped: "secondary",
  failed: "destructive",
};

const RECIPIENT_LABELS: Record<string, string> = {
  "": "All recipients",
  pending: "Pending",
  sent: "Sent",
  render_only: "Rendered only (delivery not configured)",
  skipped: "Skipped (unsubscribed)",
  failed: "Failed",
};

export default function CampaignDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const id = Number(params.id);

  const [campaign, setCampaign] = useState<EmailCampaignAdmin | null>(null);
  const [values, setValues] = useState<CampaignFormValues>(EMPTY_CAMPAIGN_FORM);
  const [competitions, setCompetitions] = useState<CompetitionAdmin[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(false);
  const [saving, setSaving] = useState(false);
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");

  const [audienceCount, setAudienceCount] = useState<number | null>(null);
  const [checkingAudience, setCheckingAudience] = useState(false);
  const [preview, setPreview] = useState<{ html: string; text: string } | null>(null);
  const [previewMode, setPreviewMode] = useState<"html" | "text">("html");
  const [recipients, setRecipients] = useState<EmailCampaignRecipientAdmin[]>([]);
  const [recipientFilter, setRecipientFilter] = useState("");

  const load = useCallback(async () => {
    try {
      const data = await adminApi.getCampaign(id);
      setCampaign(data);
      setValues(campaignFromAdmin(data));
      setLoadError(false);
      if (data.status !== "draft") {
        try {
          const rows = await adminApi.campaignRecipients(id, { page_size: 100, status: recipientFilter || undefined });
          setRecipients(rows.results);
        } catch {
          // Recipient table stays empty; the summary counters still show.
        }
      }
    } catch {
      setLoadError(true);
    } finally {
      setLoading(false);
    }
  }, [id, recipientFilter]);

  useEffect(() => {
    (async () => {
      try {
        const data = await adminApi.listCompetitions({ page_size: 100 });
        setCompetitions(data.results);
      } catch {
        // Only matters for hackathon audiences.
      }
      await load();
    })();
  }, [load]);

  async function saveChanges(): Promise<boolean> {
    setSaving(true);
    setError("");
    setNotice("");
    try {
      const updated = await adminApi.updateCampaign(id, campaignToPayload(values));
      setCampaign(updated);
      setNotice("Draft saved.");
      return true;
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "The campaign could not be saved.");
      return false;
    } finally {
      setSaving(false);
    }
  }

  async function checkAudience() {
    if (campaign && campaign.status !== "draft") return;
    setCheckingAudience(true);
    setError("");
    try {
      if (!(await saveChanges())) return;
      const data = await adminApi.campaignAudienceCount(id);
      setAudienceCount(data.count);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "The audience size could not be counted.");
    } finally {
      setCheckingAudience(false);
    }
  }

  async function showPreview() {
    setError("");
    setPreview(null);
    if (campaign && campaign.status === "draft") {
      if (!(await saveChanges())) return;
    }
    try {
      const data = await adminApi.campaignPreview(id);
      setPreview(data);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "The preview could not be rendered.");
    }
  }

  async function sendTest() {
    setError("");
    setNotice("");
    try {
      const data = await adminApi.campaignTest(id);
      setNotice(data.detail || "A test copy was delivered to your account email.");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "The test email could not be sent.");
    }
  }

  async function sendCampaign() {
    if (!campaign) return;
    const counted = audienceCount !== null ? audienceCount : campaign.recipient_count;
    const confirmed = confirm(
      `Send "${campaign.name}" to about ${counted} recipients now?\n\n` +
        "This is irreversible — a campaign's emails are never re-sent, and each " +
        "recipient receives at most one copy. Content published earlier stays " +
        "published either way.",
    );
    if (!confirmed) return;
    setSaving(true);
    setError("");
    setNotice("");
    try {
      const data = await adminApi.campaignSend(id);
      setNotice(
        `Sending started for ${data.estimated_recipients} recipients. ` +
          "Status and per-recipient results appear below — refresh to update.",
      );
      await load();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "The campaign could not be started.");
    } finally {
      setSaving(false);
    }
  }

  async function deleteDraft() {
    if (!campaign || !confirm(`Discard the draft "${campaign.name}"?`)) return;
    setSaving(true);
    setError("");
    try {
      await adminApi.deleteCampaign(id);
      router.push("/admin/email-campaigns");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "The draft could not be deleted.");
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="animate-pulse space-y-4">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-64" />
      </div>
    );
  }

  if (loadError || !campaign) return <NetworkError onRetry={load} />;

  const isDraft = campaign.status === "draft";

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold">{campaign.name}</h1>
          <div className="mt-1 flex items-center gap-2 text-sm text-muted-foreground">
            <Badge variant={STATUS_BADGE[campaign.status] || "secondary"}>{campaign.status}</Badge>
            {campaign.essential && <Badge variant="outline">Essential</Badge>}
            {!isDraft && campaign.sent_at && <span>sent {new Date(campaign.sent_at).toLocaleString()}</span>}
          </div>
        </div>
        <Link href="/admin/email-campaigns">
          <Button variant="outline" size="sm">Back to campaigns</Button>
        </Link>
      </div>

      {notice && (
        <p className="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-2 text-sm text-emerald-800 dark:border-emerald-800 dark:bg-emerald-950 dark:text-emerald-200">
          {notice}
        </p>
      )}
      {error && (
        <p role="alert" className="rounded-md border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700 dark:border-red-800 dark:bg-red-950 dark:text-red-200">
          {error}
        </p>
      )}

      {!isDraft && (
        <Card>
          <CardHeader>
            <CardTitle>Delivery results</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-3 sm:grid-cols-4">
              {[
                ["Recipients", campaign.recipient_count],
                ["Sent", campaign.sent_count],
                ["Skipped", campaign.skipped_count],
                ["Failed", campaign.failed_count],
              ].map(([label, value]) => (
                <div key={label} className="rounded-lg border p-3">
                  <p className="text-xs uppercase tracking-wide text-muted-foreground">{label}</p>
                  <p className="text-xl font-bold">{value}</p>
                </div>
              ))}
            </div>
            <div className="flex flex-wrap items-center gap-3">
              <Button variant="outline" size="sm" onClick={load}>Refresh status</Button>
              <select
                value={recipientFilter}
                onChange={(e) => setRecipientFilter(e.target.value)}
                className="rounded-md border bg-background px-3 py-2 text-sm"
              >
                {Object.entries(RECIPIENT_LABELS).map(([value, label]) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </select>
            </div>
            {recipients.length === 0 ? (
              <p className="text-sm text-muted-foreground">No recipient rows for this filter.</p>
            ) : (
              <div className="space-y-2">
                {recipients.map((row) => (
                  <div key={row.id} className="flex flex-wrap items-center justify-between gap-2 rounded-md border px-3 py-2 text-sm">
                    <div className="flex items-center gap-2">
                      <span className="font-medium">{row.username}</span>
                      <span className="text-muted-foreground">{row.email}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant={RECIPIENT_BADGE[row.status] || "secondary"}>{row.status.replace(/_/g, " ")}</Badge>
                      {row.error && <span className="text-xs text-red-600 dark:text-red-400">{row.error}</span>}
                      {row.sent_at && <span className="text-xs text-muted-foreground">{new Date(row.sent_at).toLocaleString()}</span>}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>{isDraft ? "Compose" : "Content (locked after sending)"}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-5">
          <CampaignForm
            values={values}
            onChange={setValues}
            competitions={competitions.map((c) => ({ id: c.id, title: c.title }))}
            submitLabel="Save draft"
            saving={saving}
            disabled={!isDraft || saving}
            onSubmit={() => {
              void saveChanges();
            }}
            onCancel={() => router.push("/admin/email-campaigns")}
          />

          {isDraft && (
            <div className="border-t pt-4">
              <p className="mb-3 text-sm text-muted-foreground">
                Check the audience size, preview the exact email, send a test to
                yourself, then send for real. Nothing below mails anyone except
                the Send buttons.
              </p>
              <div className="flex flex-wrap gap-2">
                <Button variant="outline" size="sm" disabled={saving || checkingAudience} onClick={checkAudience}>
                  {checkingAudience ? "Counting..." : "Check audience size"}
                </Button>
                {audienceCount !== null && (
                  <Badge variant="secondary" className="self-center">
                    {audienceCount} recipient{audienceCount === 1 ? "" : "s"}
                  </Badge>
                )}
                <Button variant="outline" size="sm" disabled={saving} onClick={showPreview}>
                  Preview email
                </Button>
                <Button variant="outline" size="sm" disabled={saving} onClick={sendTest}>
                  Send test to me
                </Button>
                <Button size="sm" disabled={saving} onClick={sendCampaign}>
                  Send campaign now
                </Button>
                <Button variant="outline" size="sm" disabled={saving} onClick={deleteDraft}>
                  Discard draft
                </Button>
              </div>
            </div>
          )}

          {preview && (
            <div className="border-t pt-4">
              <div className="mb-2 flex items-center justify-between">
                <p className="text-sm font-medium">Preview — subject: “{campaign.subject}”</p>
                <div className="flex gap-1">
                  <Button size="sm" variant={previewMode === "html" ? "default" : "outline"} onClick={() => setPreviewMode("html")}>
                    HTML
                  </Button>
                  <Button size="sm" variant={previewMode === "text" ? "default" : "outline"} onClick={() => setPreviewMode("text")}>
                    Plain text
                  </Button>
                </div>
              </div>
              {previewMode === "html" ? (
                <iframe
                  title="Email preview"
                  srcDoc={preview.html}
                  className="h-[480px] w-full rounded-md border bg-white"
                  sandbox=""
                />
              ) : (
                <pre className="h-[480px] w-full overflow-auto rounded-md border bg-muted p-4 text-xs whitespace-pre-wrap">
                  {preview.text}
                </pre>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
