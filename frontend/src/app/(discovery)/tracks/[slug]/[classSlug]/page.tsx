'use client';

import Link from 'next/link';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { useParams } from 'next/navigation';
import { ArrowRight, BookOpen, ClipboardCheck, FlaskConical } from 'lucide-react';
import {
  ApiError,
  tracks as tracksApi,
  practicals as practicalsApi,
  type TrackDetail,
} from '@/lib/api';
import type { Course, PracticalClass } from '@/types';
import { useAuth } from '@/hooks/use-auth';
import { NetworkError, NotFoundError } from '@/components/learning/workspace/error-states';
import {
  canonicalClassSlug,
  classSlugToLabel,
  formatAcademicClass,
  practicalClassMatchesSlug,
  trackDifficultyTone,
} from '@/components/learning/tracks/shared';

/**
 * CLASS OVERVIEW: the bridge between a Sindh Board class's theory and its
 * practical work. Both already exist as separate backend systems — theory as
 * `Course` records tagged with `academic_class`, practicals as `PracticalClass`
 * — and are bound here purely by a normalized label match, so no relationship
 * is invented and no learner data is duplicated. Signed-in learners open the
 * course workspace; visitors get the public course page. Nothing is fabricated:
 * unpublished theory or practical work is shown honestly as not yet available.
 */

function theoryHref(course: Course, signedIn: boolean): string {
  if (!signedIn) return `/courses/${course.slug}`;
  const inProgress = course.enrolled && (course.progress_percentage ?? 0) > 0;
  if (inProgress || course.enrolled) return `/learn/${course.slug}`;
  return `/learn/${course.slug}/dashboard`;
}

function theoryCta(course: Course, signedIn: boolean): string {
  if (!signedIn) return 'View course';
  const inProgress = course.enrolled && (course.progress_percentage ?? 0) > 0;
  if (inProgress) return 'Continue';
  return course.enrolled ? 'Open course' : 'Start course';
}

function TheoryCard({ course, signedIn }: { course: Course; signedIn: boolean }) {
  const enrolled = course.enrolled;
  const progress = course.progress_percentage ?? 0;
  return (
    <li className="flex flex-col gap-3 rounded-card border border-border bg-card p-4 transition-colors hover:border-primary/50 sm:flex-row sm:items-center">
      <BookOpen aria-hidden="true" className="h-6 w-6 shrink-0 text-cta" />
      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-center gap-2 text-[11px] font-semibold uppercase tracking-wider">
          <span className={`rounded-pill px-2 py-0.5 ${trackDifficultyTone(course.difficulty)}`}>
            {course.difficulty}
          </span>
          {course.language && course.language !== 'none' && (
            <span className="text-muted-foreground">{course.language}</span>
          )}
        </div>
        <h3 className="mt-1.5 font-bold text-foreground">{course.title}</h3>
        <p className="mt-1 line-clamp-2 text-sm text-muted-foreground">
          {course.subtitle || course.description}
        </p>
        {enrolled && (
          <div className="mt-2 flex items-center gap-2">
            <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-muted sm:max-w-48">
              <div className="h-full rounded-full bg-cta" style={{ width: `${Math.max(progress, 2)}%` }} />
            </div>
            <span className="text-xs font-medium text-muted-foreground">{progress}%</span>
          </div>
        )}
      </div>
      <Link
        href={theoryHref(course, signedIn)}
        className="focus-ring inline-flex min-h-10 shrink-0 items-center gap-1.5 rounded-lg bg-cta px-4 py-2 text-sm font-bold text-cta-fg transition-colors hover:bg-cta-hover"
      >
        {theoryCta(course, signedIn)}
        <ArrowRight aria-hidden="true" className="h-4 w-4" />
      </Link>
    </li>
  );
}

export default function ClassOverviewPage() {
  const params = useParams<{ slug: string; classSlug: string }>();
  const { isAuthenticated } = useAuth();
  const [track, setTrack] = useState<TrackDetail | null>(null);
  const [practicalClasses, setPracticalClasses] = useState<PracticalClass[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<'network' | 'not_found' | null>(null);

  const load = useCallback(async () => {
    try {
      const [detail, classes] = await Promise.all([
        tracksApi.detail(params.slug),
        practicalsApi.classes().catch(() => [] as PracticalClass[]),
      ]);
      setTrack(detail);
      setPracticalClasses(classes);
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

  // Theory: the track's published courses whose academic class matches the
  // route segment. Practicals: the published class whose slug/title matches.
  const classCourses = useMemo(
    () =>
      (track?.courses ?? []).filter(
        (course) => course.academic_class && canonicalClassSlug(course.academic_class) === params.classSlug,
      ),
    [track, params.classSlug],
  );
  const practical = useMemo(
    () => practicalClasses.find((pc) => practicalClassMatchesSlug(pc, params.classSlug)) ?? null,
    [practicalClasses, params.classSlug],
  );

  const isBoard = track?.category === 'school_board';
  const theoryReady = classCourses.length > 0;
  const practicalReady = Boolean(practical && practical.subject_count > 0);
  const classLabel = classCourses[0]?.academic_class
    ? formatAcademicClass(classCourses[0].academic_class)
    : classSlugToLabel(params.classSlug);

  if (loading) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-6 sm:px-6 lg:px-8">
        <div className="h-40 animate-pulse rounded-card border border-border bg-card" />
        <div className="mt-6 space-y-3">
          {[1, 2].map((item) => (
            <div key={item} className="h-28 animate-pulse rounded-card border border-border bg-card" />
          ))}
        </div>
      </div>
    );
  }
  if (error === 'not_found' || (track && !isBoard)) return <NotFoundError resource="Class" />;
  if (error === 'network') return <NetworkError onRetry={load} />;
  if (!track) return null;

  return (
    <div className="mx-auto max-w-4xl px-4 py-6 sm:px-6 lg:px-8">
      <nav className="mb-4 flex flex-wrap items-center gap-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
        <Link href="/tracks" className="rounded hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring">
          Learning Tracks
        </Link>
        <span aria-hidden="true">/</span>
        <Link href={`/tracks/${track.slug}`} className="rounded hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring">
          {track.title}
        </Link>
        <span aria-hidden="true">/</span>
        <span className="text-foreground">{classLabel}</span>
      </nav>

      <header className="rounded-card border border-border bg-hero-navy p-6 text-white sm:p-8">
        <p className="text-xs font-bold uppercase tracking-[0.14em] text-white/60">
          {track.title} · Computer Science
        </p>
        <h1 className="mt-2 text-2xl font-bold sm:text-3xl">{classLabel}</h1>
        <p className="mt-2 max-w-2xl text-sm text-white/70">
          Study the {classLabel} theory and complete the matching practical work — both live
          together inside this class of the Sindh Board curriculum.
        </p>
      </header>

      {/* Theory & Courses */}
      <section aria-labelledby="theory-heading" className="mt-6 rounded-card border border-border bg-card p-6">
        <div className="flex items-center gap-2">
          <BookOpen aria-hidden="true" className="h-5 w-5 text-primary" />
          <h2 id="theory-heading" className="text-lg font-bold text-foreground">Theory &amp; Courses</h2>
        </div>
        {theoryReady ? (
          <>
            <p className="mt-1 text-sm text-muted-foreground">
              Chapters and lessons, taught in the recommended order.
            </p>
            <ul className="mt-4 space-y-3">
              {classCourses.map((course) => (
                <TheoryCard key={course.id} course={course} signedIn={isAuthenticated} />
              ))}
            </ul>
          </>
        ) : (
          <div className="mt-3 rounded-card border border-dashed border-border bg-muted/40 p-6 text-center">
            <h3 className="font-semibold text-foreground">Theory not published yet</h3>
            <p className="mt-1 text-sm text-muted-foreground">
              This class&apos;s lessons appear here once they have been verified against the textbook.
            </p>
          </div>
        )}
      </section>

      {/* Practicals */}
      <section aria-labelledby="practicals-heading" className="mt-6 rounded-card border border-border bg-card p-6">
        <div className="flex items-center gap-2">
          <FlaskConical aria-hidden="true" className="h-5 w-5 text-cta" />
          <h2 id="practicals-heading" className="text-lg font-bold text-foreground">Practicals</h2>
        </div>
        {practicalReady && practical ? (
          <>
            <p className="mt-1 text-sm text-muted-foreground">
              Curriculum lab work for {classLabel}, organized by subject.
            </p>
            <Link
              href={`/learn/practicals/${practical.slug}`}
              className="focus-ring mt-4 flex items-center justify-between gap-3 rounded-card border border-border bg-card p-4 transition-colors hover:border-primary/50"
            >
              <span className="flex items-center gap-3">
                <ClipboardCheck aria-hidden="true" className="h-6 w-6 text-cta" />
                <span>
                  <span className="block font-bold text-foreground">{practical.title} Practicals</span>
                  <span className="block text-sm text-muted-foreground">
                    {practical.subject_count} subject{practical.subject_count === 1 ? '' : 's'}
                  </span>
                </span>
              </span>
              <span className="inline-flex items-center gap-1 text-sm font-semibold text-primary">
                Open practicals
                <ArrowRight aria-hidden="true" className="h-4 w-4" />
              </span>
            </Link>
          </>
        ) : (
          <div className="mt-3 rounded-card border border-dashed border-border bg-muted/40 p-6 text-center">
            <h3 className="font-semibold text-foreground">Practicals not published yet</h3>
            <p className="mt-1 text-sm text-muted-foreground">
              Verified practical work for {classLabel} will appear here once it is published.
            </p>
          </div>
        )}
      </section>
    </div>
  );
}
