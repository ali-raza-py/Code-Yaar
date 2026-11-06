"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, Loader2, Plus, Save, Trash2 } from "lucide-react";
import Link from "next/link";
import { adminApi } from "@/lib/admin-api";
import type { ChapterAdmin, CourseAdmin, LessonAdmin } from "@/lib/admin-api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input, Label, StudioError, StudioField, Textarea } from "@/components/admin/studio/studio-fields";
import { Skeleton } from "@/components/ui/skeleton";

export default function ChapterDetailPage() {
  const params = useParams();
  const router = useRouter();
  const chapterId = Number(params.id);

  const [chapter, setChapter] = useState<ChapterAdmin | null>(null);
  const [courses, setCourses] = useState<CourseAdmin[]>([]);
  const [lessons, setLessons] = useState<LessonAdmin[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [form, setForm] = useState({
    title: "",
    description: "",
    course: "",
    order: 1,
    xp_reward: 0,
    is_active: true,
  });
  const [creatingLesson, setCreatingLesson] = useState(false);
  const [lessonTitle, setLessonTitle] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [chapterData, coursesData] = await Promise.all([
        adminApi.getChapter(chapterId),
        adminApi.listCourses({ page_size: 100 }),
      ]);
      setChapter(chapterData);
      setCourses(coursesData.results);
      if (chapterData.course) {
        const lessonsData = await adminApi.listLessons({ page_size: 100, course: chapterData.course });
        setLessons((lessonsData.results || []).sort((a, b) => a.order - b.order));
      }
      setForm({
        title: chapterData.title,
        description: chapterData.description,
        course: String(chapterData.course),
        order: chapterData.order,
        xp_reward: chapterData.xp_reward,
        is_active: chapterData.is_active,
      });
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not load chapter.");
    } finally {
      setLoading(false);
    }
  }, [chapterId]);

  useEffect(() => {
    load();
  }, [load]);

  const update = (key: string, value: string | number | boolean) =>
    setForm((current) => ({ ...current, [key]: value }));

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setError("");
    try {
      await adminApi.updateChapter(chapterId, {
        title: form.title.trim(),
        description: form.description.trim(),
        course: Number(form.course),
        order: Number(form.order) || 1,
        xp_reward: Number(form.xp_reward) || 0,
        is_active: form.is_active,
      });
      router.replace("/admin/chapters");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Chapter could not be updated.");
      setSaving(false);
    }
  }

  async function handleCreateLesson() {
    if (!lessonTitle.trim()) return;
    if (!chapter) return;
    setSaving(true);
    setError("");
    try {
      await adminApi.studioCreateLesson(courseId, {
        chapter: chapter.id,
        title: lessonTitle.trim(),
        content_body: "# Introduction\n\nStart writing here...",
        learning_objective: "Understand the key concepts.",
        is_active: false,
        order: lessons.length + 1,
        duration_minutes: 10,
      });
      setCreatingLesson(false);
      setLessonTitle("");
      await load();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not create lesson.");
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete() {
    if (!confirm("Are you sure you want to delete this chapter?")) return;
    setSaving(true);
    try {
      await adminApi.deleteChapter(chapterId);
      router.replace("/admin/chapters");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not delete chapter.");
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="animate-pulse space-y-6">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-96" />
      </div>
    );
  }

  if (!chapter) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
        <p className="text-center text-destructive">Chapter not found</p>
        <Link href="/admin/chapters"><Button variant="outline">Back to chapters</Button></Link>
      </div>
    );
  }

  const courseTitle = chapter.course_title || "Course";
  const courseId = chapter.course;

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      {/* Breadcrumb */}
      <nav className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
        <Link href="/admin/courses">Admin</Link>
        <span aria-hidden="true">/</span>
        <Link href={`/admin/courses/${courseId}`}>{courseTitle}</Link>
        <span aria-hidden="true">/</span>
        <span className="text-foreground">{chapter.title}</span>
      </nav>

      <div className="flex items-center gap-4">
        <Link href="/admin/chapters"><Button variant="ghost" size="icon"><ArrowLeft className="h-4 w-4" /></Button></Link>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Edit Chapter</h1>
          <p className="mt-1 text-sm text-muted-foreground">Chapter ID: {chapter.id}</p>
        </div>
      </div>

      {error && <StudioError message={error} />}

      <Card>
        <CardHeader>
          <CardTitle>Chapter Details</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={submit} className="space-y-5">
            <StudioField label="Title" htmlFor="chapter-title" required>
              <Input id="chapter-title" value={form.title} onChange={(e) => update("title", e.target.value)} required />
            </StudioField>

            <StudioField label="Course" htmlFor="chapter-course" required>
              <select
                id="chapter-course"
                className="mt-1 w-full rounded-md border border-input bg-background px-3 py-2"
                value={form.course}
                onChange={(e) => update("course", e.target.value)}
                required
              >
                <option value="">Select a course</option>
                {courses.map((course) => (
                  <option key={course.id} value={course.id}>{course.title}</option>
                ))}
              </select>
            </StudioField>

            <StudioField label="Description" htmlFor="chapter-description">
              <Textarea id="chapter-description" value={form.description} onChange={(e) => update("description", e.target.value)} rows={4} required />
            </StudioField>

            <div className="grid gap-4 sm:grid-cols-2">
              <StudioField label="Order" htmlFor="chapter-order">
                <Input id="chapter-order" type="number" min="1" value={form.order} onChange={(e) => update("order", Number(e.target.value))} />
              </StudioField>
              <StudioField label="XP Reward" htmlFor="chapter-xp">
                <Input id="chapter-xp" type="number" min="0" value={form.xp_reward} onChange={(e) => update("xp_reward", Number(e.target.value))} />
              </StudioField>
            </div>

            <StudioField label="Status" htmlFor="chapter-active">
              <label className="flex items-center gap-2">
                <input
                  id="chapter-active"
                  type="checkbox"
                  checked={form.is_active}
                  onChange={(e) => update("is_active", e.target.checked)}
                  className="h-4 w-4 rounded border-input"
                />
                <span>Active (visible to learners)</span>
              </label>
            </StudioField>

            {error && <StudioError message={error} />}

            <div className="flex justify-end gap-3 pt-4 border-t">
              <Button type="button" variant="outline" onClick={() => router.back()}>Cancel</Button>
              <Button type="submit" disabled={saving}>{saving ? "Saving..." : "Save changes"}</Button>
              <Button type="button" variant="destructive" onClick={handleDelete} disabled={saving}>Delete</Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Lessons */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            Lessons
            {creatingLesson ? (
              <div className="flex items-center gap-2">
                <Input
                  id="lesson-title-input"
                  value={lessonTitle}
                  onChange={(e) => setLessonTitle(e.target.value)}
                  placeholder="Lesson title"
                  className="w-48 text-sm"
                />
                <Button size="sm" onClick={handleCreateLesson} disabled={saving || !lessonTitle.trim()}>
                  <Plus className="mr-1 h-4 w-4" /> Add
                </Button>
                <Button variant="outline" size="sm" onClick={() => setCreatingLesson(false)}>Cancel</Button>
              </div>
            ) : (
              <Button size="sm" onClick={() => setCreatingLesson(true)}>
                <Plus className="mr-1 h-4 w-4" /> Add lesson
              </Button>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {lessons.length === 0 ? (
            <p className="px-4 py-8 text-center text-sm text-muted-foreground">
              No lessons yet. Add one to start building this chapter.
            </p>
          ) : (
            <div className="space-y-2">
              {lessons.map((lesson) => (
                <div key={lesson.id} className="flex items-center gap-3 px-3 py-2 rounded-md border border-border/50 hover:bg-muted/50">
                  <span className="text-xs text-muted-foreground w-8">#{lesson.order}</span>
                  <Link
                    href={`/admin/lessons/${lesson.id}`}
                    className="truncate flex-1 text-sm font-medium hover:underline"
                  >
                    {lesson.title}
                  </Link>
                  <span className="text-xs text-muted-foreground">{lesson.duration_minutes} min</span>
                  <span className="text-xs text-muted-foreground">{lesson.xp_reward} XP</span>
                  {!lesson.is_active && <span className="text-xs text-muted-foreground">draft</span>}
                  <span className="ml-auto text-xs text-muted-foreground">{lesson.exercise_count} exercises</span>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
