'use client';

import Link from 'next/link';

// ─── Mock data (will be replaced by API) ────────────────────────────────────
const courseData = {
  title: 'Python Foundations',
  slug: 'python-foundations',
  progress: 35,
  totalLessons: 8,
  completedLessons: 3,
  totalExercises: 46,
  completedExercises: 16,
  totalChapters: 4,
  completedChapters: 1,
  xpEarned: 1350,
  totalXp: 3900,
  streak: 5,
  resumeLesson: {
    title: 'Loops',
    chapter: 'Control Flow',
    chapterNum: 2,
    lessonNum: 4,
    slug: 'loops',
  },
  chapters: [
    { id: 1, title: 'Python Basics', progress: 100, lessons: 2, completed: 2 },
    { id: 2, title: 'Control Flow', progress: 50, lessons: 2, completed: 1 },
    { id: 3, title: 'Functions', progress: 0, lessons: 1, completed: 0 },
    { id: 4, title: 'Data Structures', progress: 0, lessons: 2, completed: 0 },
  ],
  resources: [
    { id: 1, title: 'Python Cheat Sheet', type: 'cheat_sheet' },
    { id: 2, title: 'Course Slides', type: 'slides' },
  ],
  recentActivity: [
    { id: 1, text: 'Completed lesson: Conditions', time: '2 hours ago' },
    { id: 2, text: 'Earned 100 XP: Print Numbers', time: '2 hours ago' },
    { id: 3, text: 'Completed lesson: Variables', time: '1 day ago' },
  ],
};

export default function CourseDashboardPage() {
  const c = courseData;

  return (
    <div className="min-h-screen bg-gray-50 p-4 sm:p-6 lg:p-8">
      <div className="mx-auto max-w-5xl">
        {/* Header */}
        <div className="mb-6">
          <Link href="/learn" className="text-sm text-gray-500 hover:text-gray-900 mb-2 inline-block">
            ← Back to Courses
          </Link>
          <h1 className="text-2xl font-bold text-gray-900">{c.title}</h1>
          <div className="mt-2 flex items-center gap-4">
            <div className="flex-1 max-w-md">
              <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
                <span>Course Progress</span>
                <span className="font-semibold text-gray-700">{c.progress}%</span>
              </div>
              <div className="h-2 w-full rounded-full bg-gray-200 overflow-hidden">
                <div
                  className="h-full rounded-full bg-green-500 transition-all"
                  style={{ width: `${c.progress}%` }}
                />
              </div>
            </div>
            <span className="text-sm font-medium text-gray-600">
              {c.xpEarned.toLocaleString()} / {c.totalXp.toLocaleString()} XP
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Column */}
          <div className="lg:col-span-2 space-y-6">
            {/* Continue Learning */}
            <div className="rounded-xl border border-gray-200 bg-gradient-to-br from-gray-900 to-gray-800 p-6 text-white">
              <p className="text-xs font-medium uppercase tracking-wider text-gray-400 mb-1">
                Continue Learning
              </p>
              <h2 className="text-xl font-bold mb-1">
                Chapter {c.resumeLesson.chapterNum}: {c.resumeLesson.chapter}
              </h2>
              <p className="text-sm text-gray-300 mb-4">
                Lesson {c.resumeLesson.lessonNum} — &quot;{c.resumeLesson.title}&quot;
              </p>
              <Link
                href={`/learn/${c.slug}`}
                className="inline-flex items-center rounded-lg bg-green-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-green-700 transition-colors"
              >
                Continue
                <svg className="ml-2 h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
                </svg>
              </Link>
            </div>

            {/* Course Map */}
            <div className="rounded-xl border border-gray-200 bg-white p-6">
              <h3 className="text-base font-semibold text-gray-900 mb-4">Course Map</h3>
              <div className="space-y-3">
                {c.chapters.map((ch) => (
                  <div key={ch.id} className="flex items-center gap-4">
                    <span className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-sm font-bold ${
                      ch.progress === 100
                        ? 'bg-green-100 text-green-700'
                        : ch.progress > 0
                        ? 'bg-blue-100 text-blue-700'
                        : 'bg-gray-100 text-gray-400'
                    }`}>
                      {ch.progress === 100 ? (
                        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                        </svg>
                      ) : (
                        ch.id
                      )}
                    </span>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm font-medium text-gray-900 truncate">{ch.title}</span>
                        <span className="text-xs text-gray-500">{ch.completed}/{ch.lessons} lessons</span>
                      </div>
                      <div className="h-1.5 w-full rounded-full bg-gray-100 overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all ${
                            ch.progress === 100 ? 'bg-green-500' : ch.progress > 0 ? 'bg-blue-500' : 'bg-gray-200'
                          }`}
                          style={{ width: `${Math.max(ch.progress, 2)}%` }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Practice */}
            <div className="rounded-xl border border-gray-200 bg-white p-6">
              <h3 className="text-base font-semibold text-gray-900 mb-2">Practice</h3>
              <p className="text-sm text-gray-600 mb-4">
                Strengthen what you&apos;ve learned with recommended exercises.
              </p>
              <div className="grid grid-cols-2 gap-3">
                <Link
                  href={`/learn/${c.slug}`}
                  className="rounded-lg border border-gray-200 p-3 text-center hover:bg-gray-50 transition-colors"
                >
                  <p className="text-sm font-medium text-gray-900">Chapter Practice</p>
                  <p className="text-xs text-gray-500 mt-1">Control Flow</p>
                </Link>
                <Link
                  href="/challenges"
                  className="rounded-lg border border-gray-200 p-3 text-center hover:bg-gray-50 transition-colors"
                >
                  <p className="text-sm font-medium text-gray-900">Challenges</p>
                  <p className="text-xs text-gray-500 mt-1">100+ available</p>
                </Link>
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Stats */}
            <div className="rounded-xl border border-gray-200 bg-white p-5">
              <h3 className="text-sm font-semibold text-gray-900 mb-3">Your Progress</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Lessons</span>
                  <span className="text-sm font-medium text-gray-900">{c.completedLessons}/{c.totalLessons}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Exercises</span>
                  <span className="text-sm font-medium text-gray-900">{c.completedExercises}/{c.totalExercises}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Chapters</span>
                  <span className="text-sm font-medium text-gray-900">{c.completedChapters}/{c.totalChapters}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">XP Earned</span>
                  <span className="text-sm font-medium text-green-700">{c.xpEarned.toLocaleString()}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Streak</span>
                  <span className="text-sm font-medium text-orange-600">{c.streak} days</span>
                </div>
              </div>
            </div>

            {/* Resources */}
            <div className="rounded-xl border border-gray-200 bg-white p-5">
              <h3 className="text-sm font-semibold text-gray-900 mb-3">Resources</h3>
              <div className="space-y-2">
                {c.resources.map((r) => (
                  <a
                    key={r.id}
                    href="#"
                    className="flex items-center gap-2 rounded-lg p-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                  >
                    <svg className="h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
                    </svg>
                    {r.title}
                  </a>
                ))}
              </div>
            </div>

            {/* Recent Activity */}
            <div className="rounded-xl border border-gray-200 bg-white p-5">
              <h3 className="text-sm font-semibold text-gray-900 mb-3">Recent Activity</h3>
              <div className="space-y-3">
                {c.recentActivity.map((a) => (
                  <div key={a.id} className="flex items-start gap-2">
                    <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-green-500" />
                    <div>
                      <p className="text-xs text-gray-700">{a.text}</p>
                      <p className="text-[10px] text-gray-400">{a.time}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
