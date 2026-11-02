"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { ExternalLink, FolderPlus, Loader2, Sparkles } from "lucide-react";
import {
  ApiError, portfolio, studentProjects,
  type PortfolioData, type PublicPortfolioData, type StudentProject,
} from "@/lib/api";
import { useAuth } from "@/hooks/use-auth";
import { buttonVariants } from "@/components/ui/button-variants";
import { Card } from "@/components/ui/card";
import { NetworkError } from "@/components/learning/workspace/error-states";
import { PortfolioIntroEditor } from "@/components/portfolio/portfolio-intro-editor";
import { PortfolioVisibilitySettings } from "@/components/portfolio/portfolio-visibility-settings";
import { PortfolioProjectsManager } from "@/components/portfolio/portfolio-projects-manager";
import { PortfolioView } from "@/components/portfolio/portfolio-view";
import { EmptyPortfolioState } from "@/components/portfolio/sections";
import { cn } from "@/lib/utils";

type LoadState = "loading" | "ready" | "network" | "auth";

/**
 * The portfolio management experience, shared by the standalone
 * /profile/portfolio route and the My Profile > Portfolio tab. `compact`
 * drops the page title block when the surrounding shell already labels the
 * view. Data is fetched once per mount from the existing portfolio endpoints.
 */
export function PortfolioDashboard({ compact = false }: { compact?: boolean }) {
  const { user } = useAuth();
  const username = user?.username ?? "";

  const [state, setState] = useState<LoadState>("loading");
  const [data, setData] = useState<PortfolioData | null>(null);
  const [projects, setProjects] = useState<StudentProject[]>([]);
  const [tab, setTab] = useState<"manage" | "preview">("manage");
  const [preview, setPreview] = useState<PublicPortfolioData | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);

  const load = useCallback(async () => {
    setState("loading");
    try {
      const [me, list] = await Promise.all([portfolio.getMy(), studentProjects.list()]);
      setData(me);
      setProjects(list);
      setState("ready");
    } catch (e) {
      if (e instanceof ApiError && e.status === 401) setState("auth");
      else setState("network");
    }
  }, []);

  useEffect(() => {
    (async () => { await load(); })();
  }, [load]);

  // Refresh the preview from the real public endpoint whenever it's opened, so
  // preview and production render from the identical privacy-filtered payload.
  useEffect(() => {
    if (tab !== "preview" || !data?.is_published || !username) return;
    let active = true;
    (async () => {
      setPreviewLoading(true);
      try {
        const p = await portfolio.getPublic(username);
        if (active) setPreview(p);
      } catch {
        if (active) setPreview(null);
      } finally {
        if (active) setPreviewLoading(false);
      }
    })();
    return () => { active = false; };
  }, [tab, data?.is_published, data?.updated_at, username]);

  if (state === "network") return <NetworkError />;
  if (state === "auth") {
    return <div className="mx-auto max-w-4xl px-4 py-12 text-center text-sm text-muted-foreground">Please sign in to manage your portfolio.</div>;
  }

  if (state === "loading" || !data) {
    return (
      <div className="mx-auto max-w-5xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="animate-pulse space-y-6">
          <div className="h-8 w-52 rounded bg-muted" />
          <div className="h-40 rounded-[var(--radius-card)] bg-muted" />
          <div className="h-64 rounded-[var(--radius-card)] bg-muted" />
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-8 sm:px-6 lg:px-8">
      {!compact && (
        <header className="mb-6 flex flex-wrap items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-foreground">Your portfolio</h1>
            <p className="mt-1 text-sm text-muted-foreground">
              Curate what you&apos;ve built and control exactly what the world sees.
            </p>
          </div>
        </header>
      )}

      <div className={cn("mb-6 flex flex-wrap items-center justify-between gap-4", compact && "mt-0")}>
        <div className="inline-flex rounded-pill border border-border bg-muted/30 p-1">
          {(["manage", "preview"] as const).map((t) => (
            <button
              key={t}
              type="button"
              onClick={() => setTab(t)}
              className={cn(
                "rounded-pill px-4 py-1.5 text-sm font-medium capitalize transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
                tab === t ? "bg-background text-foreground shadow-sm" : "text-muted-foreground hover:text-foreground",
              )}
            >
              {t === "preview" ? "Public preview" : "Manage"}
            </button>
          ))}
        </div>

        <div className="flex flex-wrap gap-2">
          <Link href="/profile/portfolio/projects/new" className={cn(buttonVariants({ variant: "outline", size: "sm" }))}>
            <FolderPlus className="h-4 w-4" /> New project
          </Link>
          {data.is_published && username && (
            <a href={`/profile/${username}/portfolio`} target="_blank" rel="noopener noreferrer" className={cn(buttonVariants({ variant: "outline", size: "sm" }))}>
              <ExternalLink className="h-4 w-4" /> Open public page
            </a>
          )}
        </div>
      </div>

      {tab === "manage" ? (
        <div className="space-y-6">
          <PortfolioIntroEditor portfolio={data} />
          <PortfolioVisibilitySettings portfolio={data} />

          <Card className="p-5 sm:p-6">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-base font-semibold text-foreground">Projects</h2>
              <Link href="/profile/portfolio/projects/new" className={cn(buttonVariants({ variant: "ghost", size: "sm" }))}>
                <FolderPlus className="h-4 w-4" /> Add
              </Link>
            </div>
            {projects.length === 0 ? (
              <EmptyPortfolioState
                title="No projects yet"
                description="Add the work you're proud of — code, demos and write-ups make your portfolio credible."
                action={
                  <Link href="/profile/portfolio/projects/new" className={cn(buttonVariants())}>
                    <FolderPlus className="h-4 w-4" /> Add your first project
                  </Link>
                }
              />
            ) : (
              <PortfolioProjectsManager projects={projects} username={username} />
            )}
          </Card>
        </div>
      ) : (
        <PreviewPanel data={data} preview={preview} previewLoading={previewLoading} />
      )}
    </div>
  );
}

function PreviewPanel({
  data, preview, previewLoading,
}: {
  data: PortfolioData; preview: PublicPortfolioData | null; previewLoading: boolean;
}) {
  if (!data.is_published) {
    return (
      <Card className="p-8 text-center">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 text-primary">
          <Sparkles className="h-6 w-6" aria-hidden="true" />
        </div>
        <h2 className="mt-4 text-lg font-semibold text-foreground">Preview unlocks when you publish</h2>
        <p className="mx-auto mt-1 max-w-md text-sm text-muted-foreground">
          Publish from the Manage tab to share a live, search-friendly portfolio page. Your preview shows exactly what visitors will see.
        </p>
      </Card>
    );
  }

  if (previewLoading && !preview) {
    return (
      <Card className="flex items-center justify-center gap-2 p-12 text-sm text-muted-foreground">
        <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> Loading preview…
      </Card>
    );
  }

  if (!preview) {
    return (
      <Card className="p-8 text-center text-sm text-muted-foreground">
        Your account profile is private, so the public page isn&apos;t reachable yet. Make your profile public in Settings to share your portfolio.
      </Card>
    );
  }

  return <PortfolioView data={preview} />;
}
