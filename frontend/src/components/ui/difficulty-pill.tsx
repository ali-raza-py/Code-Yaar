/**
 * Single governed difficulty pill. Badge difficulty uses the
 * `beginner|intermediate|advanced` vocabulary while courses/challenges use
 * `easy|medium|hard`; both map onto the same design tokens so every surface
 * stays consistent. No raw hex here — the colours come from the Tailwind
 * `--difficulty-*` tokens defined in the stylesheet.
 */

const DIFFICULTY_TONES: Record<string, string> = {
  beginner: 'bg-difficulty-easy-soft text-difficulty-easy',
  easy: 'bg-difficulty-easy-soft text-difficulty-easy',
  intermediate: 'bg-difficulty-medium-soft text-difficulty-medium',
  medium: 'bg-difficulty-medium-soft text-difficulty-medium',
  advanced: 'bg-difficulty-hard-soft text-difficulty-hard',
  hard: 'bg-difficulty-hard-soft text-difficulty-hard',
};

/** Governed pill classes for any difficulty value across the app. */
export function difficultyTone(difficulty: string): string {
  const key = (difficulty ?? '').toLowerCase();
  return DIFFICULTY_TONES[key] ?? 'bg-muted text-muted-foreground';
}

interface DifficultyPillProps {
  difficulty: string;
  /** Override the visible label (defaults to the raw difficulty value). */
  label?: string;
  size?: 'sm' | 'md';
  className?: string;
}

export function DifficultyPill({
  difficulty,
  label,
  size = 'md',
  className = '',
}: DifficultyPillProps) {
  const tone = difficultyTone(difficulty);
  const sizing = size === 'sm' ? 'px-2 py-0.5 text-[10px]' : 'px-2.5 py-1 text-[11px]';
  return (
    <span
      className={`inline-flex items-center rounded-pill font-bold capitalize ${sizing} ${tone} ${className}`.trim()}
    >
      {label ?? difficulty}
    </span>
  );
}
