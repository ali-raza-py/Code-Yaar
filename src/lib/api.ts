/**
 * API client for Code-Yaar learning platform.
 * Connects the Next.js frontend to the Django REST API.
 *
 * All progress, XP, and exercise state is managed server-side.
 * The frontend only requests actions; Django validates and returns authoritative state.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

// ─── Auth ───────────────────────────────────────────────────────────────────

function getToken(): string | null {
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
    const error = await res.json().catch(() => ({ detail: 'Network error' }));
    throw new ApiError(res.status, error.detail || error.error || 'Request failed');
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

// ─── Auth Endpoints ─────────────────────────────────────────────────────────

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

  getProfile: () => request('/auth/profile/'),
  updateProfile: (data: Record<string, unknown>) =>
    request('/auth/profile/', { method: 'PATCH', body: JSON.stringify(data) }),
};

// ─── Course Endpoints ───────────────────────────────────────────────────────

export const courses = {
  list: (params?: { track?: string; difficulty?: string; language?: string }) => {
    const query = new URLSearchParams();
    if (params?.track) query.set('track', params.track);
    if (params?.difficulty) query.set('difficulty', params.difficulty);
    if (params?.language) query.set('language', params.language);
    const qs = query.toString();
    return request(`/courses/${qs ? `?${qs}` : ''}`);
  },

  detail: (slug: string) =>
    request(`/courses/${slug}/`),

  enroll: (slug: string) =>
    request(`/courses/${slug}/enroll/`, { method: 'POST' }),

  chapters: (courseSlug: string) =>
    request(`/courses/${courseSlug}/chapters/`),

  chapterDetail: (courseSlug: string, chapterSlug: string) =>
    request(`/courses/${courseSlug}/chapters/${chapterSlug}/`),

  lessons: (courseSlug: string) =>
    request(`/courses/${courseSlug}/lessons/`),

  lessonDetail: (courseSlug: string, lessonSlug: string) =>
    request(`/courses/${courseSlug}/lessons/${lessonSlug}/`),
};

// ─── Exercise Endpoints ─────────────────────────────────────────────────────

export const exercises = {
  list: (lessonId: number) =>
    request(`/lessons/${lessonId}/exercises/`),

  detail: (exerciseId: number) =>
    request(`/exercises/${exerciseId}/`),

  run: (exerciseId: number, code: string) =>
    request<{ status: string; output: string; error: string; attempt_id: number }>(
      `/exercises/${exerciseId}/run/`,
      { method: 'POST', body: JSON.stringify({ code }) }
    ),

  submit: (exerciseId: number, data: { code?: string; selected_answer?: string | string[]; time_spent_seconds?: number }) =>
    request<{
      status: string;
      feedback: string;
      output: string;
      error: string;
      test_results: Array<{ test: number; status: string; message: string }>;
      xp_earned: number;
      correct_answer?: unknown;
      attempt_id: number;
    }>(`/exercises/${exerciseId}/submit/`, {
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
    list: () => request('/enrollments/'),
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

export const tracks = {
  list: () => request('/tracks/'),
  detail: (slug: string) => request(`/tracks/${slug}/`),
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
  list: (params?: { track?: string; difficulty?: string }) => {
    const query = new URLSearchParams();
    if (params?.track) query.set('track', params.track);
    if (params?.difficulty) query.set('difficulty', params.difficulty);
    const qs = query.toString();
    return request(`/projects/${qs ? `?${qs}` : ''}`);
  },
  detail: (slug: string) => request(`/projects/${slug}/`),
};

export const challenges = {
  list: (params?: { topic?: string; difficulty?: string }) => {
    const query = new URLSearchParams();
    if (params?.topic) query.set('topic', params.topic);
    if (params?.difficulty) query.set('difficulty', params.difficulty);
    const qs = query.toString();
    return request(`/challenges/${qs ? `?${qs}` : ''}`);
  },
  detail: (slug: string) => request(`/challenges/${slug}/`),
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
