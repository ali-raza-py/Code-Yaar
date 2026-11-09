import Link from "next/link";
import { ArrowLeft, Code2, ExternalLink, FileText, Star } from "lucide-react";
import type { PublicProject } from "@/lib/api";
import { PROJECT_CATEGORY_LABELS } from "@/lib/api";
import { cn } from "@/lib/utils";
import { CATEGORY_TONES, STATUS_TONES, EXTERNAL_LINK_PROPS, formatMonthYear } from "./shared";

function Prose({ children }: { children: string }) {
  return <p className="whitespace-pre-line text-[15px] leading-7 text-muted-foreground">{children}</p>;
}

function Block({ title, body }: { title: string; body: string }) {
  if (!body) return null;
  return (
    <section className="border-t border-border pt-6">
      <h2 className="mb-3 text-lg font-semibold tracking-tight text-foreground">{title}</h2>
      <Prose>{body}</Prose>
    </section>
  );
}

/** Full detail presentation for a single project. Links appear only if given. */
export function ProjectDetails({
  project, username,
}: { project: PublicProject; username: string }) {
  const dates = [
    formatMonthYear(project.start_date),
    formatMonthYear(project.completion_date),
  ].filter(Boolean).join(" – ");

  return (
    <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6 lg:px-8">
      <Link
        href={`/profile/${username}/portfolio`}
        className="mb-6 inline-flex items-center gap-1.5 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
      >
        <ArrowLeft className="h-4 w-4" aria-hidden="true" /> Back to portfolio
      </Link>

      <div className="mb-6 flex flex-wrap items-center gap-2">
        <span className={cn("inline-flex rounded-pill border px-2 py-0.5 text-[11px] font-medium", CATEGORY_TONES[project.category])}>
          {PROJECT_CATEGORY_LABELS[project.category]}
        </span>
        {project.status_label && (
          <span className={cn("inline-flex rounded-pill border px-2 py-0.5 text-[11px] font-medium", STATUS_TONES[project.status])}>
            {project.status_label}
          </span>
        )}
        {project.featured && (
          <span className="inline-flex items-center gap-1 rounded-pill bg-primary/10 px-2 py-0.5 text-[11px] font-semibold text-primary">
            <Star className="h-3 w-3 fill-current" aria-hidden="true" /> Featured
          </span>
        )}
        {dates && <span className="text-xs text-muted-foreground">{dates}</span>}
      </div>

      <h1 className="text-3xl font-bold tracking-tight text-foreground">{project.title}</h1>
      <p className="mt-2 text-base text-muted-foreground">{project.short_description}</p>

      <div className="mt-6 flex flex-wrap gap-2">
        {project.github_url && (
          <a href={project.github_url} {...EXTERNAL_LINK_PROPS} className="inline-flex items-center gap-2 rounded-lg border border-border bg-background px-3 py-2 text-sm font-medium text-foreground transition-colors hover:border-primary/30 hover:bg-primary/5">
            <Code2 className="h-4 w-4" aria-hidden="true" /> Repository
          </a>
        )}
        {project.live_demo_url && (
          <a href={project.live_demo_url} {...EXTERNAL_LINK_PROPS} className="inline-flex items-center gap-2 rounded-lg border border-border bg-background px-3 py-2 text-sm font-medium text-foreground transition-colors hover:border-primary/30 hover:bg-primary/5">
            <ExternalLink className="h-4 w-4" aria-hidden="true" /> Live demo
          </a>
        )}
        {project.docs_url && (
          <a href={project.docs_url} {...EXTERNAL_LINK_PROPS} className="inline-flex items-center gap-2 rounded-lg border border-border bg-background px-3 py-2 text-sm font-medium text-foreground transition-colors hover:border-primary/30 hover:bg-primary/5">
            <FileText className="h-4 w-4" aria-hidden="true" /> Documentation
          </a>
        )}
      </div>

      {project.cover_image_url && (
        // eslint-disable-next-line @next/next/no-img-element
        <img src={project.cover_image_url} alt={project.title} className="mt-8 aspect-[16/9] w-full rounded-[var(--radius-card)] border border-border object-cover" />
      )}

      {project.technologies.length > 0 && (
        <div className="mt-6 flex flex-wrap gap-1.5">
          {project.technologies.map((tech) => (
            <span key={tech} className="rounded-md bg-muted px-2.5 py-1 text-xs font-medium text-muted-foreground">{tech}</span>
          ))}
        </div>
      )}

      <div className="mt-8 space-y-6">
        {project.overview && (
          <section>
            <h2 className="mb-3 text-lg font-semibold tracking-tight text-foreground">Overview</h2>
            <Prose>{project.overview}</Prose>
          </section>
        )}
        <Block title="The problem" body={project.problem_statement} />
        <Block title="The solution" body={project.solution} />
        <Block title="Technical implementation" body={project.technical_details} />
        <Block title="My role & contributions" body={project.contributions} />
        <Block title="Challenges" body={project.challenges} />
        <Block title="What I learned" body={project.lessons_learned} />

        {project.images.length > 0 && (
          <section className="border-t border-border pt-6">
            <h2 className="mb-4 text-lg font-semibold tracking-tight text-foreground">Screenshots</h2>
            <div className="grid gap-4 sm:grid-cols-2">
              {project.images.map((image) => (
                // eslint-disable-next-line @next/next/no-img-element
                <img key={image.id} src={image.image_url} alt={image.alt_text || project.title} className="aspect-video w-full rounded-[var(--radius-card)] border border-border object-cover" loading="lazy" />
              ))}
            </div>
          </section>
        )}
      </div>
    </div>
  );
}
