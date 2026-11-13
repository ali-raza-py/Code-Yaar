import type { Metadata } from "next";
import Link from "next/link";
import {
  ArrowRight,
  BriefcaseBusiness,
  CircleHelp,
  Mail,
  ShieldCheck,
  Sparkles,
  Users,
} from "lucide-react";

import { FoundingTeam } from "@/components/marketing/founding-team";

export const metadata: Metadata = {
  title: "About Code-Yaar",
  description: "Learn how Code-Yaar helps developers move from concepts to confident building.",
};

const principles = [
  {
    icon: Sparkles,
    title: "Learn by doing",
    text: "Every concept earns its place by helping you build something tangible.",
  },
  {
    icon: Users,
    title: "Grow in public",
    text: "Share progress, compare approaches, and learn alongside a community of builders.",
  },
  {
    icon: ShieldCheck,
    title: "Build with proof",
    text: "Projects and challenges turn practice into work you can explain and show.",
  },
];

export default function AboutPage() {
  return (
    <div className="bg-background">
      <section className="border-b border-border bg-hero-navy text-[var(--color-text-dark-hero)]">
        <div className="mx-auto max-w-6xl px-4 py-20 sm:px-6 lg:px-8 lg:py-28">
          <p className="tech-label text-primary">ABOUT CODE YAAR</p>
          <h1 className="mt-5 max-w-3xl text-4xl font-semibold leading-tight tracking-tight sm:text-6xl">
            Become the developer who can actually build.
          </h1>
          <p className="mt-6 max-w-2xl text-lg leading-relaxed text-[var(--color-text-dark-muted)]">
            Code Yaar is a practical learning platform for people who are done collecting tutorials and ready to turn understanding into working software.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link href="/tracks" className="focus-ring inline-flex items-center gap-2 rounded-lg bg-primary px-5 py-3 text-sm font-semibold text-primary-foreground transition-colors hover:bg-cta-hover">
              Explore learning paths <ArrowRight className="h-4 w-4" />
            </Link>
            <Link href="#contact" className="focus-ring inline-flex items-center gap-2 rounded-lg border border-white/15 bg-white/5 px-5 py-3 text-sm font-semibold text-[var(--color-text-dark-hero)] transition-colors hover:border-primary/40 hover:bg-white/10">
              Talk to us <Mail className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 py-16 sm:px-6 lg:px-8">
        <div className="grid gap-10 lg:grid-cols-[1.1fr_1fr] lg:items-end">
          <div>
            <p className="tech-label text-primary">THE CODE YAAR METHOD</p>
            <h2 className="mt-3 text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">Concepts are the beginning, not the finish line.</h2>
          </div>
          <p className="text-base leading-relaxed text-muted-foreground">
            We combine structured lessons, focused challenges, and ambitious projects into one loop. Learn the idea, use it immediately, then keep the result as evidence of your progress.
          </p>
        </div>
        <div className="mt-12 grid gap-4 md:grid-cols-3">
          {principles.map(({ icon: Icon, title, text }) => (
            <div key={title} className="rounded-[var(--radius-card)] border border-border bg-card p-6 shadow-none">
              <Icon className="h-6 w-6 text-primary" />
              <h3 className="mt-5 text-lg font-semibold text-foreground">{title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{text}</p>
            </div>
          ))}
        </div>
      </section>

      <FoundingTeam />

      <section className="border-y border-border bg-surface-recessed">
        <div className="mx-auto grid max-w-6xl gap-10 px-4 py-16 sm:px-6 lg:grid-cols-[0.8fr_1.2fr] lg:px-8">
          <div>
            <p className="tech-label text-primary">QUICK ANSWERS</p>
            <h2 className="mt-3 text-3xl font-semibold tracking-tight text-foreground">Questions, answered clearly.</h2>
          </div>
          <div id="faq" className="space-y-3">
            {[
              ["Is Code Yaar for beginners?", "Yes. Start with a guided track, then increase the difficulty as your confidence grows."],
              ["What makes a project different from a course?", "Courses teach the building blocks. Projects ask you to make the important decisions yourself."],
              ["Can I learn at my own pace?", "Absolutely. Your dashboard keeps your next step visible without forcing a schedule."],
            ].map(([question, answer]) => (
              <details key={question} className="group border-b border-border py-4">
                <summary className="flex cursor-pointer list-none items-center justify-between gap-4 font-medium text-foreground">
                  {question}<CircleHelp className="h-4 w-4 shrink-0 text-muted-foreground transition-transform duration-200 group-open:rotate-45" />
                </summary>
                <p className="mt-3 max-w-2xl text-sm leading-relaxed text-muted-foreground">{answer}</p>
              </details>
            ))}
          </div>
        </div>
      </section>

      <section id="careers" className="mx-auto max-w-6xl px-4 py-16 sm:px-6 lg:px-8">
        <div className="grid gap-6 md:grid-cols-2">
          <div className="rounded-[var(--radius-card)] border border-border bg-card p-8">
            <BriefcaseBusiness className="h-6 w-6 text-primary" />
            <h2 className="mt-5 text-2xl font-semibold tracking-tight text-foreground">Help shape the next learning platform.</h2>
            <p className="mt-3 text-sm leading-relaxed text-muted-foreground">We are building a small, thoughtful team around practical education and better developer tools.</p>
            <a href="mailto:careers@codeyaar.dev" className="focus-ring mt-6 inline-flex items-center gap-2 text-sm font-semibold text-primary transition-colors hover:text-cta-hover">See opportunities <ArrowRight className="h-4 w-4" /></a>
          </div>
          <div id="contact" className="rounded-[var(--radius-card)] border border-primary/20 bg-accent p-8 text-foreground">
            <Mail className="h-6 w-6 text-primary" />
            <h2 className="mt-5 text-2xl font-semibold tracking-tight">Have a question or idea?</h2>
            <p className="mt-3 text-sm leading-relaxed text-muted-foreground">Tell us what you are building, what you are stuck on, or what you want to see next.</p>
            <a href="mailto:hello@codeyaar.dev" className="focus-ring mt-6 inline-flex items-center gap-2 text-sm font-semibold text-primary transition-colors hover:text-cta-hover">hello@codeyaar.dev <ArrowRight className="h-4 w-4" /></a>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 pb-16 sm:px-6 lg:px-8">
        <div id="privacy" className="border-t border-border pt-10">
          <h2 className="text-lg font-semibold text-foreground">Privacy Policy</h2>
          <p className="mt-2 max-w-3xl text-sm leading-relaxed text-muted-foreground">We collect only the information needed to provide your account, track learning progress, and improve the platform. We do not sell personal data.</p>
        </div>
        <div id="terms" className="mt-8 border-t border-border pt-10">
          <h2 className="text-lg font-semibold text-foreground">Terms of Service</h2>
          <p className="mt-2 max-w-3xl text-sm leading-relaxed text-muted-foreground">Use Code Yaar responsibly, keep your account secure, and share only work you have the right to publish. Learning content is provided for educational use.</p>
        </div>
      </section>
    </div>
  );
}
