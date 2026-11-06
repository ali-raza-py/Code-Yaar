"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { adminApi } from "@/lib/admin-api";
import type { EmailCampaignAdmin } from "@/lib/admin-api";
import { useAuth } from "@/hooks/use-auth";
import { NetworkError } from "@/components/learning/workspace/error-states";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Plus } from "lucide-react";

const STATUS_BADGE: Record<EmailCampaignAdmin["status"], "default" | "secondary" | "outline" | "destructive"> = {
  draft: "outline",
  queued: "secondary",
  sending: "secondary",
  sent: "default",
  partial: "destructive",
  failed: "destructive",
};

const AUDIENCE_LABELS: Record<string, string> = {
  all: "All registered users",
  students: "Students",
  instructors: "Instructors",
  admins: "Administrators",
  specific: "Selected recipients",
  comp_participants: "Hackathon participants",
  comp_approved: "Approved applicants",
  comp_pending: "Pending applicants",
  comp_waitlisted: "Waitlisted applicants",
};

export default function EmailCampaignsPage() {
  const { user, loading: authLoading } = useAuth();
  const isSuperAdmin = Boolean(user?.is_super_admin);
  const [campaigns, setCampaigns] = useState<EmailCampaignAdmin[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(false);
  const [forbidden, setForbidden] = useState(false);
  // History filters handled server-side: search over name/subject/recipient
  // emails, plus status and a creation-date range.
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");

  const load = useCallback(async () => {
    if (!user) return;
    try {
      const data = await adminApi.listCampaigns({
        page_size: 100,
        ordering: "-created_at",
        search: search || undefined,
        status: statusFilter || undefined,
        date_from: dateFrom || undefined,
        date_to: dateTo || undefined,
      });
      setCampaigns(data.results);
      setLoadError(false);
    } catch (caught) {
      if (caught instanceof Error && /403|permission|Super Admin/i.test(caught.message)) {
        setForbidden(true);
      } else {
        setLoadError(true);
      }
    } finally {
      setLoading(false);
    }
  }, [user, search, statusFilter, dateFrom, dateTo]);

  useEffect(() => {
    (async () => { await load(); })();
  }, [load]);

  if (authLoading || loading) {
    return (
      <div className="animate-pulse space-y-4">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-24" />
        <Skeleton className="h-24" />
      </div>
    );
  }

  if (forbidden) {
    return (
      <Card className="mx-auto max-w-xl">
        <CardContent className="py-8 text-center">
          <p className="font-medium">Super Admin access required</p>
          <p className="mt-1 text-sm text-muted-foreground">
            Only Super Admins can compose and send platform-wide emails.
          </p>
        </CardContent>
      </Card>
    );
  }

  if (loadError) return <NetworkError onRetry={load} />;

  const hasActiveFilters = Boolean(search || statusFilter || dateFrom || dateTo);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold">Email Campaigns</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Every bulk email goes through this history. Drafts are harmless until
            you press Send — publishing content and emailing about it are always
            separate actions.
          </p>
        </div>
        {isSuperAdmin && (
          <div className="flex gap-2">
            <Link href="/admin/send-email">
              <Button size="sm">Send official email</Button>
            </Link>
            <Link href="/admin/email-campaigns/new">
              <Button size="sm" variant="outline">
                <Plus className="mr-1 h-4 w-4" /> New campaign
              </Button>
            </Link>
          </div>
        )}
      </div>

      <Card>
        <CardContent className="grid gap-3 py-4 md:grid-cols-4">
          <input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search by name, subject or recipient email…"
            className="rounded-md border bg-background px-3 py-2 text-sm"
          />
          <select
            value={statusFilter}
            onChange={(event) => setStatusFilter(event.target.value)}
            className="rounded-md border bg-background px-3 py-2 text-sm"
          >
            <option value="">Any status</option>
            {Object.keys(STATUS_BADGE).map((status) => (
              <option key={status} value={status}>{status}</option>
            ))}
          </select>
          <label className="text-sm">
            <span className="text-xs text-muted-foreground">From</span>
            <input type="date" value={dateFrom} onChange={(event) => setDateFrom(event.target.value)} className="mt-0.5 w-full rounded-md border bg-background px-3 py-1.5 text-sm" />
          </label>
          <label className="text-sm">
            <span className="text-xs text-muted-foreground">To</span>
            <input type="date" value={dateTo} onChange={(event) => setDateTo(event.target.value)} className="mt-0.5 w-full rounded-md border bg-background px-3 py-1.5 text-sm" />
          </label>
        </CardContent>
        {hasActiveFilters && (
          <CardContent className="pb-4 pt-0">
            <button
              type="button"
              className="text-xs text-muted-foreground underline hover:text-foreground"
              onClick={() => { setSearch(""); setStatusFilter(""); setDateFrom(""); setDateTo(""); }}
            >
              Clear filters
            </button>
          </CardContent>
        )}
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Campaign history ({campaigns.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {campaigns.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No campaigns yet. Drafts created from an announcement or platform
              update also show up here.
            </p>
          ) : (
            <div className="space-y-3">
              {campaigns.map((campaign) => (
                <Link
                  key={campaign.id}
                  href={`/admin/email-campaigns/${campaign.id}`}
                  className="block rounded-lg border p-4 transition-colors hover:bg-muted/50"
                >
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="font-medium">{campaign.name}</span>
                      <Badge variant={STATUS_BADGE[campaign.status] || "secondary"}>
                        {campaign.status}
                      </Badge>
                      {campaign.essential && <Badge variant="outline">Essential</Badge>}
                    </div>
                    <span className="text-xs text-muted-foreground">
                      {new Date(campaign.created_at).toLocaleString()}
                    </span>
                  </div>
                  <p className="mt-1 text-sm text-muted-foreground">
                    {AUDIENCE_LABELS[campaign.audience] || campaign.audience} ·
                    template “{campaign.template.replace(/_/g, " ")}”
                  </p>
                  {campaign.status !== "draft" && (
                    <p className="mt-1 text-xs">
                      Recipients: {campaign.recipient_count} ·
                      Sent: {campaign.sent_count} ·
                      Skipped: {campaign.skipped_count} ·
                      Failed: {campaign.failed_count}
                      {campaign.sent_at ? ` · sent ${new Date(campaign.sent_at).toLocaleString()}` : ""}
                    </p>
                  )}
                </Link>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
