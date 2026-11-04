"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { Plus, Edit, Trash2 } from "lucide-react";
import { adminApi } from "@/lib/admin-api";
import type { ChapterAdmin, AdminPaginatedResponse } from "@/lib/admin-api";
import { useAuth } from "@/hooks/use-auth";
import { NetworkError } from "@/components/learning/workspace/error-states";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

export default function AdminChaptersPage() {
  const { user, loading: authLoading } = useAuth();
  const [chapters, setChapters] = useState<ChapterAdmin[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const load = useCallback(async () => {
    if (!user) return;
    try {
      const data = await adminApi.listChapters({ page_size: 100 });
      setChapters(data.results);
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
    if (!confirm("Are you sure you want to delete this chapter?")) return;
    try {
      await adminApi.deleteChapter(id);
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
          <h1 className="text-3xl font-bold tracking-tight text-foreground">Chapters</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Manage course chapters and their content
          </p>
        </div>
        <Link href="/admin/chapters/create">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Create Chapter
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
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Course</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Order</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Lessons</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Exercises</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Status</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--color-section-border)]">
                {chapters.map((chapter) => (
                  <tr key={chapter.id} className="hover:bg-[var(--color-section-light)]">
                    <td className="px-4 py-3 font-medium">{chapter.title}</td>
                    <td className="px-4 py-3 text-muted-foreground">{chapter.course_title}</td>
                    <td className="px-4 py-3">{chapter.order}</td>
                    <td className="px-4 py-3">{chapter.lesson_count}</td>
                    <td className="px-4 py-3">{chapter.exercise_count}</td>
                    <td className="px-4 py-3">
                      <Badge variant={chapter.is_active ? "default" : "secondary"}>
                        {chapter.is_active ? "Active" : "Inactive"}
                      </Badge>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <Link href={`/admin/chapters/${chapter.id}`}>
                          <Button variant="ghost" size="sm">
                            <Edit className="h-4 w-4" />
                          </Button>
                        </Link>
                        <Button variant="ghost" size="sm" onClick={() => handleDelete(chapter.id)}>
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