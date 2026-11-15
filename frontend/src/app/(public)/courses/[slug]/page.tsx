import { fetchCourseDetailServer } from '@/lib/server-api';
import { CourseDetailClient } from '@/components/learning/course-detail-client';
import { NotFoundError, ServerError } from '@/components/learning/workspace/error-states';

export default async function CourseLandingPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;

  let course: any = null;
  let serverError: Error | null = null;
  let notFound = false;

  try {
    course = await fetchCourseDetailServer(slug);
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    const status = (err as any)?.status;
    if (status === 404 || message.startsWith('404')) {
      notFound = true;
    } else {
      serverError = err instanceof Error ? err : new Error('Failed to load course');
    }
  }

  if (notFound || !course) {
    return <NotFoundError resource="Course" />;
  }

  if (serverError) {
    return <ServerError />;
  }

  return <CourseDetailClient course={course} />;
}
