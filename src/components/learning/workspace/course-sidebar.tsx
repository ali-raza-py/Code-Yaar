'use client';

import { Chapter, LessonStatus } from '@/types';

interface CourseSidebarProps {
  chapters: Chapter[];
  currentLessonId: number;
  isOpen: boolean;
  onToggle: () => void;
  courseProgress: number;
  courseTitle: string;
}

function StatusIcon({ status }: { status: LessonStatus }) {
  switch (status) {
    case 'completed':
    case 'mastered':
      return (
        <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-green-500 text-white">
          <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" strokeWidth={3} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
          </svg>
        </span>
      );
    case 'in_progress':
      return (
        <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full border-2 border-green-500 bg-white">
          <span className="h-2 w-2 rounded-full bg-green-500" />
        </span>
      );
    default:
      return (
        <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full border border-gray-300 bg-white" />
      );
  }
}

export default function CourseSidebar({
  chapters,
  currentLessonId,
  isOpen,
  onToggle,
  courseProgress,
  courseTitle,
}: CourseSidebarProps) {
  if (!isOpen) return null;

  return (
    <aside className="flex w-64 shrink-0 flex-col border-r border-gray-200 bg-white overflow-hidden">
      {/* Course Header */}
      <div className="border-b border-gray-200 px-4 py-3">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-gray-900 truncate">{courseTitle}</h2>
          <button
            onClick={onToggle}
            className="rounded p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
            </svg>
          </button>
        </div>
        {/* Progress */}
        <div className="mt-2">
          <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
            <span>Course Progress</span>
            <span className="font-medium text-gray-700">{courseProgress}%</span>
          </div>
          <div className="h-1.5 w-full rounded-full bg-gray-200 overflow-hidden">
            <div
              className="h-full rounded-full bg-green-500 transition-all duration-500"
              style={{ width: `${courseProgress}%` }}
            />
          </div>
        </div>
      </div>

      {/* Chapter/Lesson List */}
      <nav className="flex-1 overflow-y-auto px-2 py-2">
        {chapters.map((chapter) => (
          <div key={chapter.id} className="mb-3">
            {/* Chapter Header */}
            <div className="flex items-center gap-2 px-2 py-1.5">
              <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded text-[10px] font-bold text-gray-400 bg-gray-100">
                {chapter.order}
              </span>
              <span className="text-xs font-semibold text-gray-600 uppercase tracking-wide truncate">
                {chapter.title}
              </span>
              {chapter.progress_percentage === 100 && (
                <svg className="h-3.5 w-3.5 shrink-0 text-green-500 ml-auto" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              )}
            </div>

            {/* Lessons */}
            <ul className="space-y-0.5">
              {chapter.lessons.map((lesson) => {
                const isCurrent = lesson.id === currentLessonId;
                return (
                  <li key={lesson.id}>
                    <a
                      href="#"
                      className={`flex items-center gap-2.5 rounded-md px-2 py-1.5 text-sm transition-colors ${
                        isCurrent
                          ? 'bg-green-50 text-green-800 font-medium'
                          : lesson.progress_status === 'completed' || lesson.progress_status === 'mastered'
                          ? 'text-gray-600 hover:bg-gray-50'
                          : 'text-gray-500 hover:bg-gray-50'
                      }`}
                    >
                      <StatusIcon status={lesson.progress_status} />
                      <span className="truncate">{lesson.title}</span>
                    </a>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </nav>
    </aside>
  );
}
