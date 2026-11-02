"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  ArrowDown, ArrowUp, Check, Eye, EyeOff, ExternalLink, Loader2,
  Lock, Pencil, Star, Trash2,
} from "lucide-react";
import {
  ApiError, studentProjects,
  type StudentProject, type StudentProjectInput,
} from "@/lib/api";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { CATEGORY_TONES, STATUS_TONES, MAX_FEATURED } from "./shared";

function toInput(p: StudentProject): StudentProjectInput {
  return {
    title: p.title,
    short_description: p.short_description,
    overview: p.overview,
    category: p.category,
    status: p.status,
    github_url: p.github_url,
    live_demo_url: p.live_demo_url,
    docs_url: p.docs_url,
    problem_statement: p.problem_statement,
    solution: p.solution,
    technical_details: p.technical_details,
    challenges: p.challenges,
    lessons_learned: p.lessons_learned,
    contributions: p.contributions,
    technologies: p.technologies,
    start_date: p.start_date,
    completion_date: p.completion_date,
    featured: p.featured,
    visibility: p.visibility,
  };
}

/**
 * Owner-facing project list. Ordering is explicit (up / down) and persisted in
 * one call; feature, visibility and delete are inline. The featured cap is
 * enforced server-side, but we surface it here too so the action fails fast
 * with a clear message instead of a surprise 400.
 */
export function PortfolioProjectsManager({
  projects, username,
}: { projects: StudentProject[]; username: string }) {
  const router = useRouter();
  const [busy, setBusy] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [confirmId, setConfirmId] = useState<number | null>(null);

  const featuredCount = projects.filter((p) => p.featured).length;

  async function mutate(id: number, fn: () => Promise<unknown>, message: string) {
    setBusy(id);
    setError(null);
    try {
      await fn();
      router.refresh();
    } catch (err) {
      setError(
        err instanceof ApiError
          ? Object.values(err.fieldErrors ?? {}).flat().join(" ") || err.message || message
          : message,
      );
    } finally {
      setBusy(null);
    }
  }

  function move(index: number, direction: -1 | 1) {
    const target = index + direction;
    if (target < 0 || target >= projects.length) return;
    const reordered = [...projects];
    [reordered[index], reordered[target]] = [reordered[target], reordered[index]];
    const items = reordered.map((p, i) => ({ id: p.id, display_order: i }));
    void mutate(projects[index].id, () => studentProjects.reorder(items), "Couldn't reorder your projects.");
  }

  function toggleFeatured(p: StudentProject) {
    if (!p.featured && featuredCount >= MAX_FEATURED) {
      setError(`You can feature at most ${MAX_FEATURED} projects. Unfeature one first.`);
      return;
    }
    const input = { ...toInput(p), featured: !p.featured };
    void mutate(p.id, () => studentProjects.update(p.id, input), "Couldn't update the featured state.");
  }

  function toggleVisibility(p: StudentProject) {
    const input = { ...toInput(p), visibility: p.visibility === "public" ? "private" as const : "public" as const };
    void mutate(p.id, () => studentProjects.update(p.id, input), "Couldn't change visibility.");
  }

  function remove(p: StudentProject) {
    void mutate(p.id, () => studentProjects.remove(p.id), "Couldn't delete this project.");
    setConfirmId(null);
  }

  if (projects.length === 0) return null;

  return (
    <section>
      {error && (
        <p role="alert" className="mb-3 rounded-lg border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
          {error}
        </p>
      )}
      <ul className="space-y-2.5">
        {projects.map((p, index) => (
          <li
            key={p.id}
            className={cn(
              "flex flex-wrap items-center gap-3 rounded-[var(--radius-card)] border border-border bg-card p-3",
              busy === p.id && "opacity-70",
            )}
          >
            <div className="flex flex-col">
              <button
                type="button" aria-label="Move up" disabled={index === 0 || busy !== null}
                onClick={() => move(index, -1)}
                className="rounded p-0.5 text-muted-foreground hover:text-foreground disabled:opacity-30"
              ><ArrowUp className="h-4 w-4" /></button>
              <button
                type="button" aria-label="Move down" disabled={index === projects.length - 1 || busy !== null}
                onClick={() => move(index, 1)}
                className="rounded p-0.5 text-muted-foreground hover:text-foreground disabled:opacity-30"
              ><ArrowDown className="h-4 w-4" /></button>
            </div>

            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2">
                <Link href={`/profile/portfolio/projects/${p.id}/edit`} className="truncate text-sm font-semibold text-foreground hover:underline">
                  {p.title}
                </Link>
                {p.featured && <Star className="h-3.5 w-3.5 shrink-0 fill-primary text-primary" aria-hidden="true" />}
              </div>
              <div className="mt-1 flex flex-wrap items-center gap-1.5 text-[11px]">
                <span className={cn("rounded-pill border px-1.5 py-0.5 font-medium", CATEGORY_TONES[p.category])}>{p.category_label}</span>
                <span className={cn("rounded-pill border px-1.5 py-0.5 font-medium", STATUS_TONES[p.status])}>{p.status_label}</span>
                <span className={cn("inline-flex items-center gap-1 text-muted-foreground", p.visibility === "private" && "text-warning")}>
                  {p.visibility === "public" ? <Eye className="h-3 w-3" /> : <Lock className="h-3 w-3" />}
                  {p.visibility}
                </span>
              </div>
            </div>

            <div className="flex items-center gap-1">
              {busy === p.id && <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" aria-hidden="true" />}
              <IconAction label={p.featured ? "Unfeature" : "Feature"} active={p.featured} disabled={busy !== null} onClick={() => toggleFeatured(p)}>
                <Star className={cn("h-4 w-4", p.featured && "fill-primary text-primary")} />
              </IconAction>
              <IconAction label={p.visibility === "public" ? "Make private" : "Make public"} disabled={busy !== null} onClick={() => toggleVisibility(p)}>
                {p.visibility === "public" ? <Eye className="h-4 w-4" /> : <EyeOff className="h-4 w-4" />}
              </IconAction>
              <IconAction label="Edit" disabled={busy !== null} onClick={() => router.push(`/profile/portfolio/projects/${p.id}/edit`)}>
                <Pencil className="h-4 w-4" />
              </IconAction>
              {p.visibility === "public" && (
                <IconAction label="View public page" disabled={busy !== null} onClick={() => router.push(`/profile/${username}/projects/${p.slug}`)}>
                  <ExternalLink className="h-4 w-4" />
                </IconAction>
              )}
              <IconAction label="Delete" danger disabled={busy !== null} onClick={() => setConfirmId(p.id)}>
                <Trash2 className="h-4 w-4" />
              </IconAction>
            </div>

            {confirmId === p.id && (
              <div className="flex w-full items-center justify-end gap-2 border-t border-border pt-2 text-sm">
                <span className="mr-auto text-muted-foreground">Delete “{p.title}” permanently?</span>
                <Button size="sm" variant="ghost" onClick={() => setConfirmId(null)}>Cancel</Button>
                <Button size="sm" variant="destructive" onClick={() => remove(p)}>
                  <Check className="h-3.5 w-3.5" /> Delete
                </Button>
              </div>
            )}
          </li>
        ))}
      </ul>
    </section>
  );
}

function IconAction({
  label, onClick, disabled, active, danger, children,
}: {
  label: string; onClick: () => void; disabled?: boolean; active?: boolean; danger?: boolean; children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      title={label}
      aria-label={label}
      onClick={onClick}
      disabled={disabled}
      className={cn(
        "inline-flex h-8 w-8 items-center justify-center rounded-md border border-transparent text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:opacity-40",
        active && "text-primary",
        danger && "hover:text-destructive",
      )}
    >
      {children}
    </button>
  );
}
