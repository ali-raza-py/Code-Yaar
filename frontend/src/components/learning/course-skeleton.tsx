'use client';

export function CourseSkeleton() {
  return (
    <div className="group overflow-hidden rounded-[var(--radius-card)] border border-[#334155] bg-[#0f172a] text-[#f8fafc] transition-[border-color,box-shadow] duration-200 hover:border-primary/30 hover:shadow-[var(--shadow-1)]">
      <div className="h-1.5 bg-primary/80" />
      <div className="p-5">
        <div className="flex items-center justify-between gap-4 text-xs font-medium uppercase tracking-wide text-[#94a3b8]">
          <div className="h-4 w-20 rounded bg-[#1e293b] animate-pulse" />
          <div className="h-4 w-16 rounded bg-[#1e293b] animate-pulse" />
        </div>
        <h2 className="mt-3 text-lg font-semibold text-[#f8fafc] animate-pulse" />
        <p className="mt-2 line-clamp-2 text-sm leading-6 text-[#cbd5e1] animate-pulse" />
        <div className="mt-5 flex items-center justify-between text-xs text-[#94a3b8]">
          <div className="h-4 w-1/3 rounded bg-[#1e293b] animate-pulse" />
          <div className="h-4 w-1/3 rounded bg-[#1e293b] animate-pulse" />
        </div>
      </div>
    </div>
  );
}
