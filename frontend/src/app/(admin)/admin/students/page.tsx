"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { Search, Users } from "lucide-react";
import { adminApi } from "@/lib/admin-api";
import type { StudentAdmin, AdminPaginatedResponse } from "@/lib/admin-api";
import { useAuth } from "@/hooks/use-auth";
import { NetworkError } from "@/components/learning/workspace/error-states";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

export default function AdminStudentsPage() {
  const { user, loading: authLoading } = useAuth();
  const [students, setStudents] = useState<StudentAdmin[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);

  const load = useCallback(async () => {
    if (!user) return;
    try {
      const data = await adminApi.listStudents({ search, page, page_size: 20 });
      setStudents(data.results);
      setError(false);
    } catch {
      setError(true);
    } finally {
      setLoading(false);
    }
  }, [user, search, page]);

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
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">Students</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Manage student accounts and view learning progress
          </p>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <input
            placeholder="Search students..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="flex h-10 w-full rounded-md border border-[var(--color-section-border)] bg-background pl-9 pr-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)]"
          />
        </div>
      </div>

      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[var(--color-section-border)]">
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Name</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Email</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">XP</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Level</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Enrollments</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Completed</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--color-section-border)]">
                {students.map((student) => (
                  <tr key={student.id} className="hover:bg-[var(--color-section-light)]">
                    <td className="px-4 py-3 font-medium">{student.full_name || student.username}</td>
                    <td className="px-4 py-3 text-muted-foreground">{student.email}</td>
                    <td className="px-4 py-3">{student.xp_points.toLocaleString()}</td>
                    <td className="px-4 py-3">{student.level}</td>
                    <td className="px-4 py-3">{student.enrollment_count}</td>
                    <td className="px-4 py-3">{student.completed_courses}</td>
                    <td className="px-4 py-3">
                      <Link href={`/admin/students/${student.id}`}>
                        <Button variant="ghost" size="sm">
                          <Users className="h-4 w-4" />
                        </Button>
                      </Link>
                    </td>
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