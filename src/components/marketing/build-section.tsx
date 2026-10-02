"use client";

import { motion } from "framer-motion";
import { Reveal } from "@/components/motion/reveal";

const pipeline = [
  { title: "Architecture", status: "complete" },
  { title: "Database", status: "complete" },
  { title: "API", status: "complete" },
  { title: "Frontend", status: "current" },
  { title: "Testing", status: "pending" },
  { title: "Deployment", status: "pending" },
];

const features = [
  { label: "Structured projects", desc: "Clear milestones and goals" },
  { label: "Real technologies", desc: "Industry-standard tools" },
  { label: "Progress tracking", desc: "See how far you've come" },
  { label: "Proof of work", desc: "Document what you've built" },
];

export function BuildSection() {
  const completedCount = pipeline.filter((s) => s.status === "complete").length;

  return (
    <section className="border-b bg-surface-recessed/50 py-20 sm:py-28">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="grid gap-12 lg:grid-cols-[1.2fr_1fr] lg:gap-20">
          {/* Left — Project pipeline visualization */}
          <Reveal variant="fade-up">
            <div>
              <div className="mb-6">
                <div className="mb-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Project Lab
                </div>
                <h3 className="text-lg font-semibold">Build: REST API</h3>
                <p className="mt-1 text-sm text-muted-foreground">
                  A complete RESTful API with validation and documentation.
                </p>
              </div>

              {/* Pipeline — not a boring progress bar */}
              <div className="space-y-1">
                {pipeline.map((stage, i) => (
                  <motion.div
                    key={stage.title}
                    className="flex items-center gap-3 rounded-md px-3 py-2"
                    initial={{ opacity: 0, x: -10 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: i * 0.06, duration: 0.3 }}
                  >
                    {/* Status indicator */}
                    <div className="relative">
                      {stage.status === "complete" && (
                        <div className="h-2.5 w-2.5 rounded-full bg-accent" />
                      )}
                      {stage.status === "current" && (
                        <>
                          <div className="h-2.5 w-2.5 rounded-full bg-primary" />
                          <motion.div
                            className="absolute inset-0 rounded-full bg-primary/30"
                            animate={{ scale: [1, 2, 1], opacity: [0.5, 0, 0.5] }}
                            transition={{ duration: 2, repeat: Infinity }}
                          />
                        </>
                      )}
                      {stage.status === "pending" && (
                        <div className="h-2.5 w-2.5 rounded-full border border-border" />
                      )}
                    </div>

                    {/* Label */}
                    <span
                      className={`text-sm ${
                        stage.status === "pending"
                          ? "text-muted-foreground/50"
                          : stage.status === "current"
                          ? "font-medium text-primary"
                          : ""
                      }`}
                    >
                      {stage.title}
                    </span>

                    {/* Status code */}
                    <span className="ml-auto font-mono text-xs text-muted-foreground/30">
                      {stage.status === "complete" && "✓"}
                      {stage.status === "current" && "→"}
                      {stage.status === "pending" && "○"}
                    </span>
                  </motion.div>
                ))}
              </div>

              {/* Progress summary */}
              <div className="mt-4 flex items-center gap-3 border-t border-border/30 pt-4">
                <div className="flex-1">
                  <div className="h-1 w-full overflow-hidden rounded-full bg-secondary">
                    <motion.div
                      className="h-full bg-primary"
                      initial={{ width: 0 }}
                      whileInView={{ width: `${(completedCount / pipeline.length) * 100}%` }}
                      viewport={{ once: true }}
                      transition={{ duration: 0.8, delay: 0.3, ease: "easeOut" }}
                    />
                  </div>
                </div>
                <span className="font-mono text-xs text-muted-foreground/60">
                  {completedCount}/{pipeline.length}
                </span>
              </div>
            </div>
          </Reveal>

          {/* Right — Editorial text */}
          <Reveal variant="fade-up" delay={0.1}>
            <div>
              <div className="mb-3 text-xs font-semibold uppercase tracking-wider text-primary">
                <span className="text-muted-foreground/60">02</span>
                <span className="ml-2">Build</span>
              </div>
              <h2 className="text-3xl font-bold tracking-tight sm:text-4xl lg:text-5xl">
                Create real
                <br />
                systems.
              </h2>
              <p className="mt-6 max-w-md text-base leading-relaxed text-muted-foreground">
                Code-Yaar is about making things. Not following along with someone else&apos;s code,
                but building your own systems from scratch.
              </p>
              <p className="mt-4 max-w-md text-base leading-relaxed text-muted-foreground">
                Each project is structured with clear milestones, so you can track your progress
                and understand what &quot;done&quot; means.
              </p>

              {/* Feature grid — structured list, not cards */}
              <div className="mt-8 grid grid-cols-2 gap-x-6 gap-y-4">
                {features.map((item, i) => (
                  <motion.div
                    key={item.label}
                    initial={{ opacity: 0, y: 8 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.2 + i * 0.08, duration: 0.4 }}
                  >
                    <p className="text-sm font-medium">{item.label}</p>
                    <p className="mt-0.5 text-xs text-muted-foreground">{item.desc}</p>
                  </motion.div>
                ))}
              </div>
            </div>
          </Reveal>
        </div>
      </div>
    </section>
  );
}
