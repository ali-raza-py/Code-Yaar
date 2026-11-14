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

const SERVER_FETCH_TIMEOUT_MS = 20000;
const SERVER_FETCH_MAX_RETRIES = 2;
const SERVER_FETCH_BACKOFF_MS = 500;

async function serverFetch(
  path: string,
  { cache = 'force-cache' }: { cache?: 'force-cache' | 'no-store' } = {}
): Promise<Response> {
  let lastError: unknown = null;
  for (let attempt = 0; attempt <= SERVER_FETCH_MAX_RETRIES; attempt++) {
    const controller = new AbortController();
    let timedOut = false;
    const timeout = setTimeout(() => {
      timedOut = true;
      controller.abort();
    }, SERVER_FETCH_TIMEOUT_MS);
    try {
      const res = await fetch(`${API_BASE}${path}`, {
        cache,
        signal: controller.signal,
        headers: {
          'Accept': 'application/json',
        },
      });
      clearTimeout(timeout);
      // Retry on transient server errors, but not on client errors (4xx)
      if (res.status >= 500 && attempt < SERVER_FETCH_MAX_RETRIES) {
        lastError = res;
        await new Promise((resolve) => setTimeout(resolve, SERVER_FETCH_BACKOFF_MS * (attempt + 1)));
        continue;
      }
      return res;
    } catch (caught) {
      clearTimeout(timeout);
      if (caught instanceof DOMException && caught.name === 'AbortError') {
        lastError = timedOut
          ? new Error(`API ${path} timed out after ${SERVER_FETCH_TIMEOUT_MS / 1000}s`)
          : caught;
      } else {
        lastError = caught;
      }
      if (attempt < SERVER_FETCH_MAX_RETRIES) {
        await new Promise((resolve) => setTimeout(resolve, SERVER_FETCH_BACKOFF_MS * (attempt + 1)));
        continue;
      }
    } finally {
      clearTimeout(timeout);
    }
  }
  throw lastError ?? new Error(`API ${path} failed`);
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
