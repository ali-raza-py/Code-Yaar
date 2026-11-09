"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { Plus, Edit, Trash2, Award } from "lucide-react";
import { adminApi } from "@/lib/admin-api";
import type { AchievementAdmin, AdminPaginatedResponse } from "@/lib/admin-api";
import { useAuth } from "@/hooks/use-auth";
import { NetworkError } from "@/components/learning/workspace/error-states";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

export default function AdminAchievementsPage() {
  const { user, loading: authLoading } = useAuth();
  const [achievements, setAchievements] = useState<AchievementAdmin[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const load = useCallback(async () => {
    if (!user) return;
    try {
      const data = await adminApi.listAchievements({ page_size: 100 });
      setAchievements(data.results);
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

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this achievement?")) return;
    try {
      await adminApi.deleteAchievement(id);
      await load();
    } catch (e) {
      console.error(e);
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
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">Achievements</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Manage badges and achievement definitions
          </p>
        </div>
        <Link href="/admin/achievements/create">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Create Achievement
          </Button>
        </Link>
      </div>

      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[var(--color-section-border)]">
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Title</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Category</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Difficulty</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">XP Bonus</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Earned</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Status</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--color-section-border)]">
                {achievements.map((ach) => (
                  <tr key={ach.id} className="hover:bg-[var(--color-section-light)]">
                    <td className="px-4 py-3 font-medium">{ach.title}</td>
                    <td className="px-4 py-3">
                      <Badge variant="outline">{ach.category}</Badge>
                    </td>
                    <td className="px-4 py-3">{ach.difficulty}</td>
                    <td className="px-4 py-3">{ach.xp_bonus}</td>
                    <td className="px-4 py-3">{ach.earned_count}</td>
                    <td className="px-4 py-3">
                      <Badge variant={ach.is_active ? "default" : "secondary"}>
                        {ach.is_active ? "Active" : "Inactive"}
                      </Badge>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <Link href={`/admin/achievements/${ach.id}`}>
                          <Button variant="ghost" size="sm">
                            <Edit className="h-4 w-4" />
                          </Button>
                        </Link>
                        <Button variant="ghost" size="sm" onClick={() => handleDelete(ach.id)}>
                          <Trash2 className="h-4 w-4 text-red-500" />
                        </Button>
                      </div>
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