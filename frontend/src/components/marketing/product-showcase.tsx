"use client";

import { useRef, useState, type KeyboardEvent } from "react";
import {
  AnimatePresence,
  motion,
  useReducedMotion,
} from "framer-motion";
import {
  Award,
  BookOpen,
  Braces,
  Check,
  CheckCircle2,
  ChevronRight,
  Circle,
  Code2,
  FileCode2,
  Folder,
  Globe2,
  Lightbulb,
  MessageCircle,
  Play,
  Sparkles,
  Terminal,
  Trophy,
  Zap,
} from "lucide-react";

const features = [
  {
    title: "Real projects, not just tutorials.",
    description:
      "Learn through practical projects that help you apply concepts to real development challenges.",
  },
  {
    title: "AI mentorship, not just answers.",
    description:
      "Get contextual guidance, explanations, debugging help and hints while learning.",
  },
  {
    title: "Practice that proves your skills.",
    description:
      "Strengthen your knowledge through coding exercises, quizzes and meaningful assessments.",
  },
  {
    title: "Progress you can actually show.",
    description:
      "Track completed courses, achievements, XP and certificates through your learning profile.",
  },
] as const;

const codeLines = [
  <><span className="text-violet-600 dark:text-violet-300">const</span> <span className="text-sky-700 dark:text-sky-300">projects</span> = [</>,
  <>  <span className="text-emerald-700 dark:text-emerald-300">"portfolio"</span>,</>,
  <>  <span className="text-emerald-700 dark:text-emerald-300">"weather-app"</span>,</>,
  <>];</>,
];

function CodeLines() {
  return (
    <pre className="overflow-x-auto font-mono text-[11px] leading-5 text-foreground sm:text-xs">
      {codeLines.map((line, index) => (
        <span key={index} className="block whitespace-pre">{line}</span>
      ))}
    </pre>
  );
}

function WindowBar({ title }: { title: string }) {
  return (
    <div className="flex h-11 items-center justify-between border-b border-forest-border px-3 dark:border-white/10 sm:px-4">
      <div className="flex items-center gap-2">
        <span className="flex h-6 w-6 items-center justify-center rounded bg-forest-deep text-[10px] font-bold text-mint">cy</span>
        <span className="text-[11px] font-semibold text-forest-ink dark:text-slate-100 sm:text-xs">{title}</span>
      </div>
      <div className="flex items-center gap-1.5" aria-hidden="true">
        <i className="h-2 w-2 rounded-full bg-[#f2b56b]" />
        <i className="h-2 w-2 rounded-full bg-[#8bcf9c]" />
        <i className="h-2 w-2 rounded-full bg-[#9cb9d7]" />
      </div>
    </div>
  );
}

function ProjectPreview() {
  return (
    <div className="overflow-hidden rounded-lg border border-forest-border bg-white shadow-[0_16px_50px_rgba(27,52,40,0.12)] dark:border-white/10 dark:bg-[#131d1a] dark:shadow-black/25">
      <WindowBar title="Portfolio project" />
      <div className="flex h-9 items-center gap-1 border-b border-forest-border px-3 dark:border-white/10">
        <span className="inline-flex h-full items-center gap-1.5 border-b-2 border-forest-accent px-2 text-[10px] font-semibold text-forest-ink dark:text-slate-100"><Code2 className="h-3 w-3" /> Editor</span>
        <span className="inline-flex h-full items-center gap-1.5 px-2 text-[10px] text-forest-muted"><Terminal className="h-3 w-3" /> Terminal</span>
        <span className="inline-flex h-full items-center gap-1.5 px-2 text-[10px] text-forest-muted"><Globe2 className="h-3 w-3" /> Preview</span>
      </div>
      <div className="grid min-h-[330px] grid-cols-[116px_minmax(0,1fr)] sm:grid-cols-[150px_minmax(0,1fr)]">
        <aside className="border-r border-forest-border bg-[#f7faf7] p-2.5 dark:border-white/10 dark:bg-white/[0.025] sm:p-3">
          <p className="mb-3 text-[9px] font-bold uppercase tracking-[0.14em] text-forest-muted">Explorer</p>
          <p className="mb-2 flex items-center gap-1.5 truncate text-[10px] font-semibold text-forest-ink dark:text-slate-200"><Folder className="h-3 w-3 text-forest-accent" /> my-portfolio</p>
          <p className="mb-2 flex items-center gap-1.5 pl-3 text-[10px] text-forest-muted"><Folder className="h-3 w-3" /> src</p>
          <p className="mb-2 flex items-center gap-1.5 rounded bg-emerald-100/70 px-1.5 py-1 text-[10px] text-forest-deep dark:bg-emerald-300/10 dark:text-emerald-200"><FileCode2 className="h-3 w-3" /> App.jsx</p>
          <p className="flex items-center gap-1.5 pl-3 text-[10px] text-forest-muted"><FileCode2 className="h-3 w-3" /> styles.css</p>
          <p className="mt-2 flex items-center gap-1.5 pl-3 text-[10px] text-forest-muted"><FileCode2 className="h-3 w-3" /> index.html</p>
        </aside>
        <div className="min-w-0">
          <div className="flex h-8 items-center border-b border-forest-border px-3 dark:border-white/10">
            <span className="font-mono text-[10px] text-forest-muted">src / App.jsx</span>
          </div>
          <div className="grid gap-3 p-3 sm:grid-cols-[1fr_0.9fr] sm:gap-4 sm:p-4">
            <div className="min-w-0">
              <p className="mb-3 font-mono text-[10px] text-forest-muted">01&nbsp;&nbsp; Build a personal portfolio website</p>
              <p className="mb-3 text-[10px] leading-4 text-forest-muted">Create a responsive home page that introduces you and highlights your work.</p>
              <div className="rounded border border-forest-border bg-[#fbfdfb] p-2.5 dark:border-white/10 dark:bg-black/15"><CodeLines /></div>
              <div className="mt-3 flex items-center gap-1.5 text-[9px] text-emerald-700 dark:text-emerald-300"><CheckCircle2 className="h-3 w-3" /> Your changes are saved</div>
            </div>
            <div className="hidden rounded border border-forest-border bg-[#f2f7f3] p-3 dark:border-white/10 dark:bg-white/[0.04] sm:block">
              <div className="flex items-center justify-between"><span className="text-[9px] font-semibold text-forest-muted">LIVE PREVIEW</span><span className="h-1.5 w-1.5 rounded-full bg-emerald-500" /></div>
              <div className="mt-5 border-l-2 border-forest-accent pl-2.5">
                <p className="font-serif text-base leading-tight text-forest-ink dark:text-slate-100">Hello, I’m Alex.</p>
                <p className="mt-1 text-[9px] leading-4 text-forest-muted">Developer, learner, and curious builder.</p>
              </div>
              <div className="mt-4 h-14 rounded bg-gradient-to-br from-emerald-100 to-sky-100 dark:from-emerald-900/50 dark:to-sky-900/50" />
              <div className="mt-3 flex gap-1.5"><span className="h-4 w-12 rounded-sm bg-forest-deep" /><span className="h-4 w-10 rounded-sm border border-forest-border dark:border-white/15" /></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function MentorPreview() {
  return (
    <div className="overflow-hidden rounded-lg border border-forest-border bg-white shadow-[0_16px_50px_rgba(27,52,40,0.12)] dark:border-white/10 dark:bg-[#131d1a] dark:shadow-black/25">
      <WindowBar title="Project mentor" />
      <div className="grid min-h-[330px] md:grid-cols-[0.8fr_1.2fr]">
        <div className="border-b border-forest-border bg-[#f7faf7] p-4 dark:border-white/10 dark:bg-white/[0.025] md:border-b-0 md:border-r sm:p-5">
          <div className="flex items-center gap-2 text-[10px] font-semibold text-forest-muted"><BookOpen className="h-3.5 w-3.5" /> YOUR PROJECT</div>
          <h3 className="mt-4 font-serif text-lg leading-tight text-forest-ink dark:text-slate-100">Personal portfolio</h3>
          <p className="mt-2 text-[11px] leading-5 text-forest-muted">Add a responsive navigation bar that collapses on smaller screens.</p>
          <div className="mt-4 rounded border border-forest-border bg-white p-3 dark:border-white/10 dark:bg-black/15">
            <p className="mb-2 text-[9px] font-semibold uppercase tracking-wide text-forest-muted">Your code</p>
            <pre className="overflow-x-auto font-mono text-[10px] leading-5 text-forest-ink dark:text-slate-200"><span className="text-violet-600 dark:text-violet-300">function</span> <span className="text-sky-700 dark:text-sky-300">Navbar</span>() {"{"}<br />  <span className="text-violet-600 dark:text-violet-300">return</span> (&lt;nav&gt;...&lt;/nav&gt;);<br />{"}"}</pre>
          </div>
          <div className="mt-4 flex items-center gap-2 text-[10px] text-forest-muted"><Circle className="h-3 w-3" /> 2 hints available</div>
        </div>
        <div className="p-4 sm:p-5">
          <div className="flex items-center gap-2 text-[10px] font-semibold text-forest-accent"><Sparkles className="h-3.5 w-3.5" /> CODE YAAR MENTOR <span className="rounded-full bg-emerald-50 px-2 py-0.5 text-[9px] text-emerald-800 dark:bg-emerald-300/10 dark:text-emerald-200">Preview</span></div>
          <div className="mt-4 rounded-md bg-[#f4f7f4] p-3 dark:bg-white/[0.045]">
            <p className="text-[10px] font-semibold text-forest-ink dark:text-slate-100">You</p>
            <p className="mt-1 text-[11px] leading-5 text-forest-muted">I’m not sure how to make the menu collapse on mobile. What should I look at?</p>
          </div>
          <div className="mt-3 flex gap-2.5">
            <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-emerald-100 text-forest-accent dark:bg-emerald-300/10"><Sparkles className="h-3 w-3" /></span>
            <div className="min-w-0">
              <p className="text-[10px] font-semibold text-forest-ink dark:text-slate-100">Let’s reason it through</p>
              <p className="mt-1 text-[11px] leading-5 text-forest-muted">You already have the navigation structure. Which CSS breakpoint could hide the links, and what might you show in their place?</p>
              <div className="mt-2 rounded border border-forest-border bg-[#fbfdfb] p-2.5 dark:border-white/10 dark:bg-black/15">
                <pre className="overflow-x-auto font-mono text-[10px] leading-5 text-forest-ink dark:text-slate-200"><span className="text-violet-600 dark:text-violet-300">@media</span> (max-width: <span className="text-orange-700 dark:text-orange-300">640px</span>) {"{"}<br />  .nav-links {"{"} display: none; {"}"}<br />{"}"}</pre>
              </div>
              <div className="mt-3 flex flex-wrap gap-2"><span className="inline-flex items-center gap-1 rounded border border-forest-border px-2 py-1 text-[9px] text-forest-muted dark:border-white/10"><Lightbulb className="h-3 w-3 text-amber-600" /> Give me a hint</span><span className="inline-flex items-center gap-1 rounded border border-forest-border px-2 py-1 text-[9px] text-forest-muted dark:border-white/10"><MessageCircle className="h-3 w-3" /> Explain this</span></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function PracticePreview() {
  return (
    <div className="overflow-hidden rounded-lg border border-forest-border bg-white shadow-[0_16px_50px_rgba(27,52,40,0.12)] dark:border-white/10 dark:bg-[#131d1a] dark:shadow-black/25">
      <WindowBar title="Daily practice" />
      <div className="flex items-center justify-between border-b border-forest-border px-4 py-2.5 dark:border-white/10">
        <div className="flex items-center gap-2 text-[10px] text-forest-muted"><Braces className="h-3.5 w-3.5 text-forest-accent" /> JavaScript fundamentals</div>
        <span className="rounded bg-emerald-50 px-2 py-1 text-[9px] font-semibold text-emerald-800 dark:bg-emerald-300/10 dark:text-emerald-200">QUESTION 04 / 08</span>
      </div>
      <div className="grid min-h-[330px] md:grid-cols-[0.9fr_1.1fr]">
        <div className="border-b border-forest-border p-4 dark:border-white/10 md:border-b-0 md:border-r sm:p-5">
          <div className="flex items-center gap-2"><span className="rounded bg-emerald-50 px-2 py-1 text-[9px] font-semibold text-emerald-800 dark:bg-emerald-300/10 dark:text-emerald-200">EASY</span><span className="text-[9px] text-forest-muted">Arrays · 10 XP</span></div>
          <h3 className="mt-4 font-serif text-lg text-forest-ink dark:text-slate-100">Find the first match</h3>
          <p className="mt-2 text-[11px] leading-5 text-forest-muted">Write a function that returns the first number greater than <code className="rounded bg-forest-bg px-1 font-mono text-[10px]">target</code>, or <code className="rounded bg-forest-bg px-1 font-mono text-[10px]">-1</code> if none exists.</p>
          <div className="mt-4 rounded border border-forest-border bg-[#f7faf7] p-3 dark:border-white/10 dark:bg-white/[0.025]"><p className="font-mono text-[9px] text-forest-muted">findNext([2, 5, 8], 5)</p><p className="mt-1 font-mono text-[10px] text-forest-ink dark:text-slate-200">// returns 8</p></div>
          <div className="mt-4 flex items-center justify-between text-[9px] text-forest-muted"><span>YOUR PROGRESS</span><span>4 of 8</span></div>
          <div className="mt-1.5 h-1.5 overflow-hidden rounded-full bg-forest-bg dark:bg-white/10"><div className="h-full w-1/2 rounded-full bg-forest-accent" /></div>
        </div>
        <div className="flex min-w-0 flex-col p-3 sm:p-4">
          <div className="flex items-center justify-between"><span className="font-mono text-[9px] text-forest-muted">solution.js</span><span className="inline-flex items-center gap-1 text-[9px] text-forest-muted"><Circle className="h-2.5 w-2.5" /> Draft</span></div>
          <div className="mt-2 min-h-[118px] flex-1 rounded border border-forest-border bg-[#fbfdfb] p-3 dark:border-white/10 dark:bg-black/15"><pre className="overflow-x-auto font-mono text-[10px] leading-5 text-forest-ink dark:text-slate-200"><span className="text-violet-600 dark:text-violet-300">function</span> <span className="text-sky-700 dark:text-sky-300">findNext</span>(numbers, target) {"{"}<br />  <span className="text-violet-600 dark:text-violet-300">return</span> numbers.find(<br />    (number) =&gt; number &gt; target<br />  ) ?? <span className="text-orange-700 dark:text-orange-300">-1</span>;<br />{"}"}</pre></div>
          <div className="mt-3 rounded border border-emerald-200 bg-emerald-50/70 p-2.5 dark:border-emerald-300/20 dark:bg-emerald-300/[0.06]">
            <div className="flex items-center gap-1.5 text-[10px] font-semibold text-emerald-800 dark:text-emerald-200"><CheckCircle2 className="h-3.5 w-3.5" /> 3 of 3 tests passing</div>
            <div className="mt-2 grid grid-cols-3 gap-1 text-[8px] text-emerald-800/80 dark:text-emerald-200/75"><span className="flex items-center gap-1"><Check className="h-2.5 w-2.5" /> Basic case</span><span className="flex items-center gap-1"><Check className="h-2.5 w-2.5" /> No match</span><span className="flex items-center gap-1"><Check className="h-2.5 w-2.5" /> Edge case</span></div>
          </div>
          <button type="button" className="mt-3 inline-flex h-8 items-center justify-center gap-1.5 self-end rounded bg-forest-deep px-3 text-[10px] font-semibold text-white"><Play className="h-3 w-3" /> Run tests</button>
        </div>
      </div>
    </div>
  );
}

function ProgressPreview() {
  return (
    <div className="overflow-hidden rounded-lg border border-forest-border bg-white shadow-[0_16px_50px_rgba(27,52,40,0.12)] dark:border-white/10 dark:bg-[#131d1a] dark:shadow-black/25">
      <WindowBar title="Learning profile" />
      <div className="border-b border-forest-border bg-[#fbfdfb] px-4 py-2 text-[9px] text-forest-muted dark:border-white/10 dark:bg-white/[0.025]">DEMO PREVIEW · SAMPLE LEARNER PROFILE</div>
      <div className="grid min-h-[310px] gap-3 p-3 sm:grid-cols-2 sm:gap-4 sm:p-4">
        <div className="rounded-md border border-forest-border p-3 dark:border-white/10 sm:p-4">
          <div className="flex items-center gap-2.5"><span className="flex h-9 w-9 items-center justify-center rounded-full bg-[#e1f3e7] text-xs font-bold text-forest-accent dark:bg-emerald-300/10 dark:text-emerald-200">AM</span><div><p className="text-[11px] font-semibold text-forest-ink dark:text-slate-100">Alex Morgan</p><p className="text-[9px] text-forest-muted">Learning since March 2026</p></div></div>
          <div className="mt-4 grid grid-cols-2 gap-2"><div className="rounded bg-[#f5f8f5] p-2.5 dark:bg-white/[0.04]"><p className="flex items-center gap-1 text-[9px] text-forest-muted"><Zap className="h-3 w-3 text-amber-600" /> TOTAL XP</p><p className="mt-1 text-base font-semibold text-forest-ink dark:text-slate-100">1,240</p></div><div className="rounded bg-[#f5f8f5] p-2.5 dark:bg-white/[0.04]"><p className="flex items-center gap-1 text-[9px] text-forest-muted"><BookOpen className="h-3 w-3 text-sky-700 dark:text-sky-300" /> COURSES</p><p className="mt-1 text-base font-semibold text-forest-ink dark:text-slate-100">3 <span className="text-[9px] font-normal text-forest-muted">complete</span></p></div></div>
          <div className="mt-4 flex items-center justify-between text-[9px] text-forest-muted"><span>Frontend foundations</span><span>68%</span></div><div className="mt-1.5 h-1.5 rounded-full bg-forest-bg dark:bg-white/10"><div className="h-full w-[68%] rounded-full bg-forest-accent" /></div>
          <div className="mt-4 flex items-center justify-between"><p className="text-[9px] font-semibold text-forest-ink dark:text-slate-100">Recent achievements</p><span className="text-[9px] text-forest-accent">View all</span></div>
          <div className="mt-2 flex gap-2"><span className="flex h-8 w-8 items-center justify-center rounded bg-amber-50 text-amber-700 dark:bg-amber-300/10 dark:text-amber-300"><Trophy className="h-4 w-4" /></span><span className="flex h-8 w-8 items-center justify-center rounded bg-sky-50 text-sky-700 dark:bg-sky-300/10 dark:text-sky-300"><Braces className="h-4 w-4" /></span><span className="flex h-8 w-8 items-center justify-center rounded bg-emerald-50 text-emerald-700 dark:bg-emerald-300/10 dark:text-emerald-300"><Award className="h-4 w-4" /></span></div>
        </div>
        <div className="flex flex-col rounded-md border border-forest-border bg-[#f8faf8] p-3 dark:border-white/10 dark:bg-white/[0.025] sm:p-4">
          <div className="flex items-center justify-between"><span className="text-[9px] font-semibold uppercase tracking-wide text-forest-muted">Certificate earned</span><Award className="h-4 w-4 text-amber-600 dark:text-amber-300" /></div>
          <div className="my-auto px-1 py-4">
            <div className="relative border border-emerald-800/20 bg-white px-3 py-5 text-center dark:border-emerald-200/20 dark:bg-[#18231e] sm:px-4">
              <div className="absolute inset-1 border border-emerald-800/10 dark:border-emerald-200/10" />
              <p className="relative font-mono text-[8px] font-semibold uppercase tracking-[0.16em] text-forest-accent">CODE YAAR</p>
              <p className="relative mt-2 font-serif text-base text-forest-ink dark:text-slate-100">Certificate of completion</p>
              <p className="relative mt-2 text-[9px] text-forest-muted">This recognizes</p>
              <p className="relative mt-1 text-xs font-semibold text-forest-ink dark:text-slate-100">Alex Morgan</p>
              <p className="relative mt-1 text-[9px] text-forest-muted">for completing Web Development Basics</p>
              <div className="relative mt-3 flex justify-center"><span className="flex h-7 w-7 items-center justify-center rounded-full border border-amber-500/40 text-amber-600 dark:text-amber-300"><Award className="h-4 w-4" /></span></div>
            </div>
          </div>
          <div className="flex items-center gap-1.5 text-[9px] text-forest-muted"><CheckCircle2 className="h-3 w-3 text-forest-accent" /> Verified learning milestone</div>
        </div>
      </div>
    </div>
  );
}

const previews = [ProjectPreview, MentorPreview, PracticePreview, ProgressPreview];

export function ProductShowcase() {
  const [activeIndex, setActiveIndex] = useState(0);
  const tabsRef = useRef<Array<HTMLButtonElement | null>>([]);
  const reduceMotion = useReducedMotion();
  const Preview = previews[activeIndex];

  function handleTabKeyDown(event: KeyboardEvent<HTMLButtonElement>) {
    let nextIndex = activeIndex;
    if (event.key === "ArrowDown" || event.key === "ArrowRight") {
      nextIndex = (activeIndex + 1) % features.length;
    } else if (event.key === "ArrowUp" || event.key === "ArrowLeft") {
      nextIndex = (activeIndex - 1 + features.length) % features.length;
    } else if (event.key === "Home") {
      nextIndex = 0;
    } else if (event.key === "End") {
      nextIndex = features.length - 1;
    } else {
      return;
    }
    event.preventDefault();
    setActiveIndex(nextIndex);
    tabsRef.current[nextIndex]?.focus();
  }

  return (
    <section id="product-showcase" aria-labelledby="product-showcase-title" className="border-y border-forest-border bg-white dark:border-white/10 dark:bg-[#111b18]">
      <div className="mx-auto grid max-w-7xl gap-10 px-5 py-16 sm:px-8 sm:py-20 lg:grid-cols-[0.78fr_1.22fr] lg:items-center lg:gap-14 lg:px-10 lg:py-24">
        <div>
          <p className="font-mono text-[10px] font-semibold uppercase tracking-[0.18em] text-forest-accent sm:text-xs">A place to put it into practice</p>
          <h2 id="product-showcase-title" className="mt-4 max-w-xl font-serif text-[2.4rem] font-normal leading-[1.08] text-forest-ink sm:text-5xl dark:text-slate-100">Learn by building, not just watching.</h2>
          <p className="mt-5 max-w-lg text-sm leading-6 text-forest-muted sm:text-base sm:leading-7">Go beyond tutorials. Build real projects, practice your skills, get AI mentorship, and create proof of what you can do.</p>

          <div role="tablist" aria-label="Explore the learning experience" aria-orientation="vertical" className="mt-8 space-y-1 sm:mt-10">
            {features.map((feature, index) => {
              const isActive = index === activeIndex;
              return (
                <button
                  key={feature.title}
                  ref={(element) => { tabsRef.current[index] = element; }}
                  type="button"
                  role="tab"
                  id={`showcase-tab-${index}`}
                  aria-selected={isActive}
                  aria-controls="showcase-preview-panel"
                  tabIndex={isActive ? 0 : -1}
                  onClick={() => setActiveIndex(index)}
                  onKeyDown={handleTabKeyDown}
                  className={`group relative flex min-h-16 w-full items-center justify-between gap-3 border-b border-forest-border py-3 pr-2 text-left transition-colors duration-300 dark:border-white/10 sm:min-h-[4.5rem] ${isActive ? "text-forest-ink dark:text-white" : "text-[#919a93] hover:text-forest-muted dark:text-slate-500 dark:hover:text-slate-300"}`}
                >
                  {isActive && <motion.span layoutId="showcase-active-indicator" className="absolute -left-3 top-2 bottom-2 w-0.5 rounded-full bg-forest-accent sm:-left-4" transition={{ duration: reduceMotion ? 0 : 0.24 }} />}
                  <span className={`font-serif text-lg leading-snug sm:text-[1.35rem] ${isActive ? "font-medium" : "font-normal"}`}>{feature.title}</span>
                  <ChevronRight className={`h-4 w-4 shrink-0 transition-transform duration-300 ${isActive ? "translate-x-0 text-forest-accent" : "-translate-x-1 opacity-0 group-hover:translate-x-0 group-hover:opacity-70"}`} />
                </button>
              );
            })}
          </div>
          <p aria-live="polite" className="mt-4 min-h-[3.5rem] max-w-lg text-sm leading-6 text-forest-muted" key={activeIndex}>{features[activeIndex].description}</p>
        </div>

        <div className="relative min-w-0 rounded-xl bg-gradient-to-br from-sky-100 via-emerald-50 to-[#f4f8ed] p-3 dark:from-sky-950/60 dark:via-emerald-950/50 dark:to-[#17251d] sm:p-5 lg:p-7">
          <div className="absolute left-7 top-6 flex items-center gap-1.5 text-[9px] font-semibold uppercase tracking-[0.14em] text-forest-accent/70 dark:text-emerald-200/60"><Sparkles className="h-3 w-3" /> Learning workspace preview</div>
          <div className="min-w-0 pt-7 sm:pt-8" role="tabpanel" id="showcase-preview-panel" aria-labelledby={`showcase-tab-${activeIndex}`} tabIndex={0}>
            <AnimatePresence mode="wait" initial={false}>
              <motion.div
                key={activeIndex}
                initial={{ opacity: 0, y: reduceMotion ? 0 : 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: reduceMotion ? 0 : -5 }}
                transition={{ duration: reduceMotion ? 0 : 0.22, ease: "easeOut" }}
                aria-label={`${features[activeIndex].title} preview`}
              >
                <Preview />
              </motion.div>
            </AnimatePresence>
          </div>
          <div className="mt-3 flex items-center justify-between px-1 text-[9px] text-forest-muted dark:text-slate-400"><span className="inline-flex items-center gap-1.5"><span className="h-1.5 w-1.5 rounded-full bg-emerald-500" /> Interactive product preview</span><span>{String(activeIndex + 1).padStart(2, "0")} / 04</span></div>
        </div>
      </div>
    </section>
  );
}