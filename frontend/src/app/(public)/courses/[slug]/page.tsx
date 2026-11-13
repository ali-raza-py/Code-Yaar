import { fetchCourseDetailServer } from '@/lib/server-api';
import { CourseDetailClient } from '@/components/learning/course-detail-client';
import { NotFoundError } from '@/components/learning/workspace/error-states';
import { CourseSkeleton } from '@/components/learning/course-skeleton';

export default async function CourseLandingPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;

  let course: any = null;
  let error: Error | null = null;

  try {
    course = await fetchCourseDetailServer(slug);
  } catch (err) {
    error = err instanceof Error ? err : new Error('Failed to load course');
  }

  if (error || !course) {
    return <NotFoundError resource="Course" />;
  }

  return <CourseDetailClient course={course} />;
}
