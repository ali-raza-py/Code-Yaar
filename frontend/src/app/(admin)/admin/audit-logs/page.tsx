"use client";

import { useCallback, useEffect, useState } from "react";
import { adminApi } from "@/lib/admin-api";
import type { AuditLogAdmin, AdminPaginatedResponse } from "@/lib/admin-api";
import { useAuth } from "@/hooks/use-auth";
import { NetworkError } from "@/components/learning/workspace/error-states";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

export default function AdminAuditLogsPage() {
  const { user, loading: authLoading } = useAuth();
  const [logs, setLogs] = useState<AuditLogAdmin[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const load = useCallback(async () => {
    if (!user) return;
    try {
      const data = await adminApi.listAuditLogs({ page_size: 100 });
      setLogs(data.results);
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
        <h1 className="text-3xl font-bold tracking-tight text-foreground">Audit Logs</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Administrative activity trail
        </p>
      </div>

      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[var(--color-section-border)]">
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Timestamp</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Admin</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Action</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Target</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">IP</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--color-section-border)]">
                {logs.map((log) => (
                  <tr key={log.id} className="hover:bg-[var(--color-section-light)]">
                    <td className="px-4 py-3 text-muted-foreground">
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                    <td className="px-4 py-3 font-medium">{log.admin_name}</td>
                    <td className="px-4 py-3">
                      <Badge variant="outline">{log.action}</Badge>
                    </td>
                    <td className="px-4 py-3 text-muted-foreground">
                      {log.target_type} {log.target_id}
                    </td>
                    <td className="px-4 py-3 text-muted-foreground">{log.ip_address || "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}