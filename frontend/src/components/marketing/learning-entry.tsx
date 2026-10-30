import Link from "next/link";
import {
  ArrowRight,
  Braces,
  Code2,
  Compass,
  FolderKanban,
  Target,
} from "lucide-react";
import { CourseResumeCard } from "@/components/marketing/course-resume-card";
import { ProductShowcase } from "@/components/marketing/product-showcase";
import { TracksStrip } from "@/components/marketing/tracks-strip";

const goals = [
  { label: "Learn Python", href: "/learn/python-foundations", icon: Braces, tone: "mint" },
  { label: "Become a web developer", href: "/learn", icon: Code2, tone: "blue" },
  { label: "Build real projects", href: "/projects", icon: FolderKanban, tone: "amber" },
  { label: "Sharpen coding skills", href: "/challenges", icon: Target, tone: "rose" },
] as const;

const loop = [
  { index: "01", title: "Discover", description: "Choose a goal and a path that fits your next move." },
  { index: "02", title: "Learn", description: "Build understanding through focused, practical lessons." },
  { index: "03", title: "Practice", description: "Write code, get feedback, and recover from mistakes." },
  { index: "04", title: "Apply", description: "Turn your new skill into a project you can show." },
];

const toneClasses = {
  mint: "bg-tone-mint-bg text-forest-accent",
  blue: "bg-tone-blue-bg text-info",
  amber: "bg-tone-amber-bg text-tone-amber-fg",
  rose: "bg-tone-rose-bg text-tone-rose-fg",
};

export function LearningEntry() {
  return (
    <div className="overflow-hidden bg-forest-bg text-forest-ink">
      <section className="relative border-b border-forest-border bg-forest-deep text-white">
        <div className="absolute inset-0 opacity-20 [background-image:linear-gradient(var(--forest-grid)_1px,transparent_1px),linear-gradient(90deg,var(--forest-grid)_1px,transparent_1px)] [background-size:4rem_4rem]" />
        <div className="relative mx-auto grid max-w-7xl gap-12 px-5 py-20 sm:px-8 lg:grid-cols-[1.1fr_0.9fr] lg:items-center lg:gap-20 lg:px-10 lg:py-28">
          <div>
            <p className="font-mono text-xs font-semibold uppercase tracking-[0.2em] text-mint-soft">
              CODE-YAAR / LEARN / BUILD / GROW
            </p>
            <h1 className="mt-6 max-w-3xl text-5xl font-bold leading-[0.98] tracking-[-0.04em] sm:text-6xl lg:text-7xl">
              Learn technology by building with it.
            </h1>
            <p className="mt-7 max-w-xl text-base leading-7 text-forest-on-deep sm:text-lg">
              Structured lessons, immediate practice, and projects that make your skills visible. Start with a goal, then keep moving one useful step at a time.
            </p>
            <div className="mt-9 flex flex-col gap-3 sm:flex-row">
              <Link href="/sign-up" className="focus-ring inline-flex items-center justify-center gap-2 rounded-md bg-mint px-5 py-3 text-sm font-bold text-forest-deep transition-transform hover:-translate-y-0.5">
                Start learning <ArrowRight className="h-4 w-4" />
              </Link>
              <Link href="/learn" className="focus-ring inline-flex items-center justify-center gap-2 rounded-md border border-forest-line px-5 py-3 text-sm font-semibold text-white hover:bg-white/10">
                Explore paths <Compass className="h-4 w-4" />
              </Link>
            </div>
          </div>

          <CourseResumeCard />
        </div>
      </section>

      <ProductShowcase />

      <section className="mx-auto max-w-7xl px-5 py-16 sm:px-8 lg:px-10 lg:py-20">
        <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
          <div>
            <p className="font-mono text-xs font-semibold uppercase tracking-[0.18em] text-forest-accent">Choose your direction</p>
            <h2 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">What do you want to achieve?</h2>
          </div>
          <Link href="/learn" className="focus-ring rounded text-sm font-semibold text-forest-accent">See every path <ArrowRight className="ml-1 inline h-4 w-4" /></Link>
        </div>
        <div className="mt-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {goals.map((goal) => {
            const Icon = goal.icon;
            return (
              <Link key={goal.label} href={goal.href} className="focus-ring group rounded-[var(--radius-card)] border border-forest-border bg-white p-5 transition hover:-translate-y-1 hover:border-forest-border-hover hover:shadow-[5px_5px_0_var(--forest-shadow-soft)]">
                <span className={`flex h-10 w-10 items-center justify-center rounded-md ${toneClasses[goal.tone]}`}><Icon className="h-5 w-5" /></span>
                <span className="mt-6 block font-semibold group-hover:text-forest-accent">{goal.label}</span>
                <ArrowRight className="mt-5 h-4 w-4 text-forest-icon transition-transform group-hover:translate-x-1 group-hover:text-forest-accent" />
              </Link>
            );
          })}
        </div>
      </section>

      <section className="border-y border-forest-border bg-white">
        <div className="mx-auto max-w-7xl px-5 py-16 sm:px-8 lg:px-10 lg:py-20">
          <div className="max-w-2xl">
            <p className="font-mono text-xs font-semibold uppercase tracking-[0.18em] text-forest-accent">The Code-Yaar loop</p>
            <h2 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">Progress you can feel in your hands.</h2>
            <p className="mt-4 leading-7 text-forest-muted">Every course connects the idea to the action, the action to a project, and the project to the next skill worth learning.</p>
          </div>
          <div className="mt-10 grid gap-px overflow-hidden border border-forest-border bg-forest-border sm:grid-cols-2 lg:grid-cols-4">
            {loop.map((step) => (
              <div key={step.index} className="bg-forest-panel p-6">
                <span className="font-mono text-xs font-semibold text-forest-line-soft">{step.index}</span>
                <h3 className="mt-8 text-xl font-bold">{step.title}</h3>
                <p className="mt-3 text-sm leading-6 text-forest-muted">{step.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-5 py-16 sm:px-8 lg:px-10 lg:py-20">
        <div className="grid gap-10 lg:grid-cols-[0.8fr_1.2fr] lg:items-start">
          <div>
            <p className="font-mono text-xs font-semibold uppercase tracking-[0.18em] text-forest-accent">Built around outcomes</p>
            <h2 className="mt-3 text-3xl font-bold tracking-tight">Find a path that leads somewhere.</h2>
            <p className="mt-4 leading-7 text-forest-muted">Career tracks connect the courses, practice, and projects needed for a real role, without making you guess what comes next.</p>
          </div>
          <TracksStrip />
        </div>
      </section>

      <section className="border-t border-forest-border bg-forest-cta-band">
        <div className="mx-auto flex max-w-7xl flex-col gap-6 px-5 py-12 sm:px-8 lg:flex-row lg:items-center lg:justify-between lg:px-10">
          <div><p className="font-mono text-xs font-semibold uppercase tracking-[0.18em] text-forest-accent">Make the next hour count</p><h2 className="mt-2 text-2xl font-bold">Start with one lesson. Leave with something working.</h2></div>
          <Link href="/sign-up" className="focus-ring inline-flex shrink-0 items-center justify-center gap-2 rounded-md bg-forest-deep px-5 py-3 text-sm font-bold text-white hover:bg-forest-deep-hover">Create your learning path <ArrowRight className="h-4 w-4" /></Link>
        </div>
      </section>
    </div>
  );
}
