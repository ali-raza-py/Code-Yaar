"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ArrowLeft, Loader2 } from "lucide-react";
import { ApiError, studentProjects, type StudentProject } from "@/lib/api";
import { buttonVariants } from "@/components/ui/button-variants";
import { NetworkError } from "@/components/learning/workspace/error-states";
import { ProjectEditor } from "@/components/portfolio/project-editor";
import { cn } from "@/lib/utils";

export default function EditProjectPage() {
  const params = useParams<{ id: string }>();
  const id = Number(params?.id);

  const [project, setProject] = useState<StudentProject | null>(null);
  const [featuredOthers, setFeaturedOthers] = useState(0);
  const [state, setState] = useState<"loading" | "ready" | "missing" | "network">("loading");

  const load = useCallback(async () => {
    if (!Number.isFinite(id)) { setState("missing"); return; }
    setState("loading");
    try {
      const [detail, all] = await Promise.all([studentProjects.get(id), studentProjects.list()]);
      setProject(detail);
      setFeaturedOthers(all.filter((p) => p.featured && p.id !== detail.id).length);
      setState("ready");
    } catch (e) {
      if (e instanceof ApiError && (e.status === 404 || e.status === 403)) setState("missing");
      else setState("network");
    }
  }, [id]);

  useEffect(() => { (async () => { await load(); })(); }, [load]);

  const backLink = (
    <Link href="/profile/portfolio" className={cn(buttonVariants({ variant: "ghost", size: "sm" }), "mb-4 -ml-2")}>
      <ArrowLeft className="h-4 w-4" /> Back to portfolio
    </Link>
  );

  if (state === "network") return <NetworkError />;
  if (state === "missing") {
    return (
      <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6 lg:px-8">
        {backLink}
        <p className="text-sm text-muted-foreground">This project no longer exists or isn&apos;t yours.</p>
      </div>
    );
  }

  if (state === "loading" || !project) {
    return (
      <div className="mx-auto flex max-w-3xl items-center justify-center gap-2 px-4 py-24 text-sm text-muted-foreground">
        <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> Loading project…
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6 lg:px-8">
      {backLink}
      <header className="mb-6">
        <h1 className="text-2xl font-bold tracking-tight text-foreground">Edit project</h1>
        <p className="mt-1 text-sm text-muted-foreground">Update the details behind “{project.title}”.</p>
      </header>
      <ProjectEditor mode="edit" project={project} alreadyFeatured={featuredOthers} />
    </div>
  );
}
