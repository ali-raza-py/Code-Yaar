"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { Plus, Edit, Trash2, ListTodo } from "lucide-react";
import { adminApi } from "@/lib/admin-api";
import type { ExerciseAdmin, AdminPaginatedResponse } from "@/lib/admin-api";
import { useAuth } from "@/hooks/use-auth";
import { NetworkError } from "@/components/learning/workspace/error-states";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

export default function AdminExercisesPage() {
  const { user, loading: authLoading } = useAuth();
  const [exercises, setExercises] = useState<ExerciseAdmin[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const load = useCallback(async () => {
    if (!user) return;
    try {
      const data = await adminApi.listExercises({ page_size: 100 });
      setExercises(data.results);
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
    if (!confirm("Are you sure you want to delete this exercise?")) return;
    try {
      await adminApi.deleteExercise(id);
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
          <h1 className="text-3xl font-bold tracking-tight text-foreground">Exercises & Quizzes</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Manage exercises, quizzes, and assessments
          </p>
        </div>
        <Link href="/admin/exercises/create">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Create Exercise
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
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Type</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Lesson</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Course</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Difficulty</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">XP</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Status</th>
                  <th className="text-left px-4 py-3 font-medium text-muted-foreground">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--color-section-border)]">
                {exercises.map((exercise) => (
                  <tr key={exercise.id} className="hover:bg-[var(--color-section-light)]">
                    <td className="px-4 py-3 font-medium">{exercise.title}</td>
                    <td className="px-4 py-3">
                      <Badge variant="outline">{exercise.exercise_type}</Badge>
                    </td>
                    <td className="px-4 py-3 text-muted-foreground">{exercise.lesson_title}</td>
                    <td className="px-4 py-3 text-muted-foreground">{exercise.course_title}</td>
                    <td className="px-4 py-3">{exercise.difficulty}</td>
                    <td className="px-4 py-3">{exercise.xp_reward}</td>
                    <td className="px-4 py-3">
                      <Badge variant={exercise.is_active ? "default" : "secondary"}>
                        {exercise.is_active ? "Active" : "Inactive"}
                      </Badge>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <Link href={`/admin/exercises/${exercise.id}`}>
                          <Button variant="ghost" size="sm">
                            <Edit className="h-4 w-4" />
                          </Button>
                        </Link>
                        <Button variant="ghost" size="sm" onClick={() => handleDelete(exercise.id)}>
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