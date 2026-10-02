import Link from "next/link";
import {
  ArrowRight,
  Braces,
  Check,
  Code2,
  Compass,
  FolderKanban,
  GitBranch,
  Target,
} from "lucide-react";
import { careerTracks } from "@/data/tracks";

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
  mint: "bg-[#d9f7e8] text-[#087443]",
  blue: "bg-[#dcecff] text-[#1659a8]",
  amber: "bg-[#fff0c9] text-[#976400]",
  rose: "bg-[#ffe0e0] text-[#a53a3a]",
};

export function LearningEntry() {
  return (
    <div className="overflow-hidden bg-[#f5f7f4] text-[#11221c]">
      <section className="relative border-b border-[#d7e2da] bg-[#102a22] text-white">
        <div className="absolute inset-0 opacity-20 [background-image:linear-gradient(#c9f5db_1px,transparent_1px),linear-gradient(90deg,#c9f5db_1px,transparent_1px)] [background-size:4rem_4rem]" />
        <div className="relative mx-auto grid max-w-7xl gap-12 px-5 py-20 sm:px-8 lg:grid-cols-[1.1fr_0.9fr] lg:items-center lg:gap-20 lg:px-10 lg:py-28">
          <div>
            <p className="font-mono text-xs font-semibold uppercase tracking-[0.2em] text-[#9ae6b4]">
              CODE-YAAR / LEARN / BUILD / GROW
            </p>
            <h1 className="mt-6 max-w-3xl text-5xl font-bold leading-[0.98] tracking-[-0.04em] sm:text-6xl lg:text-7xl">
              Learn technology by building with it.
            </h1>
            <p className="mt-7 max-w-xl text-base leading-7 text-[#c4d8ce] sm:text-lg">
              Structured lessons, immediate practice, and projects that make your skills visible. Start with a goal, then keep moving one useful step at a time.
            </p>
            <div className="mt-9 flex flex-col gap-3 sm:flex-row">
              <Link href="/sign-up" className="inline-flex items-center justify-center gap-2 rounded-md bg-[#a7f3c3] px-5 py-3 text-sm font-bold text-[#102a22] transition-transform hover:-translate-y-0.5">
                Start learning <ArrowRight className="h-4 w-4" />
              </Link>
              <Link href="/learn" className="inline-flex items-center justify-center gap-2 rounded-md border border-[#668b79] px-5 py-3 text-sm font-semibold text-white hover:bg-white/10">
                Explore paths <Compass className="h-4 w-4" />
              </Link>
            </div>
          </div>

          <div className="relative border border-[#456557] bg-[#173a2e] p-5 shadow-[12px_12px_0_#0b1d17] sm:p-7">
            <div className="flex items-center justify-between border-b border-[#456557] pb-4">
              <span className="font-mono text-xs text-[#9ae6b4]">YOUR NEXT SESSION</span>
              <span className="rounded-full bg-[#a7f3c3] px-2.5 py-1 font-mono text-[10px] font-bold text-[#102a22]">READY</span>
            </div>
            <div className="py-7">
              <p className="font-mono text-xs uppercase tracking-wider text-[#9ab9aa]">Python foundations</p>
              <h2 className="mt-2 text-2xl font-bold">Functions that do useful work</h2>
              <p className="mt-3 text-sm leading-6 text-[#c4d8ce]">Learn the concept, try the example, then write a function that passes a real test.</p>
            </div>
            <div className="flex items-center justify-between border-t border-[#456557] pt-4 text-sm">
              <span className="text-[#9ab9aa]">Lesson 5 of 8 · 15 min</span>
              <Link href="/learn/python-foundations" className="font-semibold text-[#a7f3c3] hover:text-white">Open course <ArrowRight className="ml-1 inline h-4 w-4" /></Link>
            </div>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-5 py-16 sm:px-8 lg:px-10 lg:py-20">
        <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
          <div>
            <p className="font-mono text-xs font-semibold uppercase tracking-[0.18em] text-[#087443]">Choose your direction</p>
            <h2 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">What do you want to achieve?</h2>
          </div>
          <Link href="/learn" className="text-sm font-semibold text-[#087443]">See every path <ArrowRight className="ml-1 inline h-4 w-4" /></Link>
        </div>
        <div className="mt-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {goals.map((goal) => {
            const Icon = goal.icon;
            return (
              <Link key={goal.label} href={goal.href} className="group border border-[#d7e2da] bg-white p-5 transition hover:-translate-y-1 hover:border-[#87b69a] hover:shadow-[5px_5px_0_#cbe4d3]">
                <span className={`flex h-10 w-10 items-center justify-center rounded-md ${toneClasses[goal.tone]}`}><Icon className="h-5 w-5" /></span>
                <span className="mt-6 block font-semibold group-hover:text-[#087443]">{goal.label}</span>
                <ArrowRight className="mt-5 h-4 w-4 text-[#6f8177] transition-transform group-hover:translate-x-1 group-hover:text-[#087443]" />
              </Link>
            );
          })}
        </div>
      </section>

      <section className="border-y border-[#d7e2da] bg-white">
        <div className="mx-auto max-w-7xl px-5 py-16 sm:px-8 lg:px-10 lg:py-20">
          <div className="max-w-2xl">
            <p className="font-mono text-xs font-semibold uppercase tracking-[0.18em] text-[#087443]">The Code-Yaar loop</p>
            <h2 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">Progress you can feel in your hands.</h2>
            <p className="mt-4 leading-7 text-[#5c6d64]">Every course connects the idea to the action, the action to a project, and the project to the next skill worth learning.</p>
          </div>
          <div className="mt-10 grid gap-px overflow-hidden border border-[#d7e2da] bg-[#d7e2da] sm:grid-cols-2 lg:grid-cols-4">
            {loop.map((step) => (
              <div key={step.index} className="bg-[#fbfdfb] p-6">
                <span className="font-mono text-xs font-semibold text-[#87a293]">{step.index}</span>
                <h3 className="mt-8 text-xl font-bold">{step.title}</h3>
                <p className="mt-3 text-sm leading-6 text-[#5c6d64]">{step.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-5 py-16 sm:px-8 lg:px-10 lg:py-20">
        <div className="grid gap-10 lg:grid-cols-[0.8fr_1.2fr] lg:items-start">
          <div>
            <p className="font-mono text-xs font-semibold uppercase tracking-[0.18em] text-[#087443]">Built around outcomes</p>
            <h2 className="mt-3 text-3xl font-bold tracking-tight">Find a path that leads somewhere.</h2>
            <p className="mt-4 leading-7 text-[#5c6d64]">Career tracks connect the courses, practice, and projects needed for a real role, without making you guess what comes next.</p>
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            {careerTracks.slice(0, 4).map((track) => (
              <Link key={track.slug} href={`/learn?track=${track.slug}`} className="group border border-[#d7e2da] bg-white p-5 hover:border-[#87b69a]">
                <div className="flex items-start justify-between gap-3">
                  <div><p className="font-mono text-[10px] uppercase tracking-wider text-[#87a293]">{track.difficulty} · {track.estimatedHours} hours</p><h3 className="mt-2 font-bold group-hover:text-[#087443]">{track.title}</h3></div>
                  <GitBranch className="h-5 w-5 text-[#87a293]" />
                </div>
                <div className="mt-5 flex flex-wrap gap-2">{track.skills.slice(0, 3).map((skill) => <span key={skill} className="inline-flex items-center gap-1 bg-[#eef6f0] px-2 py-1 text-xs text-[#446254]"><Check className="h-3 w-3 text-[#087443]" />{skill}</span>)}</div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      <section className="border-t border-[#d7e2da] bg-[#e7f4eb]">
        <div className="mx-auto flex max-w-7xl flex-col gap-6 px-5 py-12 sm:px-8 lg:flex-row lg:items-center lg:justify-between lg:px-10">
          <div><p className="font-mono text-xs font-semibold uppercase tracking-[0.18em] text-[#087443]">Make the next hour count</p><h2 className="mt-2 text-2xl font-bold">Start with one lesson. Leave with something working.</h2></div>
          <Link href="/sign-up" className="inline-flex shrink-0 items-center justify-center gap-2 rounded-md bg-[#102a22] px-5 py-3 text-sm font-bold text-white hover:bg-[#1b4939]">Create your learning path <ArrowRight className="h-4 w-4" /></Link>
        </div>
      </section>
    </div>
  );
}