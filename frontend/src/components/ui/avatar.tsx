"use client";

import { useState } from "react";

/**
 * Shared avatar: renders a real picture when one exists and degrades to
 * deterministic initials on a stable tinted background otherwise. Used in the
 * sidebar, leaderboard rows, profile, settings preview and public profiles so
 * a broken image never shows — the `onError` path falls back to initials.
 */

// Named Tailwind tints so the fallback colour reads consistently in both themes.
const PALETTE = [
  "bg-emerald-500/15 text-emerald-700 dark:text-emerald-300",
  "bg-sky-500/15 text-sky-700 dark:text-sky-300",
  "bg-violet-500/15 text-violet-700 dark:text-violet-300",
  "bg-amber-500/15 text-amber-700 dark:text-amber-300",
  "bg-rose-500/15 text-rose-700 dark:text-rose-300",
  "bg-teal-500/15 text-teal-700 dark:text-teal-300",
  "bg-indigo-500/15 text-indigo-700 dark:text-indigo-300",
];

function hashString(value: string): number {
  let hash = 0;
  for (let i = 0; i < value.length; i += 1) {
    hash = (hash << 5) - hash + value.charCodeAt(i);
    hash |= 0; // keep it a 32-bit int
  }
  return Math.abs(hash);
}

function toneFor(seed: string | undefined): string {
  if (!seed) return PALETTE[0];
  return PALETTE[hashString(seed) % PALETTE.length];
}

/**
 * Up to two initials: "Ali Raza" -> "AR", a single word -> its first letter,
 * nothing usable -> "?".
 */
export function initialsFor(name: string, fallback?: string): string {
  const source = name?.trim() || fallback?.trim() || "";
  if (!source) return "?";
  const parts = source.split(/\s+/).filter(Boolean);
  if (parts.length === 1) return parts[0].charAt(0).toUpperCase();
  const first = parts[0].charAt(0);
  const last = parts[parts.length - 1].charAt(0);
  return (first + last).toUpperCase();
}

interface AvatarProps {
  /** Picture URL; empty/undefined (or a load error) falls back to initials. */
  src?: string | null;
  /** Display name used to derive initials. */
  name?: string | null;
  /** Stable seed for the fallback tint (username is ideal). */
  username?: string | null;
  /** Edge length in CSS pixels. */
  size?: number;
  className?: string;
  alt?: string;
}

export function Avatar({ src, name, username, size = 40, className = "", alt }: AvatarProps) {
  const [failedSrc, setFailedSrc] = useState<string | null>(null);
  const initials = initialsFor(name ?? "", username ?? "");
  const round = "rounded-full";
  const failed = Boolean(src && failedSrc === src);

  if (src && !failed) {
    return (
      // eslint-disable-next-line @next/next/no-img-element
      <img
        src={src}
        alt={alt ?? name ?? username ?? "avatar"}
        width={size}
        height={size}
        onError={() => setFailedSrc(src)}
        className={`shrink-0 object-cover ${round} ${className}`.trim()}
        style={{ width: size, height: size }}
        loading="lazy"
      />
    );
  }

  return (
    <span
      aria-hidden="true"
      className={`inline-flex shrink-0 select-none items-center justify-center font-bold uppercase ${round} ${toneFor(
        username ?? name ?? undefined
      )} ${className}`.trim()}
      style={{ width: size, height: size, fontSize: Math.round(size * 0.4) }}
    >
      {initials}
    </span>
  );
}
