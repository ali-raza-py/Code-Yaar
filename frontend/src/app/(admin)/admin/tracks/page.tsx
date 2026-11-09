"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { Plus, Edit, Trash2, Eye, EyeOff, ArrowUp, ArrowDown } from "lucide-react";
import { adminApi } from "@/lib/admin-api";
import type { CareerTrackAdmin, AdminPaginatedResponse } from "@/lib/admin-api";
import { useAuth } from "@/hooks/use-auth";
import { NetworkError } from "@/components/learning/workspace/error-states";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

export default function AdminTracksPage() {
  const { user, loading: authLoading } = useAuth();
  const [tracks, setTracks] = useState<CareerTrackAdmin[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const load = useCallback(async () => {
    if (!user) return;
    try {
      const data = await adminApi.listTracks({ page_size: 100 });
      setTracks(data.results);
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

  const handlePublish = async (id: number) => {
    try {
      await adminApi.publishTrack(id);
      await load();
    } catch (e) {
      console.error(e);
    }
  };

  const handleUnpublish = async (id: number) => {
    try {
      await adminApi.unpublishTrack(id);
      await load();
    } catch (e) {
      console.error(e);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this track?")) return;
    try {
      await adminApi.deleteTrack(id);
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
          <h1 className="text-3xl font-bold tracking-tight text-foreground">Learning Tracks</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Manage learning tracks, categories, and publication status
          </p>
        </div>
        <Link href="/admin/tracks/create">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Create Track
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
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Courses</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Status</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--color-section-border)]">
                {tracks.map((track) => (
                  <tr key={track.id} className="hover:bg-[var(--color-section-light)]">
                    <td className="px-4 py-3 font-medium">{track.title}</td>
                    <td className="px-4 py-3">
                      <Badge variant="outline">{track.category}</Badge>
                    </td>
                    <td className="px-4 py-3">{track.difficulty}</td>
                    <td className="px-4 py-3">
                      {track.published_courses_count} / {track.courses_count}
                    </td>
                    <td className="px-4 py-3">
                      <Badge variant={track.is_published ? "default" : "secondary"}>
                        {track.is_published ? "Published" : "Draft"}
                      </Badge>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <Link href={`/admin/tracks/${track.id}`}>
                          <Button variant="ghost" size="sm">
                            <Edit className="h-4 w-4" />
                          </Button>
                        </Link>
                        {track.is_published ? (
                          <Button variant="ghost" size="sm" onClick={() => handleUnpublish(track.id)}>
                            <EyeOff className="h-4 w-4" />
                          </Button>
                        ) : (
                          <Button variant="ghost" size="sm" onClick={() => handlePublish(track.id)}>
                            <Eye className="h-4 w-4" />
                          </Button>
                        )}
                        <Button variant="ghost" size="sm" onClick={() => handleDelete(track.id)}>
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