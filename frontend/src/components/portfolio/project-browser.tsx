"use client";

import { useMemo, useState } from "react";
import type { ProjectCategory, PublicProject } from "@/lib/api";
import { PROJECT_CATEGORY_LABELS } from "@/lib/api";
import { cn } from "@/lib/utils";
import { ProjectGrid, ALL_CATEGORIES } from "./sections";

/**
 * Filterable view of a developer's projects. Filters are intentionally simple:
 * a single category and a single technology. Everything is derived from the
 * projects the owner actually published — no synthetic counts.
 */
export function ProjectBrowser({
  projects, username,
}: { projects: PublicProject[]; username: string }) {
  const [category, setCategory] = useState<ProjectCategory | "all">("all");
  const [technology, setTechnology] = useState<string>("all");

  const technologies = useMemo(() => {
    const set = new Set<string>();
    for (const project of projects) for (const tech of project.technologies) set.add(tech);
    return ["all", ...Array.from(set).sort((a, b) => a.localeCompare(b))];
  }, [projects]);

  const presentCategories = useMemo(() => {
    const present = new Set(projects.map((p) => p.category));
    return ALL_CATEGORIES.filter((c) => present.has(c));
  }, [projects]);

  const filtered = projects.filter((project) => {
    if (category !== "all" && project.category !== category) return false;
    if (technology !== "all" && !project.technologies.includes(technology)) return false;
    return true;
  });

  if (projects.length === 0) return null;

  return (
    <section>
      <div className="mb-4 flex flex-col gap-3">
        <div className="flex flex-wrap gap-1.5">
          <FilterChip active={category === "all"} onClick={() => setCategory("all")}>All</FilterChip>
          {presentCategories.map((c) => (
            <FilterChip key={c} active={category === c} onClick={() => setCategory(c)}>
              {PROJECT_CATEGORY_LABELS[c]}
            </FilterChip>
          ))}
        </div>
        {technologies.length > 1 && (
          <label className="flex items-center gap-2 text-sm text-muted-foreground">
            <span>Technology</span>
            <select
              value={technology}
              onChange={(e) => setTechnology(e.target.value)}
              className="rounded-md border border-border bg-background px-2 py-1 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            >
              {technologies.map((t) => (
                <option key={t} value={t}>{t === "all" ? "All technologies" : t}</option>
              ))}
            </select>
          </label>
        )}
      </div>

      {filtered.length > 0 ? (
        <ProjectGrid projects={filtered} username={username} />
      ) : (
        <p className="rounded-[var(--radius-card)] border border-dashed border-border bg-muted/20 px-4 py-10 text-center text-sm text-muted-foreground">
          No projects match these filters.
        </p>
      )}
    </section>
  );
}

function FilterChip({
  active, onClick, children,
}: { active: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "rounded-pill border px-3 py-1 text-xs font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
        active
          ? "border-primary bg-primary text-primary-foreground"
          : "border-border bg-background text-muted-foreground hover:border-primary/30 hover:text-foreground",
      )}
    >
      {children}
    </button>
  );
}
