'use client';

import Link from 'next/link';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { useParams } from 'next/navigation';
import { ArrowRight, Award, CheckCircle2, Clock, BookOpen, Target } from 'lucide-react';
import {
  ApiError,
  tracks as tracksApi,
  type TrackDetail,
} from '@/lib/api';
import type { Course } from '@/types';
import { useAuth } from '@/hooks/use-auth';
import { NetworkError, NotFoundError } from '@/components/learning/workspace/error-states';
import { formatAcademicClass, trackDifficultyTone } from '@/components/learning/tracks/shared';

/**
 * Track detail: overview, objectives and the track's courses in the
 * recommended sequence. Courses keep their existing pages — this page only
 * organizes them, it never duplicates lesson content.
 */

function CourseRow({ course, index }: { course: Course; index: number }) {
  const inProgress = course.enrolled && (course.progress_percentage ?? 0) > 0;
  const done = (course.progress_percentage ?? 0) >= 100;
  return (
    <li className="flex flex-col gap-3 rounded-card border border-border bg-card p-4 transition-colors hover:border-primary/50 sm:flex-row sm:items-center">
      <span
        className={`grid h-9 w-9 shrink-0 place-items-center rounded-full text-sm font-bold ${
          done ? 'bg-cta/15 text-[var(--difficulty-easy)]' : 'bg-muted text-muted-foreground'
        }`}
        aria-hidden="true"
      >
        {done ? <CheckCircle2 className="h-5 w-5" /> : index}
      </span>
      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-center gap-2 text-[11px] font-semibold uppercase tracking-wider">
          <span className={`rounded-pill px-2 py-0.5 ${trackDifficultyTone(course.difficulty)}`}>
            {course.difficulty}
          </span>
          {course.language && course.language !== 'none' && (
            <span className="text-muted-foreground">{course.language}</span>
          )}
          {course.estimated_hours > 0 && (
            <span className="inline-flex items-center gap-1 text-muted-foreground">
              <Clock aria-hidden="true" className="h-3 w-3" />
              {course.estimated_hours}h
            </span>
          )}
        </div>
        <h3 className="mt-1.5 font-bold text-foreground">{course.title}</h3>
        {course.description && (
          <p className="mt-1 line-clamp-2 text-sm text-muted-foreground">{course.description}</p>
        )}
        {course.enrolled && (
          <div className="mt-2 flex items-center gap-2">
            <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-muted sm:max-w-48">
              <div
                className="h-full rounded-full bg-cta"
                style={{ width: `${Math.max(course.progress_percentage ?? 0, 2)}%` }}
              />
            </div>
            <span className="text-xs font-medium text-muted-foreground">
              {course.progress_percentage ?? 0}%
            </span>
          </div>
        )}
      </div>
      <Link
        href={inProgress || course.enrolled ? `/learn/${course.slug}` : `/learn/${course.slug}/dashboard`}
        className="focus-ring inline-flex min-h-10 shrink-0 items-center gap-1.5 rounded-lg bg-cta px-4 py-2 text-sm font-bold text-cta-fg transition-colors hover:bg-cta-hover"
      >
        {inProgress ? 'Continue' : course.enrolled ? 'Open course' : 'Start course'}
        <ArrowRight aria-hidden="true" className="h-4 w-4" />
      </Link>
    </li>
  );
}

export default function TrackDetailPage() {
  const params = useParams<{ slug: string }>();
  const { isAuthenticated } = useAuth();
  const [track, setTrack] = useState<TrackDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<'network' | 'not_found' | null>(null);
  const [enrolling, setEnrolling] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const data = await tracksApi.detail(params.slug);
      setTrack(data);
      setError(null);
    } catch (reason) {
      if (reason instanceof ApiError && reason.status === 404) setError('not_found');
      else setError('network');
    } finally {
      setLoading(false);
    }
  }, [params.slug]);

  useEffect(() => {
    // Deferred via await so the effect never sets state synchronously.
    (async () => { await load(); })();
  }, [load]);

  // Courses arrive ordered by the admin-set sequence; group them under their
  // academic class when the track is a board path (Class X → XI → XII).
  const sections = useMemo(() => {
    const courses = track?.courses ?? [];
    const grouped = courses.every((course) => course.academic_class);
    if (!grouped) return [{ label: null as string | null, courses }];
    const out: { label: string | null; courses: Course[] }[] = [];
    for (const course of courses) {
      const label = formatAcademicClass(course.academic_class ?? '');
      const last = out[out.length - 1];
      if (last && last.label === label) last.courses.push(course);
      else out.push({ label, courses: [course] });
    }
    return out;
  }, [track]);

  const handleEnroll = async () => {
    if (!track) return;
    setEnrolling(true);
    setNotice(null);
    try {
      await tracksApi.enroll(track.slug);
      await load();
    } catch (reason) {
      setNotice(
        reason instanceof ApiError
          ? reason.message
          : 'Enrollment failed: the server could not be reached.',
      );
    } finally {
      setEnrolling(false);
    }
  };

  if (loading) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-6 sm:px-6 lg:px-8">
        <div className="h-44 animate-pulse rounded-card border border-border bg-card" />
        <div className="mt-6 space-y-3">
          {[1, 2].map((item) => (
            <div key={item} className="h-24 animate-pulse rounded-card border border-border bg-card" />
          ))}
        </div>
      </div>
    );
  }
  if (error === 'not_found') return <NotFoundError resource="Track" />;
  if (error === 'network') return <NetworkError onRetry={load} />;
  if (!track) return null;

  const enrolled = track.enrolled_course_count > 0;

  return (
    <div className="mx-auto max-w-4xl px-4 py-6 sm:px-6 lg:px-8">
      <nav className="mb-4 flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
        <Link href="/learn/tracks" className="rounded focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring hover:text-foreground">
          Tracks
        </Link>
        <span aria-hidden="true">/</span>
        <span className="text-foreground">{track.title}</span>
      </nav>

      <header className="overflow-hidden rounded-card border border-border bg-card">
        {track.cover_url && (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={track.cover_url} alt="" className="h-40 w-full object-cover sm:h-52" />
        )}
        <div className="p-6 sm:p-8">
          <div className="flex flex-wrap items-center gap-2 text-[11px] font-semibold uppercase tracking-wider">
            <span className="rounded-pill bg-hero-navy px-2.5 py-1 text-white">
              {track.category_display}
            </span>
            <span className={`rounded-pill px-2 py-0.5 ${trackDifficultyTone(track.difficulty)}`}>
              {track.difficulty}
            </span>
          </div>
          <h1 className="mt-3 text-2xl font-bold text-foreground sm:text-3xl">{track.title}</h1>
          <p className="mt-2 max-w-2xl text-sm text-muted-foreground">{track.description}</p>

          <dl className="mt-5 flex flex-wrap gap-x-6 gap-y-2 text-sm text-muted-foreground">
            <div className="flex items-center gap-1.5">
              <BookOpen aria-hidden="true" className="h-4 w-4" />
              <dt className="sr-only">Courses</dt>
              <dd>{track.course_count} course{track.course_count === 1 ? '' : 's'}</dd>
            </div>
            {track.estimated_hours > 0 && (
              <div className="flex items-center gap-1.5">
                <Clock aria-hidden="true" className="h-4 w-4" />
                <dt className="sr-only">Estimated duration</dt>
                <dd>~{track.estimated_hours} hours</dd>
              </div>
            )}
            {track.total_xp > 0 && (
              <div className="flex items-center gap-1.5">
                <Award aria-hidden="true" className="h-4 w-4" />
                <dt className="sr-only">XP</dt>
                <dd>{track.total_xp} XP</dd>
              </div>
            )}
          </dl>

          {enrolled && (
            <div className="mt-5 rounded-card bg-muted/60 p-4">
              <div className="flex items-center justify-between text-sm font-medium">
                <span className="text-foreground">Track progress</span>
                <span className="text-muted-foreground">
                  {track.completed_course_count}/{track.course_count} courses · {track.progress_percentage}%
                </span>
              </div>
              <div className="mt-2 h-2 overflow-hidden rounded-full bg-border">
                <div
                  className="h-full rounded-full bg-cta transition-[width] duration-300"
                  style={{ width: `${Math.max(track.progress_percentage, 2)}%` }}
                />
              </div>
            </div>
          )}

          <div className="mt-6 flex flex-wrap items-center gap-3">
            {!enrolled &&
              (isAuthenticated ? (
                <button
                  type="button"
                  onClick={handleEnroll}
                  disabled={enrolling}
                  className="focus-ring inline-flex min-h-10 items-center gap-2 rounded-lg bg-cta px-5 py-2.5 text-sm font-bold text-cta-fg transition-colors hover:bg-cta-hover disabled:opacity-60"
                >
                  {enrolling ? 'Enrolling...' : 'Enroll in track'}
                </button>
              ) : (
                <Link
                  href="/sign-in"
                  className="focus-ring inline-flex min-h-10 items-center gap-2 rounded-lg bg-cta px-5 py-2.5 text-sm font-bold text-cta-fg transition-colors hover:bg-cta-hover"
                >
                  Sign in to enroll
                </Link>
              ))}
            {track.continue_url_slug && (
              <Link
                href={`/learn/${track.continue_url_slug}`}
                className="focus-ring inline-flex min-h-10 items-center gap-1.5 rounded-lg border border-border px-4 py-2.5 text-sm font-semibold text-foreground transition-colors hover:bg-muted"
              >
                Continue learning
                <ArrowRight aria-hidden="true" className="h-4 w-4" />
              </Link>
            )}
          </div>
          {notice && (
            <p role="alert" className="mt-3 rounded-lg border border-danger/30 bg-danger/10 px-3 py-2 text-sm text-danger">
              {notice}
            </p>
          )}
        </div>
      </header>

      {track.learning_objectives.length > 0 && (
        <section aria-labelledby="objectives-heading" className="mt-6 rounded-card border border-border bg-card p-6">
          <h2 id="objectives-heading" className="flex items-center gap-2 text-lg font-bold text-foreground">
            <Target aria-hidden="true" className="h-5 w-5 text-primary" />
            What you will learn
          </h2>
          <ul className="mt-3 space-y-2">
            {track.learning_objectives.map((objective) => (
              <li key={objective} className="flex items-start gap-2 text-sm text-muted-foreground">
                <CheckCircle2 aria-hidden="true" className="mt-0.5 h-4 w-4 shrink-0 text-[var(--difficulty-easy)]" />
                {objective}
              </li>
            ))}
          </ul>
        </section>
      )}

      <section aria-labelledby="courses-heading" className="mt-6">
        <h2 id="courses-heading" className="text-lg font-bold text-foreground">
          Courses in this track
        </h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Followed in the recommended order below — each course opens its own lessons,
          exercises and assessments.
        </p>
        {sections.map((section, sectionIndex) => (
          <div key={section.label ?? 'all'} className="mt-4">
            {section.label && (
              <h3 className="mb-2 text-xs font-bold uppercase tracking-[0.12em] text-muted-foreground">
                {sectionIndex === 0 && !enrolled ? `${section.label} · Start here` : section.label}
              </h3>
            )}
            <ul className="space-y-3">
              {section.courses.map((course) => (
                <CourseRow
                  key={course.id}
                  course={course}
                  index={track.courses.indexOf(course) + 1}
                />
              ))}
            </ul>
          </div>
        ))}
      </section>
    </div>
  );
}
