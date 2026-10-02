"use client";

import Link from "next/link";
import { ArrowRight, Check } from "lucide-react";

export function DcCta() {
  return (
    <section className="dc-dark-section relative overflow-hidden py-16 sm:py-20">
      {/* Background pattern */}
      <div className="absolute inset-0 opacity-[0.04]" style={{
        backgroundImage: "radial-gradient(circle at 1px 1px, white 1px, transparent 0)",
        backgroundSize: "32px 32px",
      }} />

      <div className="relative mx-auto max-w-3xl px-4 text-center sm:px-6 lg:px-8">
        <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
          Start building real projects today.
        </h2>
        <p className="mx-auto mt-4 max-w-xl text-lg text-[var(--color-text-dark-muted)]">
          Join thousands of developers who are learning by doing.
          No tutorials, no hand-holding — just real code and real results.
        </p>

        <div className="mt-8 flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
          <Link href="/sign-up" className="dc-btn-primary !py-3 !px-8 text-base">
            Get started for free <ArrowRight className="h-4 w-4" />
          </Link>
          <Link href="/learn" className="dc-btn-outline !border-white/20 !text-white hover:!bg-white/10">
            Explore tracks
          </Link>
        </div>

        <div className="mt-6 flex items-center justify-center gap-4 text-sm text-[var(--color-text-dark-muted)]">
          <span className="flex items-center gap-1.5">
            <Check className="h-4 w-4 text-[var(--color-cta-green)]" />
            Free to start
          </span>
          <span className="flex items-center gap-1.5">
            <Check className="h-4 w-4 text-[var(--color-cta-green)]" />
            No credit card
          </span>
          <span className="flex items-center gap-1.5">
            <Check className="h-4 w-4 text-[var(--color-cta-green)]" />
            Cancel anytime
          </span>
        </div>
      </div>
    </section>
  );
}
