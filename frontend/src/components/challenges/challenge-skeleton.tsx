export function ChallengeSkeleton() {
  return (
    <div className="min-h-[220px] animate-pulse rounded-xl border border-[var(--challenge-border)] bg-[var(--challenge-surface)] p-5">
      <div className="flex justify-between"><div className="h-6 w-20 rounded-full bg-[var(--challenge-surface-muted)]" /><div className="h-4 w-16 rounded bg-[var(--challenge-surface-muted)]" /></div>
      <div className="mt-6 h-5 w-3/4 rounded bg-[var(--challenge-surface-muted)]" />
      <div className="mt-3 h-3 w-full rounded bg-[var(--challenge-surface-muted)]" />
      <div className="mt-2 h-3 w-2/3 rounded bg-[var(--challenge-surface-muted)]" />
      <div className="mt-8 border-t border-[var(--challenge-border)] pt-4"><div className="h-4 w-1/2 rounded bg-[var(--challenge-surface-muted)]" /></div>
    </div>
  );
}
