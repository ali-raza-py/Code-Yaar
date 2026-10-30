"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowRight } from "lucide-react";
import { auth, courses as coursesApi, progress } from "@/lib/api";
import type { AuthProfileData } from "@/lib/api";
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
      const token = typeof window !== "undefined" && localStorage.getItem("auth_token");
      if (!token) {
        if (!cancelled) setState({ status: "anonymous" });
        return;
      }
      try {
        const [profile, enrollments] = await Promise.all([
          auth.getProfile() as Promise<AuthProfileData>,
          progress.enrollments.list(),
        ]);
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
        void profile;
      } catch {
        if (!cancelled) setState({ status: "unavailable" });
      }
    }

    load();
    return () => { cancelled = true; };
  }, []);

  if (state.status === "loading") {
    return (
      <div className="relative border border-forest-line bg-forest-surface p-5 shadow-[12px_12px_0_var(--forest-shadow-deep)] sm:p-7">
        <div className="animate-pulse space-y-4">
          <div className="h-3 w-40 rounded bg-forest-line" />
          <div className="h-6 w-56 rounded bg-forest-line" />
          <div className="h-4 w-full rounded bg-forest-line" />
          <div className="h-4 w-2/3 rounded bg-forest-line" />
        </div>
      </div>
    );
  }

  if (state.status === "unavailable") {
    return (
      <div className="relative border border-forest-line bg-forest-surface p-5 shadow-[12px_12px_0_var(--forest-shadow-deep)] sm:p-7">
        <span className="font-mono text-xs text-mint-soft">LEARNING STATUS</span>
        <p className="mt-4 text-sm leading-6 text-forest-on-deep">
          We couldn&apos;t reach the server to load your progress. Browse courses below instead.
        </p>
        <Link href="/learn" className="focus-ring mt-4 inline-flex items-center rounded font-semibold text-mint hover:text-white">
          Browse courses <ArrowRight className="ml-1 inline h-4 w-4" />
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
    <div className="relative border border-forest-line bg-forest-surface p-5 shadow-[12px_12px_0_var(--forest-shadow-deep)] sm:p-7">
      <div className="flex items-center justify-between border-b border-forest-line pb-4">
        <span className="font-mono text-xs text-mint-soft">
          {isResume ? "YOUR NEXT SESSION" : "START YOUR FIRST SESSION"}
        </span>
        <span className="rounded-pill bg-mint px-2.5 py-1 font-mono text-[10px] font-bold text-forest-deep">FREE</span>
      </div>
      <div className="py-7">
        <p className="font-mono text-xs uppercase tracking-wider text-forest-on-deep-soft">
          {isResume ? state.enrollment!.course_title : "Featured course"}
        </p>
        <h2 className="mt-2 text-2xl font-bold">{title}</h2>
        <p className="mt-3 text-sm leading-6 text-forest-on-deep">
          Learn the concept, try the example, then write code that passes a real test.
        </p>
      </div>
      <div className="flex items-center justify-between border-t border-forest-line pt-4 text-sm">
        <span className="text-forest-on-deep-soft">
          {isResume
            ? state.lessonProgress
            : "Sign in to save your progress and earn XP"}
        </span>
        <Link
          href={isResume ? `/learn/${state.enrollment!.course_slug}` : "/courses/python-foundations"}
          className="focus-ring rounded font-semibold text-mint hover:text-white"
        >
          {isResume ? "Continue" : "Open course"} <ArrowRight className="ml-1 inline h-4 w-4" />
        </Link>
      </div>
    </div>
  );
}
