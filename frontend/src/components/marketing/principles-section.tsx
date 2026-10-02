"use client";

import { motion } from "framer-motion";
import { Reveal } from "@/components/motion/reveal";

const principles = [
  {
    number: "01",
    title: "Learn by doing",
    description: "Concepts stick when you build with them, not just read about them.",
    symbol: "=>",
  },
  {
    number: "02",
    title: "Build real things",
    description: "Projects that solve real problems, not abstract exercises.",
    symbol: "{}",
  },
  {
    number: "03",
    title: "Prove the skill",
    description: "Create evidence of what you can actually do, not just what you've watched.",
    symbol: "<>",
  },
  {
    number: "04",
    title: "Avoid tutorial hell",
    description: "Move from consuming content to producing work.",
    symbol: "::",
  },
  {
    number: "05",
    title: "Progressive difficulty",
    description: "Start manageable. Grow steadily. Challenge yourself appropriately.",
    symbol: "++",
  },
  {
    number: "06",
    title: "Practical over flashy",
    description: "Substance over style. Working code over impressive-looking demos.",
    symbol: ";",
  },
];

export function PrinciplesSection() {
  return (
    <section className="border-b bg-surface-recessed/50 py-20 sm:py-28 overflow-hidden">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <Reveal variant="fade-up">
          <div className="mb-16 max-w-lg">
            <div className="mb-3 text-xs font-semibold uppercase tracking-wider text-primary">
              Principles
            </div>
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl lg:text-5xl">
              Why Code-Yaar
            </h2>
            <p className="mt-4 text-base leading-relaxed text-muted-foreground">
              Product principles that guide everything we build.
            </p>
          </div>
        </Reveal>

        {/* Editorial grid — asymmetric, not uniform cards */}
        <div className="grid gap-0 divide-y divide-border/20 sm:grid-cols-2 sm:divide-y-0 sm:[&>*:nth-child(odd)]:border-r sm:[&>*:nth-child(odd)]:border-border/20 lg:grid-cols-3 lg:[&>*:nth-child(odd)]:border-r lg:[&>*:nth-child(3n)]:border-r-0">
          {principles.map((principle, i) => (
            <motion.div
              key={principle.title}
              className="group relative px-6 py-8"
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.06, duration: 0.4 }}
            >
              {/* Background symbol */}
              <span className="absolute right-4 top-4 font-mono text-2xl font-bold text-primary/[0.04]">
                {principle.symbol}
              </span>

              <span className="text-xs font-medium text-muted-foreground/40">
                {principle.number}
              </span>
              <h3 className="mt-3 text-sm font-semibold">{principle.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                {principle.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
