import type { Challenge, Chapter, Course, Enrollment, ExerciseDetail, ExerciseResult, LessonDetail, Project } from "@/types";

/**
 * API client for Code-Yaar learning platform.
 * Connects the Next.js frontend to the Django REST API.
 *
 * Auth model:
 * - The access token lives in memory only, never in storage, so a script
 *   injected into the page cannot lift a durable credential out of it.
 * - The refresh token is an HttpOnly cookie issued by the API. JavaScript
 *   cannot read it; `credentials: 'include'` sends it to `/auth/*` endpoints,
 *   which additionally require a CSRF double-submit header.
 * - A single boolean storage hint records "this browser had a session" so a
 *   first-time visitor does not pay for two pointless requests on load.
 *
 * All progress, XP, and exercise state is managed server-side.
 * The frontend only requests actions; Django validates and returns authoritative state.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

const SESSION_HINT_KEY = 'cy_has_session';

/** Endpoints that must never trigger an access-token refresh from their own 401. */
const NO_REFRESH = new Set([
  '/auth/csrf/',
  '/auth/login/',
  '/auth/register/',
  '/auth/logout/',
  '/auth/token/refresh/',
  '/auth/password-reset/',
  '/auth/password-reset/confirm/',
  '/auth/verify-email/',
]);

// ─── Token storage (memory only) ────────────────────────────────────────────

let accessToken: string | null = null;

export function getAccessToken(): string | null {
  return accessToken;
}

export function setAccessToken(token: string) {
  accessToken = token;
}

export function clearAccessToken() {
  accessToken = null;
}

// Legacy aliases: several modules still import these names.
export const getToken = getAccessToken;
export const setToken = setAccessToken;

/** True when this browser previously signed in (survives a reload). */
export function hasSessionHint(): boolean {
  if (typeof window === 'undefined') return false;
  return window.localStorage.getItem(SESSION_HINT_KEY) === '1';
}

function markSessionHint() {
  if (typeof window === 'undefined') return;
  window.localStorage.setItem(SESSION_HINT_KEY, '1');
}

function clearSessionHint() {
  if (typeof window === 'undefined') return;
  window.localStorage.removeItem(SESSION_HINT_KEY);
}

/** Forget the session locally. The refresh cookie is only cleared server-side. */
export function clearToken() {
  clearAccessToken();
  clearSessionHint();
}

// ─── Errors ─────────────────────────────────────────────────────────────────

export class ApiError extends Error {
  status: number;
  /** DRF field errors keyed by field name, e.g. `{ email: ['Already taken.'] }`. */
  fieldErrors?: Record<string, string[]>;
  /** Machine-readable code the API may attach (e.g. `token_expired`). */
  code?: string;

  constructor(
    status: number,
    message: string,
    fieldErrors?: Record<string, string[]>,
    code?: string
  ) {
    super(message);
    this.status = status;
    this.name = 'ApiError';
    this.fieldErrors = fieldErrors;
    this.code = code;
  }
}

function flattenErrors(data: unknown, prefix = ''): Record<string, string[]> {
  const errors: Record<string, string[]> = {};
  if (!data || typeof data !== 'object') return errors;

  for (const [key, value] of Object.entries(data as Record<string, unknown>)) {
    const field = prefix ? `${prefix}.${key}` : key;
    if (typeof value === 'string') {
      if (key !== 'detail' && key !== 'error' && key !== 'code') {
        (errors[field] ||= []).push(value);
      }
    } else if (Array.isArray(value)) {
      const messages = value.filter((item): item is string => typeof item === 'string');
      if (messages.length) {
        errors[field] = messages;
      } else {
        value.forEach((item) => Object.assign(errors, flattenErrors(item, field)));
      }
    } else if (value && typeof value === 'object') {
      Object.assign(errors, flattenErrors(value, field));
    }
  }
  return errors;
}

async function readError(res: Response): Promise<ApiError> {
  let message = `Request failed (${res.status})`;
  let fieldErrors: Record<string, string[]> | undefined;
  let code: string | undefined;

  const text = await res.text().catch(() => '');
  if (text) {
    try {
      const data = JSON.parse(text) as Record<string, unknown>;
      const flattened = flattenErrors(data);
      if (Object.keys(flattened).length) fieldErrors = flattened;

      if (typeof data.detail === 'string') message = data.detail;
      else if (typeof data.error === 'string') message = data.error;
      else if (fieldErrors) message = Object.values(fieldErrors)[0]?.[0] ?? message;
      if (typeof data.code === 'string') code = data.code;
    } catch {
      // A server error under DEBUG answers with Django's HTML debug page.
      // Rendering that in the UI is noise, so it becomes a short message.
      const body = text.trim();
      if (body.startsWith('<')) {
        message = `The API returned a server error (${res.status}). Check the server log for the traceback.`;
      } else if (body) {
        message = body.slice(0, 300);
      }
    }
  }
  return new ApiError(res.status, message, fieldErrors, code);
}

/**
 * Human-readable reason a verification-email request failed.
 *
 * DRF answers 429 with "Request was throttled. Expected available in N
 * seconds.", which is accurate but reads like a stack trace to a user, so the
 * wait is restated in minutes. Anything that is not an ApiError never reached
 * the server at all (offline, API stopped), and saying so is more useful than
 * pretending the mail was sent.
 */
export function describeResendError(caught: unknown): string {
  if (!(caught instanceof ApiError)) {
    return "We couldn't reach the API, so no email was sent. Check your connection and try again.";
  }
  if (caught.status === 429) {
    const seconds = Number(/(\d+)\s*second/i.exec(caught.message)?.[1] ?? 0);
    if (seconds > 0) {
      const minutes = Math.ceil(seconds / 60);
      return `Too many requests. Try again in ${minutes} minute${minutes === 1 ? '' : 's'}.`;
    }
    return 'Too many requests. Try again in a few minutes.';
  }
  return caught.message || 'The verification email could not be sent. Please try again.';
}

// DRF paginates list endpoints globally (PageNumberPagination): they return
// { count, next, previous, results } rather than a bare array. Normalize so
// callers always get a plain array.
type Paginated<T> = T[] | { results: T[]; count: number; next: string | null; previous: string | null };

function unwrapList<T>(data: Paginated<T>): T[] {
  return Array.isArray(data) ? data : data.results;
}

// ─── CSRF + refresh plumbing ────────────────────────────────────────────────

/**
 * `fetch` rejects with a bare "Failed to fetch" when the API is unreachable
 * (server down, wrong origin rejected by CORS, DNS failure). That message is
 * unactionable in the UI, so it becomes an ApiError naming the API base URL.
 * `status: 0` marks it as a transport failure rather than an HTTP status.
 */
async function fetchOrThrow(url: string, init: RequestInit = {}): Promise<Response> {
  try {
    return await fetch(url, init);
  } catch {
    throw new ApiError(
      0,
      `Can't reach the API at ${API_BASE}. Is the Django server running? (start both with scripts/dev.ps1)`
    );
  }
}

let csrfToken: string | null = null;
let csrfInFlight: Promise<string> | null = null;

async function fetchCsrfToken(): Promise<string> {
  const res = await fetchOrThrow(`${API_BASE}/auth/csrf/`, { credentials: 'include' });
  if (!res.ok) return '';
  const data = (await res.json()) as { csrfToken?: string };
  csrfToken = data.csrfToken || '';
  return csrfToken;
}

/** Fetch (once per page load) the token echoed back in `X-CSRFToken`. */
export function ensureCsrfToken(): Promise<string> {
  if (csrfToken) return Promise.resolve(csrfToken);
  if (!csrfInFlight) {
    csrfInFlight = fetchCsrfToken()
      .catch(() => '')
      .finally(() => { csrfInFlight = null; });
  }
  return csrfInFlight;
}

let refreshInFlight: Promise<string | null> | null = null;

async function performRefresh(): Promise<string | null> {
  const token = await ensureCsrfToken();
  if (!token) return null;

  const res = await fetchOrThrow(`${API_BASE}/auth/token/refresh/`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': token },
  });

  if (!res.ok) {
    if (res.status === 401 || res.status === 403) {
      // The API already cleared its cookie; mirror that locally.
      clearToken();
    }
    return null;
  }

  const data = (await res.json()) as { access?: string };
  accessToken = data.access ?? null;
  markSessionHint();
  return accessToken;
}

/**
 * Exchange the HttpOnly refresh cookie for a new access token.
 * Concurrent callers share one request so a burst of 401s cannot rotate the
 * refresh token several times in parallel (which would invalidate itself).
 */
export function refreshAccessToken(): Promise<string | null> {
  if (!refreshInFlight) {
    refreshInFlight = performRefresh()
      .catch(() => null)
      .finally(() => { refreshInFlight = null; });
  }
  return refreshInFlight;
}

// ─── Request core ───────────────────────────────────────────────────────────

interface ApiRequestOptions extends RequestInit {
  /** Attach the in-memory access token. Defaults to true. */
  withAuth?: boolean;
  /** Disable the automatic refresh-and-retry on 401. */
  retryOnUnauthorized?: boolean;
}

async function send(
  endpoint: string,
  init: RequestInit,
  withAuth: boolean
): Promise<Response> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...((init.headers as Record<string, string>) || {}),
  };
  if (withAuth && accessToken) {
    headers.Authorization = `Bearer ${accessToken}`;
  }
  return fetchOrThrow(`${API_BASE}${endpoint}`, {
    ...init,
    headers,
    credentials: 'include',
  });
}

async function request<T>(
  endpoint: string,
  options: ApiRequestOptions = {}
): Promise<T> {
  const { withAuth = true, retryOnUnauthorized = true, ...init } = options;

  let res = await send(endpoint, init, withAuth);

  if (res.status === 401 && withAuth && retryOnUnauthorized && !NO_REFRESH.has(endpoint)) {
    const refreshed = await refreshAccessToken();
    if (refreshed) res = await send(endpoint, init, withAuth);
  }

  if (!res.ok) throw await readError(res);

  // Handle 204 No Content
  if (res.status === 204) return {} as T;

  const text = await res.text();
  return (text ? JSON.parse(text) : {}) as T;
}

/** Raw fetch on a protected endpoint with the same refresh-and-retry policy. */
async function authorizedFetch(endpoint: string, init: RequestInit = {}): Promise<Response> {
  let res = await send(endpoint, init, true);
  if (res.status === 401) {
    const refreshed = await refreshAccessToken();
    if (refreshed) res = await send(endpoint, init, true);
  }
  return res;
}

// ─── Auth Endpoints ─────────────────────────────────────────────────────────

export type UserRole = 'student' | 'instructor' | 'administrator';

export interface AuthUser {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  date_joined: string;
  role: UserRole;
  email_verified: boolean;
}

export interface ProfileFields {
  avatar: string;
  bio: string;
  institution: string;
  education_level: string;
  github_url: string;
  linkedin_url: string;
}

export interface UserProfileData extends ProfileFields {
  full_name: string;
  role: string;
  email_verified: boolean;
  email_verified_at: string | null;
  xp_points: number;
  streak_days: number;
  level: number;
  last_active_at: string | null;
  created_at: string;
}

/** Payload of `GET /auth/me/`: nested `user`/`profile` plus flat profile keys. */
export interface MePayload extends ProfileFields {
  user: AuthUser;
  profile: UserProfileData;
  role: string;
  email_verified: boolean;
  xp_points: number;
  streak_days: number;
  level: number;
  last_active_at: string | null;
  email_changed?: boolean;
  verification_email_sent?: boolean;
}

/** Name kept for existing consumers of the old `/auth/profile/` shape. */
export type AuthProfileData = MePayload;

export interface SessionResponse {
  access: string;
  token_type: string;
  expires_in: number;
  user: AuthUser;
  verification_email_sent?: boolean;
}

/**
 * Registration answer. When the API enforces email verification it withholds
 * the session until the address is confirmed, so `access` is absent and the
 * client must show the "check your email" screen instead of signing in.
 */
export interface RegisterResponse {
  user: AuthUser;
  access?: string;
  token_type?: string;
  expires_in?: number;
  verification_email_sent?: boolean;
}

export interface RegisterPayload {
  full_name: string;
  username: string;
  email: string;
  password: string;
  confirm_password: string;
}

/** Fields the profile API accepts. Privilege fields are rejected server-side. */
export interface UpdateProfilePayload extends Partial<ProfileFields> {
  username?: string;
  email?: string;
  first_name?: string;
  last_name?: string;
  full_name?: string;
}

export const auth = {
  /** Echoes back the CSRF secret needed by cookie-authenticated endpoints. */
  csrf: () =>
    request<{ csrfToken: string }>('/auth/csrf/', {
      withAuth: false,
      retryOnUnauthorized: false,
    }),

  register: async (data: RegisterPayload): Promise<RegisterResponse> => {
    const session = await request<RegisterResponse>('/auth/register/', {
      method: 'POST',
      body: JSON.stringify(data),
      withAuth: false,
      retryOnUnauthorized: false,
    });
    if (session.access) {
      setAccessToken(session.access);
      markSessionHint();
    }
    return session;
  },

  /** `identifier` is either an email address or a username. */
  login: async (data: { identifier: string; password: string }): Promise<SessionResponse> => {
    const session = await request<SessionResponse>('/auth/login/', {
      method: 'POST',
      body: JSON.stringify(data),
      withAuth: false,
      retryOnUnauthorized: false,
    });
    setAccessToken(session.access);
    markSessionHint();
    return session;
  },

  logout: async (): Promise<void> => {
    const token = await ensureCsrfToken();
    try {
      await request<{ detail: string }>('/auth/logout/', {
        method: 'POST',
        headers: token ? { 'X-CSRFToken': token } : undefined,
        withAuth: false,
        retryOnUnauthorized: false,
      });
    } finally {
      clearToken();
      csrfToken = null;
    }
  },

  me: () => request<MePayload>('/auth/me/'),

  updateMe: (data: UpdateProfilePayload) =>
    request<MePayload>('/auth/me/', { method: 'PATCH', body: JSON.stringify(data) }),

  changePassword: async (data: {
    current_password: string;
    new_password: string;
    confirm_password: string;
  }): Promise<{ detail: string; access: string }> => {
    const result = await request<{ detail: string; access: string }>(
      '/auth/change-password/',
      { method: 'POST', body: JSON.stringify(data) }
    );
    // The server revoked every other session and issued this one a new pair.
    setAccessToken(result.access);
    markSessionHint();
    return result;
  },

  verifyEmail: (token: string) =>
    request<{ detail: string; user: AuthUser }>('/auth/verify-email/', {
      method: 'POST',
      body: JSON.stringify({ token }),
      withAuth: false,
      retryOnUnauthorized: false,
    }),

  /** Signed-in callers may omit the email (their own address is used). */
  resendVerification: (email?: string) =>
    request<{ detail: string; verification_email_sent?: boolean }>(
      '/auth/resend-verification/',
      {
        method: 'POST',
        body: JSON.stringify(email ? { email } : {}),
      }
    ),

  requestPasswordReset: (email: string) =>
    request<{ detail: string }>('/auth/password-reset/', {
      method: 'POST',
      body: JSON.stringify({ email }),
      withAuth: false,
      retryOnUnauthorized: false,
    }),

  confirmPasswordReset: (data: { token: string; password: string; confirm_password: string }) =>
    request<{ detail: string }>('/auth/password-reset/confirm/', {
      method: 'POST',
      body: JSON.stringify(data),
      withAuth: false,
      retryOnUnauthorized: false,
    }),

  // Aliases kept for the pages that still speak the old profile vocabulary.
  getProfile: () => request<MePayload>('/auth/me/'),
  updateProfile: (data: Record<string, unknown>) =>
    request<MePayload>('/auth/me/', { method: 'PATCH', body: JSON.stringify(data) }),
};

/**
 * Re-establish an in-memory access token from the refresh cookie.
 * Returns the signed-in user payload, or null when there is no usable session.
 */
export async function restoreSession(): Promise<MePayload | null> {
  if (!hasSessionHint()) {
    clearAccessToken();
    return null;
  }

  const token = await refreshAccessToken();
  if (!token) return null;

  try {
    return await auth.me();
  } catch {
    clearToken();
    return null;
  }
}

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

  // Download is owner-restricted and bearer-authenticated, so stream the PDF
  // through fetch with the Authorization header and hand the blob to the
  // browser rather than navigating to the URL directly.
  download: async (publicId: string): Promise<void> => {
    const res = await authorizedFetch(
      `/certificates/${encodeURIComponent(publicId)}/download/`
    );
    if (!res.ok) {
      throw await readError(res);
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

