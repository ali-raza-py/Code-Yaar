'use client';

/**
 * Skeleton loading states (spec §44)
 *
 * Prevent layout shift by rendering placeholder structures
 * that match the dimensions of the actual content.
 * All colors are governed design tokens (light + dark aware).
 */

// ─── Course Sidebar Skeleton ────────────────────────────────────────────────

export function CourseSidebarSkeleton() {
  return (
    <aside className="flex w-64 shrink-0 flex-col animate-pulse overflow-hidden border-r border-border bg-card">
      <div className="border-b border-border px-4 py-3">
        <div className="h-4 w-32 rounded bg-muted" />
        <div className="mt-3 h-1.5 w-full rounded-full bg-muted" />
      </div>
      <div className="flex-1 space-y-4 px-2 py-2">
        {[1, 2, 3, 4].map((i) => (
          <div key={i}>
            <div className="mb-2 h-3 w-20 rounded bg-muted" />
            <div className="space-y-1.5 pl-2">
              <div className="h-3 w-28 rounded bg-muted/60" />
              <div className="h-3 w-24 rounded bg-muted/60" />
            </div>
          </div>
        ))}
      </div>
    </aside>
  );
}

// ─── Lesson Content Skeleton ────────────────────────────────────────────────

export function LessonContentSkeleton() {
  return (
    <div className="mx-auto max-w-2xl animate-pulse px-6 py-6">
      <div className="mb-6">
        <div className="mb-3 h-3 w-24 rounded bg-muted" />
        <div className="mb-3 h-7 w-48 rounded bg-muted" />
        <div className="mb-4 h-3 w-72 rounded bg-muted/60" />
        <div className="flex gap-3">
          <div className="h-5 w-16 rounded-pill bg-muted" />
          <div className="h-5 w-12 rounded bg-muted/60" />
        </div>
      </div>
      <div className="space-y-3">
        <div className="h-3 w-full rounded bg-muted/60" />
        <div className="h-3 w-5/6 rounded bg-muted/60" />
        <div className="h-3 w-4/6 rounded bg-muted/60" />
        <div className="mt-4 h-24 w-full rounded-[var(--radius-card)] bg-muted/60" />
        <div className="h-3 w-full rounded bg-muted/60" />
        <div className="h-3 w-3/4 rounded bg-muted/60" />
      </div>
    </div>
  );
}

// ─── Code Editor Skeleton ───────────────────────────────────────────────────

export function CodeEditorSkeleton() {
  return (
    <div className="flex h-full animate-pulse flex-col editor-surface">
      <div className="flex items-center gap-2 border-b border-[var(--editor-border)] bg-[var(--editor-chrome)] px-3 py-1.5">
        <div className="h-3 w-3 rounded bg-[var(--editor-border)]" />
        <div className="h-3 w-16 rounded bg-[var(--editor-border)]" />
      </div>
      <div className="flex flex-1">
        <div className="w-10 shrink-0 space-y-2 bg-[var(--editor-gutter)] pt-3 pr-2">
          {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
            <div key={i} className="ml-auto h-3 w-4 rounded bg-[var(--editor-border)]" />
          ))}
        </div>
        <div className="flex-1 space-y-2 p-3">
          {[62, 45, 78, 53, 88, 34, 70, 48].map((w, i) => (
            <div key={i} className="h-3 rounded bg-[var(--overlay-field)]" style={{ width: `${w}%` }} />
          ))}
        </div>
      </div>
    </div>
  );
}

// ─── Exercise Panel Skeleton ────────────────────────────────────────────────

export function ExercisePanelSkeleton() {
  return (
    <div className="max-h-[240px] animate-pulse overflow-hidden border-b border-[var(--editor-border)] bg-[var(--editor-chrome)] p-4">
      <div className="mb-3 flex items-center justify-between">
        <div className="h-4 w-28 rounded bg-[var(--editor-border)]" />
        <div className="h-4 w-12 rounded-pill bg-[var(--overlay-field)]" />
      </div>
      <div className="space-y-2">
        <div className="h-3 w-full rounded bg-[var(--overlay-field)]" />
        <div className="h-3 w-4/5 rounded bg-[var(--overlay-field)]" />
        <div className="h-3 w-3/5 rounded bg-[var(--overlay-field)]" />
      </div>
    </div>
  );
}

// ─── Course Card Skeleton ───────────────────────────────────────────────────

export function CourseCardSkeleton() {
  return (
    <div className="animate-pulse overflow-hidden rounded-[var(--radius-card)] border border-border bg-card">
      <div className="h-40 bg-muted" />
      <div className="space-y-2 p-4">
        <div className="h-4 w-16 rounded-pill bg-muted" />
        <div className="h-5 w-48 rounded bg-muted" />
        <div className="h-3 w-full rounded bg-muted/60" />
        <div className="h-3 w-2/3 rounded bg-muted/60" />
        <div className="mt-3 flex gap-2">
          <div className="h-4 w-12 rounded bg-muted/60" />
          <div className="h-4 w-12 rounded bg-muted/60" />
          <div className="h-4 w-12 rounded bg-muted/60" />
        </div>
      </div>
    </div>
  );
}

// ─── Dashboard Skeleton ─────────────────────────────────────────────────────

export function DashboardSkeleton() {
  return (
    <div className="min-h-screen animate-pulse bg-background p-6">
      <div className="mx-auto max-w-5xl">
        <div className="mb-4 h-7 w-48 rounded bg-muted" />
        <div className="mb-8 h-2 w-full max-w-md rounded bg-muted" />
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="space-y-6 lg:col-span-2">
            <div className="h-40 rounded-[var(--radius-card)] bg-muted" />
            <div className="h-60 rounded-[var(--radius-card)] bg-muted" />
          </div>
          <div className="space-y-6">
            <div className="h-48 rounded-[var(--radius-card)] bg-muted" />
            <div className="h-32 rounded-[var(--radius-card)] bg-muted" />
          </div>
        </div>
      </div>
    </div>
  );
}
