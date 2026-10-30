"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { AlertCircle, Check, Clock, FolderGit2, RotateCcw, Search } from "lucide-react";
import { ApiError, projects as projectsApi } from "@/lib/api";
import { demoProjects } from "@/data/projects";
import type { Project } from "@/types";

const DIFFICULTY_TABS = ["all", "beginner", "intermediate", "advanced"] as const;

function DifficultyBadge({ difficulty }: { difficulty: Project["difficulty"] }) {
  const colors: Record<Project["difficulty"], string> = {
    beginner: "bg-difficulty-easy-soft text-difficulty-easy",
    intermediate: "bg-difficulty-medium-soft text-difficulty-medium",
    advanced: "bg-difficulty-hard-soft text-difficulty-hard",
  };
  return (
    <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-semibold capitalize ${colors[difficulty]}`}>
      {difficulty}
    </span>
  );
}

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<"network" | "auth" | null>(null);
  const [usingDemoData, setUsingDemoData] = useState(false);
  const [difficulty, setDifficulty] = useState<(typeof DIFFICULTY_TABS)[number]>("all");
  const [searchInput, setSearchInput] = useState("");
  const [search, setSearch] = useState("");

  const load = useCallback(() => {
    projectsApi
      .list()
      .then((live) => {
        const useDemo = live.length === 0 && process.env.NODE_ENV === "development";
        setProjects(useDemo ? demoProjects : live);
        setUsingDemoData(useDemo);
        setError(null);
      })
      .catch((e) => setError(e instanceof ApiError && e.status === 401 ? "auth" : "network"))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    // Deferred via await so the effect never sets state synchronously.
    (async () => { await load(); })();
  }, [load]);

  useEffect(() => {
    const t = window.setTimeout(() => setSearch(searchInput.trim()), 250);
    return () => window.clearTimeout(t);
  }, [searchInput]);

  const technologies = useMemo(
    () => Array.from(new Set(projects.flatMap((p) => p.technologies))).sort((a, b) => a.localeCompare(b)),
    [projects]
  );

  const filtered = useMemo(
    () =>
      projects.filter((p) => {
        if (difficulty !== "all" && p.difficulty !== difficulty) return false;
        if (search && !`${p.title} ${p.description} ${p.technologies.join(" ")}`.toLowerCase().includes(search.toLowerCase())) return false;
        return true;
      }),
    [projects, difficulty, search]
  );

  const hasFilters = Boolean(search) || difficulty !== "all";
  const clearFilters = () => {
    setSearchInput("");
    setSearch("");
    setDifficulty("all");
  };

  return (
    <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
      {/* Dark Banner */}
      <div className="mb-6 overflow-hidden rounded-xl bg-[#0f1d32] p-8 text-white sm:p-10">
        <div className="flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-3xl font-bold sm:text-4xl">Real World Projects</h1>
            <p className="mt-3 max-w-xl text-white/70">
              Engage with real-world challenges using code editors and development tools.
              Apply your knowledge to real scenarios in a practical environment.
            </p>
          </div>
          <div className="hidden sm:block">
            <div className="relative h-28 w-28">
              <div className="absolute inset-0 rounded-full border-2 border-dashed border-white/20" />
              <div className="absolute left-1/2 top-0 -translate-x-1/2 -translate-y-1/2 flex h-8 w-8 items-center justify-center rounded-full bg-white/20">
                <FolderGit2 className="h-4 w-4 text-white" />
              </div>
              <div className="absolute right-0 top-1/2 translate-x-1/2 -translate-y-1/2 flex h-8 w-8 items-center justify-center rounded-full bg-white/20">
                <span className="text-[10px] font-bold text-white">APPLY</span>
              </div>
              <div className="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-1/2 flex h-8 w-8 items-center justify-center rounded-full bg-white/20">
                <span className="text-[10px] font-bold text-white">BUILD</span>
              </div>
              <div className="absolute left-0 top-1/2 -translate-x-1/2 -translate-y-1/2 flex h-8 w-8 items-center justify-center rounded-full bg-white/20">
                <span className="text-[10px] font-bold text-white">PROVE</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Difficulty filter tabs */}
      <div className="mb-4 flex flex-wrap gap-2">
        {DIFFICULTY_TABS.map((tab) => (
          <button
            key={tab}
            onClick={() => setDifficulty(tab)}
            className={`rounded-lg px-4 py-2 text-sm font-medium capitalize transition-colors ${
              difficulty === tab
                ? "bg-[#0f1d32] text-white"
                : "bg-white text-foreground border border-[var(--color-section-border)] hover:bg-[var(--color-section-light)]"
            }`}
          >
            {tab === "all" ? "All" : tab}
          </button>
        ))}
      </div>

      {/* Search */}
      <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative">
          <input
            type="text"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder="Search projects..."
            aria-label="Search projects"
            className="w-64 rounded-lg border border-[var(--color-section-border)] bg-white px-4 py-2 pl-9 text-sm outline-none focus:border-[var(--primary)]"
          />
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        </div>
        <p className="text-sm font-semibold text-muted-foreground" aria-live="polite">
          {loading ? "Loading projects…" : `${filtered.length} project${filtered.length === 1 ? "" : "s"}`}
        </p>
      </div>

      {usingDemoData && (
        <p className="mb-4 text-xs text-muted-foreground">
          <Check aria-hidden="true" className="mr-1 inline h-3.5 w-3.5 text-success" />
          Development preview using local project examples while the project library is empty.
        </p>
      )}

      {error === "network" && (
        <div role="alert" className="mb-6 flex items-center justify-between gap-4 rounded-lg border border-danger/30 bg-danger/10 px-4 py-3 text-sm text-danger">
          <span className="inline-flex items-center gap-2"><AlertCircle aria-hidden="true" className="h-4 w-4" />Could not load the project library.</span>
          <button type="button" onClick={() => { setLoading(true); setError(null); load(); }} className="rounded font-bold underline underline-offset-2">Try again</button>
        </div>
      )}
      {error === "auth" && (
        <div role="alert" className="mb-6 rounded-lg border border-warning/30 bg-warning/10 px-4 py-3 text-sm text-amber-700">
          Sign in to view projects. <Link href="/sign-in" className="rounded font-bold underline underline-offset-2">Sign in</Link>
        </div>
      )}

      {/* Project Grid */}
      {loading ? (
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="h-52 animate-pulse rounded-xl border border-[var(--color-section-border)] bg-white/60" />
          ))}
        </div>
      ) : !error && filtered.length === 0 ? (
        <div className="rounded-xl border border-dashed border-[var(--color-section-border)] bg-white/50 px-6 py-16 text-center">
          <h2 className="text-lg font-semibold text-foreground">No projects found</h2>
          <p className="mx-auto mt-2 max-w-md text-sm text-muted-foreground">
            {hasFilters
              ? "No projects match your current filters. Try adjusting your search or difficulty."
              : "The project library is being prepared. Check back soon for hands-on builds."}
          </p>
          {hasFilters && (
            <button onClick={clearFilters} className="mt-4 inline-flex items-center gap-1.5 rounded-lg bg-[#0f1d32] px-4 py-2 text-sm font-semibold text-white">
              <RotateCcw className="h-4 w-4" /> Clear filters
            </button>
          )}
        </div>
      ) : (
        !error && (
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {filtered.map((project) => (
              <Link
                key={project.id}
                href={`/projects/${project.slug}`}
                className="group overflow-hidden rounded-xl border border-[var(--color-section-border)] bg-white transition-all hover:border-[var(--primary)] hover:shadow-md"
              >
                <div className="h-2 bg-[var(--primary)]" />
                <div className="p-5">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Project</span>
                    <DifficultyBadge difficulty={project.difficulty} />
                  </div>
                  <h3 className="mt-2 text-lg font-bold text-foreground group-hover:text-[var(--primary)]">{project.title}</h3>
                  <p className="mt-1 text-sm text-muted-foreground line-clamp-2">{project.description}</p>
                  <div className="mt-4 flex items-center gap-3 text-xs text-muted-foreground">
                    <span className="flex items-center gap-1"><Clock className="h-3.5 w-3.5" />{project.estimated_hours}h</span>
                    <span className="h-1 w-1 rounded-full bg-border" />
                    <span>{project.milestones.length} milestones</span>
                  </div>
                  <div className="mt-3 flex flex-wrap gap-1.5">
                    {project.technologies.slice(0, 3).map((tech) => (
                      <span key={tech} className="rounded-md bg-[var(--color-section-light)] px-2 py-0.5 text-xs font-medium text-foreground">{tech}</span>
                    ))}
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )
      )}

      {!loading && !error && technologies.length > 0 && (
        <p className="mt-6 text-xs text-muted-foreground">Covered technologies: {technologies.join(", ")}.</p>
      )}
    </div>
  );
}
