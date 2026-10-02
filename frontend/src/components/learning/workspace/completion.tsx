'use client';

import Link from 'next/link';

// ─── Chapter Completion Card (spec §26) ─────────────────────────────────────

interface ChapterCompletionProps {
  chapterTitle: string;
  skillsLearned: string[];
  xpEarned: number;
  nextChapterTitle?: string;
  nextChapterUrl?: string;
  courseSlug: string;
}

export function ChapterCompletionCard({
  chapterTitle,
  skillsLearned,
  xpEarned,
  nextChapterTitle,
  nextChapterUrl,
  courseSlug,
}: ChapterCompletionProps) {
  return (
    <div className="rounded-xl border border-green-200 bg-green-50 p-6 text-center">
      <div className="flex justify-center mb-3">
        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-green-500 text-white">
          <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
          </svg>
        </div>
      </div>

      <h2 className="text-lg font-bold text-green-900 mb-1">Chapter Complete</h2>
      <p className="text-sm text-green-700 mb-4">{chapterTitle}</p>

      <div className="mb-4">
        <p className="text-xs font-medium text-green-600 uppercase tracking-wider mb-2">
          You&apos;ve learned:
        </p>
        <div className="flex flex-wrap justify-center gap-2">
          {skillsLearned.map((skill, i) => (
            <span
              key={i}
              className="inline-flex items-center rounded-full bg-white px-2.5 py-0.5 text-xs font-medium text-green-800 border border-green-200"
            >
              {skill}
            </span>
          ))}
        </div>
      </div>

      <p className="text-sm font-bold text-green-800 mb-4">+{xpEarned} XP</p>

      {nextChapterTitle && nextChapterUrl ? (
        <Link
          href={nextChapterUrl}
          className="inline-flex items-center rounded-lg bg-green-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-green-700 transition-colors"
        >
          Continue to {nextChapterTitle}
          <svg className="ml-2 h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
          </svg>
        </Link>
      ) : (
        <Link
          href={`/learn/${courseSlug}/dashboard`}
          className="inline-flex items-center rounded-lg bg-green-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-green-700 transition-colors"
        >
          Back to Dashboard
        </Link>
      )}
    </div>
  );
}

// ─── Course Completion Modal (spec §27) ─────────────────────────────────────

interface CourseCompletionProps {
  courseTitle: string;
  xpEarned: number;
  skillsDemonstrated: string[];
  certificateUrl?: string;
  profileUrl?: string;
}

export function CourseCompletionModal({
  courseTitle,
  xpEarned,
  skillsDemonstrated,
  certificateUrl,
  profileUrl,
}: CourseCompletionProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="mx-4 w-full max-w-md rounded-2xl bg-white p-8 text-center shadow-2xl">
        {/* Trophy */}
        <div className="flex justify-center mb-4">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-yellow-400 to-amber-500 text-white shadow-lg">
            <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 18.75h-9m9 0a3 3 0 013 3h-15a3 3 0 013-3m9 0v-3.375c0-.621-.503-1.125-1.125-1.125h-.871M7.5 18.75v-3.375c0-.621.504-1.125 1.125-1.125h.872m5.007 0H9.497m5.007 0a7.454 7.454 0 01-.982-3.172M9.497 14.25a7.454 7.454 0 00.981-3.172M5.25 4.236c-.982.143-1.954.317-2.916.52A6.003 6.003 0 007.73 9.728M5.25 4.236V4.5c0 2.108.966 3.99 2.48 5.228M5.25 4.236V2.721C7.456 2.41 9.71 2.25 12 2.25c2.291 0 4.545.16 6.75.47v1.516M18.75 4.236c.982.143 1.954.317 2.916.52A6.003 6.003 0 0116.27 9.728M18.75 4.236V4.5c0 2.108-.966 3.99-2.48 5.228m0 0a6.023 6.023 0 01-2.77.852m0 0l-.5.075a7.48 7.48 0 01-1 .067 7.48 7.48 0 01-1-.067l-.5-.075m3 0a6.022 6.022 0 01-2.77-.852" />
            </svg>
          </div>
        </div>

        <h1 className="text-xl font-bold text-gray-900 mb-1">COURSE COMPLETE</h1>
        <p className="text-2xl font-bold text-gray-900 mb-2">{courseTitle}</p>

        <div className="mb-4">
          <p className="text-sm text-gray-600">100% Complete</p>
          <p className="text-lg font-bold text-green-700">{xpEarned.toLocaleString()} XP earned</p>
        </div>

        <div className="mb-6">
          <p className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-2">
            Skills demonstrated
          </p>
          <div className="flex flex-wrap justify-center gap-2">
            {skillsDemonstrated.map((skill, i) => (
              <span
                key={i}
                className="inline-flex items-center rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-700"
              >
                {skill}
              </span>
            ))}
          </div>
        </div>

        <div className="flex flex-col gap-2">
          {certificateUrl && (
            <Link
              href={certificateUrl}
              className="inline-flex items-center justify-center rounded-lg bg-green-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-green-700 transition-colors"
            >
              View Certificate
            </Link>
          )}
          {profileUrl && (
            <Link
              href={profileUrl}
              className="inline-flex items-center justify-center rounded-lg border border-gray-300 px-5 py-2.5 text-sm font-semibold text-gray-700 hover:bg-gray-50 transition-colors"
            >
              View Profile
            </Link>
          )}
        </div>
      </div>
    </div>
  );
}
