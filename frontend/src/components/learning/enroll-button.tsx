'use client';

import { useState } from 'react';
import { useAuth } from '@/hooks/use-auth';
import { courses as coursesApi } from '@/lib/api';
import type { Course } from '@/types';
import Link from 'next/link';

interface EnrollButtonProps {
  course: Course;
  user: { id: number; username: string } | null;
}

export function EnrollButton({ course, user }: EnrollButtonProps) {
  const [enrolling, setEnrolling] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);

  const handleStart = async () => {
    setEnrolling(true);
    setNotice(null);
    try {
      await coursesApi.enroll(course.slug);
    } catch (reason) {
      setNotice(reason instanceof Error ? reason.message : 'Enrollment failed. Please try again.');
    } finally {
      setEnrolling(false);
    }
  };

  if (!user) {
    return (
      <Link
        href={`/sign-up?next=${encodeURIComponent(`/courses/${course.slug}`)}`}
        className="inline-flex items-center rounded-lg bg-cta px-5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-cta-hover transition-colors"
      >
        Sign up to start
      </Link>
    );
  }

  return (
    <>
      {course.enrolled ? (
        <Link
          href={`/learn/${course.slug}`}
          className="inline-flex items-center rounded-lg bg-cta px-5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-cta-hover transition-colors"
        >
          {(course.progress_percentage ?? 0) > 0 ? 'Continue Course' : 'Start Course'}
        </Link>
      ) : (
        <>
          <button
            onClick={handleStart}
            disabled={enrolling}
            className="inline-flex items-center rounded-lg bg-cta px-5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-cta-hover transition-colors disabled:opacity-50"
          >
            {enrolling ? 'Enrolling…' : 'Enroll & Start'}
          </button>
          {notice && <p role="alert" className="mt-3 text-sm text-danger">{notice}</p>}
        </>
      )}
    </>
  );
}
