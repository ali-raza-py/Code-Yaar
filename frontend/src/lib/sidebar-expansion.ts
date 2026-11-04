"use client";

import { useCallback, useSyncExternalStore } from "react";

/**
 * Sidebar expansion state for the app navigation, held outside React so it
 * survives route changes.
 *
 * Why a module store instead of component state: the student shell is mounted
 * by two different route groups — `/(app)` for Dashboard/Learn and
 * `/(discovery)` for Tracks/Leaderboard/Challenges — so crossing between them
 * remounts `AppSidebar` and wipes any `useState` it owns. Expansion then falls
 * back to its defaults and the learner sees branches reopen on their own. A
 * store keyed by node id keeps the choice exactly where it belongs: with the
 * click that made it.
 *
 * Persistence uses `sessionStorage`, so a fresh browser session starts from
 * the defaults below while tabs, reloads and navigation inside one session
 * keep the learner's arrangement.
 */

const STORAGE_KEY = "codeyaar:sidebar-expansion";

/** Node ids are stable strings derived from what the row actually points at. */
export const sidebarNode = {
  /** A collapsible section header, e.g. "Learn" / "Apply". */
  section: (label: string) => `section:${label}`,
  /** The nested "Learning Tracks" root row. */
  tracksRoot: "tracks:root",
  /** One track inside Learning Tracks (its classes are the subtracks). */
  track: (slug: string) => `track:${slug}`,
} as const;

// Rows that read better open on a first visit: the two section groups and the
// Learning Tracks root, so the tracks themselves stay reachable. Every track
// with subtracks starts collapsed and only a click opens it.
const EXPANDED_BY_DEFAULT: readonly string[] = [
  sidebarNode.section("Learn"),
  sidebarNode.section("Apply"),
  sidebarNode.tracksRoot,
];

/** Snapshot of stored choices. Replaced, never mutated, so React sees a new ref. */
let choices: Record<string, boolean> = {};
let restored = false;
const listeners = new Set<() => void>();

function readStoredChoices(): Record<string, boolean> {
  try {
    const raw = window.sessionStorage.getItem(STORAGE_KEY);
    if (!raw) return {};
    const parsed: unknown = JSON.parse(raw);
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) return {};
    return Object.fromEntries(
      Object.entries(parsed as Record<string, unknown>).filter(
        (entry): entry is [string, boolean] => typeof entry[1] === "boolean",
      ),
    );
  } catch {
    // Blocked or corrupt storage is not worth a broken sidebar.
    return {};
  }
}

function writeStoredChoices() {
  try {
    window.sessionStorage.setItem(STORAGE_KEY, JSON.stringify(choices));
  } catch {
    // The choice still holds for this visit when storage is unavailable.
  }
}

function notify() {
  listeners.forEach((listener) => listener());
}

function subscribe(listener: () => void) {
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
  };
}

/** Default arrangement, used for the server render and before restoration. */
function defaultExpanded(key: string): boolean {
  return EXPANDED_BY_DEFAULT.includes(key);
}

function isExpanded(key: string): boolean {
  return choices[key] ?? defaultExpanded(key);
}

/**
 * Lifts the stored arrangement into the snapshot. Called once after mount so
 * the first client render still matches the server-rendered defaults and no
 * hydration warning is raised.
 */
export function restoreSidebarExpansion() {
  if (restored || typeof window === "undefined") return;
  restored = true;
  const stored = readStoredChoices();
  if (Object.keys(stored).length > 0) {
    choices = stored;
    notify();
  }
}

export function toggleSidebarNode(key: string) {
  choices = { ...choices, [key]: !isExpanded(key) };
  writeStoredChoices();
  notify();
}

/** Read/write handle for one collapsible row. */
export function useSidebarNodeExpansion(key: string) {
  const expanded = useSyncExternalStore(
    subscribe,
    () => isExpanded(key),
    () => defaultExpanded(key),
  );
  const toggle = useCallback(() => toggleSidebarNode(key), [key]);

  return [expanded, toggle] as const;
}
