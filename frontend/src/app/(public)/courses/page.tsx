'use client';

import Link from 'next/link';
import { Suspense, useEffect, useMemo, useState } from 'react';
import { ArrowRight, BookOpen, Search } from 'lucide-react';
import { courses as coursesApi } from '@/lib/api';
import type { Course } from '@/types';
import { NetworkError } from '@/components/learning/workspace/error-states';

/**
 * PUBLIC course catalog: every published course, browsable without an
 * account. Card links land on /courses/[slug], the public course page that
 * converts visitors into students at the enroll moment.
 */

function CoursesCatalog() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [category, setCategory] = useState('All');
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const load = async () => {
    try {
      const data = await coursesApi.list();
      setCourses(data);
      setError(false);
    } catch {
      setError(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Deferred via await so the effect never sets state synchronously.
    (async () => { await load(); })();
  }, []);

  // Category chips reflect languages that actually exist in the catalog.
  const categories = useMemo(
    () => ['All', ...Array.from(new Set(courses.map((course) => course.language))).sort((a, b) => a.localeCompare(b))],
    [courses]
  );

  const filteredCourses = useMemo(() => courses.filter((course) => {
    const matchesCategory = category === 'All' || course.language.toLowerCase() === category.toLowerCase();
    const query = search.trim().toLowerCase();
    return matchesCategory && (!query || `${course.title} ${course.description} ${course.track_title}`.toLowerCase().includes(query));
  }), [category, courses, search]);

  if (error) return <NetworkError onRetry={load} />;

  return (
    <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
      <div className="mb-6 overflow-hidden rounded-card border border-border bg-hero-navy p-8 text-white sm:p-10">
        <div className="max-w-2xl">
          <nav className="mb-3 flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-white/60">
            <Link href="/tracks" className="hover:text-white">Tracks</Link>
            <span>/</span>
            <span className="text-cta">All courses</span>
          </nav>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold sm:text-4xl">Courses</h1>
            <span className="inline-flex items-center gap-1.5 rounded-pill bg-cta px-3 py-1 text-xs font-bold text-cta-fg"><BookOpen className="h-3.5 w-3.5" />Hands-on learning</span>
          </div>
          <p className="mt-3 text-white/70">Follow a structured path, practice the concept immediately, and build the confidence to use it in a real project.</p>
        </div>
      </div>

      <div className="mb-6 flex flex-wrap gap-2">
        {categories.map((item) => <button key={item} onClick={() => setCategory(item)} className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${category === item ? 'bg-hero-navy text-white' : 'border border-border bg-card text-foreground hover:bg-muted'}`}>{item}</button>)}
      </div>

      <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <span className="text-sm font-medium text-muted-foreground">{loading ? 'Loading courses...' : `${filteredCourses.length} course${filteredCourses.length === 1 ? '' : 's'}`}</span>
        <label className="relative block w-full sm:w-80"><span className="sr-only">Search courses</span><Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" /><input value={search} onChange={(event) => setSearch(event.target.value)} type="search" placeholder="Search courses..." className="w-full rounded-lg border border-border bg-card px-4 py-2 pl-9 text-sm outline-none focus:border-primary" /></label>
      </div>

      {loading ? <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">{[1, 2, 3].map((item) => <div key={item} className="h-48 animate-pulse rounded-card border border-border bg-card" />)}</div> : filteredCourses.length === 0 ? <div className="rounded-card border border-dashed border-border bg-card p-12 text-center"><h2 className="font-semibold">No courses match that search</h2><p className="mt-2 text-sm text-muted-foreground">Try another technology or clear the search.</p></div> : <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">{filteredCourses.map((course) => <Link key={course.id} href={`/courses/${course.slug}`} className="group overflow-hidden rounded-card border border-border bg-card transition-all hover:border-primary hover:shadow-[var(--shadow-2)]"><div className="h-2 bg-primary" /><div className="p-5"><div className="flex items-center justify-between text-xs font-semibold uppercase tracking-wider text-muted-foreground"><span>{course.track_title || course.language}</span><span>{course.difficulty}</span></div><h2 className="mt-3 text-lg font-bold text-foreground group-hover:text-primary">{course.title}</h2><p className="mt-2 line-clamp-2 text-sm text-muted-foreground">{course.description}</p><div className="mt-5 flex items-center justify-between text-xs text-muted-foreground"><span>{course.estimated_hours}h · {course.lesson_count} lessons</span><span className="font-semibold text-primary">View course<ArrowRight className="ml-1 inline h-3.5 w-3.5" /></span></div></div></Link>)}</div>}
    </div>
  );
}

export default function CoursesPage() {
  return (
    <Suspense fallback={<div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8"><div className="h-40 animate-pulse rounded-card border border-border bg-card" /></div>}>
      <CoursesCatalog />
    </Suspense>
  );
}
