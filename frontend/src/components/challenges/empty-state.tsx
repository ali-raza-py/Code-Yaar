import Link from "next/link";
import { ArrowRight, RotateCcw, SearchX } from "lucide-react";

interface EmptyStateProps {
  filtered: boolean;
  onClear: () => void;
}

export function EmptyState({ filtered, onClear }: EmptyStateProps) {
  if (!filtered) {
    return (
      <section className="rounded-xl border border-dashed border-[var(--challenge-border)] bg-[var(--challenge-surface)] px-6 py-12 text-center">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full border border-[var(--challenge-border)] bg-[var(--challenge-surface-muted)] text-[var(--challenge-accent)]"><SearchX aria-hidden="true" className="h-5 w-5" /></div>
        <h2 className="mt-5 text-lg font-bold text-[var(--challenge-text)]">Challenges are coming soon</h2>
        <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-[var(--challenge-muted)]">We are preparing the first set of focused practice problems. Explore a learning track while the challenge library is being prepared.</p>
        <Link href="/learn" className="mt-5 inline-flex min-h-10 items-center gap-2 rounded-lg bg-[var(--challenge-accent)] px-4 text-sm font-bold text-white transition-colors hover:bg-[var(--challenge-accent-strong)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--challenge-accent)] focus-visible:ring-offset-2"><span>Explore tracks</span><ArrowRight aria-hidden="true" className="h-4 w-4" /></Link>
      </section>
    );
  }

  return (
    <section className="rounded-xl border border-dashed border-[var(--challenge-border)] bg-[var(--challenge-surface)] px-6 py-12 text-center">
      <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full border border-[var(--challenge-border)] bg-[var(--challenge-surface-muted)] text-[var(--challenge-muted)]"><SearchX aria-hidden="true" className="h-5 w-5" /></div>
      <h2 className="mt-5 text-lg font-bold text-[var(--challenge-text)]">No matching challenges</h2>
      <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-[var(--challenge-muted)]">Try a different topic or search term. Arrays, Strings, and Data Structures are popular starting points.</p>
      <button type="button" onClick={onClear} className="mt-5 inline-flex min-h-10 items-center gap-2 rounded-lg border border-[var(--challenge-border)] bg-[var(--challenge-surface)] px-4 text-sm font-bold text-[var(--challenge-text)] transition-colors hover:border-[var(--challenge-accent)] hover:text-[var(--challenge-accent-strong)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--challenge-accent)]"><RotateCcw aria-hidden="true" className="h-4 w-4" />Clear filters</button>
    </section>
  );
}
