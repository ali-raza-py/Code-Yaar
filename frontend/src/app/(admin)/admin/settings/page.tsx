"use client";

import { useCallback, useEffect, useState } from "react";
import { adminApi } from "@/lib/admin-api";
import type { PlatformSettingsAdmin } from "@/lib/admin-api";
import { useAuth } from "@/hooks/use-auth";
import { NetworkError } from "@/components/learning/workspace/error-states";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";

export default function AdminSettingsPage() {
  const { user, loading: authLoading } = useAuth();
  const [settings, setSettings] = useState<PlatformSettingsAdmin | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState("");

  const load = useCallback(async () => {
    if (!user) return;
    try {
      const data = await adminApi.getSettings();
      setSettings(data);
      setError(false);
    } catch {
      setError(true);
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    (async () => { await load(); })();
  }, [load]);

  const handleSave = async () => {
    if (!settings) return;
    if (
      settings.maintenance_mode &&
      !window.confirm(
        "Enable maintenance mode? Visitors and non-Super Admin users will be blocked."
      )
    ) return;
    setSaving(true);
    setSaveMessage("");
    try {
      const saved = await adminApi.updateSettings({
        platform_name: settings.platform_name,
        enrollment_enabled: settings.enrollment_enabled,
        maintenance_mode: settings.maintenance_mode,
        maintenance_message: settings.maintenance_message,
        estimated_return_time: settings.estimated_return_time
          ? new Date(settings.estimated_return_time).toISOString()
          : "",
      });
      setSettings(saved);
      window.dispatchEvent(new CustomEvent("maintenance-status-changed", {
        detail: {
          maintenance_mode: saved.maintenance_mode,
          maintenance_message: saved.maintenance_message,
          estimated_return_time: saved.estimated_return_time,
        },
      }));
      setSaveMessage("Settings saved.");
    } catch {
      setSaveMessage("Settings could not be saved. Please try again.");
    } finally {
      setSaving(false);
    }
  };

  if (authLoading || (loading && user)) {
    return (
      <div className="animate-pulse space-y-4">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-64" />
      </div>
    );
  }

  if (error) return <NetworkError onRetry={load} />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-foreground">Platform Settings</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Configure platform-wide settings
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>General Settings</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label htmlFor="platformName" className="text-sm font-medium text-foreground">Platform Name</label>
            <input
              id="platformName"
              type="text"
              value={settings?.platform_name || ""}
              onChange={(e) =>
                setSettings((s) => (s ? { ...s, platform_name: e.target.value } : null))
              }
              className="flex h-10 w-full rounded-md border border-[var(--color-section-border)] bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)]"
            />
          </div>
          <div className="flex items-center justify-between">
            <label htmlFor="enrollmentEnabled" className="text-sm font-medium text-foreground">Enrollment Enabled</label>
            <input
              id="enrollmentEnabled"
              type="checkbox"
              checked={settings?.enrollment_enabled ?? true}
              onChange={(e) =>
                setSettings((s) => (s ? { ...s, enrollment_enabled: e.target.checked } : null))
              }
              className="h-4 w-4"
            />
          </div>
          <div className="space-y-4 rounded-md border border-[var(--color-section-border)] bg-muted/30 p-4">
            <div className="flex items-center justify-between">
              <div>
                <label htmlFor="maintenanceMode" className="text-sm font-medium text-foreground">
                  Maintenance Mode
                </label>
                <p className="mt-1 text-xs text-muted-foreground">
                  Only authenticated Super Admins can bypass this mode.
                </p>
              </div>
              <input
                id="maintenanceMode"
                type="checkbox"
                checked={settings?.maintenance_mode ?? false}
                onChange={(e) =>
                  setSettings((s) => (s ? { ...s, maintenance_mode: e.target.checked } : null))
                }
                className="h-4 w-4"
              />
            </div>
            <div className="space-y-2">
              <label htmlFor="maintenanceMessage" className="text-sm font-medium text-foreground">
                Maintenance announcement
              </label>
              <textarea
                id="maintenanceMessage"
                rows={2}
                value={settings?.maintenance_message || ""}
                onChange={(e) =>
                  setSettings((s) => (s ? { ...s, maintenance_message: e.target.value } : null))
                }
                placeholder="We are making improvements and will be back shortly."
                className="flex w-full rounded-md border border-[var(--color-section-border)] bg-background px-3 py-2 text-sm text-foreground"
              />
            </div>
            <div className="space-y-2">
              <label htmlFor="estimatedReturnTime" className="text-sm font-medium text-foreground">
                Estimated return time
              </label>
              <input
                id="estimatedReturnTime"
                type="datetime-local"
                value={settings?.estimated_return_time ? settings.estimated_return_time.slice(0, 16) : ""}
                onChange={(e) =>
                  setSettings((s) => (s ? { ...s, estimated_return_time: e.target.value } : null))
                }
                className="flex h-10 w-full rounded-md border border-[var(--color-section-border)] bg-background px-3 py-2 text-sm text-foreground"
              />
            </div>
          </div>
          <div className="flex items-center gap-4">
            <Button onClick={handleSave} disabled={saving}>
              {saving ? "Saving..." : "Save Settings"}
            </Button>
            {saveMessage && <p role="status" className="text-sm text-muted-foreground">{saveMessage}</p>}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}