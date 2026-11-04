"use client";

import { useCallback, useEffect, useState } from "react";
import { adminApi } from "@/lib/admin-api";
import type { EmailSettingsAdmin } from "@/lib/admin-api";
import { useAuth } from "@/hooks/use-auth";
import { NetworkError } from "@/components/learning/workspace/error-states";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

function Row({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-2 border-b py-2.5 text-sm last:border-b-0">
      <span className="text-muted-foreground">{label}</span>
      <span className="font-medium text-right break-all">{value}</span>
    </div>
  );
}

export default function EmailSettingsPage() {
  const { user, loading: authLoading } = useAuth();
  const [settings, setSettings] = useState<EmailSettingsAdmin | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(false);
  const [forbidden, setForbidden] = useState(false);

  const load = useCallback(async () => {
    if (!user) return;
    try {
      const data = await adminApi.getEmailSettings();
      setSettings(data);
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
  }, [user]);

  useEffect(() => {
    (async () => { await load(); })();
  }, [load]);

  if (authLoading || loading) {
    return (
      <div className="animate-pulse space-y-4">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-48" />
      </div>
    );
  }

  if (forbidden) {
    return (
      <Card className="mx-auto max-w-xl">
        <CardContent className="py-8 text-center">
          <p className="font-medium">Super Admin access required</p>
          <p className="mt-1 text-sm text-muted-foreground">
            Email transport settings are visible to Super Admins only.
          </p>
        </CardContent>
      </Card>
    );
  }

  if (loadError || !settings) return <NetworkError onRetry={load} />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Email Settings</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Read-only view of the outgoing mail transport. Credentials are managed
          exclusively through backend environment variables and are never
          displayed or editable here.
        </p>
      </div>

      <Card className="mx-auto max-w-2xl">
        <CardHeader>
          <div className="flex flex-wrap items-center justify-between gap-2">
            <CardTitle>Outgoing mail transport</CardTitle>
            <Badge variant={settings.delivery_ready ? "default" : "secondary"}>
              {settings.delivery_ready ? "Live SMTP configured" : "No live delivery"}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          {!settings.delivery_ready && (
            <p className="mb-4 rounded-md border border-amber-200 bg-amber-50 px-4 py-2 text-sm text-amber-800 dark:border-amber-800 dark:bg-amber-950 dark:text-amber-200">
              With no SMTP host configured, campaigns still record exactly what
              each recipient would receive (rendered-only) but no real email
              leaves the server. Statuses below always tell the truth about this.
            </p>
          )}
          <Row label="Backend" value={settings.backend || "—"} />
          <Row label="SMTP host" value={settings.host || "—"} />
          <Row label="SMTP port" value={settings.port ?? "—"} />
          <Row label="Username" value={settings.username || "—"} />
          <Row
            label="Password"
            value={
              settings.password_configured ? (
                <span className="flex items-center gap-2">
                  <span className="tracking-widest">••••••••</span>
                  <Badge variant="outline">configured</Badge>
                </span>
              ) : (
                <Badge variant="secondary">not set</Badge>
              )
            }
          />
          <Row label="TLS / SSL" value={`TLS: ${settings.use_tls ? "on" : "off"} · SSL: ${settings.use_ssl ? "on" : "off"}`} />
          <Row label="From address" value={settings.from_email || "—"} />
          {settings.note && (
            <p className="mt-4 rounded-md bg-muted px-4 py-3 text-xs text-muted-foreground">
              {settings.note}
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
