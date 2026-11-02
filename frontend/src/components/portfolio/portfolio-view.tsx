import type { PublicPortfolioData } from "@/lib/api";
import {
  PortfolioHeader, PortfolioAbout, FeaturedProjects, SkillsSection,
  PortfolioAchievements, LearningJourney, SectionHeading,
} from "./sections";
import { ProjectBrowser } from "./project-browser";

/**
 * The public portfolio layout, composed once and reused by the shareable page
 * and by the in-app preview, so what the owner previews is exactly what a
 * visitor sees. Sections render only when the owner has content and has opted
 * them in — the API has already stripped anything kept private.
 */
export function PortfolioView({ data }: { data: PublicPortfolioData }) {
  const hasProjects = data.projects.length > 0;
  return (
    <div className="mx-auto max-w-5xl px-4 py-8 sm:px-6 sm:py-10 lg:px-8">
      <div className="space-y-12">
        <PortfolioHeader data={data} />
        <PortfolioAbout data={data} />

        <section>
          <FeaturedProjects projects={data.projects} username={data.username} />
          {hasProjects && (
            <div className="mt-10">
              <SectionHeading eyebrow="Portfolio" title="All projects" />
              <ProjectBrowser projects={data.projects} username={data.username} />
            </div>
          )}
        </section>

        <SkillsSection data={data} />
        <PortfolioAchievements data={data} />
        <LearningJourney data={data} />
      </div>
    </div>
  );
}
