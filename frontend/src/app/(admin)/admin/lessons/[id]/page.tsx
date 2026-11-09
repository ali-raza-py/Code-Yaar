"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, Loader2, Save, Trash2 } from "lucide-react";
import Link from "next/link";
import { adminApi } from "@/lib/admin-api";
import type { ChapterAdmin, LessonAdmin, StudioLesson } from "@/lib/admin-api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { StudioError } from "@/components/admin/studio/studio-fields";
import { Skeleton } from "@/components/ui/skeleton";
import LessonEditor from "@/components/admin/studio/lesson-editor";

export default function LessonDetailPage() {
  const params = useParams();
  const router = useRouter();
  const lessonId = Number(params.id);

  const [lesson, setLesson] = useState<LessonAdmin | null>(null);
  const [chapters, setChapters] = useState<ChapterAdmin[]>([]);
  const [chapterLessons, setChapterLessons] = useState<StudioLesson[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [lessonData, chaptersData] = await Promise.all([
        adminApi.getLesson(lessonId),
        adminApi.listChapters({ page_size: 100 }),
      ]);
      setLesson(lessonData);
      setChapters((chaptersData.results || []));
      if (lessonData.chapter) {
        const chapterLessonsData = await adminApi.listLessons({
          page_size: 100,
          chapter: lessonData.chapter,
        });
        setChapterLessons((chapterLessonsData.results || []).map((l) => ({
          id: l.id,
          slug: l.slug,
          title: l.title,
          content_type: l.content_type,
          learning_objective: l.learning_objective,
          content_body: l.content_body,
          video_url: l.video_url,
          order: l.order,
          duration_minutes: l.duration_minutes,
          xp_reward: l.xp_reward,
          is_active: l.is_active,
          is_required: true,
          prerequisite: null,
          estimated_reading_minutes: 0,
          instructor_notes: "",
          exercise_count: l.exercise_count,
          exercises: [],
          updated_at: l.updated_at,
        })));
      }
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not load lesson.");
    } finally {
      setLoading(false);
    }
  }, [lessonId]);

  useEffect(() => {
    load();
  }, [load]);

  const handleSaved = useCallback((saved: StudioLesson) => {
    if (lesson) {
      setLesson({
        ...lesson,
        title: saved.title,
        content_body: saved.content_body,
        learning_objective: saved.learning_objective,
        order: saved.order,
        duration_minutes: saved.duration_minutes,
        xp_reward: saved.xp_reward,
        is_active: saved.is_active,
        updated_at: saved.updated_at,
      });
    }
  }, [lesson]);

  if (loading) {
    return (
      <div className="animate-pulse space-y-6">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-96" />
      </div>
    );
  }

  if (!lesson) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
        <p className="text-center text-destructive">Lesson not found</p>
        <Link href="/admin/lessons"><Button variant="outline">Back to lessons</Button></Link>
      </div>
    );
  }

  const chapter = chapters.find((c) => c.id === lesson.chapter);
  const courseTitle = chapter?.course_title || "Course";
  const chapterTitle = chapter?.title || "Chapter";

  const studioLesson: StudioLesson = {
    id: lesson.id,
    slug: lesson.slug,
    title: lesson.title,
    content_type: lesson.content_type,
    learning_objective: lesson.learning_objective,
    content_body: lesson.content_body,
    video_url: lesson.video_url,
    order: lesson.order,
    duration_minutes: lesson.duration_minutes,
    xp_reward: lesson.xp_reward,
    is_active: lesson.is_active,
    is_required: true,
    prerequisite: null,
    estimated_reading_minutes: 0,
    instructor_notes: "",
    exercise_count: lesson.exercise_count,
    exercises: [],
    updated_at: lesson.updated_at,
  };

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      {/* Breadcrumb */}
      <nav className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
        <Link href="/admin/courses">Admin</Link>
        <span aria-hidden="true">/</span>
        <Link href={`/admin/courses/${chapter?.course}`}>{courseTitle}</Link>
        <span aria-hidden="true">/</span>
        <Link href={`/admin/chapters/${lesson.chapter}`}>{chapterTitle}</Link>
        <span aria-hidden="true">/</span>
        <span className="text-foreground">{lesson.title}</span>
      </nav>

      <div className="flex items-center gap-4">
        <Link href="/admin/lessons"><Button variant="ghost" size="icon"><ArrowLeft className="h-4 w-4" /></Button></Link>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Edit Lesson</h1>
          <p className="mt-1 text-sm text-muted-foreground">Lesson ID: {lesson.id}</p>
        </div>
      </div>

      {error && <StudioError message={error} />}

      <Card>
        <CardContent>
          <LessonEditor
            courseId={chapter?.course ?? 0}
            lesson={studioLesson}
            chapterLessons={chapterLessons}
            onSaved={handleSaved}
            onClose={() => router.replace("/admin/lessons")}
          />
        </CardContent>
      </Card>
    </div>
  );
}
