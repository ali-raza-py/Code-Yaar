import Link from 'next/link';
import { ArrowRight, BookOpen, Search } from 'lucide-react';
import { fetchCoursesServer } from '@/lib/server-api';
import type { Course } from '@/types';
import { NetworkError } from '@/components/learning/workspace/error-states';
import { CourseSkeleton } from '@/components/learning/course-skeleton';

interface CoursesCatalogProps {
  searchParams: { track?: string; difficulty?: string; language?: string; search?: string };
  courses: Course[];
  error: Error | null;
}

function CoursesCatalog({ searchParams, courses, error }: CoursesCatalogProps) {
  const { track, difficulty, language, search } = searchParams;

  if (error) {
    return (
      <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        <NetworkError onRetry={() => { /* handled by Next.js refresh */ }} />
      </div>
    );
  }

  // Category chips reflect languages that actually exist in the catalog.
  const categories = ['All', ...Array.from(new Set(courses.map((course) => course.language))).sort((a, b) => a.localeCompare(b))];

  const query = (search || '').trim().toLowerCase();
  const filteredCourses = courses.filter((course) => {
    const matchesCategory = !track || course.language === track;
    const matchesDifficulty = !difficulty || course.difficulty === difficulty;
    const matchesLanguage = !language || course.language === language;
    const matchesSearch = !query ||
      `${course.title} ${course.description} ${course.track_title || ''}`.toLowerCase().includes(query);
    return matchesCategory && matchesDifficulty && matchesLanguage && matchesSearch;
  });

  const activeFilter = track || difficulty || language || 'All';

  return (
    <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
      <div className="mb-6 overflow-hidden rounded-[var(--radius-card)] border border-[#334155] bg-[#0f172a] p-8 text-[#f8fafc] sm:p-10">
        <div className="max-w-2xl">
          <nav className="mb-3 flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-[#cbd5e1]">
            <Link href="/tracks" className="transition-colors hover:text-[#f8fafc]">Tracks</Link>
            <span>/</span>
            <span className="text-primary">All courses</span>
          </nav>
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl text-[#f8fafc]">Courses</h1>
            <span className="inline-flex items-center gap-1.5 rounded-pill bg-primary px-3 py-1 text-xs font-semibold text-primary-foreground"><BookOpen className="h-3.5 w-3.5" />Hands-on learning</span>
          </div>
          <p className="mt-3 text-[#94a3b8]">Follow a structured path, practice the concept immediately, and build the confidence to use it in a real project.</p>
        </div>
      </div>

      <div className="mb-6 flex flex-wrap gap-2">
        {categories.map((item) => (
          <button
            key={item}
            onClick={() => { /* client-side filter handled below */ }}
            className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring ${activeFilter === item ? 'bg-primary text-primary-foreground' : 'border border-[#475569] bg-[#1e293b] text-[#f8fafc] hover:bg-[#334155] hover:text-[#f8fafc]'}`}
          >
            {item}
          </button>
        ))}
      </div>

      <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <span className="text-sm font-medium text-[#94a3b8]">{filteredCourses.length} course{filteredCourses.length === 1 ? '' : 's'}</span>
        <label className="relative block w-full sm:w-80"><span className="sr-only">Search courses</span><Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[#94a3b8]" /><input value={search || ''} onChange={() => {}} type="search" placeholder="Search courses..." className="w-full rounded-lg border border-[#475569] bg-[#1e293b] px-4 py-2 pl-9 text-sm text-[#f8fafc] outline-none transition-colors focus:border-primary focus:ring-2 focus:ring-primary/20 placeholder:text-[#64748b]" /></label>
      </div>

      {filteredCourses.length === 0 ? (
        <div className="rounded-[var(--radius-card)] border border-dashed border-[#334155] bg-[#1e293b] p-12 text-center">
          <h2 className="font-semibold text-[#f8fafc]">No courses match that search</h2>
          <p className="mt-2 text-sm text-[#94a3b8]">Try another technology or clear the search.</p>
        </div>
      ) : (
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {filteredCourses.map((course) => (
            <Link key={course.id} href={`/courses/${course.slug}`} prefetch className="group overflow-hidden rounded-[var(--radius-card)] border border-[#334155] bg-[#0f172a] text-[#f8fafc] transition-[border-color,box-shadow] duration-200 hover:border-primary/30 hover:shadow-[var(--shadow-1)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring">
              <div className="h-1.5 bg-primary/80" />
              <div className="p-5">
                <div className="flex items-center justify-between text-xs font-medium uppercase tracking-wide text-[#94a3b8]">
                  <span>{course.track_title || course.language}</span>
                  <span className="capitalize text-[#f8fafc]">{course.difficulty}</span>
                </div>
                <h2 className="mt-3 text-lg font-semibold text-[#f8fafc] transition-colors group-hover:text-primary">{course.title}</h2>
                <p className="mt-2 line-clamp-2 text-sm leading-6 text-[#cbd5e1]">{course.description}</p>
                <div className="mt-5 flex items-center justify-between text-xs text-[#94a3b8]">
                  <span>{course.estimated_hours}h · {course.lesson_count} lessons</span>
                  <span className="inline-flex items-center gap-1 font-medium text-primary">View course<ArrowRight className="h-3.5 w-3.5 transition-transform group-hover:translate-x-0.5" /></span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

export default async function CoursesPage({
  searchParams,
}: {
  searchParams: Promise<{ track?: string; difficulty?: string; language?: string; search?: string }>;
}) {
  const params = await searchParams;

  let courses: Course[] = [];
  let error: Error | null = null;

  try {
    courses = await fetchCoursesServer({
      track: params.track,
      difficulty: params.difficulty,
      language: params.language,
      search: params.search,
      page_size: 100,
    });
  } catch (err) {
    error = err instanceof Error ? err : new Error('Failed to load courses');
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <NetworkError onRetry={() => { /* handled by Next.js refresh */ }} />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {courses.length > 0 ? (
        <CoursesCatalog searchParams={params} courses={courses} error={null} />
      ) : (
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <CourseSkeleton key={i} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
