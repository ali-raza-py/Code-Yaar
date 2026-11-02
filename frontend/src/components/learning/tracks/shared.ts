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

/**
 * Collapse an arbitrary class identifier to a canonical URL slug segment.
 * "Class X" / "class-x" / "Class-X " all reduce to "class-x", so a track's
 * `academic_class` and a `PracticalClass` slug/title can be matched without a
 * database relationship. Roman numerals (X, XI, XII) survive as-is.
 */
export function canonicalClassSlug(value: string): string {
  return value
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

/**
 * Pretty label for a canonical class slug: "class-xi" -> "Class XI". The roman
 * numeral is upper-cased so route segments read like the textbook, not a slug.
 */
export function classSlugToLabel(slug: string): string {
  const parts = slug.split('-').filter(Boolean);
  if (parts.length === 0) return '';
  const head = parts.slice(0, -1);
  const tail = parts[parts.length - 1].toUpperCase();
  const words = [...head.map((word) => word.replace(/\b\w/g, (c) => c.toUpperCase())), tail];
  return words.join(' ');
}

/** True when a `PracticalClass` slug/title refers to the same class as `slug`. */
export function practicalClassMatchesSlug(
  practicalClass: { slug: string; title: string },
  slug: string,
): boolean {
  const target = canonicalClassSlug(slug);
  return canonicalClassSlug(practicalClass.slug) === target
    || canonicalClassSlug(practicalClass.title) === target;
}
