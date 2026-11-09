import Link from "next/link";
import { Code2, ExternalLink, Star } from "lucide-react";
import type { PublicProject } from "@/lib/api";
import { PROJECT_CATEGORY_LABELS } from "@/lib/api";
import { cn } from "@/lib/utils";
import { CATEGORY_TONES, STATUS_TONES, EXTERNAL_LINK_PROPS } from "./shared";

/**
 * A single portfolio project card. Presentational and server-render safe: it
 * shows only what the owner supplied (a repo/demo icon appears only when the
 * matching link exists) and never invents content.
 */
export function ProjectCard({
  project,
  detailHref,
}: {
  project: PublicProject;
  detailHref?: string;
}) {
  const categoryLabel = PROJECT_CATEGORY_LABELS[project.category] ?? project.category;
  const statusLabel = project.status_label;
  const tags = project.technologies.slice(0, 4);
  const extraTags = project.technologies.length - tags.length;

  const cover = (
    <div className="relative aspect-[16/9] w-full overflow-hidden rounded-t-[var(--radius-card)] bg-muted">
      {project.cover_image_url ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={project.cover_image_url}
          alt={project.title}
          className="h-full w-full object-cover"
          loading="lazy"
        />
      ) : (
        <div className="flex h-full w-full items-center justify-center bg-gradient-to-br from-primary/5 to-primary/15 text-4xl font-black text-primary/30">
          {project.title.charAt(0).toUpperCase()}
        </div>
      )}
      {project.featured && (
        <span className="absolute left-3 top-3 inline-flex items-center gap-1 rounded-pill bg-card/90 px-2 py-0.5 text-[11px] font-semibold text-primary shadow-sm backdrop-blur">
          <Star className="h-3 w-3 fill-current" aria-hidden="true" /> Featured
        </span>
      )}
    </div>
  );

  const body = (
    <div className="flex flex-1 flex-col gap-3 p-5">
      <div className="flex flex-wrap items-center gap-2">
        <span className={cn("inline-flex rounded-pill border px-2 py-0.5 text-[11px] font-medium", CATEGORY_TONES[project.category])}>
          {categoryLabel}
        </span>
        {statusLabel && (
          <span className={cn("inline-flex rounded-pill border px-2 py-0.5 text-[11px] font-medium", STATUS_TONES[project.status])}>
            {statusLabel}
          </span>
        )}
      </div>

      <h3 className="text-lg font-semibold leading-snug tracking-tight text-foreground">{project.title}</h3>
      <p className="line-clamp-2 text-sm leading-relaxed text-muted-foreground">{project.short_description}</p>

      {tags.length > 0 && (
        <div className="mt-auto flex flex-wrap gap-1.5 pt-1">
          {tags.map((tech) => (
            <span key={tech} className="rounded-md bg-muted px-2 py-0.5 text-[11px] font-medium text-muted-foreground">
              {tech}
            </span>
          ))}
          {extraTags > 0 && (
            <span className="rounded-md px-1 py-0.5 text-[11px] text-muted-foreground">+{extraTags}</span>
          )}
        </div>
      )}

      <div className="flex items-center justify-between pt-2">
        <div className="flex items-center gap-3">
          {project.github_url && (
            <a
              href={project.github_url}
              {...EXTERNAL_LINK_PROPS}
              className="inline-flex items-center gap-1 text-xs font-medium text-muted-foreground transition-colors hover:text-foreground"
            >
              <Code2 className="h-4 w-4" aria-hidden="true" /> Code
            </a>
          )}
          {project.live_demo_url && (
            <a
              href={project.live_demo_url}
              {...EXTERNAL_LINK_PROPS}
              className="inline-flex items-center gap-1 text-xs font-medium text-muted-foreground transition-colors hover:text-foreground"
            >
              <ExternalLink className="h-4 w-4" aria-hidden="true" /> Live
            </a>
          )}
        </div>
        {detailHref && (
          <span className="text-xs font-semibold text-primary">View details →</span>
        )}
      </div>
    </div>
  );

  const cardClass =
    "group flex flex-col overflow-hidden rounded-[var(--radius-card)] border border-border bg-card transition-colors hover:border-primary/30";

  if (detailHref) {
    return (
      <Link href={detailHref} className={cn(cardClass, "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring")}>
        {cover}
        {body}
      </Link>
    );
  }
  return <article className={cardClass}>{cover}{body}</article>;
}
