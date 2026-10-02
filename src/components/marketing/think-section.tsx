"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Reveal } from "@/components/motion/reveal";

const considerations = [
  { id: "data", label: "Data model", hint: "What entities exist?" },
  { id: "api", label: "API design", hint: "How do clients interact?" },
  { id: "storage", label: "Storage", hint: "Where does data live?" },
  { id: "scale", label: "Scalability", hint: "What happens at 10x?" },
];

export function ThinkSection() {
  const [selected, setSelected] = useState<string[]>([]);

  const toggle = (id: string) => {
    setSelected((prev) =>
      prev.includes(id) ? prev.filter((s) => s !== id) : [...prev, id]
    );
  };

  return (
    <section className="border-b bg-white py-20 sm:py-28">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="grid gap-12 lg:grid-cols-[1fr_1.2fr] lg:gap-20">
          {/* Left — Editorial text */}
          <Reveal variant="fade-up">
            <div>
              <div className="mb-3 text-xs font-semibold uppercase tracking-wider text-primary">
                <span className="text-muted-foreground/60">01</span>
                <span className="ml-2">Think</span>
              </div>
              <h2 className="text-3xl font-bold tracking-tight sm:text-4xl lg:text-5xl">
                Understand
                <br />
                before you code.
              </h2>
              <p className="mt-6 max-w-md text-base leading-relaxed text-muted-foreground">
                Engineering starts with thinking. Before writing a single line of code,
                you learn to analyze problems, consider trade-offs, and make informed decisions.
              </p>
              <p className="mt-4 max-w-md text-base leading-relaxed text-muted-foreground">
                Code-Yaar guides you through the reasoning process that separates
                developers from engineers.
              </p>
            </div>
          </Reveal>

          {/* Right — Interactive problem analysis */}
          <Reveal variant="fade-up" delay={0.15}>
            <div className="relative">
              {/* Problem statement */}
              <div className="mb-6">
                <div className="text-xs font-semibold uppercase tracking-wider text-muted-foreground/60 mb-2">
                  Problem
                </div>
                <h3 className="text-lg font-semibold">
                  Build a URL shortener.
                </h3>
                <p className="mt-1.5 text-sm text-muted-foreground">
                  What would you consider first? Select your approach:
                </p>
              </div>

              {/* Considerations grid */}
              <div className="grid grid-cols-2 gap-2">
                {considerations.map((item) => {
                  const isSelected = selected.includes(item.id);
                  return (
                    <motion.button
                      key={item.id}
                      onClick={() => toggle(item.id)}
                      className={`relative rounded-md border bg-white p-4 text-left transition-colors ${
                        isSelected
                          ? "border-primary/40 bg-primary/5"
                          : "border-border/50 hover:border-primary/20 hover:shadow-sm"
                      }`}
                      whileHover={{ scale: 1.01 }}
                      whileTap={{ scale: 0.99 }}
                      transition={{ type: "spring", stiffness: 400, damping: 25 }}
                    >
                      <span className={`text-sm font-medium ${isSelected ? "text-primary" : ""}`}>
                        {item.label}
                      </span>
                      <AnimatePresence>
                        {isSelected && (
                          <motion.span
                            initial={{ opacity: 0, y: 4 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: 4 }}
                            className="mt-1 block text-xs text-muted-foreground/60"
                          >
                            {item.hint}
                          </motion.span>
                        )}
                      </AnimatePresence>
                    </motion.button>
                  );
                })}
              </div>

              {/* Selection feedback */}
              <AnimatePresence>
                {selected.length > 0 && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.25 }}
                    className="overflow-hidden"
                  >
                    <div className="mt-4 rounded-md border border-primary/10 bg-primary/5 p-3">
                      <p className="font-mono text-xs text-muted-foreground">
                        <span className="text-primary/60">{selected.length}</span> consideration{selected.length > 1 ? "s" : ""} selected.
                        <br />
                        <span className="text-muted-foreground/50">
                          → good engineering starts with asking the right questions.
                        </span>
                      </p>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </Reveal>
        </div>
      </div>
    </section>
  );
}
