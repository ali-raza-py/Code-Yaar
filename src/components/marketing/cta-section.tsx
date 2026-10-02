"use client";

import Link from "next/link";
import { Reveal } from "@/components/motion/reveal";
import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";

export function CtaSection() {
  return (
    <section className="relative overflow-hidden bg-surface-recessed/50 py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <Reveal variant="fade-in">
            <div className="mb-5 text-xs font-semibold uppercase tracking-wider text-primary">
              Ready
            </div>
          </Reveal>

          <Reveal variant="fade-up" delay={0.1}>
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl lg:text-5xl">
              Stop consuming.
              <br />
              <span className="text-primary">Start building.</span>
            </h2>
          </Reveal>

          <Reveal variant="fade-up" delay={0.2}>
            <p className="mt-6 text-base leading-relaxed text-muted-foreground sm:text-lg">
              Track your progress. Prove what you can do.
              Your engineering journey begins with a single commit.
            </p>
          </Reveal>

          <Reveal variant="fade-up" delay={0.3}>
            <div className="mt-8 flex flex-col justify-center gap-3 sm:flex-row">
              <Link href="/learn">
                <Button size="lg" className="gap-2">
                  Get Started
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </Link>
              <Link href="/projects">
                <Button variant="outline" size="lg">
                  View Projects
                </Button>
              </Link>
            </div>
          </Reveal>
        </div>
      </div>
    </section>
  );
}
