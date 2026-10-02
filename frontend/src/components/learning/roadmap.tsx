"use client";

import { useRef } from "react";
import { motion, useInView } from "framer-motion";
import { RoadmapStage } from "./roadmap-stage";
import { roadmapStages } from "@/data/roadmap";
import { Reveal } from "@/components/motion/reveal";

export function Roadmap() {
  const headerRef = useRef<HTMLDivElement>(null);
  const headerInView = useInView(headerRef, { once: true, margin: "-80px" });

  return (
    <section id="roadmap" className="py-20 sm:py-28 overflow-hidden bg-surface-recessed/50">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        {/* Section header */}
        <div ref={headerRef} className="mb-16 sm:mb-20">
          <Reveal variant="fade-in">
            <div className="mb-3 text-xs font-semibold uppercase tracking-wider text-primary">
              Your Engineering Path
            </div>
          </Reveal>
          <Reveal variant="fade-up" delay={0.1}>
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl lg:text-5xl">
              Six stages.
              <br />
              <span className="text-primary">One continuous path.</span>
            </h2>
          </Reveal>
          <Reveal variant="fade-up" delay={0.2}>
            <p className="mt-4 max-w-lg text-sm leading-relaxed text-muted-foreground sm:text-base">
              Each stage builds on the last. Master fundamentals, develop problem-solving skills,
              build for the web, create complete applications, ship real projects, and prove your engineering ability.
            </p>
          </Reveal>

          {/* Terminal micro-detail */}
          <Reveal variant="fade-in" delay={0.3}>
            <div className="mt-4 font-mono text-xs text-muted-foreground/40">
              roadmap.stages <span className="text-primary/30">=</span> {roadmapStages.length}
              <span className="text-muted-foreground/30"> | </span>
              module.status <span className="text-primary/30">=</span> <span className="text-accent">unlocked</span>
            </div>
          </Reveal>
        </div>

        {/* Roadmap visualization — spatial with perspective */}
        <div className="perspective-scene">
          <div className="space-y-0">
            {roadmapStages.map((stage, i) => (
              <RoadmapStage
                key={stage.id}
                stage={stage}
                index={i}
                isLast={i === roadmapStages.length - 1}
              />
            ))}
          </div>
        </div>

        {/* End node */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={headerInView ? { opacity: 1, scale: 1 } : { opacity: 0, scale: 0.9 }}
          transition={{ duration: 0.5, delay: 1.2 }}
          className="mt-12 flex justify-center"
        >
          <div className="flex items-center gap-3 rounded-full border border-primary/15 bg-surface-elevated px-6 py-3 shadow-sm">
            <motion.div
              className="h-2.5 w-2.5 rounded-full bg-accent"
              animate={{ scale: [1, 1.3, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
            />
            <span className="font-mono text-xs font-medium text-muted-foreground">
              journey complete
            </span>
            <span className="text-xs text-muted-foreground/40">→</span>
            <span className="font-mono text-xs text-primary font-semibold">evolve</span>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
