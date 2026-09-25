"use client";

import { LearningModule } from "./learning-module";
import { StaggerContainer, StaggerItem } from "@/components/motion/stagger-container";
import { roadmapStages } from "@/data/roadmap";
import { Reveal } from "@/components/motion/reveal";

export function LearningModules() {
  return (
    <section className="border-t py-20 sm:py-28">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        {/* Section header */}
        <Reveal variant="fade-up">
          <div className="mb-12 sm:mb-16">
            <div className="mb-3 text-xs font-semibold uppercase tracking-wider text-primary">
              Modules
            </div>
            <h2 className="text-2xl font-bold tracking-tight sm:text-3xl lg:text-4xl">
              Explore each stage.
            </h2>
            <p className="mt-3 max-w-lg text-sm leading-relaxed text-muted-foreground sm:text-base">
              Every module is a self-contained learning unit with lessons, exercises,
              and clear outcomes. Start anywhere that matches your level.
            </p>
          </div>
        </Reveal>

        {/* Editorial layout — featured first module + grid */}
        <StaggerContainer staggerDelay={0.08}>
          {/* Featured first module — spans full width on desktop */}
          <StaggerItem>
            <div className="mb-6">
              <LearningModule stage={roadmapStages[0]} featured />
            </div>
          </StaggerItem>

          {/* Remaining modules in 2-col grid */}
          <div className="grid gap-4 sm:grid-cols-2">
            {roadmapStages.slice(1).map((stage) => (
              <StaggerItem key={stage.id}>
                <LearningModule stage={stage} />
              </StaggerItem>
            ))}
          </div>
        </StaggerContainer>
      </div>
    </section>
  );
}
