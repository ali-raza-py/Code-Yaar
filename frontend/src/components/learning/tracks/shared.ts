/**
 * Shared presentation helpers for the Tracks discovery layer. Labels and
 * tones live here so the list and detail pages never drift apart.
 */

const DIFFICULTY_TONES: Record<string, string> = {
  beginner: 'bg-difficulty-easy-soft text-difficulty-easy',
  intermediate: 'bg-difficulty-medium-soft text-difficulty-medium',
  advanced: 'bg-difficulty-hard-soft text-difficulty-hard',
};

/** Governed pill classes for a track/course difficulty value. */
export function trackDifficultyTone(difficulty: string): string {
  return DIFFICULTY_TONES[difficulty] ?? 'bg-muted text-muted-foreground';
}

/** "Class X" reads better as a section label than "class x" ever would. */
export function formatAcademicClass(value: string): string {
  return value.replace(/\b\w/g, (char) => char.toUpperCase());
}
