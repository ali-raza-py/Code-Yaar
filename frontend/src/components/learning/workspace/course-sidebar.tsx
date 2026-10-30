'use client';

import Link from 'next/link';
import { Chapter, LessonStatus } from '@/types';

interface CourseSidebarProps {
  chapters: Chapter[];
  courseSlug: string;
  currentLessonId: number;
  isOpen: boolean;
  onToggle: () => void;
  courseProgress: number;
  courseTitle: string;
}

function StatusIcon({ status }: { status: LessonStatus }) {
  switch (status) {
    case 'completed':
    case 'mastered':
      return (
        <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-cta text-cta-fg">
          <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" strokeWidth={3} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
          </svg>
        </span>
      );
    case 'in_progress':
      return (
        <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full border-2 border-cta bg-card">
          <span className="h-2 w-2 rounded-full bg-cta" />
        </span>
      );
    default:
      return (
        <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full border border-border bg-card" />
      );
  }
}

export default function CourseSidebar({
  chapters,
  courseSlug,
  currentLessonId,
  isOpen,
  onToggle,
  courseProgress,
  courseTitle,
}: CourseSidebarProps) {
  if (!isOpen) return null;

  return (
    <aside className="fixed inset-y-0 left-0 z-40 flex w-72 max-w-[82%] shrink-0 flex-col overflow-hidden border-r border-border bg-card lg:static lg:z-auto lg:w-64 lg:max-w-none">
      {/* Course Header */}
      <div className="border-b border-border px-4 py-3">
        <div className="flex items-center justify-between">
          <h2 className="truncate text-sm font-semibold text-foreground">{courseTitle}</h2>
          <button
            onClick={onToggle}
            aria-label="Collapse course navigation"
            className="focus-ring rounded-md p-1 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
            </svg>
          </button>
        </div>
        {/* Progress */}
        <div className="mt-2">
          <div className="mb-1 flex items-center justify-between text-xs text-muted-foreground">
            <span>Course Progress</span>
            <span className="font-medium text-foreground">{courseProgress}%</span>
          </div>
          <div
            className="h-1.5 w-full overflow-hidden rounded-full bg-muted"
            role="progressbar"
            aria-valuenow={courseProgress}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-label="Course progress"
          >
            <div
              className="h-full rounded-full bg-cta transition-all duration-500"
              style={{ width: `${courseProgress}%` }}
            />
          </div>
        </div>
      </div>

      {/* Chapter/Lesson List */}
      <nav className="flex-1 overflow-y-auto px-2 py-2">
        {chapters.map((chapter) => (
          <div key={chapter.id} className="mb-3">
            {/* Chapter Header */}
            <div className="flex items-center gap-2 px-2 py-1.5">
              <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-[var(--radius-tool)] bg-muted text-[10px] font-bold text-muted-foreground">
                {chapter.order}
              </span>
              <span className="truncate text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                {chapter.title}
              </span>
              {chapter.progress_percentage === 100 && (
                <svg className="ml-auto h-3.5 w-3.5 shrink-0 text-cta" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              )}
            </div>

            {/* Lessons */}
            <ul className="space-y-0.5">
              {chapter.lessons.map((lesson) => {
                const isCurrent = lesson.id === currentLessonId;
                const done = lesson.progress_status === 'completed' || lesson.progress_status === 'mastered';
                return (
                  <li key={lesson.id}>
                    <Link
                      href={`/learn/${courseSlug}?lesson=${lesson.slug}`}
                      aria-current={isCurrent ? 'true' : undefined}
                      className={`focus-ring flex items-center gap-2.5 rounded-md px-2 py-1.5 text-sm transition-colors ${
                        isCurrent
                          ? 'bg-cta/10 font-medium text-[var(--difficulty-easy)]'
                          : done
                          ? 'text-muted-foreground hover:bg-muted'
                          : 'text-muted-foreground hover:bg-muted'
                      }`}
                    >
                      <StatusIcon status={lesson.progress_status} />
                      <span className="truncate">{lesson.title}</span>
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </nav>
    </aside>
  );
}
