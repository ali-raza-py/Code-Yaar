"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { ArrowRight, BookOpen, Search } from "lucide-react";
import { ApiError, courses as coursesApi } from "@/lib/api";
import type { Course } from "@/types";
import { NetworkError } from "@/components/learning/workspace/error-states";

const categories = ["All", "Python", "JavaScript", "React", "Node.js", "TypeScript", "SQL", "Git", "Docker", "AWS"];

export default function LearnPage() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [category, setCategory] = useState("All");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    coursesApi.list()
      .then((data) => setCourses(Array.isArray(data) ? data as Course[] : []))
      .catch((reason) => {
        if (reason instanceof ApiError || reason instanceof TypeError) setError(true);
      })
      .finally(() => setLoading(false));
  }, []);

  const filteredCourses = useMemo(() => courses.filter((course) => {
    const matchesCategory = category === "All" || course.language.toLowerCase() === category.toLowerCase();
    const query = search.trim().toLowerCase();
    return matchesCategory && (!query || `${course.title} ${course.description} ${course.track_title}`.toLowerCase().includes(query));
  }), [category, courses, search]);

  if (error) return <NetworkError />;

  return (
    <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
      <div className="mb-6 overflow-hidden rounded-xl bg-[#0f1d32] p-8 text-white sm:p-10">
        <div className="max-w-2xl">
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold sm:text-4xl">Courses</h1>
            <span className="inline-flex items-center gap-1.5 rounded-full bg-[#2dbe52] px-3 py-1 text-xs font-bold"><BookOpen className="h-3.5 w-3.5" />Hands-on learning</span>
          </div>
          <p className="mt-3 text-white/70">Follow a structured path, practice the concept immediately, and build the confidence to use it in a real project.</p>
        </div>
      </div>

      <div className="mb-6 flex flex-wrap gap-2">
        {categories.map((item) => <button key={item} onClick={() => setCategory(item)} className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${category === item ? "bg-[#0f1d32] text-white" : "border border-[var(--color-section-border)] bg-white text-foreground hover:bg-[var(--color-section-light)]"}`}>{item}</button>)}
      </div>

      <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <span className="text-sm font-medium text-muted-foreground">{loading ? "Loading courses..." : `${filteredCourses.length} course${filteredCourses.length === 1 ? "" : "s"}`}</span>
        <label className="relative block w-full sm:w-80"><span className="sr-only">Search courses</span><Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" /><input value={search} onChange={(event) => setSearch(event.target.value)} type="search" placeholder="Search courses..." className="w-full rounded-lg border border-[var(--color-section-border)] bg-white px-4 py-2 pl-9 text-sm outline-none focus:border-[var(--primary)]" /></label>
      </div>

      {loading ? <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">{[1, 2, 3].map((item) => <div key={item} className="h-48 animate-pulse rounded-xl bg-white" />)}</div> : filteredCourses.length === 0 ? <div className="border border-dashed border-[var(--color-section-border)] bg-white p-12 text-center"><h2 className="font-semibold">No courses match that search</h2><p className="mt-2 text-sm text-muted-foreground">Try another technology or clear the search.</p></div> : <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">{filteredCourses.map((course) => <Link key={course.id} href={`/courses/${course.slug}`} className="group overflow-hidden rounded-xl border border-[var(--color-section-border)] bg-white transition-all hover:border-[var(--primary)] hover:shadow-md"><div className="h-2 bg-[var(--primary)]" /><div className="p-5"><div className="flex items-center justify-between text-xs font-semibold uppercase tracking-wider text-muted-foreground"><span>{course.track_title || course.language}</span><span>{course.difficulty}</span></div><h2 className="mt-3 text-lg font-bold text-foreground group-hover:text-[var(--primary)]">{course.title}</h2><p className="mt-2 line-clamp-2 text-sm text-muted-foreground">{course.description}</p><div className="mt-5 flex items-center justify-between text-xs text-muted-foreground"><span>{course.estimated_hours}h · {course.lesson_count} lessons</span><span className="font-semibold text-[var(--primary)]">{course.progress_percentage > 0 ? `${course.progress_percentage}% complete` : "Start course"}<ArrowRight className="ml-1 inline h-3.5 w-3.5" /></span></div></div></Link>)}</div>}
    </div>
  );
}
