// Server-side API client for Next.js Server Components.
// Uses native `fetch` (available in Next.js server runtime) to call the Django
// API directly from the server. No browser-only features (localStorage, cookies,
// credentials) are used — these endpoints are public read-only endpoints that
// do not require authentication.
//
// Responses are cached by Next.js's fetch cache based on the `cache` option:
// - `force-cache` (default): cached until next revalidation or tag purge
// - `no-store`: fresh on every request
//
// Public course data changes only when an admin publishes/edits, so a short
// stale-while-revalidate window is appropriate.

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

async function serverFetch(path: string, { cache = 'force-cache' }: { cache?: 'force-cache' | 'no-store' } = {}): Promise<Response> {
  const res = await fetch(`${API_BASE}${path}`, {
    cache,
    headers: {
      'Accept': 'application/json',
    },
  });
  if (!res.ok) {
    throw new Error(`API ${path} returned ${res.status}`);
  }
  return res;
}

export async function fetchCoursesServer(params?: {
  track?: string;
  difficulty?: string;
  language?: string;
  search?: string;
  page_size?: number;
}): Promise<any[]> {
  const query = new URLSearchParams();
  if (params?.track) query.set('track', params.track);
  if (params?.difficulty) query.set('difficulty', params.difficulty);
  if (params?.language) query.set('language', params.language);
  if (params?.search) query.set('search', params.search);
  query.set('page_size', String(params?.page_size ?? 100));
  const qs = query.toString();
  const res = await serverFetch(`/courses/${qs ? `?${qs}` : ''}`);
  const data = await res.json();
  return Array.isArray(data) ? data : (data.results || []);
}

export async function fetchCourseDetailServer(slug: string): Promise<any> {
  const res = await serverFetch(`/courses/${encodeURIComponent(slug)}/`);
  return res.json();
}

export async function fetchChaptersServer(courseSlug: string): Promise<any[]> {
  const res = await serverFetch(`/courses/${encodeURIComponent(courseSlug)}/chapters/`);
  const data = await res.json();
  return Array.isArray(data) ? data : (data.results || []);
}

export async function fetchLessonsServer(courseSlug: string): Promise<any[]> {
  const res = await serverFetch(`/courses/${encodeURIComponent(courseSlug)}/lessons/`);
  const data = await res.json();
  return Array.isArray(data) ? data : (data.results || []);
}

export async function fetchLessonDetailServer(courseSlug: string, lessonSlug: string): Promise<any> {
  const res = await serverFetch(`/courses/${encodeURIComponent(courseSlug)}/lessons/${encodeURIComponent(lessonSlug)}/`);
  return res.json();
}

export async function fetchExercisesServer(lessonId: number): Promise<any[]> {
  const res = await serverFetch(`/lessons/${lessonId}/exercises/`);
  const data = await res.json();
  return Array.isArray(data) ? data : (data.results || []);
}

export async function fetchLeaderboardServer(params?: { limit?: number; offset?: number }): Promise<any> {
  const query = new URLSearchParams();
  if (params?.limit) query.set('limit', String(params.limit));
  if (params?.offset) query.set('offset', String(params.offset));
  const qs = query.toString();
  const res = await serverFetch(`/leaderboard/${qs ? `?${qs}` : ''}`);
  return res.json();
}

export async function fetchTracksServer(params?: { category?: string; search?: string }): Promise<any[]> {
  const query = new URLSearchParams();
  if (params?.category) query.set('category', params.category);
  if (params?.search) query.set('search', params.search);
  const qs = query.toString();
  const res = await serverFetch(`/tracks/${qs ? `?${qs}` : ''}`);
  const data = await res.json();
  return Array.isArray(data) ? data : (data.results || []);
}

export async function fetchAnnouncementsServer(params?: { category?: string }): Promise<any[]> {
  const query = new URLSearchParams();
  if (params?.category) query.set('category', params.category);
  const qs = query.toString();
  const res = await serverFetch(`/announcements/${qs ? `?${qs}` : ''}`);
  const data = await res.json();
  return Array.isArray(data) ? data : (data.results || []);
}
