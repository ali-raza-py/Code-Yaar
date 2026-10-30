"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { AlertCircle, ArrowLeft, Circle, Clock, ListChecks, SearchX } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ApiError, projects as projectsApi } from "@/lib/api";
import { demoProjects } from "@/data/projects";
import type { Project } from "@/types";

export default function ProjectDetailPage() {
  const params = useParams<{ slug: string }>();
  const slug = params.slug;

  const [project, setProject] = useState<Project | null>(null);
  const [isDemo, setIsDemo] = useState(false);
  const [state, setState] = useState<"ok" | "loading" | "not_found" | "error">("loading");

  useEffect(() => {
    let cancelled = false;
    (async () => {
      // Deferred so the effect never sets state synchronously (also resets on slug change).
      await Promise.resolve();
      if (cancelled) return;
      setState("loading");
      try {
        const data = await projectsApi.detail(slug);
        if (cancelled) return;
        setProject(data);
        setIsDemo(false);
        setState("ok");
      } catch (e) {
        if (cancelled) return;
        if (e instanceof ApiError && e.status === 404 && process.env.NODE_ENV === "development") {
          const fallback = demoProjects.find((p) => p.slug === slug);
          if (fallback) {
            setProject(fallback);
            setIsDemo(true);
            setState("ok");
            return;
          }
        }
        setState(e instanceof ApiError && e.status === 404 ? "not_found" : "error");
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [slug]);

  if (state === "loading") {
    return (
      <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="h-6 w-32 animate-pulse rounded bg-secondary" />
        <div className="mt-8 h-10 w-2/3 animate-pulse rounded bg-secondary" />
        <div className="mt-4 h-24 animate-pulse rounded bg-secondary" />
      </div>
    );
  }

  if (state === "not_found") {
    return (
      <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6 lg:px-8">
        <Link href="/projects" className="mb-8 inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground">
          <ArrowLeft className="h-4 w-4" /> Back to Projects
        </Link>
        <div className="rounded-xl border border-dashed border-[var(--color-section-border)] px-6 py-16 text-center">
          <SearchX className="mx-auto h-8 w-8 text-muted-foreground" />
          <h1 className="mt-4 text-xl font-bold">Project not found</h1>
          <p className="mt-2 text-sm text-muted-foreground">This project doesn&apos;t exist or has been removed.</p>
        </div>
      </div>
    );
  }

  if (state === "error") {
    return (
      <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6 lg:px-8">
        <Link href="/projects" className="mb-8 inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground">
          <ArrowLeft className="h-4 w-4" /> Back to Projects
        </Link>
        <div role="alert" className="flex items-center gap-3 rounded-lg border border-danger/30 bg-danger/10 px-4 py-3 text-sm text-danger">
          <AlertCircle className="h-4 w-4 shrink-0" />
          We couldn&apos;t load this project. Please try again later.
        </div>
      </div>
    );
  }

  if (!project) return null;

  return (
    <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6 sm:py-16 lg:px-8">
      <Link href="/projects" className="mb-8 inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground">
        <ArrowLeft className="h-4 w-4" /> Back to Projects
      </Link>
      <div className="mb-8">
        {isDemo && (
          <p className="mb-4 rounded-lg border border-info/25 bg-info/10 px-3 py-2 text-xs text-info">
            Demo project definition shown for development. It is not part of the live library yet.
          </p>
        )}
        <div className="flex flex-wrap items-center gap-3">
          <Badge
            variant="outline"
            className={
              project.difficulty === "beginner"
                ? "bg-accent/10 text-accent"
                : project.difficulty === "intermediate"
                ? "bg-primary/10 text-primary"
                : "bg-destructive/10 text-destructive"
            }
          >
            {project.difficulty}
          </Badge>
          <div className="flex items-center gap-1 text-sm text-muted-foreground">
            <Clock className="h-4 w-4" /> {project.estimated_hours}h
          </div>
          <div className="flex items-center gap-1 text-sm text-muted-foreground">
            <ListChecks className="h-4 w-4" /> {project.milestones.length} milestones
          </div>
        </div>
        <h1 className="mt-4 text-3xl font-bold tracking-tight sm:text-4xl">{project.title}</h1>
        <p className="mt-4 text-muted-foreground">{project.description}</p>
      </div>

      <div className="grid gap-8 md:grid-cols-3">
        <div className="md:col-span-2">
          <h2 className="mb-4 text-lg font-semibold">Milestones</h2>
          <p className="mb-4 text-sm text-muted-foreground">
            The recommended build order for this project. Progress tracking for projects is not available yet.
          </p>
          <div className="space-y-3">
            {[...project.milestones]
              .sort((a, b) => a.order - b.order)
              .map((milestone, i) => (
                <div key={milestone.id} className="flex items-start gap-3 rounded-lg border p-4">
                  <Circle className="mt-0.5 h-5 w-5 shrink-0 text-muted-foreground" aria-hidden="true" />
                  <div>
                    <p className="text-sm font-medium">{i + 1}. {milestone.title}</p>
                    <p className="mt-1 text-xs text-muted-foreground">{milestone.description}</p>
                  </div>
                </div>
              ))}
          </div>
        </div>
        <div>
          <h2 className="mb-4 text-lg font-semibold">Technologies</h2>
          <div className="flex flex-wrap gap-2">
            {project.technologies.map((tech) => (
              <Badge key={tech} variant="secondary">{tech}</Badge>
            ))}
          </div>
          <Card className="mt-8">
            <CardContent className="p-4 text-sm text-muted-foreground">
              The guided project workspace is under development. For now, use these milestones as your build checklist.
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
