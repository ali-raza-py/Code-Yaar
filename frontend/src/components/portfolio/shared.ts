import type { ProjectCategory, ProjectStatus } from "@/lib/api";

/** Editorial tone per category — restrained, one hue, works light & dark. */
export const CATEGORY_TONES: Record<ProjectCategory, string> = {
  web_development: "bg-sky-500/10 text-sky-700 dark:text-sky-300 border-sky-500/20",
  ai: "bg-violet-500/10 text-violet-700 dark:text-violet-300 border-violet-500/20",
  machine_learning: "bg-indigo-500/10 text-indigo-700 dark:text-indigo-300 border-indigo-500/20",
  backend: "bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 border-emerald-500/20",
  frontend: "bg-teal-500/10 text-teal-700 dark:text-teal-300 border-teal-500/20",
  mobile: "bg-amber-500/10 text-amber-700 dark:text-amber-300 border-amber-500/20",
  developer_tools: "bg-cyan-500/10 text-cyan-700 dark:text-cyan-300 border-cyan-500/20",
  automation: "bg-orange-500/10 text-orange-700 dark:text-orange-300 border-orange-500/20",
  data_science: "bg-rose-500/10 text-rose-700 dark:text-rose-300 border-rose-500/20",
  other: "bg-muted text-muted-foreground border-border",
};

export const STATUS_TONES: Record<ProjectStatus, string> = {
  in_progress: "bg-warning/10 text-warning border-warning/25",
  completed: "bg-success/10 text-success border-success/25",
  archived: "bg-muted text-muted-foreground border-border",
};

/** Format an ISO date (or null) as "Mar 2026"; empty string when absent. */
export function formatMonthYear(value: string | null | undefined): string {
  if (!value) return "";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return "";
  return d.toLocaleDateString("en-US", { month: "short", year: "numeric" });
}

/** A safe external link always opens in a new tab, isolated from our origin. */
export const EXTERNAL_LINK_PROPS = {
  target: "_blank",
  rel: "noopener noreferrer",
} as const;

export const MAX_FEATURED = 3;
