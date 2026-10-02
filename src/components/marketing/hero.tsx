"use client";

import { Reveal } from "@/components/motion/reveal";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { ArrowRight } from "lucide-react";

export function Hero() {
  return (
    <section className="relative min-h-[85vh] overflow-hidden border-b bg-white">
      <div className="mx-auto flex min-h-[85vh] max-w-7xl flex-col justify-center px-4 py-20 sm:px-6 lg:flex-row lg:items-center lg:gap-16 lg:px-8 lg:py-28">
        {/* LEFT — Typography & CTA */}
        <div className="flex flex-1 flex-col justify-center lg:pr-4">
          <Reveal variant="fade-in" delay={0.1}>
            <div className="mb-5 text-xs font-semibold uppercase tracking-wider text-primary">
              Think. Build. Evolve.
            </div>
          </Reveal>

          <Reveal variant="fade-up" delay={0.2}>
            <h1 className="text-4xl font-bold leading-tight tracking-tight text-foreground sm:text-5xl lg:text-6xl">
              Learn the
              <br />
              fundamentals.
              <br />
              <span className="text-primary">
                Build real systems.
              </span>
            </h1>
          </Reveal>

          <Reveal variant="fade-up" delay={0.35}>
            <p className="mt-5 max-w-lg text-base leading-relaxed text-muted-foreground sm:text-lg">
              Understand deeply. Practice deliberately. Build things that matter.
              Code-Yaar is the engineering path from concept to proof.
            </p>
          </Reveal>

          <Reveal variant="fade-up" delay={0.45}>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <Link href="/learn">
                <Button size="lg" className="gap-2">
                  Start Learning
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </Link>
              <Link href="/projects">
                <Button variant="outline" size="lg">
                  Explore Projects
                </Button>
              </Link>
            </div>
          </Reveal>
        </div>

        {/* RIGHT — Visual element */}
        <div className="mt-12 flex flex-1 items-center justify-center lg:mt-0">
          <Reveal variant="fade-in" delay={0.3}>
            <div className="relative w-full max-w-md">
              {/* Code editor mockup */}
              <div className="rounded-xl border border-border/60 bg-surface-recessed p-5 shadow-sm">
                <div className="mb-3 flex items-center gap-1.5">
                  <div className="h-3 w-3 rounded-full bg-red-400/70" />
                  <div className="h-3 w-3 rounded-full bg-yellow-400/70" />
                  <div className="h-3 w-3 rounded-full bg-green-400/70" />
                  <span className="ml-2 font-mono text-xs text-muted-foreground/50">
                    app.py
                  </span>
                </div>
                <pre className="font-mono text-sm leading-relaxed">
                  <code>
                    <span className="text-muted-foreground/40"># </span>
                    <span className="text-muted-foreground/60">Build something real</span>
                    {"\n"}
                    <span className="text-primary">from</span>
                    <span className="text-muted-foreground"> flask </span>
                    <span className="text-primary">import</span>
                    <span className="text-muted-foreground"> Flask</span>
                    {"\n\n"}
                    <span className="text-muted-foreground">app </span>
                    <span className="text-primary">=</span>
                    <span className="text-muted-foreground"> Flask(</span>
                    <span className="text-accent">__name__</span>
                    <span className="text-muted-foreground">)</span>
                    {"\n\n"}
                    <span className="text-primary">@</span>
                    <span className="text-muted-foreground">app.route(</span>
                    <span className="text-accent">"/"</span>
                    <span className="text-muted-foreground">)</span>
                    {"\n"}
                    <span className="text-primary">def</span>
                    <span className="text-muted-foreground"> </span>
                    <span className="text-primary">index</span>
                    <span className="text-muted-foreground">():</span>
                    {"\n"}
                    <span className="text-muted-foreground">    </span>
                    <span className="text-primary">return</span>
                    <span className="text-muted-foreground"> </span>
                    <span className="text-accent">"Hello, Code-Yaar!"</span>
                  </code>
                </pre>
              </div>
            </div>
          </Reveal>
        </div>
      </div>
    </section>
  );
}
