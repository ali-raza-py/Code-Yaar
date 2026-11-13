"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowRight } from "lucide-react";
import { courses as coursesApi, hasSessionHint, progress } from "@/lib/api";
import type { Course, Enrollment } from "@/types";

/**
 * Honest next-session card for the homepage.
 * - Signed in with activity: shows the real resume lesson from the API.
 * - Signed in without activity: invites to start the first course.
 * - Anonymous: generic course intro, no invented personal progress.
 */
export function CourseResumeCard() {
  const [state, setState] = useState<{
    status: "loading" | "anonymous" | "no-activity" | "resume" | "unavailable";
    enrollment?: Enrollment;
    course?: Course;
    lessonTitle?: string;
    lessonProgress?: string;
  }>({ status: "loading" });

  useEffect(() => {
    let cancelled = false;

    async function load() {
      // The access token lives in memory, so the refresh cookie is the only
      // durable signal that this browser had a session. Without the hint we
      // skip the request entirely and render the anonymous card.
      if (!hasSessionHint()) {
        if (!cancelled) setState({ status: "anonymous" });
        return;
      }
      try {
        const enrollments = await progress.enrollments.list();
        if (cancelled) return;

        const active = enrollments.find((e) => e.status === "active") ?? enrollments[0];
        if (!active) {
          setState({ status: "no-activity", course: await coursesApi.detail("python-foundations").catch(() => undefined) });
          return;
        }

        const course = await coursesApi.detail(active.course_slug).catch(() => undefined);
        if (cancelled) return;
        setState({
          status: "resume",
          enrollment: active,
          course,
          lessonTitle: course?.resume_lesson?.title,
          lessonProgress: `${active.progress_percentage}% complete`,
        });
      } catch {
        if (!cancelled) setState({ status: "unavailable" });
      }
    }

    load();
    return () => { cancelled = true; };
  }, []);

  if (state.status === "loading") {
    return (
      <div className="relative rounded-[var(--radius-card)] border border-white/10 bg-white/5 p-5 shadow-[var(--shadow-2)] backdrop-blur-sm sm:p-7">
        <div className="animate-pulse space-y-4">
          <div className="h-3 w-40 rounded bg-white/10" />
          <div className="h-6 w-56 rounded bg-white/10" />
          <div className="h-4 w-full rounded bg-white/10" />
          <div className="h-4 w-2/3 rounded bg-white/10" />
        </div>
      </div>
    );
  }

  if (state.status === "unavailable") {
    return (
      <div className="relative rounded-[var(--radius-card)] border border-white/10 bg-white/5 p-5 text-[var(--color-text-dark-hero)] shadow-[var(--shadow-2)] backdrop-blur-sm sm:p-7">
        <span className="font-mono text-xs font-semibold tracking-wide text-primary">LEARNING STATUS</span>
        <p className="mt-4 text-sm leading-6 text-[var(--color-text-dark-muted)]">
          We couldn&apos;t reach the server to load your progress. Browse courses below instead.
        </p>
        <Link href="/learn" className="focus-ring mt-4 inline-flex items-center gap-1 rounded font-semibold text-primary transition-colors hover:text-cta-hover">
          Browse courses <ArrowRight className="h-4 w-4" />
        </Link>
      </div>
    );
  }

  const isResume = state.status === "resume" && state.enrollment;
  const title = isResume
    ? state.lessonTitle ?? state.enrollment!.course_title
    : state.status === "no-activity" && state.course
      ? state.course.title
      : "Python Foundations";

  return (
    <div className="relative rounded-[var(--radius-card)] border border-white/10 bg-white/[0.06] p-5 text-[var(--color-text-dark-hero)] shadow-[var(--shadow-2)] backdrop-blur-sm sm:p-7">
      <div className="flex items-center justify-between border-b border-white/10 pb-4">
        <span className="font-mono text-xs font-semibold tracking-wide text-primary">
          {isResume ? "YOUR NEXT SESSION" : "START YOUR FIRST SESSION"}
        </span>
        <span className="rounded-pill bg-primary px-2.5 py-1 font-mono text-[10px] font-bold text-primary-foreground">FREE</span>
      </div>
      <div className="py-7">
        <p className="font-mono text-xs uppercase tracking-wider text-[var(--color-text-dark-muted)]">
          {isResume ? state.enrollment!.course_title : "Featured course"}
        </p>
        <h2 className="mt-2 text-2xl font-semibold text-[var(--color-text-dark-hero)]">{title}</h2>
        <p className="mt-3 text-sm leading-6 text-[var(--color-text-dark-muted)]">
          Learn the concept, try the example, then write code that passes a real test.
        </p>
      </div>
      <div className="flex items-center justify-between gap-4 border-t border-white/10 pt-4 text-sm">
        <span className="text-[var(--color-text-dark-muted)]">
          {isResume
            ? state.lessonProgress
            : "Sign in to save your progress and earn XP"}
        </span>
        <Link
          href={isResume ? `/learn/${state.enrollment!.course_slug}` : "/courses/python-foundations"}
          className="focus-ring inline-flex items-center gap-1 rounded font-semibold text-primary transition-colors hover:text-cta-hover"
        >
          {isResume ? "Continue" : "Open course"} <ArrowRight className="h-4 w-4" />
        </Link>
      </div>
    </div>
  );
}
