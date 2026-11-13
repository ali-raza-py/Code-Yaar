"use client";

import Link from "next/link";
import {
  ArrowRight,
  Award,
  Compass,
  Medal,
  ShieldCheck,
} from "lucide-react";
import { CourseResumeCard } from "@/components/marketing/course-resume-card";
import { FeaturedCourses } from "@/components/marketing/featured-courses";
import { LeaderboardPreview } from "@/components/marketing/leaderboard-preview";
import { ProductShowcase } from "@/components/marketing/product-showcase";
import { TracksStrip } from "@/components/marketing/tracks-strip";

const loop = [
  { index: "01", title: "Discover", description: "Choose a track and a course that fits your next move." },
  { index: "02", title: "Learn", description: "Build understanding through focused, practical lessons." },
  { index: "03", title: "Practice", description: "Write code, get feedback, and recover from mistakes." },
  { index: "04", title: "Apply", description: "Turn your new skill into a project you can show." },
];

export function LearningEntry() {
  return (
    <div className="overflow-hidden bg-background text-foreground">
      {/* 1 — Hero */}
      <section className="relative border-b border-border bg-hero-navy text-[var(--color-text-dark-hero)]">
        <div className="absolute inset-0 bg-grid-sm opacity-[0.06]" aria-hidden="true" />
        <div className="relative mx-auto grid max-w-7xl gap-12 px-5 py-20 sm:px-8 lg:grid-cols-[1.1fr_0.9fr] lg:items-center lg:gap-20 lg:px-10 lg:py-28">
          <div>
            <p className="font-mono text-xs font-semibold uppercase tracking-[0.2em] text-primary">
              THINK. BUILD. EVOLVE.
            </p>
            <h1 className="mt-6 max-w-3xl text-[var(--color-text-dark-hero)]">
              Learn computer science by building with it.
            </h1>
            <p className="mt-7 max-w-xl text-base leading-7 text-[var(--color-text-dark-muted)] sm:text-lg">
              Code Yaar is a computer science education platform: structured
              tracks, hands-on lessons, real projects and challenges — with every step
              earned as visible progress.
            </p>
            <div className="mt-9 flex flex-col gap-3 sm:flex-row">
              <Link href="/sign-up" className="focus-ring inline-flex items-center justify-center gap-2 rounded-lg bg-primary px-5 py-3 text-sm font-semibold text-primary-foreground transition-colors hover:bg-cta-hover">
                Get started free <ArrowRight className="h-4 w-4" />
              </Link>
              <Link href="/courses" className="focus-ring inline-flex items-center justify-center gap-2 rounded-lg border border-white/15 bg-white/5 px-5 py-3 text-sm font-semibold text-[var(--color-text-dark-hero)] transition-colors hover:border-primary/40 hover:bg-white/10">
                Browse courses <Compass className="h-4 w-4" />
              </Link>
            </div>
            <div className="mt-8 flex flex-wrap gap-x-5 gap-y-2 text-xs font-medium text-[var(--color-text-dark-muted)]">
              {["Structured tracks", "Hands-on practice", "Real projects"].map((item) => (
                <span key={item} className="inline-flex items-center gap-2">
                  <span aria-hidden="true" className="h-1.5 w-1.5 rounded-full bg-primary" />
                  {item}
                </span>
              ))}
            </div>
          </div>

          <div className="relative">
            <div aria-hidden="true" className="absolute -inset-3 rounded-[22px] border border-primary/20 bg-primary/10 blur-sm" />
            <div className="relative">
              <CourseResumeCard />
            </div>
          </div>
        </div>
      </section>

      {/* 2 — The product, shown honestly */}
      <ProductShowcase />

      {/* 3 — Learning tracks overview */}
      <section className="mx-auto max-w-7xl px-5 py-16 sm:px-8 lg:px-10 lg:py-20">
        <div className="grid gap-10 lg:grid-cols-[0.8fr_1.2fr] lg:items-start">
          <div>
            <p className="font-mono text-xs font-semibold uppercase tracking-[0.18em] text-primary">Built around outcomes</p>
            <h2 className="mt-3 text-3xl font-semibold tracking-tight">Find a path that leads somewhere.</h2>
            <p className="mt-4 leading-7 text-muted-foreground">Learning tracks connect the courses, practice, and projects needed for a real goal — from school curriculum to web development and AI — without making you guess what comes next.</p>
            <Link href="/tracks" className="focus-ring mt-6 inline-flex items-center gap-1 rounded text-sm font-semibold text-primary transition-colors hover:text-cta-hover">Explore all tracks <ArrowRight className="h-4 w-4" /></Link>
          </div>
          <TracksStrip />
        </div>
      </section>

      {/* 4 — Featured courses */}
      <section className="border-y border-border bg-surface-recessed">
        <div className="mx-auto max-w-7xl px-5 py-16 sm:px-8 lg:px-10 lg:py-20">
          <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
            <div>
              <p className="font-mono text-xs font-semibold uppercase tracking-[0.18em] text-primary">Start with a course</p>
              <h2 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">Featured courses</h2>
            </div>
            <Link href="/courses" className="focus-ring rounded text-sm font-semibold text-primary transition-colors hover:text-cta-hover">View the full catalog <ArrowRight className="ml-1 inline h-4 w-4" /></Link>
          </div>
          <div className="mt-8">
            <FeaturedCourses />
          </div>
        </div>
      </section>

      {/* 5 — How Code Yaar works */}
      <section id="how-it-works" className="mx-auto max-w-7xl px-5 py-16 sm:px-8 lg:px-10 lg:py-20">
        <div className="max-w-2xl">
          <p className="font-mono text-xs font-semibold uppercase tracking-[0.18em] text-primary">The Code-Yaar loop</p>
          <h2 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">Progress you can feel in your hands.</h2>
          <p className="mt-4 leading-7 text-muted-foreground">Every course connects the idea to the action, the action to a project, and the project to the next skill worth learning.</p>
        </div>
        <div className="mt-10 grid gap-px overflow-hidden rounded-xl border border-border bg-border sm:grid-cols-2 lg:grid-cols-4">
          {loop.map((step) => (
            <div key={step.index} className="bg-card p-6">
              <span className="font-mono text-xs font-semibold text-primary">{step.index}</span>
              <h3 className="mt-8 text-xl font-semibold">{step.title}</h3>
              <p className="mt-3 text-sm leading-6 text-muted-foreground">{step.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* 6 — Proof: live rankings and verifiable credentials */}
      <section className="border-y border-border bg-surface-recessed">
        <div className="mx-auto grid max-w-7xl gap-10 px-5 py-16 sm:px-8 lg:grid-cols-2 lg:px-10 lg:py-20">
          <div>
            <p className="font-mono text-xs font-semibold uppercase tracking-[0.18em] text-primary"><Medal className="mr-1.5 inline h-4 w-4" />Live community</p>
            <h2 className="mt-3 text-2xl font-semibold tracking-tight sm:text-3xl">Where does your name sit?</h2>
            <p className="mt-3 text-sm leading-6 text-muted-foreground">XP is earned by finishing lessons, exercises and challenges — the leaderboard is just the scoreboard of that work.</p>
            <div className="mt-6">
              <LeaderboardPreview />
            </div>
          </div>
          <div className="lg:pt-16">
            <p className="font-mono text-xs font-semibold uppercase tracking-[0.18em] text-primary"><Award className="mr-1.5 inline h-4 w-4" />Credentials with proof</p>
            <h2 className="mt-3 text-2xl font-semibold tracking-tight sm:text-3xl">Certificates anyone can verify.</h2>
            <p className="mt-3 text-sm leading-6 text-muted-foreground">
              Completing a course earns a certificate with a unique code; badges mark real
              milestones. Every credential can be checked against the registry by teachers,
              parents or employers — no account needed.
            </p>
            <div className="mt-6 rounded-[var(--radius-card)] border border-border bg-card p-5">
              <div className="flex items-start gap-3">
                <ShieldCheck className="mt-0.5 h-5 w-5 shrink-0 text-primary" />
                <div>
                  <p className="text-sm font-semibold">Check any credential in seconds</p>
                  <p className="mt-1 text-xs leading-5 text-muted-foreground">Paste a certificate or badge code into the public registry check.</p>
                  <Link href="/verify" className="focus-ring mt-3 inline-flex items-center gap-1 rounded text-sm font-semibold text-primary transition-colors hover:text-cta-hover">Open the verifier <ArrowRight className="h-4 w-4" /></Link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 7 — Final registration CTA */}
      <section className="border-t border-border bg-hero-navy">
        <div className="mx-auto flex max-w-7xl flex-col gap-6 px-5 py-12 sm:px-8 lg:flex-row lg:items-center lg:justify-between lg:px-10">
          <div>
            <p className="font-mono text-xs font-semibold uppercase tracking-[0.18em] text-primary">Make the next hour count</p>
            <h2 className="mt-2 text-2xl font-semibold tracking-tight text-[var(--color-text-dark-hero)]">Start with one lesson. Leave with something working.</h2>
          </div>
          <Link href="/sign-up" className="focus-ring inline-flex shrink-0 items-center justify-center gap-2 rounded-lg bg-primary px-5 py-3 text-sm font-semibold text-primary-foreground transition-colors hover:bg-cta-hover">Create your learning path <ArrowRight className="h-4 w-4" /></Link>
        </div>
      </section>
    </div>
  );
}
