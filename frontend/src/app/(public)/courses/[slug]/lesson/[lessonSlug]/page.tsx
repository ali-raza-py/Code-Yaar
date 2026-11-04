'use client';

import { useCallback, useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { ArrowRight, BookOpen, Lock } from 'lucide-react';
import { ApiError, courses as coursesApi } from '@/lib/api';
import type { LessonDetail } from '@/types';
import { useAuth } from '@/hooks/use-auth';
import LessonContent from '@/components/learning/workspace/lesson-content';
import { NetworkError, NotFoundError } from '@/components/learning/workspace/error-states';

/**
 * PUBLIC read-only lesson preview. The lesson API already answers anonymous
 * reads, so "Preview first lesson" is finally honest: visitors read real
 * curriculum content here — statically rendered, with no editor, no code
 * execution and no progress tracking. Those belong to the workspace, behind
 * sign-up. Only lessons an educator flagged as `is_free_preview` (or any
 * lesson for a signed-in student) render in full; everyone else gets a
 * clear locked state instead of a broken promise.
 */

export default function LessonPreviewPage() {
  const params = useParams<{ slug: string; lessonSlug: string }>();
  const { isAuthenticated } = useAuth();

  const [lesson, setLesson] = useState<LessonDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<'network' | 'not_found' | null>(null);

  const load = useCallback(async () => {
    try {
      const data = await coursesApi.lessonDetail(params.slug, params.lessonSlug);
      setLesson(data);
      setError(null);
    } catch (reason) {
      if (reason instanceof ApiError && reason.status === 404) setError('not_found');
      else setError('network');
    } finally {
      setLoading(false);
    }
  }, [params.slug, params.lessonSlug]);

  useEffect(() => {
    // Deferred via await so the effect never sets state synchronously.
    (async () => { await load(); })();
  }, [load]);

  if (loading) {
    return (
      <div className="mx-auto max-w-2xl animate-pulse px-4 py-10 sm:px-6 lg:px-8">
        <div className="h-4 w-32 rounded bg-muted" />
        <div className="mt-4 h-10 w-2/3 rounded bg-muted" />
        <div className="mt-6 h-6 w-full rounded bg-muted" />
        <div className="mt-3 h-6 w-5/6 rounded bg-muted" />
        <div className="mt-3 h-6 w-4/6 rounded bg-muted" />
      </div>
    );
  }
  if (error === 'not_found' || !lesson) return <NotFoundError resource="Lesson" />;
  if (error === 'network') return <NetworkError onRetry={load} />;

  const previewHref = `/courses/${params.slug}/lesson/${params.lessonSlug}`;
  const joinHref = `/sign-up?next=${encodeURIComponent(previewHref)}`;
  // Educators flag preview lessons; signed-in students can read any lesson.
  const readable = isAuthenticated || lesson.is_free_preview;

  return (
    <div className="min-h-full bg-background">
      <div className="border-b border-border bg-card">
        <div className="mx-auto flex max-w-2xl items-center justify-between gap-4 px-4 py-4 sm:px-6">
          <nav className="flex min-w-0 items-center gap-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            <Link href="/courses" className="rounded hover:text-foreground">Courses</Link>
            <span aria-hidden="true">/</span>
            <Link href={`/courses/${params.slug}`} className="rounded truncate hover:text-foreground">{lesson.course_title}</Link>
            <span aria-hidden="true">/</span>
            <span className="text-foreground">Preview</span>
          </nav>
          <span className="hidden shrink-0 items-center gap-1.5 text-xs font-semibold text-muted-foreground sm:inline-flex">
            <BookOpen aria-hidden="true" className="h-3.5 w-3.5" />
            Free lesson preview
          </span>
        </div>
      </div>

      {readable ? (
        <>
          {/* No sandbox callback on purpose: preview code blocks render
              statically — we never advertise execution that isn't wired up
              for this audience. */}
          <LessonContent lesson={lesson} />

          <div className="mx-auto max-w-2xl px-4 pb-12 sm:px-6">
            <div className="rounded-card border border-primary/25 bg-primary/[0.04] p-6">
              <h2 className="text-lg font-bold text-foreground">
                {isAuthenticated ? 'Keep going in your workspace' : `Want the rest of ${lesson.course_title}?`}
              </h2>
              <p className="mt-2 text-sm text-muted-foreground">
                {lesson.exercise_count > 0
                  ? `This course continues with ${lesson.exercise_count} hands-on exercise${lesson.exercise_count === 1 ? '' : 's'} in this lesson alone, plus graded progress, XP and a certificate on completion.`
                  : 'Continue with the full course: every lesson, hands-on practice, graded progress and a certificate on completion.'}
              </p>
              <div className="mt-4 flex flex-wrap items-center gap-3">
                {isAuthenticated ? (
                  <Link
                    href={`/learn/${params.slug}?lesson=${params.lessonSlug}`}
                    className="inline-flex h-10 items-center gap-2 rounded-lg bg-cta px-4 text-sm font-semibold text-cta-fg transition-colors hover:bg-cta-hover"
                  >
                    Open the lesson workspace <ArrowRight aria-hidden="true" className="h-4 w-4" />
                  </Link>
                ) : (
                  <Link
                    href={joinHref}
                    className="inline-flex h-10 items-center gap-2 rounded-lg bg-cta px-4 text-sm font-semibold text-cta-fg transition-colors hover:bg-cta-hover"
                  >
                    Create a free account to continue <ArrowRight aria-hidden="true" className="h-4 w-4" />
                  </Link>
                )}
                <Link
                  href={`/courses/${params.slug}`}
                  className="inline-flex h-10 items-center rounded-lg border border-border px-4 text-sm font-semibold text-foreground transition-colors hover:bg-muted"
                >
                  Back to course
                </Link>
              </div>
            </div>
          </div>
        </>
      ) : (
        <div className="mx-auto max-w-2xl px-4 py-16 sm:px-6">
          <div className="rounded-card border border-border bg-card p-8 text-center">
            <span className="mx-auto grid h-12 w-12 place-items-center rounded-full bg-muted">
              <Lock aria-hidden="true" className="h-6 w-6 text-muted-foreground" />
            </span>
            <h1 className="mt-5 text-xl font-bold text-foreground">{lesson.title}</h1>
            <p className="mt-2 text-sm text-muted-foreground">
              This lesson isn&apos;t part of the free preview set for this course. Create a
              free account to unlock every lesson, exercise and assessment.
            </p>
            <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
              <Link
                href={joinHref}
                className="inline-flex h-10 items-center gap-2 rounded-lg bg-cta px-4 text-sm font-semibold text-cta-fg transition-colors hover:bg-cta-hover"
              >
                Get started free <ArrowRight aria-hidden="true" className="h-4 w-4" />
              </Link>
              <Link
                href={`/courses/${params.slug}`}
                className="inline-flex h-10 items-center rounded-lg border border-border px-4 text-sm font-semibold text-foreground transition-colors hover:bg-muted"
              >
                Back to course
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
