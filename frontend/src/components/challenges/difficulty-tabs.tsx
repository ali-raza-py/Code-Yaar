"use client";

import { Check, Circle } from "lucide-react";

export type Difficulty = "all" | "beginner" | "intermediate" | "advanced";

interface DifficultyTabsProps {
  value: Difficulty;
  onChange: (value: Difficulty) => void;
}

const options: Array<{ value: Difficulty; label: string; color?: string }> = [
  { value: "all", label: "All" },
  { value: "beginner", label: "Beginner", color: "text-emerald-600" },
  { value: "intermediate", label: "Intermediate", color: "text-amber-600" },
  { value: "advanced", label: "Advanced", color: "text-rose-600" },
];

export function DifficultyTabs({ value, onChange }: DifficultyTabsProps) {
  return (
    <div
      aria-label="Difficulty"
      className="inline-flex min-h-10 items-center rounded-lg border border-[var(--challenge-border)] bg-[var(--challenge-surface)] p-1"
      role="group"
    >
      {options.map((option) => {
        const selected = value === option.value;
        return (
          <button
            key={option.value}
            type="button"
            aria-pressed={selected}
            onClick={() => onChange(option.value)}
            className={`inline-flex min-h-8 items-center gap-1.5 rounded-md px-2.5 text-xs font-semibold transition-colors duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--challenge-accent)] sm:px-3 ${
              selected
                ? "bg-[var(--challenge-accent-soft)] text-[var(--challenge-accent-strong)]"
                : "text-[var(--challenge-muted)] hover:bg-[var(--challenge-surface-muted)] hover:text-[var(--challenge-text)]"
            }`}
          >
            {option.value === "all" ? (
              selected ? <Check aria-hidden="true" className="h-3.5 w-3.5" /> : <Circle aria-hidden="true" className="h-3 w-3" />
            ) : (
              <span aria-hidden="true" className={`h-1.5 w-1.5 rounded-full bg-current ${option.color}`} />
            )}
            {option.label}
          </button>
        );
      })}
    </div>
  );
}
