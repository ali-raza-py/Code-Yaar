import Link from "next/link";
import { ArrowUpRight, Circle, CheckCircle2, Clock3, MinusCircle } from "lucide-react";
import type { Challenge } from "@/types";

interface ChallengeCardProps {
  challenge: Challenge;
  acceptanceRate: number;
  solved?: boolean;
}

const difficultyStyles = {
  beginner: "bg-emerald-50 text-emerald-700",
  intermediate: "bg-amber-50 text-amber-700",
  advanced: "bg-rose-50 text-rose-700",
};

export function ChallengeCard({ challenge, acceptanceRate, solved = false }: ChallengeCardProps) {
  return (
    <article className="group flex min-h-[220px] flex-col rounded-xl border border-[var(--challenge-border)] bg-[var(--challenge-surface)] p-5 shadow-[var(--challenge-shadow)] transition-all duration-200 ease-out hover:-translate-y-0.5 hover:border-[var(--challenge-accent)]/45 hover:shadow-[var(--challenge-shadow-hover)]">
      <div className="flex items-center justify-between gap-3">
        <span className={`rounded-full px-2.5 py-1 text-[11px] font-bold capitalize ${difficultyStyles[challenge.difficulty]}`}>
          {challenge.difficulty}
        </span>
        <span className="inline-flex items-center gap-1.5 text-xs text-[var(--challenge-muted)]">
          {solved ? <CheckCircle2 aria-label="Solved" className="h-4 w-4 text-emerald-600" /> : <Circle aria-label="Unsolved" className="h-4 w-4" />}
          {solved ? "Solved" : "Open"}
        </span>
      </div>
      <div className="mt-5 flex-1">
        <h2 className="text-base font-bold tracking-tight text-[var(--challenge-text)]">{challenge.title}</h2>
        <p className="mt-2 line-clamp-2 text-sm leading-6 text-[var(--challenge-muted)]">{challenge.description}</p>
      </div>
      <div className="mt-5 flex items-center justify-between border-t border-[var(--challenge-border)] pt-4 text-xs text-[var(--challenge-muted)]">
        <div className="flex items-center gap-3">
          <span className="rounded-md bg-[var(--challenge-surface-muted)] px-2 py-1 font-semibold text-[var(--challenge-text-soft)]">{challenge.topic}</span>
          <span className="inline-flex items-center gap-1"><Clock3 aria-hidden="true" className="h-3.5 w-3.5" />{challenge.estimated_minutes}m</span>
          <span>{acceptanceRate}% accepted</span>
        </div>
        <Link href={`/challenges/${challenge.slug}`} aria-label={`Start ${challenge.title}`} className="inline-flex min-h-9 items-center gap-1 rounded-md px-2.5 font-bold text-[var(--challenge-accent-strong)] opacity-75 transition-all group-hover:opacity-100 hover:bg-[var(--challenge-accent-soft)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--challenge-accent)]">
          Start <ArrowUpRight aria-hidden="true" className="h-3.5 w-3.5" />
        </Link>
      </div>
    </article>
  );
}
