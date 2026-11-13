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
  <><span className="text-primary">const</span> <span className="text-primary">projects</span> = [</>,
  <>  <span className="text-primary">&quot;portfolio&quot;</span>,</>,
  <>  <span className="text-primary">&quot;weather-app&quot;</span>,</>,
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
    <div className="flex h-11 items-center justify-between border-b border-border px-3 sm:px-4">
      <div className="flex items-center gap-2">
        <span className="flex h-6 w-6 items-center justify-center rounded bg-primary text-[10px] font-bold text-primary-foreground">cy</span>
        <span className="text-[11px] font-semibold text-foreground sm:text-xs">{title}</span>
      </div>
      <div className="flex items-center gap-1.5" aria-hidden="true">
        <i className="h-2 w-2 rounded-full bg-secondary" />
        <i className="h-2 w-2 rounded-full bg-secondary" />
        <i className="h-2 w-2 rounded-full bg-secondary" />
      </div>
    </div>
  );
}

function ProjectPreview() {
  return (
    <div className="overflow-hidden rounded-[var(--radius-card)] border border-border bg-card shadow-[0_16px_50px_rgba(0,0,0,0.08)]">
      <WindowBar title="Portfolio project" />
      <div className="flex h-9 items-center gap-1 border-b border-border px-3">
        <span className="inline-flex h-full items-center gap-1.5 border-b-2 border-primary px-2 text-[10px] font-semibold text-foreground"><Code2 className="h-3 w-3" /> Editor</span>
        <span className="inline-flex h-full items-center gap-1.5 px-2 text-[10px] text-muted-foreground"><Terminal className="h-3 w-3" /> Terminal</span>
        <span className="inline-flex h-full items-center gap-1.5 px-2 text-[10px] text-muted-foreground"><Globe2 className="h-3 w-3" /> Preview</span>
      </div>
      <div className="grid min-h-[330px] grid-cols-[116px_minmax(0,1fr)] sm:grid-cols-[150px_minmax(0,1fr)]">
        <aside className="border-r border-border p-2.5 sm:p-3">
          <p className="mb-3 text-[9px] font-bold uppercase tracking-[0.14em] text-muted-foreground">Explorer</p>
          <p className="mb-2 flex items-center gap-1.5 truncate text-[10px] font-semibold text-foreground"><Folder className="h-3 w-3 text-primary" /> my-portfolio</p>
          <p className="mb-2 flex items-center gap-1.5 pl-3 text-[10px] text-muted-foreground"><Folder className="h-3 w-3" /> src</p>
          <p className="mb-2 flex items-center gap-1.5 rounded border border-primary/20 bg-primary/10 px-1.5 py-1 text-[10px] font-semibold text-primary"><FileCode2 className="h-3 w-3" /> App.jsx</p>
          <p className="flex items-center gap-1.5 pl-3 text-[10px] text-muted-foreground"><FileCode2 className="h-3 w-3" /> styles.css</p>
          <p className="mt-2 flex items-center gap-1.5 pl-3 text-[10px] text-muted-foreground"><FileCode2 className="h-3 w-3" /> index.html</p>
        </aside>
        <div className="min-w-0">
          <div className="flex h-8 items-center border-b border-border px-3">
            <span className="font-mono text-[10px] text-muted-foreground">src / App.jsx</span>
          </div>
          <div className="grid gap-3 p-3 sm:grid-cols-[1fr_0.9fr] sm:gap-4 sm:p-4">
            <div className="min-w-0">
              <p className="mb-3 font-mono text-[10px] text-muted-foreground">01&nbsp;&nbsp; Build a personal portfolio website</p>
              <p className="mb-3 text-[10px] leading-4 text-muted-foreground">Create a responsive home page that introduces you and highlights your work.</p>
              <div className="rounded border border-border bg-muted p-2.5"><CodeLines /></div>
              <div className="mt-3 flex items-center gap-1.5 text-[9px] text-primary"><CheckCircle2 className="h-3 w-3" /> Your changes are saved</div>
            </div>
            <div className="hidden rounded border border-border bg-secondary/50 p-3 sm:block">
              <div className="flex items-center justify-between"><span className="text-[9px] font-semibold text-muted-foreground">LIVE PREVIEW</span><span className="h-1.5 w-1.5 rounded-full bg-primary" /></div>
              <div className="mt-5 border-l-2 border-primary pl-2.5">
                <p className="font-serif text-base leading-tight text-foreground">Hello, I’m Alex.</p>
                <p className="mt-1 text-[9px] leading-4 text-muted-foreground">Developer, learner, and curious builder.</p>
              </div>
              <div className="mt-4 h-14 rounded bg-secondary/60" />
              <div className="mt-3 flex gap-1.5"><span className="h-4 w-12 rounded-sm bg-muted" /><span className="h-4 w-10 rounded-sm border border-border" /></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function MentorPreview() {
  return (
    <div className="overflow-hidden rounded-[var(--radius-card)] border border-border bg-card">
      <WindowBar title="Project mentor" />
      <div className="grid min-h-[330px] md:grid-cols-[0.8fr_1.2fr]">
        <div className="border-b border-border p-4 sm:p-5 md:border-b-0 md:border-r">
          <div className="flex items-center gap-2 text-[10px] font-semibold text-muted-foreground"><BookOpen className="h-3.5 w-3.5" /> YOUR PROJECT</div>
          <h3 className="mt-4 font-serif text-lg leading-tight text-foreground">Personal portfolio</h3>
          <p className="mt-2 text-[11px] leading-5 text-muted-foreground">Add a responsive navigation bar that collapses on smaller screens.</p>
          <div className="mt-4 rounded border border-border bg-muted p-3">
            <p className="mb-2 text-[9px] font-semibold uppercase tracking-wide text-muted-foreground">Your code</p>
            <pre className="overflow-x-auto font-mono text-[10px] leading-5 text-foreground"><span className="text-primary">function</span> <span className="text-primary">Navbar</span>() {"{"}<br />  <span className="text-primary">return</span> (&lt;nav&gt;...&lt;/nav&gt;);<br />{"}"}</pre>
          </div>
          <div className="mt-4 flex items-center gap-2 text-[10px] text-muted-foreground"><Circle className="h-3 w-3" /> 2 hints available</div>
        </div>
        <div className="p-4 sm:p-5">
          <div className="flex items-center gap-2 text-[10px] font-semibold text-primary"><Sparkles className="h-3.5 w-3.5" /> CODE YAAR MENTOR <span className="rounded-full bg-primary/10 px-2 py-0.5 text-[9px] font-semibold text-primary">Preview</span></div>
          <div className="mt-4 rounded-md bg-secondary/50 p-3">
            <p className="text-[10px] font-semibold text-foreground">You</p>
            <p className="mt-1 text-[11px] leading-5 text-muted-foreground">I’m not sure how to make the menu collapse on mobile. What should I look at?</p>
          </div>
          <div className="mt-3 flex gap-2.5">
            <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary"><Sparkles className="h-3 w-3" /></span>
            <div className="min-w-0">
              <p className="text-[10px] font-semibold text-foreground">Let’s reason it through</p>
              <p className="mt-1 text-[11px] leading-5 text-muted-foreground">You already have the navigation structure. Which CSS breakpoint could hide the links, and what might you show in their place?</p>
              <div className="mt-2 rounded border border-border bg-muted p-2.5">
                <pre className="overflow-x-auto font-mono text-[10px] leading-5 text-foreground"><span className="text-primary">@media</span> (max-width: <span className="text-primary">640px</span>) {"{"}<br />  .nav-links {"{"} display: none; {"}"}<br />{"}"}</pre>
              </div>
              <div className="mt-3 flex flex-wrap gap-2"><span className="inline-flex items-center gap-1 rounded border border-border px-2 py-1 text-[9px] text-muted-foreground"><Lightbulb className="h-3 w-3 text-primary" /> Give me a hint</span><span className="inline-flex items-center gap-1 rounded border border-border px-2 py-1 text-[9px] text-muted-foreground"><MessageCircle className="h-3 w-3" /> Explain this</span></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function PracticePreview() {
  return (
    <div className="overflow-hidden rounded-[var(--radius-card)] border border-border bg-card">
      <WindowBar title="Daily practice" />
      <div className="flex items-center justify-between border-b border-border px-4 py-2.5">
        <div className="flex items-center gap-2 text-[10px] text-muted-foreground"><Braces className="h-3.5 w-3.5 text-primary" /> JavaScript fundamentals</div>
        <span className="rounded bg-primary/10 px-2 py-1 text-[9px] font-semibold text-primary">QUESTION 04 / 08</span>
      </div>
      <div className="grid min-h-[330px] md:grid-cols-[0.9fr_1.1fr]">
        <div className="border-b border-border p-4 md:border-b-0 md:border-r sm:p-5">
          <div className="flex items-center gap-2"><span className="rounded bg-primary/10 px-2 py-1 text-[9px] font-semibold text-primary">EASY</span><span className="text-[9px] text-muted-foreground">Arrays · 10 XP</span></div>
          <h3 className="mt-4 font-serif text-lg text-foreground">Find the first match</h3>
          <p className="mt-2 text-[11px] leading-5 text-muted-foreground">Write a function that returns the first number greater than <code className="rounded bg-secondary px-1 font-mono text-[10px]">target</code>, or <code className="rounded bg-secondary px-1 font-mono text-[10px]">-1</code> if none exists.</p>
          <div className="mt-4 rounded border border-border bg-secondary/50 p-3"><p className="font-mono text-[9px] text-muted-foreground">findNext([2, 5, 8], 5)</p><p className="mt-1 font-mono text-[10px] text-foreground">{`// returns 8`}</p></div>
          <div className="mt-4 flex items-center justify-between text-[9px] text-muted-foreground"><span>YOUR PROGRESS</span><span>4 of 8</span></div>
          <div className="mt-1.5 h-1.5 overflow-hidden rounded-full bg-secondary"><div className="h-full w-1/2 rounded-full bg-primary" /></div>
        </div>
        <div className="flex min-w-0 flex-col p-3 sm:p-4">
          <div className="flex items-center justify-between"><span className="font-mono text-[9px] text-muted-foreground">solution.js</span><span className="inline-flex items-center gap-1 text-[9px] text-muted-foreground"><Circle className="h-2.5 w-2.5" /> Draft</span></div>
          <div className="mt-2 min-h-[118px] flex-1 rounded border border-border bg-secondary/50 p-3"><pre className="overflow-x-auto font-mono text-[10px] leading-5 text-foreground"><span className="text-primary">function</span> <span className="text-primary">findNext</span>(numbers, target) {"{"}<br />  <span className="text-primary">return</span> numbers.find(<br />    (number) =&gt; number &gt; target<br />  ) ?? <span className="text-primary">-1</span>;<br />{"}"}</pre></div>
          <div className="mt-3 rounded border border-primary/20 bg-primary/10 p-2.5">
            <div className="flex items-center gap-1.5 text-[10px] font-semibold text-primary"><CheckCircle2 className="h-3.5 w-3.5" /> 3 of 3 tests passing</div>
            <div className="mt-2 grid grid-cols-3 gap-1 text-[8px] text-primary/80"><span className="flex items-center gap-1"><Check className="h-2.5 w-2.5" /> Basic case</span><span className="flex items-center gap-1"><Check className="h-2.5 w-2.5" /> No match</span><span className="flex items-center gap-1"><Check className="h-2.5 w-2.5" /> Edge case</span></div>
          </div>
          <button type="button" className="mt-3 inline-flex h-8 items-center justify-center gap-1.5 self-end rounded bg-primary px-3 text-[10px] font-semibold text-primary-foreground"><Play className="h-3 w-3" /> Run tests</button>
        </div>
      </div>
    </div>
  );
}

function ProgressPreview() {
  return (
    <div className="overflow-hidden rounded-[var(--radius-card)] border border-border bg-card">
      <div className="border-b border-border p-3 py-2 text-[9px] text-muted-foreground">DEMO PREVIEW · SAMPLE LEARNER PROFILE</div>
      <div className="grid min-h-[310px] gap-3 p-3 sm:grid-cols-2 sm:gap-4 sm:p-4">
        <div className="rounded-md border border-border p-3 sm:p-4">
          <div className="flex items-center gap-2.5"><span className="flex h-9 w-9 items-center justify-center rounded-full bg-primary/10 text-xs font-bold text-primary">AM</span><div><p className="text-[11px] font-semibold text-foreground">Alex Morgan</p><p className="text-[9px] text-muted-foreground">Learning since March 2026</p></div></div>
          <div className="mt-4 grid grid-cols-2 gap-2"><div className="rounded bg-secondary p-2.5"><p className="flex items-center gap-1 text-[9px] text-muted-foreground"><Zap className="h-3 w-3 text-primary" /> TOTAL XP</p><p className="mt-1 text-base font-semibold text-foreground">1,240</p></div><div className="rounded bg-secondary p-2.5"><p className="flex items-center gap-1 text-[9px] text-muted-foreground"><BookOpen className="h-3 w-3 text-primary" /> COURSES</p><p className="mt-1 text-base font-semibold text-foreground">3 <span className="text-[9px] font-normal text-muted-foreground">complete</span></p></div></div>
          <div className="mt-4 flex items-center justify-between text-[9px] text-muted-foreground"><span>Frontend foundations</span><span>68%</span></div><div className="mt-1.5 h-1.5 rounded-full bg-secondary"><div className="h-full w-[68%] rounded-full bg-primary" /></div>
          <div className="mt-4 flex items-center justify-between"><p className="text-[9px] font-semibold text-foreground">Recent achievements</p><span className="text-[9px] text-primary">View all</span></div>
          <div className="mt-2 flex gap-2"><span className="flex h-8 w-8 items-center justify-center rounded bg-primary/10 text-primary"><Trophy className="h-4 w-4" /></span><span className="flex h-8 w-8 items-center justify-center rounded bg-primary/10 text-primary"><Braces className="h-4 w-4" /></span><span className="flex h-8 w-8 items-center justify-center rounded bg-primary/10 text-primary"><Award className="h-4 w-4" /></span></div>
        </div>
        <div className="flex flex-col rounded-md border border-border bg-secondary/50 p-3 sm:p-4">
          <div className="flex items-center justify-between"><span className="text-[9px] font-semibold uppercase tracking-wide text-muted-foreground">Certificate earned</span><Award className="h-4 w-4 text-primary" /></div>
          <div className="my-auto px-1 py-4">
            <div className="relative border border-primary/10 bg-card px-3 py-5 text-center sm:px-4">
              <div className="absolute inset-1 border border-primary/10" />
              <p className="relative font-mono text-[8px] font-semibold uppercase tracking-[0.16em] text-primary">CODE YAAR</p>
              <p className="relative mt-2 font-serif text-base text-foreground">Certificate of completion</p>
              <p className="relative mt-2 text-[9px] text-muted-foreground">This recognizes</p>
              <p className="relative mt-1 text-xs font-semibold text-foreground">Alex Morgan</p>
              <p className="relative mt-1 text-[9px] text-muted-foreground">for completing Web Development Basics</p>
              <div className="relative mt-3 flex justify-center"><span className="flex h-7 w-7 items-center justify-center rounded-full border border-primary/20 text-primary"><Award className="h-4 w-4" /></span></div>
            </div>
          </div>
          <div className="flex items-center gap-1.5 text-[9px] text-muted-foreground"><CheckCircle2 className="h-3 w-3 text-primary" /> Verified learning milestone</div>
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
    <section id="product-showcase" aria-labelledby="product-showcase-title" className="border-y border-border bg-card">
      <div className="mx-auto grid max-w-7xl gap-10 px-5 py-16 sm:px-8 sm:py-20 lg:grid-cols-[0.78fr_1.22fr] lg:items-center lg:gap-14 lg:px-10 lg:py-24">
        <div>
          <p className="font-mono text-[10px] font-semibold uppercase tracking-[0.18em] text-primary sm:text-xs">A place to put it into practice</p>
          <h2 id="product-showcase-title" className="mt-4 max-w-xl font-serif text-[2.4rem] font-normal leading-[1.08] text-foreground sm:text-5xl">Learn by building, not just watching.</h2>
          <p className="mt-5 max-w-lg text-sm leading-6 text-muted-foreground sm:text-base sm:leading-7">Go beyond tutorials. Build real projects, practice your skills, get AI mentorship, and create proof of what you can do.</p>

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
                  className={`group relative flex min-h-16 w-full items-center justify-between gap-3 border-b border-border py-3 pr-2 text-left transition-colors duration-300 sm:min-h-[4.5rem] ${isActive ? "text-foreground" : "text-muted-foreground hover:text-foreground"}`}
                >
                  {isActive && <motion.span layoutId="showcase-active-indicator" className="absolute -left-3 top-2 bottom-2 w-0.5 rounded-full bg-primary sm:-left-4" transition={{ duration: reduceMotion ? 0 : 0.24 }} />}
                  <span className={`font-serif text-lg leading-snug sm:text-[1.35rem] ${isActive ? "font-medium" : "font-normal"}`}>{feature.title}</span>
                  <ChevronRight className={`h-4 w-4 shrink-0 transition-transform duration-300 ${isActive ? "translate-x-0 text-primary" : "-translate-x-1 opacity-0 group-hover:translate-x-0 group-hover:opacity-70"}`} />
                </button>
              );
            })}
          </div>
          <p aria-live="polite" className="mt-4 min-h-[3.5rem] max-w-lg text-sm leading-6 text-muted-foreground" key={activeIndex}>{features[activeIndex].description}</p>
        </div>

        <div className="relative min-w-0 rounded-[var(--radius-card)] border border-border p-3 sm:p-5 lg:p-7">
          <div className="absolute left-7 top-6 flex items-center gap-1.5 text-[9px] font-semibold uppercase tracking-[0.14em] text-primary/70"><Sparkles className="h-3 w-3" /> Learning workspace preview</div>
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
          <div className="mt-3 flex items-center justify-between px-1 text-[9px] text-muted-foreground"><span className="inline-flex items-center gap-1.5"><span className="h-1.5 w-1.5 rounded-full bg-primary" /> Interactive product preview</span><span>{String(activeIndex + 1).padStart(2, "0")} / 04</span></div>
        </div>
      </div>
    </section>
  );
}
