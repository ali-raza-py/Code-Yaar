"use client";

import { motion } from "framer-motion";
import { Reveal } from "@/components/motion/reveal";
import {
  BookOpen,
  Trophy,
  FolderGit2,
  BarChart3,
  Shield,
  Sparkles,
} from "lucide-react";

const features = [
  {
    icon: BookOpen,
    title: "Structured Learning",
    description:
      "Follow a clear engineering path from fundamentals to advanced concepts. Each module builds on the last.",
    status: "available" as const,
  },
  {
    icon: Trophy,
    title: "Coding Challenges",
    description:
      "Focused problems that test specific skills. Think before you code. Optimize for understanding, not speed.",
    status: "available" as const,
  },
  {
    icon: FolderGit2,
    title: "Real Projects",
    description:
      "Build actual systems with structured milestones, real technologies, and clear definitions of done.",
    status: "available" as const,
  },
  {
    icon: BarChart3,
    title: "Progress Tracking",
    description:
      "See how far you've come. Track concepts learned, challenges solved, and projects completed.",
    status: "available" as const,
  },
  {
    icon: Shield,
    title: "Proof of Skills",
    description:
      "Build a portfolio of real work that demonstrates what you can actually do as an engineer.",
    status: "available" as const,
  },
  {
    icon: Sparkles,
    title: "AI Mentorship",
    description:
      "Get intelligent guidance on your approach, code quality, and engineering decisions. Coming soon.",
    status: "coming-soon" as const,
  },
];

export function FeaturesSection() {
  return (
    <section id="features" className="border-b bg-surface-recessed/50 py-20 sm:py-28">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <Reveal variant="fade-up">
          <div className="mx-auto max-w-2xl text-center">
            <div className="mb-3 text-xs font-semibold uppercase tracking-wider text-primary">
              Capabilities
            </div>
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl lg:text-5xl">
              Everything you need to grow
            </h2>
            <p className="mt-4 text-base leading-relaxed text-muted-foreground">
              Tools and structure designed to develop real engineering ability.
              Not another tutorial platform.
            </p>
          </div>
        </Reveal>

        <div className="mt-16 grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature, i) => (
            <motion.div
              key={feature.title}
              className={`group relative rounded-lg border bg-white p-6 transition-colors ${
                feature.status === "coming-soon"
                  ? "border-border/20 opacity-70"
                  : "border-border/40 hover:border-primary/20 hover:shadow-sm"
              }`}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.08, duration: 0.4 }}
            >
              <div className="flex items-start justify-between">
                <feature.icon className="h-6 w-6 text-primary" />
                {feature.status === "coming-soon" && (
                  <span className="rounded-full border border-border/40 px-2 py-0.5 text-[10px] font-medium text-muted-foreground">
                    Coming Soon
                  </span>
                )}
              </div>

              <h3 className="mt-4 text-base font-semibold">{feature.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
