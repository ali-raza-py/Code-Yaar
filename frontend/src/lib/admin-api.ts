import { request, getAccessToken, refreshAccessToken } from "@/lib/api";

export interface AdminDashboardStats {
  totalStudents: number;
  activeStudents: number;
  totalCourses: number;
  publishedCourses: number;
  totalTracks: number;
  publishedTracks: number;
  totalEnrollments: number;
  activeEnrollments: number;
  completedCourses: number;
  totalAssessments: number;
  totalChallenges: number;
  certificatesIssued: number;
  activeCompetitions: number;
  totalLessons?: number;
  pendingRegistrations?: number;
  scheduledCourses?: number;
  archivedCourses?: number;
}

export interface AdminRecentActivity {
  id: string;
  action: string;
  admin: string;
  target: string;
  timestamp: string;
  metadata?: Record<string, unknown>;
}

export interface AdminTopCourse {
  id: number;
  title: string;
  track: string;
  enrollments: number;
  completionRate: number;
}

export interface AdminListParams {
  page?: number;
  page_size?: number;
  search?: string;
  ordering?: string;
  [key: string]: unknown;
}

export interface AdminPaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface CareerTrackAdmin {
  id: number;
  slug: string;
  title: string;
  description: string;
  icon: string;
  category: string;
  cover_image: string | null;
  learning_objectives: string[];
  difficulty: string;
  estimated_hours: number;
  order: number;
  is_published: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  courses_count: number;
  published_courses_count: number;
}

export interface CourseAdmin {
  id: number;
  slug: string;
  title: string;
  subtitle: string;
  description: string;
  thumbnail: string;
  track: number;
  track_title: string;
  academic_class: string;
  difficulty: string;
  language: string;
  instructor: string;
  prerequisites: string;
  learning_objectives: string[];
  is_free: boolean;
  order: number;
  is_published: boolean;
  is_active: boolean;
  certification_enabled: boolean;
  certification_passing_score: number;
  require_all_lessons: boolean;
  require_final_assessment: boolean;
  created_at: string;
  updated_at: string;
  chapter_count: number;
  lesson_count: number;
  exercise_count: number;
  enrollment_count: number;
  completion_rate: number;
}

export interface ChapterAdmin {
  id: number;
  title: string;
  slug: string;
  description: string;
  course: number;
  course_title: string;
  order: number;
  xp_reward: number;
  is_active: boolean;
  source_type: string;
  verification_status: string;
  textbook_board: string;
  textbook_class: string;
  textbook_unit: string;
  textbook_topic: string;
  textbook_pages: string;
  created_at: string;
  updated_at: string;
  lesson_count: number;
  exercise_count: number;
}

export interface LessonAdmin {
  id: number;
  title: string;
  slug: string;
  content_type: string;
  chapter: number;
  chapter_title: string;
  course_title: string;
  learning_objective: string;
  content_body: string;
  video_url: string;
  video_duration_seconds: number;
  order: number;
  duration_minutes: number;
  xp_reward: number;
  is_free_preview: boolean;
  is_active: boolean;
  source_type: string;
  verification_status: string;
  textbook_board: string;
  textbook_class: string;
  textbook_unit: string;
  textbook_topic: string;
  textbook_pages: string;
  created_at: string;
  updated_at: string;
  exercise_count: number;
}

export interface ExerciseAdmin {
  id: number;
  title: string;
  slug: string;
  exercise_type: string;
  lesson: number;
  lesson_title: string;
  chapter_title: string;
  course_title: string;
  instructions: string;
  context: string;
  constraints: string;
  expected_behavior: string;
  explain: string;
  difficulty: string;
  language: string;
  starter_code: string;
  solution_code: string;
  expected_output: string;
  choices: Array<{ id: string; text: string; is_correct: boolean }>;
  test_cases: unknown[];
  hidden_tests: unknown[];
  xp_reward: number;
  max_attempts: number;
  is_final_assessment: boolean;
  order: number;
  is_active: boolean;
  source_type: string;
  verification_status: string;
  created_at: string;
  updated_at: string;
}

export interface StudentAdmin {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  avatar: string;
  role: string;
  institution: string;
  education_level: string;
  xp_points: number;
  streak_days: number;
  level: number;
  is_profile_public: boolean;
  date_joined: string;
  last_active_at: string | null;
  enrollment_count: number;
  completed_courses: number;
  completed_lessons: number;
}

export interface InstructorAdmin {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  avatar: string;
  institution: string;
  assigned_courses_count: number;
  assigned_courses: Array<{ id: number; title: string; slug: string }>;
}

export interface EnrollmentAdmin {
  id: number;
  user: number;
  student_name: string;
  student_email: string;
  course: number;
  course_title: string;
  course_slug: string;
  track_title: string;
  enrolled_at: string;
  completed_at: string | null;
  last_activity_at: string | null;
  status: string;
  progress_percentage: number;
}

export interface CompetitionAdmin {
  id: number;
  slug: string;
  title: string;
  short_description: string;
  description: string;
  banner: string;
  category: string;
  difficulty: string;
  format: string;
  delivery_mode: string;
  location: string;
  registration_start: string;
  registration_deadline: string;
  competition_start: string;
  competition_end: string;
  submission_deadline: string;
  judging_end: string | null;
  results_announcement: string | null;
  participant_limit: number | null;
  minimum_team_size: number;
  maximum_team_size: number;
  eligibility_rules: unknown[];
  competition_rules: unknown[];
  problem_statement: string;
  submission_configuration: Record<string, unknown>;
  prize_information: string;
  tags: string[];
  host_name: string;
  time_zone: string;
  registration_fee: string;
  participation_instructions: string;
  evaluation_criteria: string;
  submission_requirements: string;
  contact_information: string;
  external_resources: Array<{ title: string; url: string }>;
  is_archived: boolean;
  is_published: boolean;
  organizer: number;
  organizer_name: string;
  participant_count: number;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface AchievementAdmin {
  id: number;
  slug: string;
  title: string;
  description: string;
  icon: string;
  category: string;
  difficulty: string;
  xp_bonus: number;
  condition_type: string;
  condition_value: string;
  how_to_earn: string;
  is_active: boolean;
  earned_count: number;
  created_at: string;
}

export interface CertificateAdmin {
  id: number;
  public_id: string;
  credential_id: string;
  student_name: string;
  student_email: string;
  course_title: string;
  course_slug: string;
  issued_at: string;
  completion_verified_at: string | null;
  final_score: number | null;
  status: string;
  is_valid: boolean;
}

export interface AnnouncementAdmin {
  id: number;
  title: string;
  slug: string;
  body: string;
  short_description: string;
  cover_image: string | null;
  category: string;
  priority: string;
  target_audience: string;
  status: "draft" | "published" | "unpublished" | "archived";
  is_published: boolean;
  scheduled_at: string | null;
  published_at: string | null;
  expires_at: string | null;
  created_by: number;
  created_by_name: string;
  created_at: string;
  updated_at: string;
}

export interface PlatformUpdateAdmin {
  id: number;
  title: string;
  slug: string;
  version: string;
  category: string;
  summary: string;
  content: string;
  change_list: string[];
  cover_image: string | null;
  target_audience: string;
  status: "draft" | "published" | "unpublished" | "archived";
  published_at: string | null;
  created_by: number;
  created_by_name: string;
  created_at: string;
  updated_at: string;
}

export type RegistrationFieldType =
  | "short_text" | "long_text" | "email" | "phone" | "number"
  | "dropdown" | "multiple_choice" | "checkboxes" | "url" | "date";

export interface RegistrationFormFieldAdmin {
  id: number;
  competition: number;
  label: string;
  field_key: string;
  field_type: RegistrationFieldType;
  description: string;
  placeholder: string;
  required: boolean;
  options: Array<string | number>;
  validation: Record<string, number>;
  order: number;
  is_active: boolean;
  is_default: boolean;
  created_at: string;
  updated_at: string;
}

export interface CompetitionRegistrationAdmin {
  id: number;
  reference: string;
  competition: number;
  competition_title: string;
  competition_slug: string;
  user: number;
  username: string;
  participant_name: string;
  participant_email: string;
  team: number | null;
  registration_status: string;
  registration_data: Record<string, string | string[]>;
  registered_at: string;
  updated_at: string;
}

export interface RegistrationStatsAdmin {
  total: number;
  by_status: Record<string, number>;
}

export interface EmailCampaignAdmin {
  id: number;
  name: string;
  subject: string;
  heading: string;
  body: string;
  template: "general" | "notice" | "platform_update" | "new_course";
  banner_image: string | null;
  cta_label: string;
  cta_url: string;
  audience: string;
  competition: number | null;
  selected_users: number[];
  custom_emails: string[];
  cc_emails: string[];
  bcc_emails: string[];
  body_html: string;
  plain_text_alternative: string;
  essential: boolean;
  related_announcement: number | null;
  related_update: number | null;
  status: "draft" | "queued" | "sending" | "sent" | "partial" | "failed";
  recipient_count: number;
  sent_count: number;
  failed_count: number;
  skipped_count: number;
  sent_at: string | null;
  created_by: number;
  created_by_name: string;
  created_at: string;
  updated_at: string;
}

export interface EmailTemplateAdmin {
  id: number;
  name: string;
  category: string;
  description: string;
  subject: string;
  heading: string;
  preview_text: string;
  body_html: string;
  plain_text: string;
  cta_label: string;
  cta_url: string;
  footer_content: string;
  is_favorite: boolean;
  created_by: number | null;
  created_by_name: string;
  variables_used: string[];
  created_at: string;
  updated_at: string;
}

export interface EmailCampaignRecipientAdmin {
  id: number;
  user: number | null;
  username: string;
  email: string;
  status: "pending" | "sent" | "render_only" | "skipped" | "failed";
  error: string;
  sent_at: string | null;
  created_at: string;
}

export interface EmailSettingsAdmin {
  backend: string;
  is_smtp: boolean;
  host: string;
  port: number | null;
  username: string;
  password_configured: boolean;
  use_tls: boolean;
  use_ssl: boolean;
  from_email: string;
  delivery_ready: boolean;
  note?: string;
}

export interface EmailThemeAdmin {
  id: number;
  slug: string;
  name: string;
  description: string;
  best_for: string;
  primary_color: string;
  accent_color: string;
  highlight_color: string;
  background_color: string;
  is_default: boolean;
}

export interface EmailAutomationAdmin {
  id: number;
  trigger: string;
  name: string;
  description: string;
  enabled: boolean;
  template: number | null;
  theme: string;
  subject_override: string;
  delay_minutes: number;
  recipient_group: string;
  last_run_at: string | null;
  success_count: number;
  failure_count: number;
}

export interface AuditLogAdmin {
  id: number;
  admin_user: number;
  admin_name: string;
  action: string;
  target_type: string;
  target_id: string;
  target_repr: string;
  metadata: Record<string, unknown>;
  ip_address: string | null;
  user_agent: string;
  timestamp: string;
}

export interface PlatformSettingsAdmin {
  platform_name: string;
  logo_light: string;
  logo_dark: string;
  default_course_visibility: string;
  supported_classes: string[];
  supported_subjects: string[];
  default_difficulty_options: string[];
  enrollment_enabled: boolean;
  notification_preferences: Record<string, boolean>;
  maintenance_mode: boolean;
  maintenance_message: string;
  estimated_return_time: string;
}

export interface StudioLesson {
  id: number;
  slug: string;
  title: string;
  content_type: string;
  learning_objective: string;
  content_body: string;
  video_url: string;
  order: number;
  duration_minutes: number;
  xp_reward: number;
  is_active: boolean;
  is_required: boolean;
  prerequisite: number | null;
  estimated_reading_minutes: number;
  instructor_notes: string;
  exercise_count: number;
  exercises: ExerciseAdmin[];
  updated_at: string;
}

export interface StudioChapter {
  id: number;
  slug: string;
  title: string;
  description: string;
  order: number;
  xp_reward: number;
  is_active: boolean;
  published_lesson_count: number;
  publication_state: 'empty' | 'draft' | 'published' | 'partial';
  lessons: StudioLesson[];
}

export interface StudioCourse {
  id: number;
  slug: string;
  title: string;
  subtitle: string;
  description: string;
  thumbnail: string;
  cover_image: string;
  category: number | null;
  category_title: string;
  track: number | null;
  track_title: string;
  academic_class: string;
  difficulty: string;
  language: string;
  instructor: string;
  instructor_user: number | null;
  instructor_user_name: string;
  prerequisites: string;
  prerequisite_courses: Array<{ id: number; title: string; slug: string }>;
  learning_objectives: string[];
  tags: string[];
  is_free: boolean;
  order: number;
  is_published: boolean;
  is_active: boolean;
  publish_at: string | null;
  published_at: string | null;
  archived_at: string | null;
  sequential_learning: boolean;
  require_all_lessons: boolean;
  require_final_assessment: boolean;
  certification_enabled: boolean;
  certification_passing_score: number;
  xp_completion_reward: number;
  estimated_hours: number;
  total_xp: number;
  updated_at: string;
}

export interface StudioBundle {
  course: StudioCourse;
  chapters: StudioChapter[];
  resources: Array<{
    id: number;
    title: string;
    resource_type: string;
    url: string;
    description: string;
    order: number;
    is_active: boolean;
  }>;
  stats: {
    chapter_count: number;
    lesson_count: number;
    published_lesson_count: number;
    enrollment_count: number;
    completion_count: number;
    total_xp: number;
  };
  permissions: { can_edit: boolean; can_publish: boolean; can_archive: boolean };
}

export interface StudioCourseRow {
  id: number;
  slug: string;
  title: string;
  subtitle: string;
  difficulty: string;
  is_published: boolean;
  is_active: boolean;
  publish_at: string | null;
  published_at: string | null;
  archived_at: string | null;
  track: string | null;
  category: string | null;
  instructor: string;
  instructor_user: number | null;
  chapter_count: number;
  lesson_count: number;
  published_lesson_count: number;
  enrollment_count: number;
  updated_at: string;
}

export interface CourseCategoryAdmin {
  id: number;
  slug: string;
  title: string;
  description: string;
  order: number;
  is_active: boolean;
  course_count: number;
}

export interface PublishIssue {
  code: string;
  message: string;
  severity: 'blocking' | 'warning';
  target?: Record<string, unknown>;
}

export interface PublishChecklist {
  ok: boolean;
  blocking: PublishIssue[];
  warnings: PublishIssue[];
  checked_at?: string;
  counts?: Record<string, number>;
}

export interface AnalyticsSeriesPoint {
  period: string;
  value: number;
}

export interface AnalyticsOverview {
  range: { from: string; to: string; bucket: string };
  students: {
    registrations: AnalyticsSeriesPoint[];
    active: AnalyticsSeriesPoint[];
    total_students: number;
    engagement_rate: number;
  };
  education: {
    enrollments: AnalyticsSeriesPoint[];
    completions: AnalyticsSeriesPoint[];
    lesson_completions: AnalyticsSeriesPoint[];
    exercise_submissions: AnalyticsSeriesPoint[];
    activity: AnalyticsSeriesPoint[];
    enrollment_completion_rate: number;
    exercise_pass_rate: number;
    exercise_attempts: { total: number; correct: number };
    top_courses: Array<{
      id: number;
      title: string;
      slug: string;
      learners: number;
      finishers: number;
      lesson_count: number;
      completion_rate: number;
    }>;
    top_tracks: Array<{
      id: number;
      title: string;
      slug: string;
      course_count: number;
      learners: number;
    }>;
    dropoff: {
      lessons: Array<{
        lesson_id: number;
        lesson: string;
        course: string;
        chapter: string;
        enrolled: number;
        completions: number;
        completion_rate: number;
      }>;
      worst: Array<{
        lesson_id: number;
        lesson: string;
        course: string;
        chapter: string;
        enrolled: number;
        completions: number;
        completion_rate: number;
      }>;
    };
    retention: Array<{ cohort: string; cohort_size: number; months: Record<string, number> }>;
  };
  competitions: {
    registrations: AnalyticsSeriesPoint[];
    total_registrations: number;
    pending_approval: number;
    by_status: Array<{ registration_status: string; count: number }>;
    top_competitions: Array<{
      id: number;
      title: string;
      slug: string;
      total: number;
      waiting: number;
    }>;
  };
  unavailable: Array<{ id: string; label: string; reason: string; phase: string }>;
}

async function adminRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  return request<T>(`/admin${endpoint}`, options);
}

export const adminApi = {
  // Dashboard
  getDashboardStats: () =>
    adminRequest<AdminDashboardStats>("/dashboard/stats/"),

  getRecentActivity: (params?: { limit?: number }) => {
    const query = new URLSearchParams();
    if (params?.limit) query.set("limit", String(params.limit));
    const qs = query.toString();
    return adminRequest<AdminRecentActivity[]>(`/dashboard/recent-activity/${qs ? `?${qs}` : ""}`);
  },

  getTopCourses: (params?: { limit?: number }) => {
    const query = new URLSearchParams();
    if (params?.limit) query.set("limit", String(params.limit));
    const qs = query.toString();
    return adminRequest<AdminTopCourse[]>(`/dashboard/top-courses/${qs ? `?${qs}` : ""}`);
  },

  // Career Tracks
  listTracks: (params?: AdminListParams) => {
    const query = new URLSearchParams();
    Object.entries(params || {}).forEach(([key, value]) => {
      if (value !== undefined && value !== "") query.set(key, String(value));
    });
    const qs = query.toString();
    return adminRequest<AdminPaginatedResponse<CareerTrackAdmin>>(`/tracks/${qs ? `?${qs}` : ""}`);
  },

  getTrack: (id: number) =>
    adminRequest<CareerTrackAdmin>(`/tracks/${id}/`),

  createTrack: (data: Partial<CareerTrackAdmin>) =>
    adminRequest<CareerTrackAdmin>("/tracks/", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  updateTrack: (id: number, data: Partial<CareerTrackAdmin>) =>
    adminRequest<CareerTrackAdmin>(`/tracks/${id}/`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  deleteTrack: (id: number) =>
    adminRequest(`/tracks/${id}/`, { method: "DELETE" }),

  publishTrack: (id: number) =>
    adminRequest<CareerTrackAdmin>(`/tracks/${id}/publish/`, { method: "POST" }),

  unpublishTrack: (id: number) =>
    adminRequest<CareerTrackAdmin>(`/tracks/${id}/unpublish/`, { method: "POST" }),

  reorderTracks: (data: Array<{ id: number; order: number }>) =>
    adminRequest("/tracks/reorder/", {
      method: "POST",
      body: JSON.stringify({ items: data }),
    }),

  // Courses
  listCourses: (params?: AdminListParams) => {
    const query = new URLSearchParams();
    Object.entries(params || {}).forEach(([key, value]) => {
      if (value !== undefined && value !== "") query.set(key, String(value));
    });
    const qs = query.toString();
    return adminRequest<AdminPaginatedResponse<CourseAdmin>>(`/courses/${qs ? `?${qs}` : ""}`);
  },

  getCourse: (id: number) =>
    adminRequest<CourseAdmin>(`/courses/${id}/`),

  createCourse: (data: Partial<CourseAdmin>) =>
    adminRequest<CourseAdmin>("/courses/", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  updateCourse: (id: number, data: Partial<CourseAdmin>) =>
    adminRequest<CourseAdmin>(`/courses/${id}/`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  deleteCourse: (id: number) =>
    adminRequest(`/courses/${id}/`, { method: "DELETE" }),

  duplicateCourse: (id: number) =>
    adminRequest<CourseAdmin>(`/courses/${id}/duplicate/`, { method: "POST" }),

  publishCourse: (id: number) =>
    adminRequest<CourseAdmin>(`/courses/${id}/publish/`, { method: "POST" }),

  unpublishCourse: (id: number) =>
    adminRequest<CourseAdmin>(`/courses/${id}/unpublish/`, { method: "POST" }),

  getCourseChapters: (courseId: number) =>
    adminRequest<ChapterAdmin[]>(`/courses/${courseId}/chapters/`),

  getCourseStudents: (courseId: number) =>
    adminRequest<StudentAdmin[]>(`/courses/${courseId}/students/`),

  // Chapters
  listChapters: (params?: AdminListParams & { course?: number }) => {
    const query = new URLSearchParams();
    Object.entries(params || {}).forEach(([key, value]) => {
      if (value !== undefined && value !== "") query.set(key, String(value));
    });
    const qs = query.toString();
    return adminRequest<AdminPaginatedResponse<ChapterAdmin>>(`/chapters/${qs ? `?${qs}` : ""}`);
  },

  getChapter: (id: number) =>
    adminRequest<ChapterAdmin>(`/chapters/${id}/`),

  createChapter: (data: Partial<ChapterAdmin>) =>
    adminRequest<ChapterAdmin>("/chapters/", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  updateChapter: (id: number, data: Partial<ChapterAdmin>) =>
    adminRequest<ChapterAdmin>(`/chapters/${id}/`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  deleteChapter: (id: number) =>
    adminRequest(`/chapters/${id}/`, { method: "DELETE" }),

  reorderChapters: (courseId: number, data: Array<{ id: number; order: number }>) =>
    adminRequest(`/courses/${courseId}/chapters/reorder/`, {
      method: "POST",
      body: JSON.stringify({ items: data }),
    }),

  // Lessons
  listLessons: (params?: AdminListParams & { chapter?: number; course?: number }) => {
    const query = new URLSearchParams();
    Object.entries(params || {}).forEach(([key, value]) => {
      if (value !== undefined && value !== "") query.set(key, String(value));
    });
    const qs = query.toString();
    return adminRequest<AdminPaginatedResponse<LessonAdmin>>(`/lessons/${qs ? `?${qs}` : ""}`);
  },

  getLesson: (id: number) =>
    adminRequest<LessonAdmin>(`/lessons/${id}/`),

  createLesson: (data: Partial<LessonAdmin>) =>
    adminRequest<LessonAdmin>("/lessons/", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  updateLesson: (id: number, data: Partial<LessonAdmin>) =>
    adminRequest<LessonAdmin>(`/lessons/${id}/`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  deleteLesson: (id: number) =>
    adminRequest(`/lessons/${id}/`, { method: "DELETE" }),

  reorderLessons: (chapterId: number, data: Array<{ id: number; order: number }>) =>
    adminRequest(`/chapters/${chapterId}/lessons/reorder/`, {
      method: "POST",
      body: JSON.stringify({ items: data }),
    }),

  // Exercises
  listExercises: (params?: AdminListParams & { lesson?: number }) => {
    const query = new URLSearchParams();
    Object.entries(params || {}).forEach(([key, value]) => {
      if (value !== undefined && value !== "") query.set(key, String(value));
    });
    const qs = query.toString();
    return adminRequest<AdminPaginatedResponse<ExerciseAdmin>>(`/exercises/${qs ? `?${qs}` : ""}`);
  },

  getExercise: (id: number) =>
    adminRequest<ExerciseAdmin>(`/exercises/${id}/`),

  createExercise: (data: Partial<ExerciseAdmin>) =>
    adminRequest<ExerciseAdmin>("/exercises/", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  updateExercise: (id: number, data: Partial<ExerciseAdmin>) =>
    adminRequest<ExerciseAdmin>(`/exercises/${id}/`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  deleteExercise: (id: number) =>
    adminRequest(`/exercises/${id}/`, { method: "DELETE" }),

  // Students
  listStudents: (params?: AdminListParams) => {
    const query = new URLSearchParams();
    Object.entries(params || {}).forEach(([key, value]) => {
      if (value !== undefined && value !== "") query.set(key, String(value));
    });
    const qs = query.toString();
    return adminRequest<AdminPaginatedResponse<StudentAdmin>>(`/students/${qs ? `?${qs}` : ""}`);
  },

  getStudent: (id: number) =>
    adminRequest<StudentAdmin>(`/students/${id}/`),

  updateStudent: (id: number, data: Partial<StudentAdmin>) =>
    adminRequest<StudentAdmin>(`/students/${id}/`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  // Instructors
  listInstructors: (params?: AdminListParams) => {
    const query = new URLSearchParams();
    Object.entries(params || {}).forEach(([key, value]) => {
      if (value !== undefined && value !== "") query.set(key, String(value));
    });
    const qs = query.toString();
    return adminRequest<AdminPaginatedResponse<InstructorAdmin>>(`/instructors/${qs ? `?${qs}` : ""}`);
  },

  getInstructor: (id: number) =>
    adminRequest<InstructorAdmin>(`/instructors/${id}/`),

  assignInstructor: (instructorId: number, courseIds: number[]) =>
    adminRequest(`/instructors/${instructorId}/assign/`, {
      method: "POST",
      body: JSON.stringify({ course_ids: courseIds }),
    }),

  unassignInstructor: (instructorId: number, courseId: number) =>
    adminRequest(`/instructors/${instructorId}/unassign/`, {
      method: "POST",
      body: JSON.stringify({ course_id: courseId }),
    }),

  // Enrollments
  listEnrollments: (params?: AdminListParams) => {
    const query = new URLSearchParams();
    Object.entries(params || {}).forEach(([key, value]) => {
      if (value !== undefined && value !== "") query.set(key, String(value));
    });
    const qs = query.toString();
    return adminRequest<AdminPaginatedResponse<EnrollmentAdmin>>(`/enrollments/${qs ? `?${qs}` : ""}`);
  },

  getEnrollment: (id: number) =>
    adminRequest<EnrollmentAdmin>(`/enrollments/${id}/`),

  updateEnrollment: (id: number, data: Partial<EnrollmentAdmin>) =>
    adminRequest<EnrollmentAdmin>(`/enrollments/${id}/`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  // Competitions
  listCompetitions: (params?: AdminListParams) => {
    const query = new URLSearchParams();
    Object.entries(params || {}).forEach(([key, value]) => {
      if (value !== undefined && value !== "") query.set(key, String(value));
    });
    const qs = query.toString();
    return adminRequest<AdminPaginatedResponse<CompetitionAdmin>>(`/competitions/${qs ? `?${qs}` : ""}`);
  },

  getCompetition: (id: number) =>
    adminRequest<CompetitionAdmin>(`/competitions/${id}/`),

  createCompetition: (data: Partial<CompetitionAdmin>) =>
    adminRequest<CompetitionAdmin>("/competitions/", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  updateCompetition: (id: number, data: Partial<CompetitionAdmin>) =>
    adminRequest<CompetitionAdmin>(`/competitions/${id}/`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  deleteCompetition: (id: number) =>
    adminRequest(`/competitions/${id}/`, { method: "DELETE" }),

  publishCompetition: (id: number) =>
    adminRequest<CompetitionAdmin>(`/competitions/${id}/publish/`, { method: "POST" }),

  unpublishCompetition: (id: number) =>
    adminRequest<CompetitionAdmin>(`/competitions/${id}/unpublish/`, { method: "POST" }),

  archiveCompetition: (id: number) =>
    adminRequest<CompetitionAdmin>(`/competitions/${id}/archive/`, { method: "POST" }),

  unarchiveCompetition: (id: number) =>
    adminRequest<CompetitionAdmin>(`/competitions/${id}/unarchive/`, { method: "POST" }),

  // Achievements
  listAchievements: (params?: AdminListParams) => {
    const query = new URLSearchParams();
    Object.entries(params || {}).forEach(([key, value]) => {
      if (value !== undefined && value !== "") query.set(key, String(value));
    });
    const qs = query.toString();
    return adminRequest<AdminPaginatedResponse<AchievementAdmin>>(`/achievements/${qs ? `?${qs}` : ""}`);
  },

  getAchievement: (id: number) =>
    adminRequest<AchievementAdmin>(`/achievements/${id}/`),

  createAchievement: (data: Partial<AchievementAdmin>) =>
    adminRequest<AchievementAdmin>("/achievements/", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  updateAchievement: (id: number, data: Partial<AchievementAdmin>) =>
    adminRequest<AchievementAdmin>(`/achievements/${id}/`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  deleteAchievement: (id: number) =>
    adminRequest(`/achievements/${id}/`, { method: "DELETE" }),

  // Certificates
  listCertificates: (params?: AdminListParams) => {
    const query = new URLSearchParams();
    Object.entries(params || {}).forEach(([key, value]) => {
      if (value !== undefined && value !== "") query.set(key, String(value));
    });
    const qs = query.toString();
    return adminRequest<AdminPaginatedResponse<CertificateAdmin>>(`/certificates/${qs ? `?${qs}` : ""}`);
  },

  getCertificate: (id: number) =>
    adminRequest<CertificateAdmin>(`/certificates/${id}/`),

  revokeCertificate: (id: number) =>
    adminRequest<CertificateAdmin>(`/certificates/${id}/revoke/`, { method: "POST" }),

  // Announcements
  listAnnouncements: (params?: AdminListParams) => {
    const query = new URLSearchParams();
    Object.entries(params || {}).forEach(([key, value]) => {
      if (value !== undefined && value !== "") query.set(key, String(value));
    });
    const qs = query.toString();
    return adminRequest<AdminPaginatedResponse<AnnouncementAdmin>>(`/announcements/${qs ? `?${qs}` : ""}`);
  },

  getAnnouncement: (id: number) =>
    adminRequest<AnnouncementAdmin>(`/announcements/${id}/`),

  createAnnouncement: (data: Partial<AnnouncementAdmin>) =>
    adminRequest<AnnouncementAdmin>("/announcements/", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  updateAnnouncement: (id: number, data: Partial<AnnouncementAdmin>) =>
    adminRequest<AnnouncementAdmin>(`/announcements/${id}/`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  deleteAnnouncement: (id: number) =>
    adminRequest(`/announcements/${id}/`, { method: "DELETE" }),

  publishAnnouncement: (id: number) =>
    adminRequest<AnnouncementAdmin>(`/announcements/${id}/publish/`, { method: "POST" }),

  unpublishAnnouncement: (id: number) =>
    adminRequest<AnnouncementAdmin>(`/announcements/${id}/unpublish/`, { method: "POST" }),

  archiveAnnouncement: (id: number) =>
    adminRequest<AnnouncementAdmin>(`/announcements/${id}/archive/`, { method: "POST" }),

  emailDraftAnnouncement: (id: number) =>
    adminRequest<EmailCampaignAdmin>(`/announcements/${id}/email-draft/`, { method: "POST" }),

  // Platform Updates / Changelog
  listPlatformUpdates: (params?: AdminListParams) => {
    const query = new URLSearchParams();
    Object.entries(params || {}).forEach(([key, value]) => {
      if (value !== undefined && value !== "") query.set(key, String(value));
    });
    const qs = query.toString();
    return adminRequest<AdminPaginatedResponse<PlatformUpdateAdmin>>(`/platform-updates/${qs ? `?${qs}` : ""}`);
  },

  getPlatformUpdate: (id: number) =>
    adminRequest<PlatformUpdateAdmin>(`/platform-updates/${id}/`),

  createPlatformUpdate: (data: Partial<PlatformUpdateAdmin>) =>
    adminRequest<PlatformUpdateAdmin>("/platform-updates/", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  updatePlatformUpdate: (id: number, data: Partial<PlatformUpdateAdmin>) =>
    adminRequest<PlatformUpdateAdmin>(`/platform-updates/${id}/`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  deletePlatformUpdate: (id: number) =>
    adminRequest(`/platform-updates/${id}/`, { method: "DELETE" }),

  publishPlatformUpdate: (id: number) =>
    adminRequest<PlatformUpdateAdmin>(`/platform-updates/${id}/publish/`, { method: "POST" }),

  unpublishPlatformUpdate: (id: number) =>
    adminRequest<PlatformUpdateAdmin>(`/platform-updates/${id}/unpublish/`, { method: "POST" }),

  archivePlatformUpdate: (id: number) =>
    adminRequest<PlatformUpdateAdmin>(`/platform-updates/${id}/archive/`, { method: "POST" }),

  emailDraftPlatformUpdate: (id: number) =>
    adminRequest<EmailCampaignAdmin>(`/platform-updates/${id}/email-draft/`, { method: "POST" }),

  // Hackathon registration form builder
  listFormFields: (params?: AdminListParams & { competition?: number }) => {
    const query = new URLSearchParams();
    Object.entries(params || {}).forEach(([key, value]) => {
      if (value !== undefined && value !== "") query.set(key, String(value));
    });
    const qs = query.toString();
    return adminRequest<AdminPaginatedResponse<RegistrationFormFieldAdmin>>(`/registration-form-fields/${qs ? `?${qs}` : ""}`);
  },

  createFormField: (data: Partial<RegistrationFormFieldAdmin>) =>
    adminRequest<RegistrationFormFieldAdmin>("/registration-form-fields/", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  updateFormField: (id: number, data: Partial<RegistrationFormFieldAdmin>) =>
    adminRequest<RegistrationFormFieldAdmin>(`/registration-form-fields/${id}/`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  deleteFormField: (id: number) =>
    adminRequest(`/registration-form-fields/${id}/`, { method: "DELETE" }),

  reorderFormFields: (items: Array<{ id: number; order: number }>) =>
    adminRequest("/registration-form-fields/reorder/", {
      method: "POST",
      body: JSON.stringify({ items }),
    }),

  resetFormDefaults: (competition: number) =>
    adminRequest<{ created: number }>("/registration-form-fields/reset-defaults/", {
      method: "POST",
      body: JSON.stringify({ competition }),
    }),

  // Hackathon applications / registrations
  listRegistrations: (params?: AdminListParams & { competition?: number; status?: string }) => {
    const query = new URLSearchParams();
    Object.entries(params || {}).forEach(([key, value]) => {
      if (value !== undefined && value !== "") query.set(key, String(value));
    });
    const qs = query.toString();
    return adminRequest<AdminPaginatedResponse<CompetitionRegistrationAdmin>>(`/hackathon-registrations/${qs ? `?${qs}` : ""}`);
  },

  updateRegistrationStatus: (id: number, status: string) =>
    adminRequest<CompetitionRegistrationAdmin>(`/hackathon-registrations/${id}/update-status/`, {
      method: "POST",
      body: JSON.stringify({ status }),
    }),

  registrationStats: (params?: { competition?: number }) => {
    const query = new URLSearchParams();
    Object.entries(params || {}).forEach(([key, value]) => {
      if (value !== undefined) query.set(key, String(value));
    });
    const qs = query.toString();
    return adminRequest<RegistrationStatsAdmin>(`/hackathon-registrations/stats/${qs ? `?${qs}` : ""}`);
  },

  // Email campaigns (Super Admin)
  listCampaigns: (params?: AdminListParams & { status?: string; date_from?: string; date_to?: string }) => {
    const query = new URLSearchParams();
    Object.entries(params || {}).forEach(([key, value]) => {
      if (value !== undefined && value !== "") query.set(key, String(value));
    });
    const qs = query.toString();
    return adminRequest<AdminPaginatedResponse<EmailCampaignAdmin>>(`/email-campaigns/${qs ? `?${qs}` : ""}`);
  },

  getCampaign: (id: number) =>
    adminRequest<EmailCampaignAdmin>(`/email-campaigns/${id}/`),

  createCampaign: (data: Partial<EmailCampaignAdmin>) =>
    adminRequest<EmailCampaignAdmin>("/email-campaigns/", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  updateCampaign: (id: number, data: Partial<EmailCampaignAdmin>) =>
    adminRequest<EmailCampaignAdmin>(`/email-campaigns/${id}/`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  deleteCampaign: (id: number) =>
    adminRequest(`/email-campaigns/${id}/`, { method: "DELETE" }),

  campaignAudienceCount: (id: number) =>
    adminRequest<{ audience: string; count: number }>(`/email-campaigns/${id}/audience-count/`),

  campaignPreview: (id: number, asUser?: number) =>
    adminRequest<{ html: string; text: string; subject?: string }>(
      `/email-campaigns/${id}/preview/${asUser ? `?as_user=${asUser}` : ""}`,
    ),

  campaignTest: (id: number, to?: string) =>
    adminRequest<{ ok: boolean; status: string; error?: string; detail?: string }>(`/email-campaigns/${id}/test/`, {
      method: "POST",
      body: JSON.stringify(to ? { to } : {}),
    }),

  campaignSend: (id: number) =>
    adminRequest<{ status: string; estimated_recipients: number }>(`/email-campaigns/${id}/send/`, {
      method: "POST",
      body: JSON.stringify({ confirm: true }),
    }),

  campaignResendFailed: (id: number) =>
    adminRequest<{ status: string; resending: number }>(`/email-campaigns/${id}/resend-failed/`, {
      method: "POST",
      body: JSON.stringify({ confirm: true }),
    }),

  campaignDuplicate: (id: number) =>
    adminRequest<EmailCampaignAdmin>(`/email-campaigns/${id}/duplicate/`, { method: "POST" }),

  // Email Templates library (Super Admin). Content only — using a template
  // never sends anything; it just seeds the composer with saved copy.
  listTemplates: (params?: AdminListParams & { category?: string }) => {
    const query = new URLSearchParams();
    Object.entries(params || {}).forEach(([key, value]) => {
      if (value !== undefined && value !== "") query.set(key, String(value));
    });
    const qs = query.toString();
    return adminRequest<AdminPaginatedResponse<EmailTemplateAdmin>>(`/email-templates/${qs ? `?${qs}` : ""}`);
  },

  getTemplate: (id: number) =>
    adminRequest<EmailTemplateAdmin>(`/email-templates/${id}/`),

  createTemplate: (data: Partial<EmailTemplateAdmin>) =>
    adminRequest<EmailTemplateAdmin>("/email-templates/", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  updateTemplate: (id: number, data: Partial<EmailTemplateAdmin>) =>
    adminRequest<EmailTemplateAdmin>(`/email-templates/${id}/`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  deleteTemplate: (id: number) =>
    adminRequest(`/email-templates/${id}/`, { method: "DELETE" }),

  duplicateTemplate: (id: number) =>
    adminRequest<EmailTemplateAdmin>(`/email-templates/${id}/duplicate/`, { method: "POST" }),

  templateCategories: () =>
    adminRequest<{ categories: string[] }>("/email-templates/categories/"),

  templatePreview: (id: number) =>
    adminRequest<{ html: string; text: string; subject?: string }>(`/email-templates/${id}/preview/`),

  // "Send Official Email" composer helpers
  searchComposerStudents: (q: string) =>
    adminRequest<{ results: Array<{ id: number; name: string; email: string; student_id: string }> }>(
      `/email-campaigns/students-search/?q=${encodeURIComponent(q)}`,
    ),

  validateComposerRecipients: (data: { user_ids: number[]; emails: string[] }) =>
    adminRequest<{
      recipients: Array<{ id: number | null; name: string; email: string; student_id: string; registered: boolean }>;
      total: number;
      invalid: string[];
      duplicates_removed: string[];
    }>("/email-campaigns/validate-recipients/", { method: "POST", body: JSON.stringify(data) }),

  composerSenderIdentity: () =>
    adminRequest<{ sender_name: string; sender_email: string; reply_to: string }>(
      "/email-campaigns/sender-identity/",
    ),

  campaignRecipients: (id: number, params?: AdminListParams & { status?: string; search?: string; date_from?: string; date_to?: string }) => {
    const query = new URLSearchParams();
    Object.entries(params || {}).forEach(([key, value]) => {
      if (value !== undefined && value !== "") query.set(key, String(value));
    });
    const qs = query.toString();
    return adminRequest<AdminPaginatedResponse<EmailCampaignRecipientAdmin>>(`/email-campaigns/${id}/recipients/${qs ? `?${qs}` : ""}`);
  },

  getEmailSettings: () =>
    adminRequest<EmailSettingsAdmin>("/email/settings/"),

  listEmailThemes: () =>
    adminRequest<AdminPaginatedResponse<EmailThemeAdmin>>("/email-themes/?page_size=100"),
  listEmailAutomations: () =>
    adminRequest<AdminPaginatedResponse<EmailAutomationAdmin>>("/email-automations/?page_size=100"),
  toggleEmailAutomation: (id: number) =>
    adminRequest<EmailAutomationAdmin>(`/email-automations/${id}/toggle/`, { method: "POST" }),

  // Audit Logs
  listAuditLogs: (params?: AdminListParams) => {
    const query = new URLSearchParams();
    Object.entries(params || {}).forEach(([key, value]) => {
      if (value !== undefined && value !== "") query.set(key, String(value));
    });
    const qs = query.toString();
    return adminRequest<AdminPaginatedResponse<AuditLogAdmin>>(`/audit-logs/${qs ? `?${qs}` : ""}`);
  },

  // Settings
  getSettings: () =>
    adminRequest<PlatformSettingsAdmin>("/settings/"),

  updateSettings: (data: Partial<PlatformSettingsAdmin>) =>
    adminRequest<PlatformSettingsAdmin>("/settings/", {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  // Roles & Permissions
  listRoles: () =>
    adminRequest<Array<{ id: number; name: string; permissions: string[] }>>("/roles/"),

  createRole: (data: { name: string; permissions: string[] }) =>
    adminRequest("/roles/", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  updateRole: (id: number, data: { name: string; permissions: string[] }) =>
    adminRequest(`/roles/${id}/`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  deleteRole: (id: number) =>
    adminRequest(`/roles/${id}/`, { method: "DELETE" }),

  assignRole: (userId: number, roleId: number) =>
    adminRequest(`/users/${userId}/roles/`, {
      method: "POST",
      body: JSON.stringify({ role_id: roleId }),
    }),

  removeRole: (userId: number, roleId: number) =>
    adminRequest(`/users/${userId}/roles/${roleId}/`, { method: "DELETE" }),

  // ── Course Creation Studio ──────────────────────────────────────────────────
  listStudioCourses: (params?: AdminListParams) => {
    const query = new URLSearchParams();
    Object.entries(params || {}).forEach(([key, value]) => {
      if (value !== undefined && value !== "") query.set(key, String(value));
    });
    const qs = query.toString();
    return adminRequest<AdminPaginatedResponse<StudioCourseRow>>(`/course-studio/${qs ? `?${qs}` : ""}`);
  },

  getStudioBundle: (id: number) =>
    adminRequest<StudioBundle>(`/course-studio/${id}/bundle/`),

  createStudioCourse: (data: Partial<StudioCourse>) =>
    adminRequest<StudioBundle>("/course-studio/", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // Autosave. Pass `expected_updated_at` and the server answers 409 when another tab
  // has already written the course, instead of silently losing the edit.
  saveStudioCourse: (id: number, data: Record<string, unknown>) =>
    adminRequest<StudioBundle>(`/course-studio/${id}/`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  studioCreateChapter: (courseId: number, data: Partial<StudioChapter>) =>
    adminRequest<StudioChapter>(`/course-studio/${courseId}/chapters/`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  studioUpdateChapter: (courseId: number, chapterId: number, data: Partial<StudioChapter>) =>
    adminRequest<StudioChapter>(`/course-studio/${courseId}/chapters/${chapterId}/`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  studioDeleteChapter: (courseId: number, chapterId: number) =>
    adminRequest(`/course-studio/${courseId}/chapters/${chapterId}/`, { method: "DELETE" }),

  duplicateChapter: (courseId: number, chapterId: number) =>
    adminRequest<StudioChapter>(`/course-studio/${courseId}/chapters/${chapterId}/duplicate/`, {
      method: "POST",
    }),

  studioReorderChapters: (courseId: number, items: Array<{ id: number; order: number }>) =>
    adminRequest(`/course-studio/${courseId}/chapters/reorder/`, {
      method: "POST",
      body: JSON.stringify({ items }),
    }),

  studioCreateLesson: (courseId: number, data: Partial<StudioLesson> & { chapter: number }) =>
    adminRequest<StudioLesson>(`/course-studio/${courseId}/lessons/`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  studioUpdateLesson: (
    courseId: number,
    lessonId: number,
    data: Partial<StudioLesson> & { expected_updated_at?: string }
  ) =>
    adminRequest<StudioLesson>(`/course-studio/${courseId}/lessons/${lessonId}/`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  studioDeleteLesson: (courseId: number, lessonId: number) =>
    adminRequest(`/course-studio/${courseId}/lessons/${lessonId}/`, { method: "DELETE" }),

  duplicateLesson: (courseId: number, lessonId: number) =>
    adminRequest<StudioLesson>(`/course-studio/${courseId}/lessons/${lessonId}/duplicate/`, {
      method: "POST",
    }),

  moveLesson: (courseId: number, lessonId: number, data: { chapter?: number; order?: number }) =>
    adminRequest<StudioLesson>(`/course-studio/${courseId}/lessons/${lessonId}/move/`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  studioReorderLessons: (
    courseId: number,
    items: Array<{ id: number; order: number; chapter?: number | null }>
  ) =>
    adminRequest(`/course-studio/${courseId}/lessons/reorder/`, {
      method: "POST",
      body: JSON.stringify({ items }),
    }),

  studioCreateExercise: (
    courseId: number,
    lessonId: number,
    data: Partial<ExerciseAdmin> & { chapter?: number }
  ) =>
    adminRequest<ExerciseAdmin>(
      `/course-studio/${courseId}/lessons/${lessonId}/exercises/`,
      { method: "POST", body: JSON.stringify(data) }
    ),

  studioUpdateExercise: (
    courseId: number,
    lessonId: number,
    exerciseId: number,
    data: Partial<ExerciseAdmin>
  ) =>
    adminRequest<ExerciseAdmin>(
      `/course-studio/${courseId}/lessons/${lessonId}/exercises/${exerciseId}/`,
      { method: "PATCH", body: JSON.stringify(data) }
    ),

  studioDeleteExercise: (courseId: number, lessonId: number, exerciseId: number) =>
    adminRequest(
      `/course-studio/${courseId}/lessons/${lessonId}/exercises/${exerciseId}/`,
      { method: "DELETE" }
    ),

  bulkPublishLessons: (courseId: number, lessons: number[], isActive = true) =>
    adminRequest<{ status: string; updated: number; checklist: PublishChecklist }>(
      `/course-studio/${courseId}/lessons/bulk-publish/`,
      { method: "POST", body: JSON.stringify({ lessons, is_active: isActive }) }
    ),

  getPublishChecklist: (courseId: number) =>
    adminRequest<PublishChecklist>(`/course-studio/${courseId}/checklist/`),

  publishStudioCourse: (courseId: number, data: { force?: boolean; override_reason?: string } = {}) =>
    adminRequest<StudioBundle>(`/course-studio/${courseId}/publish/`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  unpublishStudioCourse: (courseId: number) =>
    adminRequest<StudioBundle>(`/course-studio/${courseId}/unpublish/`, { method: "POST" }),

  scheduleStudioCourse: (courseId: number, publishAt: string) =>
    adminRequest<StudioBundle>(`/course-studio/${courseId}/schedule/`, {
      method: "POST",
      body: JSON.stringify({ publish_at: publishAt }),
    }),

  unscheduleStudioCourse: (courseId: number) =>
    adminRequest<StudioBundle>(`/course-studio/${courseId}/unschedule/`, { method: "POST" }),

  archiveStudioCourse: (courseId: number, reason?: string) =>
    adminRequest<StudioBundle>(`/course-studio/${courseId}/archive/`, {
      method: "POST",
      body: JSON.stringify(reason ? { reason } : {}),
    }),

  unarchiveStudioCourse: (courseId: number) =>
    adminRequest<StudioBundle>(`/course-studio/${courseId}/unarchive/`, { method: "POST" }),

  // ── Course categories ───────────────────────────────────────────────────────
  listCategories: () =>
    adminRequest<AdminPaginatedResponse<CourseCategoryAdmin>>("/course-categories/"),

  createCategory: (data: Partial<CourseCategoryAdmin>) =>
    adminRequest<CourseCategoryAdmin>("/course-categories/", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  updateCategory: (id: number, data: Partial<CourseCategoryAdmin>) =>
    adminRequest<CourseCategoryAdmin>(`/course-categories/${id}/`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  // ── Analytics ───────────────────────────────────────────────────────────────
  getAnalyticsOverview: (params?: { from?: string; to?: string; bucket?: string }) => {
    const query = new URLSearchParams();
    Object.entries(params || {}).forEach(([key, value]) => {
      if (value) query.set(key, String(value));
    });
    const qs = query.toString();
    return adminRequest<AnalyticsOverview>(`/analytics/overview/${qs ? `?${qs}` : ""}`);
  },
};

/**
 * Reports the analytics overview charts the data for; these are the same rows
 * rendered as a downloadable CSV. Kept in sync with ``CSV_REPORTS`` server-side -
 * an unknown name is refused there with the current list, so a stale entry here
 * fails with a message rather than silently exporting the wrong thing.
 */
export const ANALYTICS_REPORTS = [
  { id: 'registrations', label: 'Student registrations' },
  { id: 'enrollments', label: 'Course enrolments' },
  { id: 'completions', label: 'Course completions' },
  { id: 'exercise_submissions', label: 'Exercise submissions' },
  { id: 'certificates', label: 'Certificates issued' },
  { id: 'competition_registrations', label: 'Competition registrations' },
] as const;

/** Stream an analytics report straight to the browser's save dialog. */
export async function downloadAnalyticsCsv(
  report: string,
  params: { from?: string; to?: string } = {}
): Promise<void> {
  const base = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";
  const query = new URLSearchParams({ report });
  Object.entries(params).forEach(([key, value]) => {
    if (value) query.set(key, value);
  });
  let token = getAccessToken();
  if (!token) token = await refreshAccessToken();
  const res = await fetch(`${base}/admin/analytics/export/?${query}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    credentials: "include",
  });
  if (!res.ok) throw new Error("The CSV export could not be generated.");
  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = `codeyaar-${report}.csv`;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  window.URL.revokeObjectURL(url);
}

/**
 * Download the filtered hackathon registrations as a CSV file. The endpoint
 * streams text/csv, so this bypasses the JSON `request` helper and triggers a
 * browser save with the caller's active access token.
 */
export async function downloadRegistrationsCsv(
  params: { competition?: number; status?: string; search?: string } = {}
): Promise<void> {
  const base = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== "") query.set(key, String(value));
  });
  let token = getAccessToken();
  if (!token) token = await refreshAccessToken();
  const res = await fetch(`${base}/admin/hackathon-registrations/export_csv/?${query}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    credentials: "include",
  });
  if (!res.ok) throw new Error("The CSV export could not be generated.");
  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = "hackathon-registrations.csv";
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  window.URL.revokeObjectURL(url);
}