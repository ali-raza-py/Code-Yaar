import type { Metadata } from "next";
import Link from "next/link";
import { FolderGit2, Clock, ArrowRight } from "lucide-react";
import { demoProjects } from "@/data/projects";

export const metadata: Metadata = {
  title: "Projects",
  description: "Build real systems. Explore projects across all difficulty levels.",
};

const categories = [
  "All",
  "Python",
  "JavaScript",
  "React",
  "Node.js",
  "TypeScript",
  "SQL",
  "Git",
  "Docker",
  "AWS",
  "Theory",
  "System Design",
  "+11",
];

function DifficultyBadge({ difficulty }: { difficulty: string }) {
  const colors: Record<string, string> = {
    beginner: "bg-green-100 text-green-700",
    intermediate: "bg-orange-100 text-orange-700",
    advanced: "bg-red-100 text-red-700",
  };
  return (
    <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-semibold ${colors[difficulty] || colors.beginner}`}>
      {difficulty.charAt(0).toUpperCase() + difficulty.slice(1)}
    </span>
  );
}

export default function ProjectsPage() {
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
          {/* Circular diagram */}
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

      {/* Category Filter Tabs */}
      <div className="mb-6 flex flex-wrap gap-2">
        {categories.map((cat) => (
          <button
            key={cat}
            className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
              cat === "All"
                ? "bg-[#0f1d32] text-white"
                : "bg-white text-foreground border border-[var(--color-section-border)] hover:bg-[var(--color-section-light)]"
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Search + filters */}
      <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative">
          <input
            type="text"
            placeholder="Search projects..."
            className="w-64 rounded-lg border border-[var(--color-section-border)] bg-white px-4 py-2 pl-9 text-sm outline-none focus:border-[var(--primary)]"
          />
          <svg className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        <div className="flex gap-2">
          <select className="rounded-lg border border-[var(--color-section-border)] bg-white px-4 py-2 text-sm outline-none">
            <option>Topic</option>
          </select>
          <button className="inline-flex items-center gap-1.5 rounded-lg border border-[var(--color-section-border)] bg-white px-4 py-2 text-sm font-medium">
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
            </svg>
            More filters
          </button>
        </div>
      </div>

      {/* Project Grid */}
      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {demoProjects.map((project) => (
          <Link
            key={project.id}
            href={`/projects/${project.slug}`}
            className="group overflow-hidden rounded-xl border border-[var(--color-section-border)] bg-white transition-all hover:border-[var(--primary)] hover:shadow-md"
          >
            <div className="h-2 bg-[var(--primary)]" />
            <div className="p-5">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Project
                </span>
                <DifficultyBadge difficulty={project.difficulty} />
              </div>
              <h3 className="mt-2 text-lg font-bold text-foreground group-hover:text-[var(--primary)]">
                {project.title}
              </h3>
              <p className="mt-1 text-sm text-muted-foreground line-clamp-2">
                {project.description}
              </p>
              <div className="mt-4 flex items-center gap-3 text-xs text-muted-foreground">
                <span className="flex items-center gap-1">
                  <Clock className="h-3.5 w-3.5" />
                  {project.estimatedHours}h
                </span>
                <span className="h-1 w-1 rounded-full bg-border" />
                <span>{project.milestones.length} milestones</span>
              </div>
              <div className="mt-3 flex flex-wrap gap-1.5">
                {project.technologies.slice(0, 3).map((tech) => (
                  <span
                    key={tech}
                    className="rounded-md bg-[var(--color-section-light)] px-2 py-0.5 text-xs font-medium text-foreground"
                  >
                    {tech}
                  </span>
                ))}
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
