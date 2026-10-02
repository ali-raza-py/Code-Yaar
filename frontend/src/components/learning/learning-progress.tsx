"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Reveal } from "@/components/motion/reveal";
import { ArrowRight } from "lucide-react";

const orbitalStages = ["Foundation", "Problem Solving", "Web", "Applications", "Projects", "Proof"];

export function LearningProgress() {
  return (
    <Reveal variant="fade-up">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="relative overflow-hidden rounded-xl border border-border/40 bg-surface-recessed/50 p-8 sm:p-12">
          {/* Subtle grid */}
          <div className="absolute inset-0 bg-grid-sm opacity-[0.04]" />

          <div className="relative flex flex-col items-center gap-8 lg:flex-row lg:gap-16">
            {/* Orbital visualization */}
            <div className="relative h-48 w-48 shrink-0 sm:h-56 sm:w-56">
              {/* Concentric orbital rings */}
              {orbitalStages.map((_, i) => (
                <motion.div
                  key={i}
                  className="absolute inset-0 rounded-full border border-primary/[0.08]"
                  style={{
                    transform: `scale(${0.3 + i * 0.14})`,
                  }}
                  animate={{ rotate: i % 2 === 0 ? 360 : -360 }}
                  transition={{
                    duration: 20 + i * 8,
                    repeat: Infinity,
                    ease: "linear",
                  }}
                >
                  {/* Small dot on each ring */}
                  <div
                    className="absolute h-1.5 w-1.5 rounded-full bg-primary/20"
                    style={{
                      top: "0",
                      left: "50%",
                      transform: "translate(-50%, -50%)",
                    }}
                  />
                </motion.div>
              ))}

              {/* Center node */}
              <div className="absolute inset-0 flex items-center justify-center">
                <motion.div
                  className="flex h-12 w-12 items-center justify-center rounded-full border border-primary/20 bg-surface-elevated"
                  animate={{ scale: [1, 1.05, 1] }}
                  transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
                >
                  <span className="font-mono text-xs font-bold text-primary/60">YOU</span>
                </motion.div>
              </div>
            </div>

            {/* Text content */}
            <div className="max-w-md text-center lg:text-left">
              <div className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-3">
                Your Path
              </div>
              <h2 className="text-xl font-bold">
                No learning activity yet.
              </h2>
              <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
                Start your first module and your progress will appear here.
                Your journey through the engineering path begins with a single step.
              </p>
              <div className="mt-6">
                <Link href="#roadmap">
                  <Button size="sm" className="gap-2">
                    Begin
                    <ArrowRight className="ml-1 h-3 w-3" />
                  </Button>
                </Link>
              </div>
              {/* Terminal micro-detail */}
              <div className="mt-6 font-mono text-xs text-muted-foreground/40">
                progress.empty() <span className="text-primary/30">{"// waiting for first commit"}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Reveal>
  );
}
