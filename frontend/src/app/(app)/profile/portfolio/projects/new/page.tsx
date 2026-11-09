"use client";

import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { buttonVariants } from "@/components/ui/button-variants";
import { ProjectEditor } from "@/components/portfolio/project-editor";
import { cn } from "@/lib/utils";

export default function NewProjectPage() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6 lg:px-8">
      <Link
        href="/profile/portfolio"
        className={cn(buttonVariants({ variant: "ghost", size: "sm" }), "mb-4 -ml-2")}
      >
        <ArrowLeft className="h-4 w-4" /> Back to portfolio
      </Link>
      <header className="mb-6">
        <h1 className="text-2xl font-bold tracking-tight text-foreground">New project</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Show the actual work: what it does, the stack, and what you learned building it.
        </p>
      </header>
      <ProjectEditor mode="create" />
    </div>
  );
}
