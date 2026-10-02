"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowRight } from "lucide-react";
import type { RoadmapStage } from "@/types";

interface LearningModuleProps {
  stage: RoadmapStage;
  featured?: boolean;
}

export function LearningModule({ stage, featured = false }: LearningModuleProps) {
  const [hovered, setHovered] = useState(false);

  const number = String(stage.number).padStart(2, "0");
  const time = formatTime(stage.estimatedMinutes);

  if (featured) {
    return (
      <motion.div
        className="group relative"
        onHoverStart={() => setHovered(true)}
        onHoverEnd={() => setHovered(false)}
        whileHover={{ y: -2 }}
        transition={{ type: "spring", stiffness: 400, damping: 25 }}
      >
        <div className="relative overflow-hidden rounded-xl border border-border/40 bg-surface-recessed/50 p-8 sm:p-10 transition-colors duration-300 hover:border-primary/20 hover:shadow-sm">
          {/* Background stage number */}
          <div className="stage-number" style={{ top: "-0.5rem", right: "1rem" }}>
            {number}
          </div>

          <div className="relative grid gap-6 md:grid-cols-[1.5fr_1fr] md:gap-12">
            {/* Left — main info */}
            <div>
              <div className="text-xs font-medium text-primary/60 mb-2">
                {number} <span className="text-primary/30">/</span> {stage.id.toUpperCase().replace("-", " ")}
              </div>
              <h3 className="text-2xl font-bold tracking-tight sm:text-3xl">
                {stage.title}
              </h3>
              <p className="mt-3 max-w-lg text-sm leading-relaxed text-muted-foreground sm:text-base">
                {stage.description}
              </p>

              {/* Skills */}
              <div className="mt-5 flex flex-wrap gap-1.5">
                {stage.skills.map((skill) => (
                  <span
                    key={skill}
                    className="rounded-sm border border-border/50 bg-surface-recessed px-2.5 py-1 font-mono text-xs text-muted-foreground"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>

            {/* Right — meta + action */}
            <div className="flex flex-col justify-between">
              <div className="space-y-3">
                <div className="flex items-center gap-4 text-xs font-mono text-muted-foreground/60">
                  <span>{stage.milestones.length} milestones</span>
                  <span className="text-primary/30">·</span>
                  <span>{time}</span>
                </div>

                {/* Milestones preview */}
                <div className="space-y-1.5">
                  {stage.milestones.slice(0, 4).map((m) => (
                    <div key={m.id} className="flex items-center gap-2 text-xs text-muted-foreground/70">
                      <span className="h-1 w-1 rounded-full bg-primary/30" />
                      <span>{m.title}</span>
                    </div>
                  ))}
                  {stage.milestones.length > 4 && (
                    <div className="text-xs text-muted-foreground/40 font-mono pl-3">
                      +{stage.milestones.length - 4} more
                    </div>
                  )}
                </div>
              </div>

              {/* Action */}
              <div className="mt-6">
                <button className="group/btn inline-flex items-center gap-2 text-sm font-medium text-primary transition-colors hover:text-primary/80">
                  Start Module
                  <ArrowRight className="h-3.5 w-3.5 transition-transform group-hover/btn:translate-x-1" />
                </button>
              </div>

              {/* Code metadata on hover */}
              <AnimatePresence>
                {hovered && (
                  <motion.div
                    initial={{ opacity: 0, y: 4 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: 4 }}
                    transition={{ duration: 0.2 }}
                    className="mt-3 font-mono text-[10px] text-muted-foreground/30"
                  >
                    module.{stage.id} <span className="text-primary/20">→</span> status: {stage.status} · difficulty: beginner
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>

          {/* Top accent line */}
          <div className="absolute left-0 top-0 h-px w-full bg-gradient-to-r from-transparent via-primary/25 to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100" />
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      className="group relative"
      onHoverStart={() => setHovered(true)}
      onHoverEnd={() => setHovered(false)}
      whileHover={{ y: -2 }}
      transition={{ type: "spring", stiffness: 400, damping: 25 }}
    >
      <div className="relative h-full overflow-hidden rounded-lg border border-border/40 bg-surface-recessed/50 p-6 transition-colors duration-300 hover:border-primary/20 hover:shadow-sm sm:p-7">
        {/* Stage number + label */}
        <div className="flex items-start justify-between">
          <div>
            <div className="text-xs font-medium text-muted-foreground/50">
              {number} <span className="text-primary/30">/</span> {stage.id.toUpperCase().replace("-", " ")}
            </div>
            <h3 className="mt-2 text-lg font-bold tracking-tight sm:text-xl">
              {stage.title}
            </h3>
          </div>
          <div className="flex flex-col items-end gap-1">
            <span className="font-mono text-xs text-muted-foreground/40">
              {stage.milestones.length} milestones
            </span>
            <span className="font-mono text-xs text-muted-foreground/40">
              {time}
            </span>
          </div>
        </div>

        {/* Description */}
        <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
          {stage.description}
        </p>

        {/* Skills */}
        <div className="mt-4 flex flex-wrap gap-1.5">
          {stage.skills.slice(0, 4).map((skill) => (
            <span
              key={skill}
              className="rounded-sm border border-border/50 bg-surface-recessed px-2 py-0.5 font-mono text-xs text-muted-foreground"
            >
              {skill}
            </span>
          ))}
          {stage.skills.length > 4 && (
            <span className="px-2 py-0.5 font-mono text-xs text-muted-foreground/40">
              +{stage.skills.length - 4}
            </span>
          )}
        </div>

        {/* Action */}
        <div className="mt-5 flex items-center justify-between">
          <button className="group/btn inline-flex items-center gap-2 text-sm font-medium text-primary transition-colors hover:text-primary/80">
            Start Module
            <ArrowRight className="h-3.5 w-3.5 transition-transform group-hover/btn:translate-x-1" />
          </button>

          {/* Code-inspired metadata on hover */}
          <AnimatePresence>
            {hovered && (
              <motion.div
                initial={{ opacity: 0, x: 8 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 8 }}
                transition={{ duration: 0.2 }}
                className="hidden font-mono text-[10px] text-muted-foreground/30 sm:block"
              >
                module.{stage.id} <span className="text-primary/20">→</span> {stage.status}
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Subtle top accent line */}
        <div className="absolute left-0 top-0 h-px w-full bg-gradient-to-r from-transparent via-primary/15 to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100" />
      </div>
    </motion.div>
  );
}

function formatTime(minutes: number): string {
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  if (h === 0) return `${m}m`;
  return `${String(h).padStart(2, "0")}h ${String(m).padStart(2, "0")}m`;
}
