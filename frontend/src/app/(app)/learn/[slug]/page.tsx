'use client';

import { Suspense, useCallback, useEffect, useMemo, useRef, useState } from 'react';
import Link from 'next/link';
import { useParams, useSearchParams } from 'next/navigation';
import { ApiError, auth, courses as coursesApi, exercises as exercisesApi, sandbox } from '@/lib/api';
import { useAuth } from '@/hooks/use-auth';
import type { ExerciseDetail, ExerciseResult, Hint, LessonDetail, Course } from '@/types';
import CourseSidebar from '@/components/learning/workspace/course-sidebar';
import LessonContent from '@/components/learning/workspace/lesson-content';
import ExercisePanel from '@/components/learning/workspace/exercise-panel';
import CodeEditor from '@/components/learning/workspace/code-editor';
import OutputPanel from '@/components/learning/workspace/output-panel';
import XPBadge from '@/components/learning/workspace/xp-badge';
import CertificatePanel from '@/components/learning/certificate-panel';

const EDITOR_FILENAMES: Record<string, string> = {
  python: 'main.py',
  javascript: 'main.js',
  cpp: 'main.cpp',
  java: 'Main.java',
};

type PageError = 'network' | 'not_found' | null;

/**
 * Run an API call, retrying once when the server cannot be reached at all.
 * The dev API restarts whenever a backend file is saved, so the first request
 * after a save can be refused; a second attempt hides that blip instead of
 * telling the learner the server is down.
 */
async function withTransportRetry<T>(call: () => Promise<T>): Promise<T> {
  try {
    return await call();
  } catch (reason) {
    if (!(reason instanceof ApiError) || reason.status !== 0) throw reason;
    await new Promise((resolve) => setTimeout(resolve, 800));
    return call();
  }
}

function Workspace() {
  const params = useParams<{ slug: string }>();
  const courseSlug = params.slug;
  const searchParams = useSearchParams();
  const requestedLessonSlug = searchParams.get('lesson');
  const { user } = useAuth();

  // Data
  const [course, setCourse] = useState<Course | null>(null);
  const [lesson, setLesson] = useState<LessonDetail | null>(null);
  const [exerciseData, setExerciseData] = useState<ExerciseDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<PageError>(null);
  const [profileXp, setProfileXp] = useState<number | null>(null);

  // Workspace state
  const [code, setCode] = useState('');
  const [output, setOutput] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState<ExerciseResult | null>(null);
  const [xpAnimation, setXpAnimation] = useState<number | null>(null);
  const [revealedHints, setRevealedHints] = useState<Hint[]>([]);
  const [hintsLoading, setHintsLoading] = useState(false);
  const [selectedAnswer, setSelectedAnswer] = useState<string | string[] | null>(null);
  const [textAnswer, setTextAnswer] = useState('');
  const [notice, setNotice] = useState<string | null>(null);
  const [enrolling, setEnrolling] = useState(false);
  const [completing, setCompleting] = useState(false);
  const [activeExerciseId, setActiveExerciseId] = useState<number | null>(null);

  // Layout state — course navigation starts collapsed so the lesson and the
  // workspace get the full width; the header button opens it on demand.
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [cursor, setCursor] = useState({ line: 1, col: 1 });
  const [editorPct, setEditorPct] = useState(62);
  const [mobileTab, setMobileTab] = useState<'code' | 'output'>('code');
  const [isDesktop, setIsDesktop] = useState(false);
  const rightPaneRef = useRef<HTMLDivElement>(null);
  const submitStartedAt = useRef<number>(0);

  useEffect(() => {
    const mq = window.matchMedia('(min-width: 1024px)');
    const onChange = () => {
      setIsDesktop(mq.matches);
      if (mq.matches) setSidebarOpen(true);
    };
    onChange();
    mq.addEventListener('change', onChange);
    return () => mq.removeEventListener('change', onChange);
  }, []);

  // ── Load course ───────────────────────────────────────────────────────────
  const loadCourse = useCallback(async () => {
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
    (async () => { await loadCourse(); })();
  }, [loadCourse]);

  // ── Resolve active lesson ─────────────────────────────────────────────────
  const allLessons = useMemo(
    () => (course?.chapters ?? []).flatMap((ch) => ch.lessons.map((l) => ({ lesson: l, chapter: ch }))),
    [course]
  );

  const activeLessonSlug = useMemo(() => {
    if (!course) return null;
    if (requestedLessonSlug) return requestedLessonSlug;
    if (course.resume_lesson?.slug) return course.resume_lesson.slug;
    return allLessons[0]?.lesson.slug ?? null;
  }, [course, requestedLessonSlug, allLessons]);

  const activeChapter = useMemo(
    () => allLessons.find((entry) => entry.lesson.slug === activeLessonSlug)?.chapter ?? null,
    [allLessons, activeLessonSlug]
  );

  // ── Load lesson ───────────────────────────────────────────────────────────
  useEffect(() => {
    if (!course || !activeLessonSlug) return;
    let cancelled = false;
    coursesApi.lessonDetail(courseSlug, activeLessonSlug)
      .then((data) => {
        if (!cancelled) setLesson(data);
      })
      .catch((reason) => {
        if (cancelled) return;
        if (reason instanceof ApiError && reason.status === 404) setError('not_found');
        else setError('network');
      });
    return () => { cancelled = true; };
  }, [course, courseSlug, activeLessonSlug]);

  // ── Exercises of the active lesson (tabbed when there is more than one) ──
  const exerciseSummaries = lesson?.exercises ?? [];
  // Selected tab falls back to the first exercise when it doesn't belong to
  // the active lesson (e.g. right after switching lessons).
  const currentSummary =
    exerciseSummaries.find((e) => e.id === activeExerciseId) ?? exerciseSummaries[0] ?? null;
  const currentExerciseId = currentSummary?.id ?? null;

  // ── Load the selected exercise's full details ────────────────────────────
  useEffect(() => {
    if (currentExerciseId === null) return;
    let cancelled = false;
    exercisesApi.detail(currentExerciseId)
      .then((data) => {
        if (cancelled) return;
        setExerciseData(data);
        setCode(data.starter_code ?? '');
        setOutput('');
        setResult(null);
        setNotice(null);
        setRevealedHints([]);
        setSelectedAnswer(null);
        setTextAnswer('');
        submitStartedAt.current = Date.now();
      })
      .catch(() => {
        if (!cancelled) setNotice('Exercise details could not be loaded.');
      });
    return () => { cancelled = true; };
  }, [currentExerciseId]);

  // Derived: only show the loaded exercise while it belongs to the active lesson
  // (replaces a synchronous clear-in-effect, keeping renders cascade-free).
  const exercise =
    exerciseData && lesson?.exercises.some((e) => e.id === exerciseData.id) ? exerciseData : null;

  // ── Profile XP (real, server-side) ────────────────────────────────────────
  useEffect(() => {
    if (!user) return;
    let cancelled = false;
    auth.getProfile()
      .then((profile) => {
        if (!cancelled) setProfileXp(profile.xp_points);
      })
      .catch(() => {
        if (!cancelled) setProfileXp(null);
      });
    return () => { cancelled = true; };
  }, [user]);

  const refreshProgress = useCallback(() => {
    if (!activeLessonSlug) return;
    coursesApi.detail(courseSlug).then(setCourse).catch(() => { /* keep stale data */ });
    coursesApi.lessonDetail(courseSlug, activeLessonSlug).then(setLesson).catch(() => { /* keep stale data */ });
    auth.getProfile().then((p) => setProfileXp(p.xp_points)).catch(() => { /* anonymous */ });
  }, [courseSlug, activeLessonSlug]);

  // ── Splitter drag ─────────────────────────────────────────────────────────
  const startDrag = useCallback((e: React.PointerEvent) => {
    e.preventDefault();
    const move = (ev: PointerEvent) => {
      const el = rightPaneRef.current;
      if (!el) return;
      const rect = el.getBoundingClientRect();
      const pct = ((ev.clientY - rect.top) / rect.height) * 100;
      setEditorPct(Math.min(85, Math.max(25, pct)));
    };
    const up = () => {
      window.removeEventListener('pointermove', move);
      window.removeEventListener('pointerup', up);
    };
    window.addEventListener('pointermove', move);
    window.addEventListener('pointerup', up);
  }, []);

  // ── Actions (all real API calls) ──────────────────────────────────────────
  const handleRun = useCallback(async () => {
    if (!exercise) return;
    if (!user) {
      setNotice('Sign in to run code.');
      return;
    }
    setIsRunning(true);
    setNotice(null);
    setOutput('Running…');
    setResult(null);
    try {
      const runResult = await withTransportRetry(() => exercisesApi.run(exercise.id, code));
      // A program may legitimately print nothing; say so instead of leaving
      // the panel on its "run your code" placeholder.
      setOutput(runResult.error || runResult.output || '(no output)');
    } catch (reason) {
      setOutput('');
      setNotice(reason instanceof ApiError
        ? `Run failed: ${reason.message}`
        : 'Run failed: the server could not be reached.');
    } finally {
      setIsRunning(false);
    }
  }, [exercise, code, user]);

  const handleSubmit = useCallback(async () => {
    if (!exercise) return;
    if (!user) {
      setNotice('Sign in to submit answers for grading.');
      return;
    }
    setIsSubmitting(true);
    setNotice(null);
    setResult(null);
    try {
      const payload: { code?: string; selected_answer?: string | string[]; time_spent_seconds?: number } = {
        time_spent_seconds: submitStartedAt.current ? Math.round((Date.now() - submitStartedAt.current) / 1000) : 0,
      };
      if (exercise.exercise_type === 'multiple_choice' || exercise.exercise_type === 'multiple_select') {
        payload.selected_answer = selectedAnswer ?? '';
      } else if (exercise.exercise_type === 'output_prediction' || exercise.exercise_type === 'fill_blank') {
        // Both are graded server-side: prediction compares text, fill_blank
        // treats the answer as the submitted code string.
        payload.code = textAnswer;
      } else {
        payload.code = code;
      }
      const submitResult = await exercisesApi.submit(exercise.id, payload);
      setResult(submitResult);
      if (submitResult.status === 'correct') {
        setXpAnimation(submitResult.xp_earned);
        setTimeout(() => setXpAnimation(null), 2000);
        refreshProgress();
      }
    } catch (reason) {
      setNotice(reason instanceof ApiError
        ? `Submission failed: ${reason.message}`
        : 'Submission failed: the server could not be reached.');
    } finally {
      setIsSubmitting(false);
    }
  }, [exercise, user, selectedAnswer, textAnswer, code, refreshProgress]);

  const handleHint = useCallback(async () => {
    if (!exercise) return;
    if (!user) {
      setNotice('Sign in to use hints.');
      return;
    }
    setHintsLoading(true);
    try {
      const data = await exercisesApi.hint(exercise.id);
      if (data.hint === null) {
        setNotice(data.message ?? 'No hints available for this exercise.');
      } else {
        setRevealedHints((prev) => (
          prev.some((h) => h.order === data.order)
            ? prev
            : [...prev, { id: data.order, content: data.hint as string, order: data.order, reveals_solution: data.reveals_solution, xp_penalty: data.xp_penalty }]
        ));
        if (data.xp_penalty > 0) {
          auth.getProfile().then((p) => setProfileXp(p.xp_points)).catch(() => { /* anonymous */ });
        }
      }
    } catch (reason) {
      setNotice(reason instanceof ApiError
        ? `Hint failed: ${reason.message}`
        : 'Hint failed: the server could not be reached.');
    } finally {
      setHintsLoading(false);
    }
  }, [exercise, user]);

  const handleReset = useCallback(() => {
    if (!exercise) return;
    setCode(exercise.starter_code ?? '');
    setOutput('');
    setResult(null);
    setNotice(null);
  }, [exercise]);

  const handleEnroll = useCallback(async () => {
    if (!course) return;
    setEnrolling(true);
    try {
      await coursesApi.enroll(course.slug);
      setCourse({ ...course, enrolled: true });
    } catch (reason) {
      setNotice(reason instanceof ApiError
        ? `Enrollment failed: ${reason.message}`
        : 'Enrollment failed: the server could not be reached.');
    } finally {
      setEnrolling(false);
    }
  }, [course]);

  // ── Lesson snippet "Run" buttons → real sandbox execution ───────────────
  const runSnippet = useCallback(async (snippet: string, lang: string) => {
    if (!user) throw new Error('Sign in to run code.');
    const res = await withTransportRetry(() => sandbox.execute(snippet, lang as 'python'));
    const combined = `${res.output}${res.error ? `\n${res.error}` : ''}`.trim();
    return combined || '(no output)';
  }, [user]);

  // ── Mark lesson complete (server decides if that's allowed) ──────────────
  const handleMarkComplete = useCallback(async () => {
    if (!lesson) return;
    if (!user) {
      setNotice('Sign in to save your progress.');
      return;
    }
    setCompleting(true);
    setNotice(null);
    try {
      const res = await coursesApi.completeLesson(lesson.id);
      setNotice(res.message);
      if (res.status === 'completed') {
        if (res.xp_awarded > 0) {
          setXpAnimation(res.xp_awarded);
          setTimeout(() => setXpAnimation(null), 2000);
        }
        refreshProgress();
      }
    } catch (reason) {
      setNotice(reason instanceof ApiError
        ? `Could not save progress: ${reason.message}`
        : 'Could not reach the server.');
    } finally {
      setCompleting(false);
    }
  }, [lesson, user, refreshProgress]);

  const isCodeExercise = !exercise || exercise.exercise_type === 'code' || exercise.exercise_type === 'debugging';

  // ── Render: loading / error states ────────────────────────────────────────
  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="flex flex-col items-center gap-3 text-muted-foreground">
          <span className="h-8 w-8 animate-spin rounded-full border-2 border-border border-t-cta" aria-hidden />
          <p className="text-sm">Loading course…</p>
        </div>
      </div>
    );
  }

  if (error === 'not_found') {
    return (
      <div className="mx-auto max-w-md py-24 text-center">
        <h1 className="text-xl font-semibold">Course not found</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          This course doesn&apos;t exist or hasn&apos;t been published yet.
        </p>
        <Link href="/learn" className="focus-ring mt-4 inline-block rounded-md bg-cta px-4 py-2 text-sm font-semibold text-cta-fg">
          Browse courses
        </Link>
      </div>
    );
  }

  if (error === 'network') {
    return (
      <div className="mx-auto max-w-md py-24 text-center">
        <h1 className="text-xl font-semibold">Couldn&apos;t load the course</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          The server could not be reached. Check your connection and try again.
        </p>
        <button onClick={loadCourse} className="focus-ring mt-4 rounded-md bg-cta px-4 py-2 text-sm font-semibold text-cta-fg">
          Try again
        </button>
      </div>
    );
  }

  if (!course || allLessons.length === 0) {
    return (
      <div className="mx-auto max-w-md py-24 text-center">
        <h1 className="text-xl font-semibold">{course?.title ?? 'Course'}</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          This course has no lessons yet. Check back soon, or explore other courses.
        </p>
        <Link href="/learn" className="focus-ring mt-4 inline-block rounded-md border border-border px-4 py-2 text-sm font-medium">
          Back to courses
        </Link>
      </div>
    );
  }

  return (
    <div className="flex workspace-full-height overflow-hidden bg-background">
      {/* ── Left: Course Sidebar ────────────────────────────────── */}
      <CourseSidebar
        chapters={course.chapters ?? []}
        courseSlug={course.slug}
        currentLessonId={lesson?.id ?? -1}
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
        courseProgress={course.progress_percentage ?? 0}
        courseTitle={course.title}
      />

      {/* Mobile drawer backdrop */}
      {sidebarOpen && !isDesktop && (
        <div
          className="fixed inset-0 z-30 bg-black/40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
          aria-hidden
        />
      )}

      {/* ── Main Content Area ───────────────────────────────────── */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Top Bar */}
        <header className="flex h-12 shrink-0 items-center justify-between border-b border-border bg-card px-4">
          <div className="flex items-center gap-3">
            {!sidebarOpen && (
              <button
                onClick={() => setSidebarOpen(true)}
                aria-label="Open course navigation"
                className="focus-ring inline-flex min-h-11 min-w-11 items-center justify-center rounded-md p-2 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
              >
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
                </svg>
              </button>
            )}
            <nav aria-label="Breadcrumb" className="flex items-center gap-2 text-sm">
              <Link href="/learn" className="focus-ring rounded text-muted-foreground transition-colors hover:text-foreground">
                {course.title}
              </Link>
              <span aria-hidden className="text-border">/</span>
              <span className="text-foreground">
                {lesson
                  ? `Chapter ${activeChapter?.order ?? '?'} · Lesson ${lesson.order}`
                  : 'Loading lesson…'}
              </span>
            </nav>
          </div>
          <div className="flex items-center gap-3">
            {xpAnimation && <XPBadge amount={xpAnimation} />}
            <span className="inline-flex items-center gap-1 rounded-pill bg-cta/10 px-2.5 py-1 text-sm font-semibold text-[var(--difficulty-easy)]">
              <span aria-hidden>⚡</span> {profileXp !== null ? `${profileXp.toLocaleString()} XP` : user ? '—' : 'Sign in'}
            </span>
          </div>
        </header>

        {/* Enrollment / sign-in banner */}
        {user && !course.enrolled && (
          <div className="flex shrink-0 items-center justify-between gap-3 border-b border-info/25 bg-info/10 px-4 py-2 text-sm">
            <span className="text-muted-foreground">You&apos;re not enrolled yet — enroll to track your progress.</span>
            <button
              onClick={handleEnroll}
              disabled={enrolling}
              className="focus-ring inline-flex min-h-9 items-center rounded-md bg-cta px-3 py-1.5 text-xs font-semibold text-cta-fg disabled:opacity-50"
            >
              {enrolling ? 'Enrolling…' : 'Enroll'}
            </button>
          </div>
        )}
        {!user && (
          <div className="flex shrink-0 items-center justify-between gap-3 border-b border-border bg-muted/50 px-4 py-2 text-sm">
            <span className="text-muted-foreground">Sign in to save progress, earn XP, and submit answers.</span>
            <Link href="/sign-in" className="focus-ring inline-flex min-h-9 items-center rounded-md border border-border px-3 py-1.5 text-xs font-medium hover:bg-muted">
              Sign in
            </Link>
          </div>
        )}

        {/* Content: Lesson + Workspace — column on mobile, split on desktop */}
        <div className="flex flex-1 flex-col overflow-hidden lg:flex-row">
          {/* Lesson Content */}
          <div className="min-h-0 flex-1 overflow-y-auto border-b border-border lg:flex-1 lg:border-b-0 lg:border-r">
            {lesson ? (
              <>
                <LessonContent lesson={lesson} onRunSandbox={runSnippet} />
                {notice && (
                  <div className="mx-auto max-w-3xl px-6 pb-4">
                    <p role="alert" className="rounded-lg border border-warning/30 bg-warning/10 px-3 py-2 text-sm text-foreground">
                      {notice}
                    </p>
                  </div>
                )}
                {/* Lesson actions: complete + prev/next (order from the API) */}
                <div className="mx-auto max-w-3xl px-6 pb-6">
                  {lesson.progress_status !== 'completed' && (
                    <div className="mb-4 flex flex-wrap items-center gap-3">
                      <button
                        onClick={handleMarkComplete}
                        disabled={completing}
                        className="focus-ring inline-flex min-h-11 items-center rounded-md bg-cta px-4 py-2 text-sm font-semibold text-cta-fg transition-colors hover:bg-cta-hover disabled:opacity-50"
                      >
                        {completing ? 'Saving…' : 'Mark lesson complete'}
                      </button>
                      <span className="text-xs text-muted-foreground">
                        {lesson.exercise_count > 0
                          ? 'Lessons with exercises complete only when every exercise is solved.'
                          : `Earns +${lesson.xp_reward} XP on completion.`}
                      </span>
                    </div>
                  )}
                  <div className="flex items-center justify-between gap-3 border-t border-border pt-4">
                    {lesson.prev_lesson ? (
                      <Link
                        href={`/learn/${course.slug}?lesson=${lesson.prev_lesson.slug}`}
                        className="focus-ring inline-flex min-h-11 items-center gap-2 rounded-md border border-border px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
                      >
                        <span aria-hidden>←</span>
                        <span className="max-w-[12rem] truncate">{lesson.prev_lesson.title}</span>
                      </Link>
                    ) : (
                      <span aria-hidden className="min-h-11" />
                    )}
                    {lesson.next_lesson ? (
                      <Link
                        href={`/learn/${course.slug}?lesson=${lesson.next_lesson.slug}`}
                        className="focus-ring inline-flex min-h-11 items-center gap-2 rounded-md bg-cta px-4 py-2 text-sm font-semibold text-cta-fg transition-colors hover:bg-cta-hover"
                      >
                        <span className="max-w-[12rem] truncate">{lesson.next_lesson.title}</span>
                        <span aria-hidden>→</span>
                      </Link>
                    ) : (
                      <span className="text-sm font-medium text-muted-foreground">
                        This is the last lesson of the course.
                      </span>
                    )}
                  </div>
                </div>
                {/* Certificate status belongs at the end of the course, next to
                    the final quiz that gates it. */}
                {(activeChapter?.is_final_assessment === true ||
                  course.progress_percentage === 100) && (
                  <div className="mx-auto max-w-3xl px-6 pb-8">
                    <CertificatePanel courseSlug={course.slug} enrolled={course.enrolled} />
                  </div>
                )}
              </>
            ) : (
              <div className="flex h-full items-center justify-center p-8">
                <p className="text-sm text-muted-foreground">Loading lesson content…</p>
              </div>
            )}
          </div>

          {/* Workspace — exercise + resizable (desktop) / tabbed (mobile) editor↔output */}
          <div
            ref={rightPaneRef}
            className="flex h-[55%] w-full shrink-0 flex-col overflow-hidden editor-surface lg:h-auto lg:w-[520px]"
          >
            {exercise ? (
              <>
                {exerciseSummaries.length > 1 && (
                  <div
                    role="tablist"
                    aria-label="Lesson exercises"
                    className="flex shrink-0 gap-1 overflow-x-auto border-b border-[var(--editor-border)] px-2 py-1.5"
                  >
                    {exerciseSummaries.map((e, i) => (
                      <button
                        key={e.id}
                        role="tab"
                        aria-selected={e.id === exercise.id}
                        title={e.title}
                        onClick={() => setActiveExerciseId(e.id)}
                        className={`seg-tab shrink-0 ${e.id === exercise.id ? 'seg-tab-active' : ''}`}
                      >
                        {i + 1}. {e.title}
                      </button>
                    ))}
                  </div>
                )}
                <ExercisePanel
                  exercise={exercise}
                  revealedHints={revealedHints}
                  hintsLoading={hintsLoading}
                  onHint={handleHint}
                  result={result}
                  selectedAnswer={selectedAnswer}
                  onAnswerChange={setSelectedAnswer}
                  textAnswer={textAnswer}
                  onTextAnswerChange={setTextAnswer}
                  authRequired={!user}
                />

                {isCodeExercise && (
                  <div className="flex min-h-0 flex-1 flex-col">
                    {/* Mobile tab switcher (desktop shows both panes via the splitter) */}
                    {!isDesktop && (
                      <div className="flex shrink-0 gap-1 border-b border-[var(--editor-border)] px-2 py-1.5">
                        <button
                          onClick={() => setMobileTab('code')}
                          aria-pressed={mobileTab === 'code'}
                          className={`seg-tab ${mobileTab === 'code' ? 'seg-tab-active' : ''}`}
                        >
                          Code
                        </button>
                        <button
                          onClick={() => setMobileTab('output')}
                          aria-pressed={mobileTab === 'output'}
                          className={`seg-tab ${mobileTab === 'output' ? 'seg-tab-active' : ''}`}
                        >
                          Output
                        </button>
                      </div>
                    )}

                    {/* Code Editor */}
                    <div
                      className={`min-h-0 flex-col ${isDesktop ? 'flex shrink-0' : mobileTab === 'code' ? 'flex flex-1' : 'hidden'}`}
                      style={isDesktop ? { height: `${editorPct}%` } : undefined}
                    >
                      <CodeEditor
                        code={code}
                        onChange={setCode}
                        language={exercise.language}
                        fileName={EDITOR_FILENAMES[exercise.language] ?? 'main.txt'}
                        onRun={handleRun}
                        onSubmit={handleSubmit}
                        onCursor={setCursor}
                      />
                    </div>

                    {/* Drag handle: code ↕ output (desktop only) */}
                    {isDesktop && (
                      <div
                        className="workspace-splitter-row"
                        onPointerDown={startDrag}
                        role="separator"
                        aria-orientation="horizontal"
                        aria-label="Resize editor and output"
                      />
                    )}

                    {/* Output Panel */}
                    <div
                      className={`min-h-0 flex-col ${isDesktop ? 'flex flex-1' : mobileTab === 'output' ? 'flex flex-1' : 'hidden'}`}
                    >
                      <OutputPanel
                        output={output}
                        isRunning={isRunning}
                        result={result}
                      />
                    </div>
                  </div>
                )}

                {/* Status bar: Ln, Col (code exercises only) */}
                {isCodeExercise && (
                  <div className="editor-statusbar flex shrink-0 items-center gap-3 px-3 py-1" aria-live="polite">
                    <span>Ln {cursor.line}, Col {cursor.col}</span>
                    <span className="ml-auto uppercase">{exercise.language}</span>
                  </div>
                )}

                {/* Action bar */}
                <div className="flex shrink-0 items-center gap-2 border-t border-[var(--editor-border)] bg-[var(--editor-chrome)] px-4 py-3">
                  <button
                    onClick={handleHint}
                    disabled={hintsLoading || exercise.hints.length === 0}
                    className="focus-ring inline-flex min-h-11 items-center rounded-md border border-[var(--overlay-border)] px-3 py-2 text-sm font-medium text-white/70 transition-colors hover:bg-[var(--overlay-hover)] hover:text-white disabled:opacity-40"
                  >
                    Hint
                  </button>
                  {isCodeExercise && (
                    <button
                      onClick={handleReset}
                      className="focus-ring inline-flex min-h-11 items-center rounded-md border border-[var(--overlay-border)] px-3 py-2 text-sm font-medium text-white/70 transition-colors hover:bg-[var(--overlay-hover)] hover:text-white"
                    >
                      Reset
                    </button>
                  )}
                  <div className="flex-1" />
                  {isCodeExercise && (
                    <button
                      onClick={handleRun}
                      disabled={isRunning || isSubmitting}
                      aria-keyshortcuts="Control+Enter Meta+Enter"
                      title="Run code (Ctrl/Cmd + Enter)"
                      className="editor-run-btn focus-ring inline-flex min-h-11 items-center justify-center gap-1.5 rounded-md bg-white/10 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-white/[0.16] disabled:opacity-50"
                    >
                      {isRunning ? 'Running…' : 'Run'}
                      <kbd className="hidden font-mono text-[10px] text-white/50 xl:inline">⌘↵</kbd>
                    </button>
                  )}
                  <button
                    onClick={handleSubmit}
                    disabled={isRunning || isSubmitting}
                    aria-keyshortcuts="Control+Shift+Enter Meta+Shift+Enter"
                    title="Submit answer (Ctrl/Cmd + Shift + Enter)"
                    className="focus-ring inline-flex min-h-11 items-center justify-center gap-1.5 rounded-md bg-cta px-5 py-2 text-sm font-semibold text-cta-fg transition-colors hover:bg-cta-hover disabled:opacity-50"
                  >
                    {isSubmitting ? 'Submitting…' : 'Submit'}
                    {!isCodeExercise && <kbd className="hidden font-mono text-[10px] text-white/70 xl:inline">⇧⌘↵</kbd>}
                  </button>
                </div>
              </>
            ) : (
              <div className="flex flex-1 items-center justify-center p-6">
                <p className="text-sm text-muted-foreground">
                  {lesson && lesson.exercises.length === 0
                    ? 'This lesson has no exercises yet — just read and continue.'
                    : 'Loading exercise…'}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function LearningWorkspacePage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-[60vh] items-center justify-center">
          <span className="h-8 w-8 animate-spin rounded-full border-2 border-border border-t-cta" aria-hidden />
        </div>
      }
    >
      <Workspace />
    </Suspense>
  );
}
