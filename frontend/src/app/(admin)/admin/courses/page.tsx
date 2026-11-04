"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { Plus, Edit, Trash2, Eye, EyeOff, BookOpen } from "lucide-react";
import { adminApi } from "@/lib/admin-api";
import type { CourseAdmin, AdminPaginatedResponse } from "@/lib/admin-api";
import { useAuth } from "@/hooks/use-auth";
import { NetworkError } from "@/components/learning/workspace/error-states";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

export default function AdminCoursesPage() {
  const { user, loading: authLoading } = useAuth();
  const [courses, setCourses] = useState<CourseAdmin[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const load = useCallback(async () => {
    if (!user) return;
    try {
      const data = await adminApi.listCourses({ page_size: 100 });
      setCourses(data.results);
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
      await adminApi.publishCourse(id);
      await load();
    } catch (e) {
      console.error(e);
    }
  };

  const handleUnpublish = async (id: number) => {
    try {
      await adminApi.unpublishCourse(id);
      await load();
    } catch (e) {
      console.error(e);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this course?")) return;
    try {
      await adminApi.deleteCourse(id);
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
          <h1 className="text-3xl font-bold tracking-tight text-foreground">Courses</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Manage courses, chapters, lessons, and publication status
          </p>
        </div>
        <Link href="/admin/courses/create">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Create Course
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
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Track</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Difficulty</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Language</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Chapters</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Enrollments</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Status</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--color-section-border)]">
                {courses.map((course) => (
                  <tr key={course.id} className="hover:bg-[var(--color-section-light)]">
                    <td className="px-4 py-3 font-medium">{course.title}</td>
                    <td className="px-4 py-3 text-muted-foreground">{course.track_title}</td>
                    <td className="px-4 py-3">{course.difficulty}</td>
                    <td className="px-4 py-3">{course.language}</td>
                    <td className="px-4 py-3">{course.chapter_count}</td>
                    <td className="px-4 py-3">{course.enrollment_count}</td>
                    <td className="px-4 py-3">
                      <Badge variant={course.is_published ? "default" : "secondary"}>
                        {course.is_published ? "Published" : "Draft"}
                      </Badge>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <Link href={`/admin/courses/${course.id}`}>
                          <Button variant="ghost" size="sm">
                            <Edit className="h-4 w-4" />
                          </Button>
                        </Link>
                        {course.is_published ? (
                          <Button variant="ghost" size="sm" onClick={() => handleUnpublish(course.id)}>
                            <EyeOff className="h-4 w-4" />
                          </Button>
                        ) : (
                          <Button variant="ghost" size="sm" onClick={() => handlePublish(course.id)}>
                            <Eye className="h-4 w-4" />
                          </Button>
                        )}
                        <Button variant="ghost" size="sm" onClick={() => handleDelete(course.id)}>
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