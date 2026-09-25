"use client";

import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowRight } from "lucide-react";
import type { RoadmapStage } from "@/types";

interface RoadmapNodeProps {
  stage: RoadmapStage;
  index: number;
}

export function RoadmapNode({ stage, index }: RoadmapNodeProps) {
  const [active, setActive] = useState(false);

  const number = String(stage.number).padStart(2, "0");
  const time = formatTime(stage.estimatedMinutes);

  const handleEnter = useCallback(() => {
    setActive(true);
  }, []);

  const handleLeave = useCallback(() => {
    setActive(false);
  }, []);

  return (
    <div
      className="relative"
      onMouseEnter={handleEnter}
      onMouseLeave={handleLeave}
      role="button"
      tabIndex={0}
      onFocus={handleEnter}
      onBlur={handleLeave}
      aria-label={`Stage ${number}: ${stage.title}. ${stage.milestones.length} milestones. ${time} estimated.`}
    >
      {/* Desktop layout — asymmetric with depth */}
      <div className="hidden lg:block">
        <div className="grid grid-cols-[1fr_auto_1fr] items-center gap-8">
          {/* Left content — stage info */}
          <div className={index % 2 === 0 ? "text-right" : "text-left order-3"}>
            <motion.div
              animate={{ y: active ? -6 : 0 }}
              transition={{ type: "spring", stiffness: 400, damping: 25 }}
            >
              {/* Oversized background number */}
              <div className="relative">
                <span className="stage-number" style={{ top: "-1.5rem", [index % 2 === 0 ? "right" : "left"]: "0" }}>
                  {number}
                </span>

                <div className="text-xs font-medium text-primary/60 mb-2">
                  {number} / {stage.id.toUpperCase().replace("-", " ")}
                </div>
                <h3 className="text-2xl font-bold tracking-tight">
                  {stage.title}
                </h3>
                <p className="mt-2 max-w-sm text-sm leading-relaxed text-muted-foreground" style={{ marginLeft: index % 2 === 0 ? "auto" : 0 }}>
                  {stage.description}
                </p>

                {/* Meta row */}
                <div className="mt-4 flex items-center gap-3 text-xs font-mono text-muted-foreground/60" style={{ justifyContent: index % 2 === 0 ? "flex-end" : "flex-start" }}>
                  <span>{stage.milestones.length} milestones</span>
                  <span className="text-primary/30">·</span>
                  <span>{time}</span>
                  <span className="text-primary/30">·</span>
                  <span className={stage.status === "available" ? "text-accent" : "text-muted-foreground/40"}>
                    {stage.status}
                  </span>
                </div>
              </div>
            </motion.div>
          </div>

          {/* Center node */}
          <div className="relative flex flex-col items-center">
            <motion.div
              animate={{
                scale: active ? 1.2 : 1,
                borderRadius: active ? "35% 65% 65% 35% / 35% 35% 65% 65%" : "50%",
              }}
              transition={{ type: "spring", stiffness: 300, damping: 20 }}
              className="relative z-10 flex h-16 w-16 items-center justify-center border-2 border-primary/30 bg-surface-elevated"
              style={{
                boxShadow: active ? "0 0 30px var(--glow-primary, oklch(0.62 0.15 195 / 0.15))" : "none",
              }}
            >
              <span className="font-mono text-lg font-bold text-primary">
                {number}
              </span>
              {/* Pulse ring for available */}
              {stage.status === "available" && (
                <motion.div
                  className="absolute inset-0 rounded-full border border-primary/20"
                  animate={{ scale: [1, 1.4, 1], opacity: [0.4, 0, 0.4] }}
                  transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
                />
              )}
            </motion.div>
          </div>

          {/* Right content — skills panel (reveals on hover) */}
          <div className={index % 2 === 0 ? "text-left order-3" : "text-right"}>
            <AnimatePresence>
              {active && (
                <motion.div
                  initial={{ opacity: 0, x: index % 2 === 0 ? -20 : 20, filter: "blur(4px)" }}
                  animate={{ opacity: 1, x: 0, filter: "blur(0px)" }}
                  exit={{ opacity: 0, x: index % 2 === 0 ? -20 : 20, filter: "blur(4px)" }}
                  transition={{ type: "spring", stiffness: 400, damping: 25 }}
                >
                  <div className="rounded-lg border border-border/40 bg-surface-elevated p-4 shadow-lg">
                    {/* Skills grid */}
                    <div className="flex flex-wrap gap-1.5">
                      {stage.skills.map((skill) => (
                        <span
                          key={skill}
                          className="rounded-sm border border-border/50 bg-surface-recessed px-2 py-0.5 font-mono text-xs text-muted-foreground"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>

                    {/* Milestones preview */}
                    <div className="mt-3 space-y-1">
                      {stage.milestones.slice(0, 3).map((m) => (
                        <div key={m.id} className="flex items-center gap-2 text-xs text-muted-foreground/70">
                          <span className="h-1 w-1 rounded-full bg-primary/40" />
                          <span>{m.title}</span>
                        </div>
                      ))}
                      {stage.milestones.length > 3 && (
                        <div className="text-xs text-muted-foreground/40 font-mono">
                          +{stage.milestones.length - 3} more
                        </div>
                      )}
                    </div>

                    {/* CTA */}
                    <div className="mt-3 flex items-center gap-2">
                      <span className="text-xs font-medium text-primary">Explore</span>
                      <ArrowRight className="h-3 w-3 text-primary" />
                    </div>

                    {/* Code metadata */}
                    <div className="mt-2 font-mono text-[10px] text-muted-foreground/30">
                      module.{stage.id} <span className="text-primary/20">→</span> status: {stage.status}
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>

      {/* Mobile layout — vertical timeline */}
      <div className="lg:hidden">
        <div className="flex gap-4">
          {/* Timeline node */}
          <div className="relative flex flex-col items-center">
            <motion.div
              animate={{
                scale: active ? 1.1 : 1,
                borderRadius: active ? "35% 65% 65% 35% / 35% 35% 65% 65%" : "50%",
              }}
              transition={{ type: "spring", stiffness: 400, damping: 20 }}
              className="relative z-10 flex h-12 w-12 items-center justify-center border-2 border-primary/30 bg-surface-elevated"
            >
              <span className="font-mono text-sm font-bold text-primary">
                {number}
              </span>
            </motion.div>
          </div>

          {/* Content */}
          <div className="flex-1 pb-12">
            <div className="text-xs font-medium text-primary/60 mb-1">{number}</div>
            <h3 className="text-lg font-bold tracking-tight">{stage.title}</h3>
            <p className="mt-1.5 text-sm leading-relaxed text-muted-foreground">
              {stage.description}
            </p>
            <div className="mt-2 flex items-center gap-2 text-xs font-mono text-muted-foreground/60">
              <span>{stage.milestones.length} milestones</span>
              <span className="text-primary/30">·</span>
              <span>{time}</span>
            </div>

            {/* Skills expand */}
            <AnimatePresence>
              {active && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.25, ease: [0.25, 0.1, 0.25, 1] }}
                  className="overflow-hidden"
                >
                  <div className="mt-3 flex flex-wrap gap-1.5">
                    {stage.skills.map((skill) => (
                      <span
                        key={skill}
                        className="rounded-sm border border-border/60 bg-surface-recessed px-2 py-0.5 font-mono text-xs text-muted-foreground"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </div>
  );
}

function formatTime(minutes: number): string {
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  if (h === 0) return `${m}m`;
  return `${String(h).padStart(2, "0")}h ${String(m).padStart(2, "0")}m`;
}
