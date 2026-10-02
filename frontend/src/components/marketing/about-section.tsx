"use client";

import { motion } from "framer-motion";
import { Reveal } from "@/components/motion/reveal";
import { Target, Lightbulb, Hammer, TrendingUp } from "lucide-react";

const principles = [
  "Learn by doing — concepts stick when you build with them.",
  "Build real things — projects that solve real problems.",
  "Prove the skill — create evidence of what you can do.",
  "Avoid tutorial hell — move from consuming to producing.",
  "Progressive difficulty — start manageable, grow steadily.",
  "Practical over flashy — substance over style.",
];

export function AboutSection() {
  return (
    <section id="about" className="border-b bg-white py-20 sm:py-28">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="grid gap-12 lg:grid-cols-2 lg:gap-20">
          {/* Left — What is Code-Yaar */}
          <Reveal variant="fade-up">
            <div>
              <div className="mb-3 text-xs font-semibold uppercase tracking-wider text-primary">
                About
              </div>
              <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
                Why Code-Yaar exists
              </h2>
              <p className="mt-6 text-base leading-relaxed text-muted-foreground">
                Many learners consume programming content without developing strong
                practical ability. Tutorial dependence, limited project practice,
                weak problem-solving confidence, and fragmented resources make it
                hard to transition from &quot;knowing about code&quot; to
                &quot;actually building things.&quot;
              </p>
              <p className="mt-4 text-base leading-relaxed text-muted-foreground">
                Code-Yaar is built around a simple loop: learn a concept, build
                something with it, and prove what you have done. No fake progress.
                No passive consumption. Real engineering practice from day one.
              </p>

              {/* Philosophy cards */}
              <div className="mt-8 grid grid-cols-3 gap-4">
                {[
                  { icon: Lightbulb, title: "Think", desc: "Reasoning over memorization" },
                  { icon: Hammer, title: "Build", desc: "Projects over exercises" },
                  { icon: TrendingUp, title: "Evolve", desc: "Progress over perfection" },
                ].map((item) => (
                  <motion.div
                    key={item.title}
                    className="rounded-lg border border-border/40 bg-surface-recessed/50 p-4 text-center"
                    whileHover={{ borderColor: "var(--primary)", transition: { duration: 0.2 } }}
                  >
                    <item.icon className="mx-auto h-5 w-5 text-primary" />
                    <p className="mt-2 text-sm font-semibold">{item.title}</p>
                    <p className="mt-1 text-xs text-muted-foreground">{item.desc}</p>
                  </motion.div>
                ))}
              </div>
            </div>
          </Reveal>

          {/* Right — Principles */}
          <Reveal variant="fade-up" delay={0.15}>
            <div>
              <div className="mb-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                Product Principles
              </div>
              <h3 className="text-lg font-semibold">
                What guides everything we build
              </h3>
              <div className="mt-6 space-y-3">
                {principles.map((principle, i) => (
                  <motion.div
                    key={principle}
                    className="flex items-start gap-3"
                    initial={{ opacity: 0, x: 10 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: i * 0.06, duration: 0.3 }}
                  >
                    <Target className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
                    <p className="text-sm text-muted-foreground">{principle}</p>
                  </motion.div>
                ))}
              </div>

              {/* Status */}
              <div className="mt-8 rounded-lg border bg-surface-recessed/50 p-4">
                <p className="text-sm font-medium">Current Status</p>
                <p className="mt-1 text-xs text-muted-foreground">
                  Code-Yaar is in active development. The platform is being built
                  with care — authentication, code execution, and full project
                  workflows are being implemented for the MVP release.
                </p>
              </div>
            </div>
          </Reveal>
        </div>
      </div>
    </section>
  );
}
