import Link from "next/link";
import {
  Award, BookOpen, Braces, Code2, Flame, Globe, Link2, MapPin,
  Mail, Sparkles, Star, Trophy, ExternalLink,
} from "lucide-react";
import type {
  PublicPortfolioData, PublicProject, ProjectCategory,
} from "@/lib/api";
import { Avatar } from "@/components/ui/avatar";
import { cn } from "@/lib/utils";
import { CATEGORY_TONES, EXTERNAL_LINK_PROPS, formatMonthYear } from "./shared";
import { ProjectCard } from "./project-card";

type Portfolio = PublicPortfolioData;

export function SectionHeading({
  eyebrow, title, description,
}: { eyebrow?: string; title: string; description?: string }) {
  return (
    <div className="mb-6">
      {eyebrow && (
        <p className="mb-1 text-xs font-semibold uppercase tracking-[0.14em] text-primary">{eyebrow}</p>
      )}
      <h2 className="text-2xl font-bold tracking-tight text-foreground">{title}</h2>
      {description && <p className="mt-1.5 max-w-2xl text-sm text-muted-foreground">{description}</p>}
    </div>
  );
}

/** Section 1 — identity, focus and the owner's chosen public links. */
export function PortfolioHeader({ data }: { data: Portfolio }) {
  const links = data.social_links || {};
  return (
    <header className="rounded-[var(--radius-card)] border border-border bg-card p-6 sm:p-8">
      <div className="flex flex-col gap-6 sm:flex-row sm:items-start sm:justify-between">
        <div className="flex min-w-0 flex-1 flex-col gap-4 sm:flex-row sm:items-center">
          <Avatar
            src={data.avatar}
            name={data.display_name}
            username={data.username}
            size={88}
            className="ring-4 ring-primary/15"
          />
          <div className="min-w-0">
            <h1 className="text-3xl font-bold tracking-tight text-foreground">{data.display_name}</h1>
            <p className="text-sm text-muted-foreground">@{data.username}</p>
            {data.headline && (
              <p className="mt-2 text-base font-medium text-foreground">{data.headline}</p>
            )}
            <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-2 text-sm text-muted-foreground">
              {data.location && (
                <span className="inline-flex items-center gap-1.5">
                  <MapPin className="h-4 w-4" aria-hidden="true" /> {data.location}
                </span>
              )}
              {data.about.currently_learning && (
                <span className="inline-flex items-center gap-1.5">
                  <Sparkles className="h-4 w-4 text-primary" aria-hidden="true" /> Learning: {data.about.currently_learning}
                </span>
              )}
            </div>
            {data.about.interests.length > 0 && (
              <div className="mt-3 flex flex-wrap gap-1.5">
                {data.about.interests.map((tag) => (
                  <span key={tag} className="rounded-pill bg-muted px-2.5 py-0.5 text-xs font-medium text-muted-foreground">
                    {tag}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="flex shrink-0 flex-wrap items-center gap-2">
          {links.github_url && (
            <HeaderLink href={links.github_url} icon={Code2} label="GitHub" />
          )}
          {links.linkedin_url && (
            <HeaderLink href={links.linkedin_url} icon={Link2} label="LinkedIn" />
          )}
          {links.website_url && (
            <HeaderLink href={links.website_url} icon={Globe} label="Website" />
          )}
          {data.contact_enabled && (
            <HeaderLink href={`/profile/${data.username}`} icon={Mail} label="Contact" internal />
          )}
        </div>
      </div>
    </header>
  );
}

function HeaderLink({
  href, icon: Icon, label, internal,
}: { href: string; icon: typeof Code2; label: string; internal?: boolean }) {
  const classes =
    "inline-flex items-center gap-2 rounded-lg border border-border bg-background px-3 py-2 text-sm font-medium text-foreground transition-colors hover:border-primary/30 hover:bg-primary/5";
  if (internal) {
    return (
      <Link href={href} className={classes}>
        <Icon className="h-4 w-4" aria-hidden="true" /> {label}
      </Link>
    );
  }
  return (
    <a href={href} {...EXTERNAL_LINK_PROPS} className={classes}>
      <Icon className="h-4 w-4" aria-hidden="true" /> {label}
    </a>
  );
}

/** Section 2 — a concise, self-written introduction (never auto-generated). */
export function PortfolioAbout({ data }: { data: Portfolio }) {
  const { about } = data;
  if (!about.text && !about.enjoys_building && about.interests.length === 0) return null;
  return (
    <section>
      <SectionHeading eyebrow="About" title="Who I am" />
      {about.text && (
        <p className="max-w-3xl whitespace-pre-line text-[15px] leading-7 text-muted-foreground">{about.text}</p>
      )}
      {about.enjoys_building && (
        <p className="mt-3 max-w-3xl text-sm text-muted-foreground">
          <span className="font-semibold text-foreground">Enjoys building: </span>{about.enjoys_building}
        </p>
      )}
    </section>
  );
}

/** Section 3 — the highlighted work, given stronger presentation. */
export function FeaturedProjects({ projects, username }: { projects: PublicProject[]; username: string }) {
  const featured = projects.filter((p) => p.featured).slice(0, 3);
  if (featured.length === 0) return null;
  return (
    <section>
      <SectionHeading eyebrow="Selected work" title="Featured projects" />
      <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
        {featured.map((project) => (
          <ProjectCard
            key={project.id}
            project={project}
            detailHref={`/profile/${username}/projects/${project.slug}`}
          />
        ))}
      </div>
    </section>
  );
}

/** Section 4 — the full collection as a readable grid. */
export function ProjectGrid({ projects, username }: { projects: PublicProject[]; username: string }) {
  if (projects.length === 0) return null;
  return (
    <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
      {projects.map((project) => (
        <ProjectCard key={project.id} project={project} detailHref={`/profile/${username}/projects/${project.slug}`} />
      ))}
    </div>
  );
}

export const ALL_CATEGORIES: ProjectCategory[] = [
  "web_development", "ai", "machine_learning", "backend", "frontend",
  "mobile", "developer_tools", "automation", "data_science", "other",
];

export function categoryTone(category: ProjectCategory): string {
  return CATEGORY_TONES[category] ?? CATEGORY_TONES.other;
}

/** Section 5 — technologies, honestly split into self-reported vs demonstrated. */
export function SkillsSection({ data }: { data: Portfolio }) {
  const skills = data.skills;
  if (!skills.visible || skills.groups.length === 0) return null;
  return (
    <section>
      <SectionHeading
        eyebrow="Capabilities"
        title="Technical skills"
        description="A checkmark marks skills backed by a completed Code Yaar course. Everything else is self-reported by the developer."
      />
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {skills.groups.map((group) => (
          <SkillCategory key={group.category} category={group.category} items={group.items} />
        ))}
      </div>
    </section>
  );
}

export function SkillCategory({
  category, items,
}: {
  category: string;
  items: PublicPortfolioData["skills"]["groups"][number]["items"];
}) {
  return (
    <div className="rounded-[var(--radius-card)] border border-border bg-card p-4">
      <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-muted-foreground">{category}</h3>
      <ul className="space-y-2">
        {items.map((item) => (
          <li key={item.name} className="flex items-center justify-between gap-2 text-sm">
            <span className="text-foreground">{item.name}</span>
            <span
              className={cn(
                "inline-flex items-center gap-1 rounded-pill px-2 py-0.5 text-[11px] font-medium",
                item.demonstrated ? "bg-success/10 text-success" : "text-muted-foreground",
              )}
              title={item.demonstrated ? "Demonstrated through a completed Code Yaar course" : "Self-reported"}
            >
              {item.demonstrated ? (
                <>
                  <Star className="h-3 w-3 fill-current" aria-hidden="true" />
                  {item.proficiency_label || "Demonstrated"}
                </>
              ) : (
                item.proficiency_label || "Self-reported"
              )}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}

const BADGE_ICONS = {
  course: BookOpen, chapter: BookOpen, streak: Flame, exercise: Braces,
  skill: Sparkles, special: Award, excellence: Trophy, project: Code2,
} as const;

/** Section 6 — real achievements from the existing badge system. */
export function PortfolioAchievements({ data }: { data: Portfolio }) {
  const achievements = data.achievements;
  if (!achievements.visible || achievements.items.length === 0) return null;
  return (
    <section>
      <SectionHeading eyebrow="Milestones" title="Achievements" description="Earned on Code Yaar — never fabricated." />
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {achievements.items.map((badge) => {
          const Icon = BADGE_ICONS[badge.category as keyof typeof BADGE_ICONS] ?? Award;
          return (
            <a
              key={badge.slug}
              href={badge.verification_url}
              {...EXTERNAL_LINK_PROPS}
              className="flex items-start gap-3 rounded-[var(--radius-card)] border border-border bg-card p-4 transition-colors hover:border-primary/30"
            >
              <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
                <Icon className="h-5 w-5" aria-hidden="true" />
              </span>
              <span className="min-w-0">
                <span className="block text-sm font-semibold text-foreground">{badge.title}</span>
                <span className="mt-0.5 block line-clamp-2 text-xs text-muted-foreground">{badge.description}</span>
                <span className="mt-1 block text-[11px] text-muted-foreground">Earned {formatMonthYear(badge.earned_at)}</span>
              </span>
            </a>
          );
        })}
      </div>
    </section>
  );
}

/** Section 7 — optional, privacy-respecting learning progress. */
export function LearningJourney({ data }: { data: Portfolio }) {
  const journey = data.learning_journey;
  if (!journey.visible || (journey.tracks_completed.length === 0 && journey.courses_completed.length === 0)) {
    return null;
  }
  return (
    <section>
      <SectionHeading eyebrow="Journey" title="Learning progress" />
      <div className="grid gap-4 lg:grid-cols-2">
        {journey.tracks_completed.length > 0 && (
          <div className="rounded-[var(--radius-card)] border border-border bg-card p-5">
            <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-muted-foreground">Completed tracks</h3>
            <ul className="space-y-2">
              {journey.tracks_completed.map((track) => (
                <li key={track.slug}>
                  <Link href={`/tracks/${track.slug}`} className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline">
                    <Trophy className="h-4 w-4" aria-hidden="true" /> {track.title}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        )}
        {journey.courses_completed.length > 0 && (
          <div className="rounded-[var(--radius-card)] border border-border bg-card p-5">
            <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-muted-foreground">Completed courses</h3>
            <ul className="space-y-2">
              {journey.courses_completed.map((course, i) => (
                <li key={`${course.title}-${i}`} className="flex items-baseline justify-between gap-3 text-sm">
                  <span className="text-foreground">{course.title}</span>
                  <span className="shrink-0 text-xs text-muted-foreground">{course.track}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </section>
  );
}

/** Full-page empty state for an owner with no projects yet. */
export function EmptyPortfolioState({
  title, description, action,
}: { title: string; description: string; action?: React.ReactNode }) {
  return (
    <div className="flex flex-col items-center justify-center rounded-[var(--radius-card)] border border-dashed border-border bg-muted/20 px-6 py-16 text-center">
      <span className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 text-primary">
        <Code2 className="h-6 w-6" aria-hidden="true" />
      </span>
      <h3 className="text-base font-semibold text-foreground">{title}</h3>
      <p className="mt-1 max-w-sm text-sm text-muted-foreground">{description}</p>
      {action && <div className="mt-5">{action}</div>}
    </div>
  );
}

export { ExternalLink };
