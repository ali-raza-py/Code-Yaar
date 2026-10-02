'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Course, Chapter, Difficulty } from '@/types';

// ─── Mock data (will be replaced by API) ────────────────────────────────────
const mockCourse: Course = {
  id: 1,
  slug: 'python-foundations',
  title: 'Python Foundations',
  subtitle: 'Build your first real programming foundation.',
  description: 'Learn Python from scratch. Master variables, control flow, functions, and data structures through hands-on exercises.',
  thumbnail: '',
  track: 1,
  track_title: 'Python',
  difficulty: 'beginner',
  language: 'python',
  estimated_hours: 4,
  total_xp: 3900,
  instructor: 'Code Yaar',
  prerequisites: 'None',
  learning_objectives: [
    'Variables and data types',
    'Conditional logic',
    'Loops and iteration',
    'Functions and parameters',
    'Lists and dictionaries',
    'String manipulation',
  ],
  is_free: true,
  lesson_count: 8,
  exercise_count: 46,
  chapter_count: 4,
  enrolled: false,
  progress_percentage: 0,
};

const mockChapters: Chapter[] = [
  {
    id: 1, title: 'Python Basics', slug: 'python-basics', order: 1, xp_reward: 500,
    description: 'Learn the fundamentals of Python programming.',
    progress_percentage: 0,
    lessons: [
      { id: 1, title: 'Hello Python', slug: 'hello-python', content_type: 'text', order: 1, duration_minutes: 10, xp_reward: 50, exercise_count: 1, progress_status: 'not_started' },
      { id: 2, title: 'Variables', slug: 'variables', content_type: 'text', order: 2, duration_minutes: 15, xp_reward: 50, exercise_count: 2, progress_status: 'not_started' },
    ],
  },
  {
    id: 2, title: 'Control Flow', slug: 'control-flow', order: 2, xp_reward: 500,
    description: 'Learn how to make decisions and repeat actions.',
    progress_percentage: 0,
    lessons: [
      { id: 3, title: 'Conditions', slug: 'conditions', content_type: 'text', order: 1, duration_minutes: 15, xp_reward: 50, exercise_count: 1, progress_status: 'not_started' },
      { id: 4, title: 'Loops', slug: 'loops', content_type: 'text', order: 2, duration_minutes: 15, xp_reward: 50, exercise_count: 1, progress_status: 'not_started' },
    ],
  },
  {
    id: 3, title: 'Functions', slug: 'functions', order: 3, xp_reward: 500,
    description: 'Learn to organize your code into reusable blocks.',
    progress_percentage: 0,
    lessons: [
      { id: 5, title: 'Defining Functions', slug: 'defining-functions', content_type: 'text', order: 1, duration_minutes: 15, xp_reward: 50, exercise_count: 1, progress_status: 'not_started' },
    ],
  },
  {
    id: 4, title: 'Data Structures', slug: 'data-structures', order: 4, xp_reward: 500,
    description: 'Master Python lists and dictionaries.',
    progress_percentage: 0,
    lessons: [
      { id: 6, title: 'Lists', slug: 'lists', content_type: 'text', order: 1, duration_minutes: 15, xp_reward: 50, exercise_count: 1, progress_status: 'not_started' },
      { id: 7, title: 'Dictionaries', slug: 'dictionaries', content_type: 'text', order: 2, duration_minutes: 15, xp_reward: 50, exercise_count: 1, progress_status: 'not_started' },
    ],
  },
];

// ─── Components ─────────────────────────────────────────────────────────────

function DifficultyBadge({ difficulty }: { difficulty: Difficulty }) {
  const colors = {
    beginner: 'bg-green-100 text-green-700',
    intermediate: 'bg-yellow-100 text-yellow-700',
    advanced: 'bg-red-100 text-red-700',
  };
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium capitalize ${colors[difficulty]}`}>
      {difficulty}
    </span>
  );
}

function CheckIcon() {
  return (
    <svg className="h-4 w-4 text-green-500" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
    </svg>
  );
}

function ChapterRow({ chapter, index }: { chapter: Chapter; index: number }) {
  const [expanded, setExpanded] = useState(false);
  const num = String(index + 1).padStart(2, '0');

  return (
    <div className="border-b border-gray-200 last:border-0">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex w-full items-center gap-4 px-5 py-4 text-left hover:bg-gray-50 transition-colors"
      >
        <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gray-100 text-sm font-semibold text-gray-500">
          {num}
        </span>
        <div className="flex-1 min-w-0">
          <h3 className="text-sm font-semibold text-gray-900">{chapter.title}</h3>
          <p className="text-xs text-gray-500 mt-0.5">
            {chapter.lessons.length} lessons · {chapter.xp_reward} XP
          </p>
        </div>
        {chapter.progress_percentage > 0 && (
          <div className="hidden sm:flex items-center gap-2">
            <div className="h-1.5 w-16 rounded-full bg-gray-200 overflow-hidden">
              <div className="h-full rounded-full bg-green-500" style={{ width: `${chapter.progress_percentage}%` }} />
            </div>
            <span className="text-xs text-gray-500">{chapter.progress_percentage}%</span>
          </div>
        )}
        <svg
          className={`h-4 w-4 text-gray-400 transition-transform ${expanded ? 'rotate-180' : ''}`}
          fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
        </svg>
      </button>
      {expanded && (
        <div className="px-5 pb-4 pl-17">
          <ul className="space-y-2">
            {chapter.lessons.map((lesson) => (
              <li key={lesson.id} className="flex items-center gap-3 text-sm">
                <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full border border-gray-300 text-[10px] text-gray-400">
                  {lesson.order}
                </span>
                <span className="text-gray-700">{lesson.title}</span>
                <span className="ml-auto text-xs text-gray-400">{lesson.duration_minutes}m</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

// ─── Page ───────────────────────────────────────────────────────────────────

export default function CourseLandingPage() {
  const course = mockCourse;
  const chapters = mockChapters;

  return (
    <div className="min-h-screen bg-white">
      {/* ── Hero / Course Header ─────────────────────────────────── */}
      <section className="border-b border-gray-200 bg-gradient-to-b from-gray-50 to-white">
        <div className="mx-auto max-w-4xl px-4 py-10 sm:px-6 lg:px-8">
          {/* Breadcrumb */}
          <nav className="mb-6 flex items-center gap-2 text-sm text-gray-500">
            <Link href="/learn" className="hover:text-gray-900">Courses</Link>
            <span>/</span>
            <span className="text-gray-900">{course.track_title}</span>
          </nav>

          {/* Title area */}
          <div className="mb-4">
            <span className="text-xs font-semibold uppercase tracking-wider text-gray-500">
              {course.track_title}
            </span>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 sm:text-4xl">
            {course.title}
          </h1>
          <p className="mt-3 text-lg text-gray-600 max-w-2xl">
            {course.description}
          </p>

          {/* CTAs */}
          <div className="mt-6 flex flex-wrap items-center gap-3">
            <Link
              href={`/learn/${course.slug}`}
              className="inline-flex items-center rounded-lg bg-green-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-green-700 transition-colors"
            >
              Start Course
            </Link>
            <button className="inline-flex items-center rounded-lg border border-gray-300 px-5 py-2.5 text-sm font-semibold text-gray-700 hover:bg-gray-50 transition-colors">
              Preview
            </button>
          </div>

          {/* Meta */}
          <div className="mt-6 flex flex-wrap items-center gap-4 text-sm text-gray-600">
            <DifficultyBadge difficulty={course.difficulty} />
            <span>{course.estimated_hours} hours</span>
            <span>{course.chapter_count} Chapters</span>
            <span>{course.exercise_count} Exercises</span>
            <span>{course.total_xp.toLocaleString()} XP</span>
          </div>
        </div>
      </section>

      {/* ── What You'll Learn ────────────────────────────────────── */}
      <section className="border-b border-gray-200">
        <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">What you&apos;ll learn</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {course.learning_objectives.map((obj, i) => (
              <div key={i} className="flex items-start gap-2.5">
                <CheckIcon />
                <span className="text-sm text-gray-700">{obj}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Course Roadmap ───────────────────────────────────────── */}
      <section className="border-b border-gray-200">
        <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Course roadmap</h2>
          <div className="rounded-lg border border-gray-200 bg-white overflow-hidden">
            {chapters.map((chapter, index) => (
              <ChapterRow key={chapter.id} chapter={chapter} index={index} />
            ))}
          </div>
        </div>
      </section>

      {/* ── Course Details ───────────────────────────────────────── */}
      <section className="border-b border-gray-200">
        <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Course details</h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            <div>
              <dt className="text-xs font-medium text-gray-500 uppercase tracking-wider">Prerequisites</dt>
              <dd className="mt-1 text-sm text-gray-900">{course.prerequisites}</dd>
            </div>
            <div>
              <dt className="text-xs font-medium text-gray-500 uppercase tracking-wider">Language</dt>
              <dd className="mt-1 text-sm text-gray-900 capitalize">{course.language}</dd>
            </div>
            <div>
              <dt className="text-xs font-medium text-gray-500 uppercase tracking-wider">Instructor</dt>
              <dd className="mt-1 text-sm text-gray-900">{course.instructor}</dd>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
