import type { Challenge, Chapter, Course, Enrollment, ExerciseDetail, ExerciseResult, LessonDetail, Project } from "@/types";

/**
 * API client for Code-Yaar learning platform.
 * Connects the Next.js frontend to the Django REST API.
 *
 * All progress, XP, and exercise state is managed server-side.
 * The frontend only requests actions; Django validates and returns authoritative state.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

// ─── Auth ───────────────────────────────────────────────────────────────────

export function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('auth_token');
}

export function setToken(token: string) {
  if (typeof window !== 'undefined') {
    localStorage.setItem('auth_token', token);
  }
}

export function clearToken() {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('auth_token');
  }
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };
  if (token) {
    headers['Authorization'] = `Token ${token}`;
  }

  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    const responseText = await res.text();
    let message = `Request failed (${res.status})`;

    if (responseText) {
      try {
        const error = JSON.parse(responseText) as { detail?: string; error?: string };
        message = error.detail || error.error || message;
      } catch {
        message = responseText;
      }
    }

    throw new ApiError(res.status, message);
  }

  // Handle 204 No Content
  if (res.status === 204) return {} as T;

  return res.json();
}

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
    this.name = 'ApiError';
  }
}

// DRF paginates list endpoints globally (PageNumberPagination): they return
// { count, next, previous, results } rather than a bare array. Normalize so
// callers always get a plain array.
type Paginated<T> = T[] | { results: T[]; count: number; next: string | null; previous: string | null };

function unwrapList<T>(data: Paginated<T>): T[] {
  return Array.isArray(data) ? data : data.results;
}

// ─── Auth Endpoints ─────────────────────────────────────────────────────────

export interface AuthProfileData {
  user: { id: number; username: string; email: string; first_name: string; last_name: string };
  avatar: string;
  bio: string;
  role: string;
  xp_points: number;
  streak_days: number;
  level: number;
  last_active_at: string | null;
}

export const auth = {
  register: (data: { username: string; email: string; password: string; first_name?: string; last_name?: string }) =>
    request<{ token: string; user: { id: number; username: string; email: string } }>('/auth/register/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  login: (data: { username: string; password: string }) =>
    request<{ token: string; user: { id: number; username: string; email: string } }>('/auth/login/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  getProfile: () => request<AuthProfileData>('/auth/profile/'),
  updateProfile: (data: Record<string, unknown>) =>
    request<AuthProfileData>('/auth/profile/', { method: 'PATCH', body: JSON.stringify(data) }),
};

// ─── Course Endpoints ───────────────────────────────────────────────────────

export const courses = {
  list: async (params?: { track?: string; difficulty?: string; language?: string; search?: string }): Promise<Course[]> => {
    const query = new URLSearchParams();
    if (params?.track) query.set('track', params.track);
    if (params?.difficulty) query.set('difficulty', params.difficulty);
    if (params?.language) query.set('language', params.language);
    if (params?.search) query.set('search', params.search);
    const qs = query.toString();
    const data = await request<Paginated<Course>>(`/courses/${qs ? `?${qs}` : ''}`);
    return unwrapList(data);
  },

  detail: (slug: string) =>
    request<Course>(`/courses/${slug}/`),

  enroll: (slug: string) =>
    request<Enrollment>(`/courses/${slug}/enroll/`, { method: 'POST' }),

  chapters: async (courseSlug: string): Promise<Chapter[]> => {
    const data = await request<Paginated<Chapter>>(`/courses/${courseSlug}/chapters/`);
    return unwrapList(data);
  },

  lessons: (courseSlug: string) =>
    request<Paginated<LessonDetail>>(`/courses/${courseSlug}/lessons/`),

  lessonDetail: (courseSlug: string, lessonSlug: string) =>
    request<LessonDetail>(`/courses/${courseSlug}/lessons/${lessonSlug}/`),

  // Mark a lesson complete. Server-side rule: lessons with exercises only
  // complete when every active exercise is solved; reading lessons are
  // self-reported. Returns the honest status, never a fabricated one.
  completeLesson: (lessonId: number) =>
    request<{
      status: string;
      xp_awarded: number;
      exercises_remaining: number;
      message: string;
    }>(`/lessons/${lessonId}/complete/`, { method: 'POST' }),
};

// ─── Sandbox Snippet Execution (lesson "Run" buttons) ────────────────────

export const sandbox = {
  execute: (code: string, language: 'python' = 'python') =>
    request<{ status: string; output: string; error: string; execution_time_ms: number }>(
      '/execute/',
      { method: 'POST', body: JSON.stringify({ code, language }) }
    ),
};

// ─── Exercise Endpoints ─────────────────────────────────────────────────────

export const exercises = {
  list: (lessonId: number) =>
    request<Paginated<unknown>>(`/lessons/${lessonId}/exercises/`),

  detail: (exerciseId: number) =>
    request<ExerciseDetail>(`/exercises/${exerciseId}/`),

  run: (exerciseId: number, code: string) =>
    request<{ status: string; output: string; error: string; attempt_id: number }>(
      `/exercises/${exerciseId}/run/`,
      { method: 'POST', body: JSON.stringify({ code }) }
    ),

  submit: (exerciseId: number, data: { code?: string; selected_answer?: string | string[]; time_spent_seconds?: number }) =>
    request<ExerciseResult>(`/exercises/${exerciseId}/submit/`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  hint: (exerciseId: number) =>
    request<{ hint: string | null; order: number; reveals_solution: boolean; xp_penalty: number; message?: string }>(
      `/exercises/${exerciseId}/hint/`
    ),
};

// ─── Progress Endpoints ─────────────────────────────────────────────────────

export const progress = {
  lessonProgress: {
    list: () => request('/lesson-progress/'),
    update: (id: number, data: { status?: string; time_spent_seconds?: number }) =>
      request(`/lesson-progress/${id}/`, { method: 'PATCH', body: JSON.stringify(data) }),
  },

  attempts: {
    list: () => request('/attempts/'),
  },

  enrollments: {
    list: async (): Promise<Enrollment[]> => {
      const data = await request<Paginated<Enrollment>>('/enrollments/');
      return unwrapList(data);
    },
  },

  xp: {
    list: () => request('/xp/'),
  },

  achievements: {
    list: () => request('/achievements/'),
    myAchievements: () => request('/my-achievements/'),
  },
};

// ─── Tracks ─────────────────────────────────────────────────────────────────

export interface TrackSummary {
  id: number;
  slug: string;
  title: string;
  description: string;
  icon: string;
  difficulty: string;
  estimated_hours: number;
  course_count: number;
}

export const tracks = {
  list: async (): Promise<TrackSummary[]> => {
    const data = await request<Paginated<TrackSummary>>('/tracks/');
    return unwrapList(data);
  },
  detail: (slug: string) => request<TrackSummary>(`/tracks/${slug}/`),
};

// ─── Leaderboard ────────────────────────────────────────────────────────────

export const leaderboard = {
  list: (params?: { limit?: number; offset?: number }) => {
    const query = new URLSearchParams();
    if (params?.limit) query.set('limit', String(params.limit));
    if (params?.offset) query.set('offset', String(params.offset));
    const qs = query.toString();
    return request<{ total: number; limit: number; offset: number; entries: LeaderboardEntry[] }>(
      `/leaderboard/${qs ? `?${qs}` : ''}`
    );
  },
};

export interface LeaderboardEntry {
  rank: number;
  user_id: number;
  username: string;
  xp_points: number;
  level: number;
  streak_days: number;
  courses_completed: number;
  challenges_solved: number;
}

// ─── Projects & Challenges ──────────────────────────────────────────────────

export const projects = {
  list: async (params?: { track?: string; difficulty?: string }): Promise<Project[]> => {
    const query = new URLSearchParams();
    if (params?.track) query.set('track', params.track);
    if (params?.difficulty) query.set('difficulty', params.difficulty);
    const qs = query.toString();
    const data = await request<Paginated<Project>>(`/projects/${qs ? `?${qs}` : ''}`);
    return unwrapList(data);
  },
  detail: (slug: string) => request<Project>(`/projects/${slug}/`),
};

export const challenges = {
  list: async (params?: { topic?: string; difficulty?: string }): Promise<Challenge[]> => {
    const query = new URLSearchParams();
    if (params?.topic) query.set('topic', params.topic);
    if (params?.difficulty) query.set('difficulty', params.difficulty);
    const qs = query.toString();
    const data = await request<Paginated<Challenge>>(
      `/challenges/${qs ? `?${qs}` : ''}`
    );
    return unwrapList(data);
  },
  detail: (slug: string) => request<Challenge>(`/challenges/${slug}/`),
};

// ─── Profile Stats ────────────────────────────────────────────────────────

export const profileStats = {
  get: () => request<ProfileStatsData>('/profile/stats/'),
};

export interface ProfileStatsData {
  user: {
    id: number;
    username: string;
    email: string;
    first_name: string;
    last_name: string;
    date_joined: string;
  };
  profile: {
    avatar: string;
    bio: string;
    role: string;
    xp_points: number;
    streak_days: number;
    level: number;
    last_active_at: string | null;
  };
  stats: {
    total_enrollments: number;
    active_enrollments: number;
    completed_courses: number;
    total_attempts: number;
    correct_attempts: number;
    unique_exercises_solved: number;
    lessons_completed: number;
    lessons_in_progress: number;
    achievements_earned: number;
    total_achievements: number;
  };
  xp_breakdown: Record<string, number>;
  xp_history: Array<{
    id: number;
    amount: number;
    action: string;
    description: string;
    created_at: string;
  }>;
  skills: Array<{
    id: number;
    name: string;
    category: string;
    proficiency: number;
    icon: string;
  }>;
  certifications: Array<{
    id: number;
    title: string;
    track_title: string;
    credential_id: string;
    earned_at: string;
  }>;
  active_enrollments: Array<{
    id: number;
    course_slug: string;
    course_title: string;
    track_title: string;
    progress_percentage: number;
    enrolled_at: string;
  }>;
}

// ─── Certificates ───────────────────────────────────────────────────────────

export interface CertificateSummary {
  id: number;
  public_id: string;
  credential_id: string;
  student_name: string;
  course_title: string;
  course: number;
  course_slug: string;
  issued_at: string;
  completion_verified_at: string | null;
  final_score: number | null;
  status: 'active' | 'revoked' | 'superseded';
  is_valid: boolean;
  verification_url: string;
  pdf_url: string;
}

export interface CertificateRequirement {
  key: string;
  label: string;
  met: boolean;
  detail: string;
}

export interface CertificateEligibility {
  eligible: boolean;
  final_score: number | null;
  requirements: CertificateRequirement[];
  lessons_required: boolean;
  lessons_completed: number;
  lessons_total: number;
  assessment_required: boolean;
  assessment_items: number;
  assessment_passed: number;
}

export interface PublicVerification {
  valid: boolean;
  found: boolean;
  public_id?: string;
  credential_id?: string;
  student_name?: string;
  course_title?: string;
  issued_at?: string;
  completion_verified_at?: string | null;
  status?: string;
  revoked?: boolean;
  superseded?: boolean;
  detail?: string;
}

export const certificates = {
  myCertificates: async (): Promise<CertificateSummary[]> => {
    const data = await request<Paginated<CertificateSummary>>('/me/certificates/');
    return unwrapList(data);
  },

  eligibility: (courseSlug: string) =>
    request<CertificateEligibility>(`/courses/${courseSlug}/certificate/eligibility/`),

  issue: (courseSlug: string) =>
    request<CertificateSummary>(`/courses/${courseSlug}/certificate/issue/`, { method: 'POST' }),

  // Public, unauthenticated verification endpoint.
  verify: (publicId: string) =>
    request<PublicVerification>(`/certificates/verify/${encodeURIComponent(publicId)}/`),

  // Download is owner-restricted and token-authenticated, so stream the PDF
  // through fetch with the Authorization header and hand the blob to the
  // browser rather than navigating to the URL directly.
  download: async (publicId: string): Promise<void> => {
    const token = getToken();
    const res = await fetch(`${API_BASE}/certificates/${encodeURIComponent(publicId)}/download/`, {
      headers: token ? { Authorization: `Token ${token}` } : {},
    });
    if (!res.ok) {
      throw new ApiError(res.status, `Download failed (${res.status})`);
    }
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `code-yaar-${publicId}.pdf`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  },
};

// ─── Settings ─────────────────────────────────────────────────────────────

export const settings = {
  getAccount: () => request<SettingsAccountData>('/settings/account/'),
  updateAccount: (data: {
    username?: string;
    email?: string;
    first_name?: string;
    last_name?: string;
    current_password?: string;
    new_password?: string;
  }) => request<SettingsAccountData & { token?: string }>('/settings/account/', {
    method: 'PATCH',
    body: JSON.stringify(data),
  }),
  updateProfile: (data: {
    avatar?: string;
    bio?: string;
    role?: string;
  }) => request('/settings/profile/', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
};

export interface SettingsAccountData {
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  has_password: boolean;
}
