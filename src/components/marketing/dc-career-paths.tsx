"use client";

import Link from "next/link";
import { ArrowRight, Layers, Server, Monitor, GitBranch } from "lucide-react";
import { careerTracks } from "@/data/tracks";

const iconMap: Record<string, React.ComponentType<{ className?: string }>> = {
  layers: Layers,
  server: Server,
  monitor: Monitor,
  "git-branch": GitBranch,
};

function DifficultyDots({ difficulty }: { difficulty: string }) {
  const levels = { beginner: 1, intermediate: 2, advanced: 3 };
  const active = levels[difficulty as keyof typeof levels] || 1;

  return (
    <div className="flex items-center gap-1">
      {[1, 2, 3].map((i) => (
        <div
          key={i}
          className={`h-1.5 w-1.5 rounded-full ${
            i <= active ? "bg-[var(--color-cta-green)]" : "bg-gray-300"
          }`}
        />
      ))}
    </div>
  );
}

export function DcCareerPaths() {
  return (
    <section className="bg-white py-16 sm:py-20">
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center">
          <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
            Find your path. Find your future.
          </h2>
          <p className="mx-auto mt-3 max-w-2xl text-lg text-muted-foreground">
            Structured career tracks that take you from beginner to job-ready.
            Each track includes courses, projects, and challenges.
          </p>
        </div>

        {/* Career Track Cards */}
        <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {careerTracks.map((track) => {
            const Icon = iconMap[track.icon] || Layers;
            return (
              <Link
                key={track.slug}
                href={`/learn?track=${track.slug}`}
                className="dc-card group flex flex-col p-6"
              >
                <div className="flex items-center justify-between">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-[var(--color-section-light)]">
                    <Icon className="h-5 w-5 text-[var(--primary)]" />
                  </div>
                  <DifficultyDots difficulty={track.difficulty} />
                </div>

                <h3 className="mt-4 text-lg font-semibold text-foreground group-hover:text-[var(--primary)]">
                  {track.title}
                </h3>
                <p className="mt-2 flex-1 text-sm leading-relaxed text-muted-foreground">
                  {track.description}
                </p>

                <div className="mt-4 flex items-center gap-3 text-xs text-muted-foreground">
                  <span>{track.courseCount} courses</span>
                  <span className="h-1 w-1 rounded-full bg-border" />
                  <span>{track.estimatedHours}h</span>
                </div>

                <div className="mt-4 flex items-center gap-1 text-sm font-medium text-[var(--primary)] opacity-0 transition-opacity group-hover:opacity-100">
                  Explore track <ArrowRight className="h-3.5 w-3.5" />
                </div>
              </Link>
            );
          })}
        </div>
      </div>
    </section>
  );
}
