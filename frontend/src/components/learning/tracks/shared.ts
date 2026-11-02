/**
 * Shared presentation helpers for the Tracks discovery layer. Labels and
 * tones live here so the list and detail pages never drift apart. The tone
 * itself defers to the single governed difficulty primitive.
 */
import { difficultyTone } from '@/components/ui/difficulty-pill';

/** Governed pill classes for a track/course difficulty value. */
export function trackDifficultyTone(difficulty: string): string {
  return difficultyTone(difficulty);
}

/** "Class X" reads better as a section label than "class x" ever would. */
export function formatAcademicClass(value: string): string {
  return value.replace(/\b\w/g, (char) => char.toUpperCase());
}
