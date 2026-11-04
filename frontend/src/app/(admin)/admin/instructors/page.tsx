"use client";

import { useCallback, useEffect, useState } from "react";
import { adminApi } from "@/lib/admin-api";
import type { InstructorAdmin, AdminPaginatedResponse } from "@/lib/admin-api";
import { useAuth } from "@/hooks/use-auth";
import { NetworkError } from "@/components/learning/workspace/error-states";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

export default function AdminInstructorsPage() {
  const { user, loading: authLoading } = useAuth();
  const [instructors, setInstructors] = useState<InstructorAdmin[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const load = useCallback(async () => {
    if (!user) return;
    try {
      const data = await adminApi.listInstructors({ page_size: 100 });
      setInstructors(data.results);
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
        <h1 className="text-3xl font-bold tracking-tight text-foreground">Instructors</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Manage instructors and their course assignments
        </p>
      </div>

      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[var(--color-section-border)]">
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Name</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Email</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Institution</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Assigned Courses</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--color-section-border)]">
                {instructors.map((instructor) => (
                  <tr key={instructor.id} className="hover:bg-[var(--color-section-light)]">
                    <td className="px-4 py-3 font-medium">
                      {instructor.full_name || instructor.username}
                    </td>
                    <td className="px-4 py-3 text-muted-foreground">{instructor.email}</td>
                    <td className="px-4 py-3 text-muted-foreground">{instructor.institution || "—"}</td>
                    <td className="px-4 py-3">{instructor.assigned_courses_count}</td>
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