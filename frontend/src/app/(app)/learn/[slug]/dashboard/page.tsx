'use client';

import Link from 'next/link';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { useParams } from 'next/navigation';
import { ApiError, auth, courses as coursesApi } from '@/lib/api';
import { useAuth } from '@/hooks/use-auth';
import type { Course } from '@/types';
import { NetworkError, NotFoundError } from '@/components/learning/workspace/error-states';
import CertificatePanel from '@/components/learning/certificate-panel';

export default function CourseDashboardPage() {
  const params = useParams<{ slug: string }>();
  const courseSlug = params.slug;
  const { user } = useAuth();

  const [course, setCourse] = useState<Course | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<'network' | 'not_found' | null>(null);
  const [streak, setStreak] = useState<number | null>(null);
  const [enrolling, setEnrolling] = useState(false);
  const [enrollNotice, setEnrollNotice] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const data = await coursesApi.detail(courseSlug);
      setCourse(data);
      setError(null);
    } catch (reason) {
      if (reason instanceof ApiError && reason.status === 404) setError('not_found');
      else setError('network');
    } finally {
      setLoading(false);
    }
  }, [courseSlug]);

  useEffect(() => {
    // Deferred via await so the effect never sets state synchronously.
    (async () => { await load(); })();
  }, [load]);

  useEffect(() => {
    if (!user) return;
    let cancelled = false;
    auth.getProfile()
      .then((profile) => {
        if (!cancelled) setStreak(profile.streak_days);
      })
      .catch(() => {
        if (!cancelled) setStreak(null);
      });
    return () => { cancelled = true; };
  }, [user]);

  const chapters = useMemo(() => course?.chapters ?? [], [course]);

  const lessonStats = useMemo(() => {
    const all = chapters.flatMap((ch) => ch.lessons);
    const completed = all.filter((l) => l.progress_status === 'completed' || l.progress_status === 'mastered');
    return { total: all.length, completed: completed.length };
  }, [chapters]);

  const completedChapters = useMemo(
    () => chapters.filter((ch) => ch.lessons.length > 0 && ch.progress_percentage === 100).length,
    [chapters]
  );

  const resumeTarget = course
    ? course.resume_lesson
      ? `/learn/${course.slug}?lesson=${course.resume_lesson.slug}`
      : `/learn/${course.slug}`
    : '/learn';

  const handleEnroll = async () => {
    if (!course) return;
    setEnrolling(true);
    setEnrollNotice(null);
    try {
      await coursesApi.enroll(course.slug);
      setCourse({ ...course, enrolled: true });
    } catch (reason) {
      setEnrollNotice(reason instanceof ApiError ? reason.message : 'Enrollment failed: the server could not be reached.');
    } finally {
      setEnrolling(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background p-4 sm:p-6 lg:p-8">
        <div className="mx-auto max-w-5xl animate-pulse space-y-6">
          <div className="h-8 w-64 rounded bg-muted" />
          <div className="h-40 rounded-xl bg-muted" />
          <div className="grid gap-6 lg:grid-cols-3">
            <div className="h-64 rounded-xl bg-muted lg:col-span-2" />
            <div className="h-64 rounded-xl bg-muted" />
          </div>
        </div>
      </div>
    );
  }

  if (error === 'not_found' || !course) {
    return (
      <div className="min-h-screen bg-background">
        <NotFoundError resource="Course" />
      </div>
    );
  }

  if (error === 'network') {
    return (
      <div className="min-h-screen bg-background">
        <NetworkError onRetry={load} />
      </div>
    );
  }

  const progress = course.progress_percentage ?? 0;

  return (
    <div className="min-h-screen bg-background p-4 sm:p-6 lg:p-8">
      <div className="mx-auto max-w-5xl">
        {/* Header */}
        <div className="mb-6">
          <Link href="/learn" className="mb-2 inline-block text-sm text-muted-foreground hover:text-foreground">
            ← Back to Courses
          </Link>
          <h1 className="text-2xl font-bold text-foreground">{course.title}</h1>
          <div className="mt-2 flex items-center gap-4">
            <div className="max-w-md flex-1">
              <div className="mb-1 flex items-center justify-between text-xs text-muted-foreground">
                <span>Course Progress</span>
                <span className="font-semibold text-foreground">{progress}%</span>
              </div>
              <div
                className="h-2 w-full overflow-hidden rounded-full bg-muted"
                role="progressbar"
                aria-valuenow={progress}
                aria-valuemin={0}
                aria-valuemax={100}
              >
                <div
                  className="h-full rounded-full bg-success transition-all"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
            <span className="inline-flex items-center gap-1 rounded-pill bg-cta/10 px-2.5 py-1 text-sm font-semibold text-success">
              {course.total_xp.toLocaleString()} XP available
            </span>
          </div>
        </div>

        {/* Enrollment state */}
        {!course.enrolled && (
          <div className="mb-6 rounded-xl border border-info/30 bg-info/10 p-4">
            {user ? (
              <div className="flex flex-wrap items-center justify-between gap-3">
                <p className="text-sm text-foreground">
                  You&apos;re not enrolled in this course yet. Enroll to track your progress and earn XP.
                </p>
                <button
                  onClick={handleEnroll}
                  disabled={enrolling}
                  className="focus-ring inline-flex min-h-9 items-center rounded-lg bg-cta px-4 py-2 text-sm font-semibold text-white hover:bg-cta-hover disabled:opacity-50"
                >
                  {enrolling ? 'Enrolling…' : 'Enroll'}
                </button>
              </div>
            ) : (
              <div className="flex flex-wrap items-center justify-between gap-3">
                <p className="text-sm text-foreground">Sign in to enroll and track your progress.</p>
                <Link
                  href="/sign-in"
                  className="focus-ring inline-flex min-h-9 items-center rounded-lg bg-cta px-4 py-2 text-sm font-semibold text-white hover:bg-cta-hover"
                >
                  Sign in
                </Link>
              </div>
            )}
            {enrollNotice && <p role="alert" className="mt-2 text-sm text-danger">{enrollNotice}</p>}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Column */}
          <div className="lg:col-span-2 space-y-6">
            {/* Continue Learning */}
            <div className="rounded-xl border border-border bg-gradient-to-br from-hero-bg to-hero-bg-alt p-6 text-white">
              <p className="text-xs font-medium uppercase tracking-wider text-white/60 mb-1">
                {course.resume_lesson ? 'Continue Learning' : 'Start Learning'}
              </p>
              {course.resume_lesson ? (
                <>
                  <h2 className="mb-1 text-xl font-bold">{course.resume_lesson.title}</h2>
                  <p className="mb-4 text-sm text-white/70">
                    {lessonStats.completed}/{lessonStats.total} lessons completed
                  </p>
                </>
              ) : (
                <>
                  <h2 className="mb-1 text-xl font-bold">
                    {lessonStats.total > 0 ? 'Ready to begin' : 'No lessons published yet'}
                  </h2>
                  <p className="mb-4 text-sm text-white/70">
                    {lessonStats.total > 0
                      ? 'Jump into the first lesson of this course.'
                      : 'This course is still being authored. Check back soon.'}
                  </p>
                </>
              )}
              {lessonStats.total > 0 && (
                <Link
                  href={resumeTarget}
                  className="focus-ring inline-flex min-h-9 items-center rounded-lg bg-cta px-5 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-cta-hover"
                >
                  {progress > 0 ? 'Continue' : 'Start course'}
                  <svg className="ml-2 h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
                  </svg>
                </Link>
              )}
            </div>

            {/* Course Map */}
            <div className="rounded-xl border border-border bg-white p-6">
              <h3 className="mb-4 text-base font-semibold text-foreground">Course Map</h3>
              {chapters.length === 0 ? (
                <p className="text-sm text-muted-foreground">No chapters have been published for this course yet.</p>
              ) : (
                <div className="space-y-3">
                  {chapters.map((ch) => {
                    const completed = ch.lessons.filter(
                      (l) => l.progress_status === 'completed' || l.progress_status === 'mastered'
                    ).length;
                    return (
                      <div key={ch.id} className="flex items-center gap-4">
                        <span className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-sm font-bold ${
                          ch.progress_percentage === 100
                            ? 'bg-success/15 text-success'
                            : ch.progress_percentage > 0
                            ? 'bg-info/10 text-info'
                            : 'bg-muted text-muted-foreground'
                        }`}>
                          {ch.progress_percentage === 100 ? (
                            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                            </svg>
                          ) : (
                            ch.order
                          )}
                        </span>
                        <div className="min-w-0 flex-1">
                          <div className="mb-1 flex items-center justify-between">
                            <Link
                              href={`/learn/${course.slug}?lesson=${ch.lessons[0]?.slug ?? ''}`}
                              className="truncate text-sm font-medium text-foreground hover:underline"
                            >
                              {ch.title}
                            </Link>
                            <span className="text-xs text-muted-foreground">{completed}/{ch.lessons.length} lessons</span>
                          </div>
                          <div className="h-1.5 w-full overflow-hidden rounded-full bg-muted">
                            <div
                              className={`h-full rounded-full transition-all ${
                                ch.progress_percentage === 100 ? 'bg-success' : ch.progress_percentage > 0 ? 'bg-info' : 'bg-muted'
                              }`}
                              style={{ width: `${Math.max(ch.progress_percentage, 2)}%` }}
                            />
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Practice */}
            <div className="rounded-xl border border-border bg-white p-6">
              <h3 className="mb-2 text-base font-semibold text-foreground">Practice</h3>
              <p className="mb-4 text-sm text-muted-foreground">
                Strengthen what you&apos;ve learned with exercises and challenges.
              </p>
              <div className="grid grid-cols-2 gap-3">
                <Link
                  href={resumeTarget}
                  className="rounded-lg border border-border p-3 text-center transition-colors hover:bg-muted/60"
                >
                  <p className="text-sm font-medium text-foreground">Course Exercises</p>
                  <p className="mt-1 text-xs text-muted-foreground">{course.exercise_count} in this course</p>
                </Link>
                <Link
                  href="/challenges"
                  className="rounded-lg border border-border p-3 text-center transition-colors hover:bg-muted/60"
                >
                  <p className="text-sm font-medium text-foreground">Challenges</p>
                  <p className="mt-1 text-xs text-muted-foreground">Practice standalone problems</p>
                </Link>
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Certificate status & issuance (server-verified) */}
            <CertificatePanel courseSlug={course.slug} enrolled={course.enrolled} />

            {/* Stats */}
            <div className="rounded-xl border border-border bg-white p-5">
              <h3 className="mb-3 text-sm font-semibold text-foreground">Your Progress</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Lessons</span>
                  <span className="text-sm font-medium text-foreground">{lessonStats.completed}/{lessonStats.total}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Chapters</span>
                  <span className="text-sm font-medium text-foreground">{completedChapters}/{chapters.length}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">XP available</span>
                  <span className="text-sm font-medium text-success">{course.total_xp.toLocaleString()}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Your streak</span>
                  <span className="text-sm font-medium text-warning">
                    {user ? (streak !== null ? `${streak} days` : '—') : 'Sign in'}
                  </span>
                </div>
                {!user && (
                  <p className="text-xs text-muted-foreground">Progress stats require an account. Browse freely.</p>
                )}
              </div>
            </div>

            {/* Resources */}
            <div className="rounded-xl border border-border bg-white p-5">
              <h3 className="mb-3 text-sm font-semibold text-foreground">Resources</h3>
              {(course.resources ?? []).length === 0 ? (
                <p className="text-sm text-muted-foreground">No resources have been added to this course yet.</p>
              ) : (
                <div className="space-y-2">
                  {(course.resources ?? []).map((r) => (
                    <a
                      key={r.id}
                      href={r.file_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2 rounded-lg p-2 text-sm text-foreground transition-colors hover:bg-muted/60"
                    >
                      <svg className="h-4 w-4 text-muted-foreground" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
                      </svg>
                      {r.title}
                    </a>
                  ))}
                </div>
              )}
            </div>

            {/* Course info */}
            <div className="rounded-xl border border-border bg-white p-5">
              <h3 className="mb-3 text-sm font-semibold text-foreground">About this course</h3>
              <div className="space-y-2 text-sm text-muted-foreground">
                <p>{course.description}</p>
                {course.instructor && (
                  <p className="text-xs text-muted-foreground">Instructor: {course.instructor}</p>
                )}
                <p className="text-xs text-muted-foreground">
                  {course.estimated_hours}h estimated · {course.lesson_count} lessons · {course.exercise_count} exercises
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
