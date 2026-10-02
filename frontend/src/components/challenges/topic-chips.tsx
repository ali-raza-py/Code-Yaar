"use client";

import { Check } from "lucide-react";

interface TopicChipsProps {
  topics: string[];
  value: string;
  showAll: boolean;
  onChange: (topic: string) => void;
  onToggleShowAll: () => void;
}

export function TopicChips({ topics, value, showAll, onChange, onToggleShowAll }: TopicChipsProps) {
  const visibleTopics = showAll ? topics : topics.slice(0, 7);
  const hiddenCount = Math.max(0, topics.length - visibleTopics.length);

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between gap-3">
        <p className="text-xs font-semibold uppercase tracking-[0.12em] text-[var(--challenge-muted)]">Topics</p>
        {topics.length > 7 && (
          <button
            type="button"
            onClick={onToggleShowAll}
            className="min-h-9 shrink-0 rounded-md px-2 text-xs font-semibold text-[var(--challenge-accent-strong)] transition-colors hover:bg-[var(--challenge-accent-soft)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--challenge-accent)]"
          >
            {showAll ? "Show fewer" : `+${hiddenCount} more`}
          </button>
        )}
      </div>
      <div className="relative -mx-1 overflow-hidden">
        <div className="pointer-events-none absolute inset-y-0 left-0 z-10 w-5 bg-gradient-to-r from-[var(--challenge-bg)] to-transparent sm:hidden" />
        <div className="pointer-events-none absolute inset-y-0 right-0 z-10 w-5 bg-gradient-to-l from-[var(--challenge-bg)] to-transparent sm:hidden" />
        <div className="flex snap-x gap-2 overflow-x-auto px-1 pb-1 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
          {visibleTopics.map((topic) => {
            const selected = value === topic;
            return (
              <button
                key={topic}
                type="button"
                aria-pressed={selected}
                onClick={() => onChange(topic)}
                className={`inline-flex min-h-9 shrink-0 snap-start items-center gap-1.5 rounded-full border px-3 text-xs font-semibold transition-colors duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--challenge-accent)] ${
                  selected
                    ? "border-[var(--challenge-accent)] bg-[var(--challenge-accent)] text-white"
                    : "border-[var(--challenge-border)] bg-[var(--challenge-surface)] text-[var(--challenge-muted)] hover:border-[var(--challenge-accent)]/50 hover:text-[var(--challenge-text)]"
                }`}
              >
                {selected && <Check aria-hidden="true" className="h-3.5 w-3.5" />}
                {topic}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
