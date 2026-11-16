import { CourseSkeleton } from "@/components/learning/course-skeleton";

export default function CoursesLoading() {
  return (
    <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <CourseSkeleton key={i} />
        ))}
      </div>
    </div>
  );
}
