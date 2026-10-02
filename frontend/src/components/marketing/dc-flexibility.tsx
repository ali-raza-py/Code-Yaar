"use client";

import { Clock, Code, MessageSquare } from "lucide-react";

const features = [
  {
    icon: Clock,
    title: "Self-Paced Learning",
    description:
      "Learn on your schedule. Access courses, projects, and challenges anytime, anywhere. No deadlines, no pressure.",
  },
  {
    icon: Code,
    title: "Hands-On Projects",
    description:
      "Build real applications from day one. Every concept is paired with a practical project you can add to your portfolio.",
  },
  {
    icon: MessageSquare,
    title: "Real-World Feedback",
    description:
      "Get actionable feedback on your code. Understand not just what works, but why — and how to improve.",
  },
];

export function DcFlexibility() {
  return (
    <section className="dc-light-section py-16 sm:py-20">
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
        <div className="grid items-center gap-12 lg:grid-cols-2">
          {/* Left — Visual */}
          <div className="relative">
            <div className="rounded-2xl bg-white p-6 shadow-lg border border-[var(--color-section-border)]">
              {/* Mockup: Learning dashboard */}
              <div className="mb-4 flex items-center gap-2">
                <div className="h-3 w-3 rounded-full bg-red-400/70" />
                <div className="h-3 w-3 rounded-full bg-yellow-400/70" />
                <div className="h-3 w-3 rounded-full bg-green-400/70" />
                <span className="ml-2 font-mono text-xs text-muted-foreground">
                  code-yaar.dev/learn
                </span>
              </div>
              <div className="space-y-3">
                <div className="flex items-center gap-3 rounded-lg bg-[var(--color-section-light)] p-3">
                  <div className="h-8 w-8 rounded-md bg-[var(--color-cta-green)]/20 flex items-center justify-center">
                    <Code className="h-4 w-4 text-[var(--color-cta-green)]" />
                  </div>
                  <div className="flex-1">
                    <div className="h-2.5 w-32 rounded bg-foreground/10" />
                    <div className="mt-1.5 h-2 w-20 rounded bg-foreground/5" />
                  </div>
                  <div className="h-2 w-16 rounded-full bg-[var(--color-cta-green)]/30">
                    <div className="h-2 w-12 rounded-full bg-[var(--color-cta-green)]" />
                  </div>
                </div>
                <div className="flex items-center gap-3 rounded-lg bg-[var(--color-section-light)] p-3">
                  <div className="h-8 w-8 rounded-md bg-[var(--primary)]/20 flex items-center justify-center">
                    <Code className="h-4 w-4 text-[var(--primary)]" />
                  </div>
                  <div className="flex-1">
                    <div className="h-2.5 w-28 rounded bg-foreground/10" />
                    <div className="mt-1.5 h-2 w-24 rounded bg-foreground/5" />
                  </div>
                  <div className="h-2 w-16 rounded-full bg-[var(--primary)]/30">
                    <div className="h-2 w-8 rounded-full bg-[var(--primary)]" />
                  </div>
                </div>
                <div className="flex items-center gap-3 rounded-lg bg-[var(--color-section-light)] p-3">
                  <div className="h-8 w-8 rounded-md bg-orange-500/20 flex items-center justify-center">
                    <Code className="h-4 w-4 text-orange-500" />
                  </div>
                  <div className="flex-1">
                    <div className="h-2.5 w-36 rounded bg-foreground/10" />
                    <div className="mt-1.5 h-2 w-16 rounded bg-foreground/5" />
                  </div>
                  <div className="h-2 w-16 rounded-full bg-orange-500/30">
                    <div className="h-2 w-4 rounded-full bg-orange-500" />
                  </div>
                </div>
              </div>
              {/* Stats row */}
              <div className="mt-4 grid grid-cols-3 gap-3">
                <div className="rounded-lg bg-[var(--color-section-light)] p-3 text-center">
                  <div className="text-lg font-bold text-foreground">12</div>
                  <div className="text-xs text-muted-foreground">Courses</div>
                </div>
                <div className="rounded-lg bg-[var(--color-section-light)] p-3 text-center">
                  <div className="text-lg font-bold text-foreground">5</div>
                  <div className="text-xs text-muted-foreground">Projects</div>
                </div>
                <div className="rounded-lg bg-[var(--color-section-light)] p-3 text-center">
                  <div className="text-lg font-bold text-[var(--color-cta-green)]">3</div>
                  <div className="text-xs text-muted-foreground">Completed</div>
                </div>
              </div>
            </div>
          </div>

          {/* Right — Content */}
          <div>
            <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
              Flexibility that fits your life.
            </h2>
            <p className="mt-4 text-lg text-muted-foreground">
              Whether you have 15 minutes or 3 hours, Code-Yaar adapts to your schedule.
              Learn at your own pace with structured guidance.
            </p>

            <div className="mt-8 space-y-6">
              {features.map((feature) => (
                <div key={feature.title} className="flex gap-4">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-[var(--primary)]/10">
                    <feature.icon className="h-5 w-5 text-[var(--primary)]" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground">{feature.title}</h3>
                    <p className="mt-1 text-sm leading-relaxed text-muted-foreground">
                      {feature.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
