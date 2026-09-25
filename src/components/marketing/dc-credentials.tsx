"use client";

import Link from "next/link";
import { Award, Shield, Briefcase, ArrowRight } from "lucide-react";

const proofItems = [
  {
    icon: Award,
    title: "Verifiable Certifications",
    description:
      "Earn certifications that employers can verify. Each credential has a unique ID and can be shared on LinkedIn.",
  },
  {
    icon: Shield,
    title: "Portfolio of Real Work",
    description:
      "Every project you complete becomes part of your portfolio. Show employers what you've actually built, not just what you've studied.",
  },
  {
    icon: Briefcase,
    title: "Skill Assessments",
    description:
      "Take timed skill assessments to prove your proficiency. Get a verified score that demonstrates your actual ability.",
  },
];

export function DcCredentials() {
  return (
    <section className="dc-light-section py-16 sm:py-20">
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
        <div className="grid items-center gap-12 lg:grid-cols-2">
          {/* Left — Content */}
          <div>
            <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
              Proof that carries weight.
            </h2>
            <p className="mt-4 text-lg text-muted-foreground">
              Don&apos;t just say you can code — prove it. Build a portfolio of verified work
              that speaks louder than any resume.
            </p>

            <div className="mt-8 space-y-6">
              {proofItems.map((item) => (
                <div key={item.title} className="flex gap-4">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-[var(--primary)]/10">
                    <item.icon className="h-5 w-5 text-[var(--primary)]" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground">{item.title}</h3>
                    <p className="mt-1 text-sm leading-relaxed text-muted-foreground">
                      {item.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>

            <Link href="/projects" className="dc-btn-primary mt-8 inline-flex">
              View Projects <ArrowRight className="h-4 w-4" />
            </Link>
          </div>

          {/* Right — Certification Card Mockup */}
          <div className="flex justify-center">
            <div className="w-full max-w-sm rounded-2xl bg-white p-6 shadow-lg border border-[var(--color-section-border)]">
              {/* Certificate header */}
              <div className="flex items-center gap-3 border-b border-[var(--color-section-border)] pb-4">
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-[var(--color-cta-green)]/10">
                  <Award className="h-6 w-6 text-[var(--color-cta-green)]" />
                </div>
                <div>
                  <div className="text-sm font-bold text-foreground">Full Stack Developer</div>
                  <div className="text-xs text-muted-foreground">Code-Yaar Certification</div>
                </div>
              </div>

              {/* Certificate body */}
              <div className="mt-4 space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Credential ID</span>
                  <span className="font-mono text-xs text-foreground">CY-FS-2026-0847</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Issued</span>
                  <span className="text-foreground">Sept 2026</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Status</span>
                  <span className="inline-flex items-center gap-1 text-[var(--color-cta-green)]">
                    <span className="h-1.5 w-1.5 rounded-full bg-[var(--color-cta-green)]" />
                    Verified
                  </span>
                </div>
              </div>

              {/* Skills covered */}
              <div className="mt-4 border-t border-[var(--color-section-border)] pt-4">
                <div className="text-xs font-medium text-muted-foreground mb-2">Skills Verified</div>
                <div className="flex flex-wrap gap-1.5">
                  {["React", "Node.js", "PostgreSQL", "REST APIs", "Docker"].map((skill) => (
                    <span
                      key={skill}
                      className="rounded-full bg-[var(--color-section-light)] px-2.5 py-0.5 text-xs font-medium text-foreground"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>

              {/* Share button */}
              <button className="mt-4 w-full rounded-lg border border-[var(--color-section-border)] py-2 text-sm font-medium text-foreground transition-colors hover:bg-[var(--color-section-light)]">
                Share to LinkedIn
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
