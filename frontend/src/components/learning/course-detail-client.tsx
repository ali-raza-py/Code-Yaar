'use client';

import Link from 'next/link';
import { useState } from 'react';
import { useAuth } from '@/hooks/use-auth';
import { Course, Chapter } from '@/types';
import { DifficultyPill } from '@/components/ui/difficulty-pill';
import { EnrollButton } from '@/components/learning/enroll-button';

interface ChapterRowProps {
  chapter: Chapter;
  index: number;
}

function ChapterRow({ chapter, index }: ChapterRowProps) {
  const [expanded, setExpanded] = useState(false);
  const num = String(index + 1).padStart(2, '0');

  return (
    <div className="border-b border-border last:border-0">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex w-full items-center gap-4 px-5 py-4 text-left hover:bg-muted transition-colors"
      >
        <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-muted text-sm font-semibold text-muted-foreground">
          {num}
        </span>
        <div className="flex-1 min-w-0">
          <h3 className="text-sm font-semibold text-foreground">{chapter.title}</h3>
          <p className="text-xs text-muted-foreground mt-0.5">
            {chapter.lessons.length} lessons · {chapter.xp_reward} XP
          </p>
        </div>
        <svg
          className={`h-4 w-4 text-muted-foreground transition-transform ${expanded ? 'rotate-180' : ''}`}
          fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
        </svg>
      </button>
      {expanded && (
        <div className="px-5 pb-4 pl-17">
          <ul className="space-y-2">
            {chapter.lessons.map((lesson) => (
              <li key={lesson.id} className="flex items-center gap-3 text-sm">
                <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full border border-input text-[10px] text-muted-foreground">
                  {lesson.order}
                </span>
                <span className="text-foreground">{lesson.title}</span>
                <span className="ml-auto text-xs text-muted-foreground">{lesson.duration_minutes}m</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export function CourseDetailClient({ course }: { course: Course }) {
  const { user } = useAuth();

  const chapters = course.chapters ?? [];
  const firstLessonSlug = chapters[0]?.lessons[0]?.slug;

  return (
    <div className="min-h-screen bg-background">
      {/* ── Hero / Course Header ─────────────────────────────────── */}
      <section className="border-b border-border bg-gradient-to-b from-muted/50 to-background">
        <div className="mx-auto max-w-4xl px-4 py-10 sm:px-6 lg:px-8">
          {/* Breadcrumb */}
          <nav className="mb-6 flex items-center gap-2 text-sm text-muted-foreground">
            <Link href="/courses" className="hover:text-foreground">Courses</Link>
            <span>/</span>
            <span className="text-foreground">{course.track_title}</span>
          </nav>

          {/* Title area */}
          <div className="mb-4">
            <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              {course.track_title}
            </span>
          </div>
          <h1 className="text-3xl font-bold text-foreground sm:text-4xl">
            {course.title}
          </h1>
          <p className="mt-3 text-lg text-muted-foreground max-w-2xl">
            {course.description}
          </p>

          {/* CTAs */}
          <div className="mt-6 flex flex-wrap items-center gap-3">
            <EnrollButton course={course} user={user} />
            {firstLessonSlug && (
              <Link
                href={`/courses/${course.slug}/lesson/${firstLessonSlug}`}
                className="inline-flex items-center rounded-lg border border-border px-5 py-2.5 text-sm font-semibold text-foreground hover:bg-muted transition-colors"
              >
                Preview first lesson
              </Link>
            )}
          </div>

          {/* Meta */}
          <div className="mt-6 flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
            <DifficultyPill difficulty={course.difficulty} />
            <span>{course.estimated_hours} hours</span>
            <span>{chapters.length} Chapters</span>
            <span>{course.lesson_count} Lessons</span>
            <span>{course.exercise_count} Exercises</span>
            <span>{course.total_xp.toLocaleString()} XP</span>
          </div>
        </div>
      </section>

      {/* ── What You'll Learn ────────────────────────────────────── */}
      <section className="border-b border-border">
        <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
          <h2 className="text-lg font-semibold text-foreground mb-4">What you&apos;ll learn</h2>
          {course.learning_objectives.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {course.learning_objectives.map((obj, i) => (
                <div key={i} className="flex items-start gap-2.5">
                  <svg className="h-4 w-4 shrink-0 text-success" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                  </svg>
                  <span className="text-sm text-foreground">{obj}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">Learning objectives haven&apos;t been published for this course yet.</p>
          )}
        </div>
      </section>

      {/* ── Course Roadmap ───────────────────────────────────────── */}
      <section className="border-b border-border">
        <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
          <h2 className="text-lg font-semibold text-foreground mb-4">Course roadmap</h2>
          {chapters.length === 0 ? (
            <p className="text-sm text-muted-foreground">The chapter outline hasn&apos;t been published for this course yet.</p>
          ) : (
            <div className="rounded-lg border border-border bg-card overflow-hidden">
              {chapters.map((chapter, index) => (
                <ChapterRow key={chapter.id} chapter={chapter} index={index} />
              ))}
            </div>
          )}
        </div>
      </section>

      {/* ── Course Details ───────────────────────────────────────── */}
      <section className="border-b border-border">
        <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
          <h2 className="text-lg font-semibold text-foreground mb-4">Course details</h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            <div>
              <dt className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Prerequisites</dt>
              <dd className="mt-1 text-sm text-foreground">{course.prerequisites}</dd>
            </div>
            <div>
              <dt className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Language</dt>
              <dd className="mt-1 text-sm text-foreground capitalize">{course.language}</dd>
            </div>
            <div>
              <dt className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Instructor</dt>
              <dd className="mt-1 text-sm text-foreground">{course.instructor || 'TBA'}</dd>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
