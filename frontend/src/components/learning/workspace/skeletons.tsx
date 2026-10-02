'use client';

/**
 * Skeleton loading states (spec §44)
 *
 * Prevent layout shift by rendering placeholder structures
 * that match the dimensions of the actual content.
 */

// ─── Course Sidebar Skeleton ────────────────────────────────────────────────

export function CourseSidebarSkeleton() {
  return (
    <aside className="flex w-64 shrink-0 flex-col border-r border-gray-200 bg-white overflow-hidden animate-pulse">
      <div className="border-b border-gray-200 px-4 py-3">
        <div className="h-4 w-32 rounded bg-gray-200" />
        <div className="mt-3 h-1.5 w-full rounded-full bg-gray-200" />
      </div>
      <div className="flex-1 px-2 py-2 space-y-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i}>
            <div className="h-3 w-20 rounded bg-gray-200 mb-2" />
            <div className="space-y-1.5 pl-2">
              <div className="h-3 w-28 rounded bg-gray-100" />
              <div className="h-3 w-24 rounded bg-gray-100" />
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
    <div className="px-6 py-6 max-w-2xl mx-auto animate-pulse">
      <div className="mb-6">
        <div className="h-3 w-24 rounded bg-gray-200 mb-3" />
        <div className="h-7 w-48 rounded bg-gray-200 mb-3" />
        <div className="h-3 w-72 rounded bg-gray-100 mb-4" />
        <div className="flex gap-3">
          <div className="h-5 w-16 rounded-full bg-gray-200" />
          <div className="h-5 w-12 rounded bg-gray-100" />
        </div>
      </div>
      <div className="space-y-3">
        <div className="h-3 w-full rounded bg-gray-100" />
        <div className="h-3 w-5/6 rounded bg-gray-100" />
        <div className="h-3 w-4/6 rounded bg-gray-100" />
        <div className="h-24 w-full rounded-lg bg-gray-100 mt-4" />
        <div className="h-3 w-full rounded bg-gray-100" />
        <div className="h-3 w-3/4 rounded bg-gray-100" />
      </div>
    </div>
  );
}

// ─── Code Editor Skeleton ───────────────────────────────────────────────────

export function CodeEditorSkeleton() {
  return (
    <div className="flex h-full flex-col bg-[#1e1e2e] animate-pulse">
      <div className="flex items-center gap-2 border-b border-gray-700 bg-[#181825] px-3 py-1.5">
        <div className="h-3 w-3 rounded bg-gray-700" />
        <div className="h-3 w-16 rounded bg-gray-700" />
      </div>
      <div className="flex flex-1">
        <div className="w-10 shrink-0 bg-[#181825] pt-3 space-y-2 pr-2">
          {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
            <div key={i} className="h-3 w-4 rounded bg-gray-800 ml-auto" />
          ))}
        </div>
        <div className="flex-1 p-3 space-y-2">
          {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
            <div key={i} className="h-3 rounded bg-gray-800" style={{ width: `${30 + Math.random() * 50}%` }} />
          ))}
        </div>
      </div>
    </div>
  );
}

// ─── Exercise Panel Skeleton ────────────────────────────────────────────────

export function ExercisePanelSkeleton() {
  return (
    <div className="border-b border-gray-200 bg-white p-4 animate-pulse max-h-[240px] overflow-hidden">
      <div className="flex items-center justify-between mb-3">
        <div className="h-4 w-28 rounded bg-gray-200" />
        <div className="h-4 w-12 rounded-full bg-gray-100" />
      </div>
      <div className="space-y-2">
        <div className="h-3 w-full rounded bg-gray-100" />
        <div className="h-3 w-4/5 rounded bg-gray-100" />
        <div className="h-3 w-3/5 rounded bg-gray-100" />
      </div>
    </div>
  );
}

// ─── Course Card Skeleton ───────────────────────────────────────────────────

export function CourseCardSkeleton() {
  return (
    <div className="rounded-xl border border-gray-200 bg-white overflow-hidden animate-pulse">
      <div className="h-40 bg-gray-200" />
      <div className="p-4 space-y-2">
        <div className="h-4 w-16 rounded-full bg-gray-200" />
        <div className="h-5 w-48 rounded bg-gray-200" />
        <div className="h-3 w-full rounded bg-gray-100" />
        <div className="h-3 w-2/3 rounded bg-gray-100" />
        <div className="flex gap-2 mt-3">
          <div className="h-4 w-12 rounded bg-gray-100" />
          <div className="h-4 w-12 rounded bg-gray-100" />
          <div className="h-4 w-12 rounded bg-gray-100" />
        </div>
      </div>
    </div>
  );
}

// ─── Dashboard Skeleton ─────────────────────────────────────────────────────

export function DashboardSkeleton() {
  return (
    <div className="min-h-screen bg-gray-50 p-6 animate-pulse">
      <div className="mx-auto max-w-5xl">
        <div className="h-7 w-48 rounded bg-gray-200 mb-4" />
        <div className="h-2 w-full max-w-md rounded bg-gray-200 mb-8" />
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <div className="h-40 rounded-xl bg-gray-200" />
            <div className="h-60 rounded-xl bg-gray-200" />
          </div>
          <div className="space-y-6">
            <div className="h-48 rounded-xl bg-gray-200" />
            <div className="h-32 rounded-xl bg-gray-200" />
          </div>
        </div>
      </div>
    </div>
  );
}
