"use client";

import { motion } from "framer-motion";
import { Reveal } from "@/components/motion/reveal";
import { BookOpen, Code2, Hammer, MessageSquare, TrendingUp, Shield } from "lucide-react";

const steps = [
  {
    number: "01",
    icon: BookOpen,
    title: "Learn",
    description: "Understand core concepts through structured modules. Build mental models, not memorized syntax.",
  },
  {
    number: "02",
    icon: Code2,
    title: "Practice",
    description: "Apply what you learn through focused challenges. Each one targets a specific skill.",
  },
  {
    number: "03",
    icon: Hammer,
    title: "Build",
    description: "Create real projects with structured milestones. Move from exercises to engineering.",
  },
  {
    number: "04",
    icon: MessageSquare,
    title: "Feedback",
    description: "Receive guidance on your approach. Understand what works and what to improve.",
  },
  {
    number: "05",
    icon: TrendingUp,
    title: "Improve",
    description: "Iterate on your work. Refactor, optimize, and develop better engineering judgment.",
  },
  {
    number: "06",
    icon: Shield,
    title: "Prove",
    description: "Build a portfolio of real work. Show what you can actually do, not what you watched.",
  },
];

export function HowItWorksSection() {
  return (
    <section id="how-it-works" className="border-b bg-white py-20 sm:py-28">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <Reveal variant="fade-up">
          <div className="mx-auto max-w-2xl text-center">
            <div className="mb-3 text-xs font-semibold uppercase tracking-wider text-primary">
              The Loop
            </div>
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl lg:text-5xl">
              How Code-Yaar works
            </h2>
            <p className="mt-4 text-base leading-relaxed text-muted-foreground">
              A continuous loop of learning, building, and improving.
              Each cycle develops deeper engineering ability.
            </p>
          </div>
        </Reveal>

        <div className="mt-16 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {steps.map((step, i) => (
            <motion.div
              key={step.number}
              className="group relative rounded-lg border border-border/40 bg-white p-6 transition-colors hover:border-primary/20 hover:shadow-sm"
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.08, duration: 0.4 }}
            >
              {/* Number */}
              <span className="text-xs font-medium text-muted-foreground/40">
                {step.number}
              </span>

              {/* Icon */}
              <div className="mt-3 flex items-center gap-3">
                <step.icon className="h-5 w-5 text-primary" />
                <h3 className="text-base font-semibold">{step.title}</h3>
              </div>

              {/* Description */}
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                {step.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
