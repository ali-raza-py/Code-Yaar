"use client";

import { motion } from "framer-motion";
import { Reveal } from "@/components/motion/reveal";

const feedbackItems = [
  { type: "warning", text: "Error handling missing in edge cases" },
  { type: "warning", text: "Input validation could be stronger" },
  { type: "success", text: "Function structure is clear and readable" },
];

const improvements = [
  { label: "Code quality", direction: "up" },
  { label: "Testing", direction: "up" },
  { label: "Architecture", direction: "up" },
];

export function EvolveSection() {
  return (
    <section className="border-b bg-white py-20 sm:py-28">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="grid gap-12 lg:grid-cols-[1fr_1.2fr] lg:gap-20">
          {/* Left — Editorial text */}
          <Reveal variant="fade-up">
            <div>
              <div className="mb-3 text-xs font-semibold uppercase tracking-wider text-primary">
                <span className="text-muted-foreground/60">03</span>
                <span className="ml-2">Evolve</span>
              </div>
              <h2 className="text-3xl font-bold tracking-tight sm:text-4xl lg:text-5xl">
                Improve through
                <br />
                iteration.
              </h2>
              <p className="mt-6 max-w-md text-base leading-relaxed text-muted-foreground">
                Writing code is only half the work. The other half is reviewing it,
                understanding what could be better, and making it better.
              </p>
              <p className="mt-4 max-w-md text-base leading-relaxed text-muted-foreground">
                Code-Yaar helps you develop the habit of continuous improvement
                that distinguishes growing engineers from stagnant ones.
              </p>
            </div>
          </Reveal>

          {/* Right — Code review visualization */}
          <Reveal variant="fade-up" delay={0.1}>
            <div>
              {/* Code snippet */}
              <div className="mb-5 rounded-lg border border-border/50 bg-surface-recessed p-4">
                <div className="mb-2 flex items-center justify-between">
                  <span className="font-mono text-xs text-muted-foreground/50">your_code.py</span>
                  <span className="font-mono text-xs text-muted-foreground/30">v2</span>
                </div>
                <pre className="font-mono text-xs leading-relaxed text-muted-foreground">
{`def getUser(id):
    user = db.find(id)
    return user`}
                </pre>
              </div>

              {/* Feedback items */}
              <div className="space-y-2">
                {feedbackItems.map((item, i) => (
                  <motion.div
                    key={i}
                    className={`flex items-start gap-2.5 rounded-md border p-3 text-xs ${
                      item.type === "warning"
                        ? "border-accent/15 bg-accent/5"
                        : "border-primary/15 bg-primary/5"
                    }`}
                    initial={{ opacity: 0, x: 10 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: i * 0.1, duration: 0.3 }}
                  >
                    <span className="mt-0.5 shrink-0">
                      {item.type === "warning" ? (
                        <span className="text-accent">!</span>
                      ) : (
                        <span className="text-primary">✓</span>
                      )}
                    </span>
                    <span className="text-muted-foreground">{item.text}</span>
                  </motion.div>
                ))}
              </div>

              {/* Improvement signals */}
              <div className="mt-5 flex items-center gap-4">
                {improvements.map((item, i) => (
                  <motion.div
                    key={item.label}
                    className="flex items-center gap-1.5"
                    initial={{ opacity: 0, y: 6 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.3 + i * 0.08, duration: 0.3 }}
                  >
                    <span className="text-accent text-xs">↑</span>
                    <span className="font-mono text-xs text-muted-foreground/60">
                      {item.label}
                    </span>
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
