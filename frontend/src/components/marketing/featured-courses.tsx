"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowRight, BookOpen, Clock } from "lucide-react";
import { courses as coursesApi } from "@/lib/api";
import type { Course } from "@/types";

/**
 * Featured courses sourced from GET /api/courses/ (published records only —
 * never invented placeholders). Shows the first few courses the API returns;
 * when the catalog is empty the section quietly steps aside.
 */
export function FeaturedCourses() {
  const [courses, setCourses] = useState<Course[] | null>(null);

  useEffect(() => {
    let cancelled = false;
    coursesApi.list()
      .then((data) => { if (!cancelled) setCourses(data); })
      .catch(() => { if (!cancelled) setCourses([]); });
    return () => { cancelled = true; };
  }, []);

  if (courses === null) {
    return (
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-44 animate-pulse rounded-[var(--radius-card)] border border-forest-border bg-card/60" />
        ))}
      </div>
    );
  }

  if (courses.length === 0) {
    return (
      <div className="rounded-[var(--radius-card)] border border-forest-border bg-card p-5 text-sm text-muted-foreground">
        Courses are being prepared. Meanwhile, the{' '}
        <Link href="/tracks" className="focus-ring rounded font-semibold text-forest-accent">learning tracks</Link>{' '}
        show where the catalog is heading.
      </div>
    );
  }

  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {courses.slice(0, 3).map((course) => (
        <Link
          key={course.id}
          href={`/courses/${course.slug}`}
          className="focus-ring group flex flex-col rounded-[var(--radius-card)] border border-forest-border bg-card p-5 text-card-foreground transition hover:-translate-y-1 hover:border-forest-border-hover hover:shadow-[5px_5px_0_var(--forest-shadow-soft)]"
        >
          <div className="flex items-center justify-between gap-3 text-[10px] font-semibold uppercase tracking-wider text-forest-line-soft">
            <span className="inline-flex items-center gap-1.5"><BookOpen className="h-3.5 w-3.5" />{course.track_title || course.language}</span>
            <span className="capitalize">{course.difficulty}</span>
          </div>
          <h3 className="mt-3 font-bold leading-snug group-hover:text-forest-accent">{course.title}</h3>
          <p className="mt-2 line-clamp-2 text-sm text-forest-muted">{course.description}</p>
          <div className="mt-auto flex items-center justify-between pt-5 text-xs text-forest-muted">
            <span className="inline-flex items-center gap-1.5"><Clock className="h-3.5 w-3.5" />{course.estimated_hours}h · {course.lesson_count} lessons</span>
            <span className="inline-flex items-center gap-1 font-semibold text-forest-accent">View course<ArrowRight className="h-3.5 w-3.5 transition-transform group-hover:translate-x-1" /></span>
          </div>
        </Link>
      ))}
    </div>
  );
}
