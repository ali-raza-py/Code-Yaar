"use client";

import { Search, SlidersHorizontal, X } from "lucide-react";
import { DifficultyTabs, type Difficulty } from "./difficulty-tabs";

export type SortOrder = "newest" | "difficulty" | "solved";

interface FilterBarProps {
  search: string;
  difficulty: Difficulty;
  sort: SortOrder;
  onSearchChange: (value: string) => void;
  onDifficultyChange: (value: Difficulty) => void;
  onSortChange: (value: SortOrder) => void;
  onClearSearch: () => void;
  onOpenFilters: () => void;
}

export function FilterBar({
  search,
  difficulty,
  sort,
  onSearchChange,
  onDifficultyChange,
  onSortChange,
  onClearSearch,
  onOpenFilters,
}: FilterBarProps) {
  return (
    <div className="sticky top-0 z-20 -mx-4 border-y border-[var(--challenge-border)] bg-[var(--challenge-bg)]/95 px-4 py-3 backdrop-blur sm:-mx-6 sm:px-6 lg:top-3 lg:rounded-xl lg:border">
      <div className="flex flex-col gap-3 lg:flex-row lg:items-center">
        <label className="relative flex min-h-10 min-w-0 flex-1 items-center">
          <Search aria-hidden="true" className="pointer-events-none absolute left-3 h-4 w-4 text-[var(--challenge-muted)]" />
          <input
            aria-label="Search challenges"
            value={search}
            onChange={(event) => onSearchChange(event.target.value)}
            placeholder="Search challenges"
            className="h-10 w-full rounded-lg border border-[var(--challenge-border)] bg-[var(--challenge-surface)] pl-9 pr-16 text-sm text-[var(--challenge-text)] outline-none transition-colors placeholder:text-[var(--challenge-muted)] focus:border-[var(--challenge-accent)] focus:ring-2 focus:ring-[var(--challenge-accent)]/15"
          />
          {search ? (
            <button type="button" aria-label="Clear search" onClick={onClearSearch} className="absolute right-9 rounded p-1 text-[var(--challenge-muted)] hover:text-[var(--challenge-text)]">
              <X aria-hidden="true" className="h-4 w-4" />
            </button>
          ) : (
            <kbd className="pointer-events-none absolute right-3 hidden rounded border border-[var(--challenge-border)] px-1.5 py-0.5 text-[10px] font-semibold text-[var(--challenge-muted)] sm:inline-block">/</kbd>
          )}
        </label>
        <div className="flex items-center gap-2 overflow-x-auto">
          <div className="hidden lg:block"><DifficultyTabs value={difficulty} onChange={onDifficultyChange} /></div>
          <button type="button" onClick={onOpenFilters} className="inline-flex min-h-10 items-center gap-2 rounded-lg border border-[var(--challenge-border)] bg-[var(--challenge-surface)] px-3 text-xs font-semibold text-[var(--challenge-muted)] hover:text-[var(--challenge-text)] lg:hidden">
            <SlidersHorizontal aria-hidden="true" className="h-4 w-4" />
            Filters
          </button>
          <label className="flex min-h-10 shrink-0 items-center gap-2 rounded-lg border border-[var(--challenge-border)] bg-[var(--challenge-surface)] px-3 text-xs font-semibold text-[var(--challenge-muted)]">
            <span className="hidden sm:inline">Sort</span>
            <select aria-label="Sort challenges" value={sort} onChange={(event) => onSortChange(event.target.value as SortOrder)} className="bg-transparent text-[var(--challenge-text)] outline-none">
              <option value="newest">Newest</option>
              <option value="difficulty">Difficulty</option>
              <option value="solved">Most solved</option>
            </select>
          </label>
        </div>
      </div>
      <div className="mt-3 overflow-x-auto lg:hidden [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
        <DifficultyTabs value={difficulty} onChange={onDifficultyChange} />
      </div>
    </div>
  );
}
