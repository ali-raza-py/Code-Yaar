export interface Project {
  id: number;
  slug: string;
  title: string;
  description: string;
  thumbnail?: string;
  difficulty: "beginner" | "intermediate" | "advanced";
  technologies: string[];
  estimated_hours: number;
  track?: number | null;
  track_title?: string | null;
  milestones: ProjectMilestone[];
}

export interface ProjectMilestone {
  id: number;
  title: string;
  description: string;
  order: number;
}

export interface Challenge {
  id: number;
  slug: string;
  title: string;
  description: string;
  difficulty: "beginner" | "intermediate" | "advanced";
  topic: string;
  estimated_minutes: number;
  xp_reward: number;
  starter_code?: string;
  solved?: boolean;
  attempts?: number;
}

export interface ChallengeExample {
  input: string;
  output: string;
  explanation?: string;
}

export interface ChallengeDetail extends Challenge {
  languages: string[];
  starter_code_cpp?: string;
  problem_statement: string;
  requirements: string[];
  input_description: string;
  output_description: string;
  constraints: string[];
  examples: ChallengeExample[];
  hints: string[];
  time_complexity: string;
  space_complexity: string;
  sample_tests: { input: string; expected_output: string }[];
  attempts: number;
}

export interface ChallengeTestResult {
  test: number;
  status: string;
  message: string;
  expected?: string;
  actual?: string;
}

export interface ChallengeRunResult {
  status: string;
  output: string;
  error: string;
  test_results: ChallengeTestResult[];
  summary?: string;
}

/**
 * A badge the server just awarded, echoed on a completion response so the
 * client can raise a toast. Mirrors `BadgeUnlock` in the API client.
 */
export interface BadgeUnlockPayload {
  slug: string;
  title: string;
  description: string;
  icon: string;
  category: string;
  difficulty: string;
  xp_bonus: number;
  public_id: string;
  credential_id: string;
}

export interface ChallengeSubmitResult {
  status: string;
  feedback: string;
  test_results: ChallengeTestResult[];
  xp_earned: number;
  xp_total?: number;
  solved: boolean;
  attempt_id?: number;
  duplicate?: boolean;
  solution_explanation?: string;
  time_complexity?: string;
  space_complexity?: string;
  reference_solution?: string;
  /** Badges unlocked by this submission — drives the unlock toast. */
  awarded_badges?: BadgeUnlockPayload[];
}

export type CompetitionStatus =
  | "draft" | "upcoming" | "registration_open" | "registration_closing_soon"
  | "registration_closed" | "ongoing" | "submission_open" | "judging" | "completed";

export interface Competition {
  id: number;
  slug: string;
  title: string;
  short_description: string;
  banner: string;
  category: string;
  difficulty: Difficulty;
  format: "individual" | "team" | "both";
  delivery_mode: "online" | "offline" | "hybrid";
  registration_deadline: string;
  competition_start: string;
  competition_end: string;
  participant_limit: number | null;
  participant_count: number;
  prize_information: string;
  status: CompetitionStatus;
  organizer_name: string;
  registration_status: string | null;
}

export interface CompetitionDetail extends Competition {
  description: string;
  location: string;
  registration_start: string;
  submission_deadline: string;
  judging_end: string | null;
  results_announcement: string | null;
  minimum_team_size: number;
  maximum_team_size: number;
  eligibility_rules: string[];
  competition_rules: string[];
  problem_statement: string;
  submission_configuration: Record<string, unknown>;
}

export interface CompetitionRegistration {
  id: number;
  reference: string;
  team: number | null;
  registration_status: string;
  registration_data: Record<string, unknown>;
  rules_accepted_at: string;
  registered_at: string;
}

export interface CompetitionSubmission {
  id: number;
  competition_slug: string;
  project_title: string;
  description: string;
  github_url: string;
  demo_url: string;
  additional_data: Record<string, unknown>;
  status: string;
  organizer_feedback: string;
  submitted_at: string | null;
  updated_at: string;
}

export interface CompetitionResult {
  rank: number;
  participant_name: string;
  project_title: string;
  final_score: string;
  award: string;
}

export interface LearningPath {
  id: string;
  title: string;
  description: string;
  concepts: string[];
  status: "available" | "coming-soon";
}

export interface RoadmapStage {
  id: string;
  number: number;
  title: string;
  description: string;
  status: "locked" | "available" | "current" | "completed";
  progress?: number;
  prerequisites?: string[];
  milestones: Milestone[];
  estimatedMinutes: number;
  skills: string[];
}

export interface Milestone {
  id: string;
  title: string;
  description: string;
  status: "locked" | "available" | "completed";
  skills: string[];
  estimatedMinutes?: number;
}

// ─── Course System Types ────────────────────────────────────────────────────

export type Difficulty = 'beginner' | 'intermediate' | 'advanced';
export type ExerciseType = 'code' | 'multiple_choice' | 'multiple_select' | 'debugging' | 'output_prediction' | 'fill_blank';
export type LessonContentType = 'video' | 'text' | 'interactive' | 'exercise';
export type LessonStatus = 'not_started' | 'in_progress' | 'completed' | 'needs_practice' | 'mastered';
export type ExerciseStatus = 'running' | 'incorrect' | 'correct' | 'error';
export type ExerciseLanguage = 'python' | 'javascript' | 'cpp' | 'java' | 'none';

export interface Course {
  id: number;
  slug: string;
  title: string;
  subtitle: string;
  description: string;
  thumbnail: string;
  track: number;
  track_title: string;
  academic_class?: string;
  difficulty: Difficulty;
  language: string;
  estimated_hours: number;
  total_xp: number;
  instructor: string;
  prerequisites: string;
  learning_objectives: string[];
  is_free: boolean;
  chapters?: Chapter[];
  resources?: Resource[];
  lesson_count: number;
  exercise_count: number;
  chapter_count?: number;
  enrolled: boolean;
  enrollment_id?: number;
  resume_lesson?: LessonSummary;
  progress_percentage?: number;
}

/**
 * Curriculum provenance, straight from the board textbook. Present only on
 * textbook-derived content — general catalogue courses return null so their UI
 * is unchanged. `source_type` is what keeps supplementary practice from being
 * shown as official Sindh Board syllabus.
 */
export interface TextbookReference {
  source_type: 'official' | 'supplementary' | 'additional';
  verification_status: '' | 'unverified' | 'verified' | 'needs_review';
  board: string;
  class: string;
  unit: string;
  topic: string;
  pages: string;
  label: string;
}

export interface Chapter {
  id: number;
  title: string;
  slug: string;
  description?: string;
  order: number;
  xp_reward: number;
  lessons: LessonSummary[];
  progress_percentage: number;
  exercise_count?: number;
  // True for the closing quiz chapter, which the sidebar always shows last.
  is_final_assessment?: boolean;
  textbook_reference?: TextbookReference | null;
}

export interface LessonSummary {
  id: number;
  title: string;
  slug: string;
  content_type: LessonContentType;
  order: number;
  duration_minutes: number;
  xp_reward: number;
  exercise_count: number;
  progress_status: LessonStatus;
}

export interface LessonDetail extends LessonSummary {
  chapter_title: string;
  course_title: string;
  course_slug: string;
  learning_objective: string;
  content_body: string;
  video_url: string;
  video_duration_seconds: number;
  is_free_preview: boolean;
  exercises: ExerciseSummary[];
  prev_lesson: { slug: string; title: string } | null;
  next_lesson: { slug: string; title: string } | null;
  textbook_reference?: TextbookReference | null;
}

export interface ExerciseSummary {
  id: number;
  title: string;
  slug: string;
  exercise_type: ExerciseType;
  difficulty: string;
  language: ExerciseLanguage;
  xp_reward: number;
  order: number;
  hint_count: number;
  textbook_reference?: TextbookReference | null;
}

export interface ExerciseDetail {
  id: number;
  title: string;
  slug: string;
  exercise_type: ExerciseType;
  difficulty: string;
  language: ExerciseLanguage;
  lesson_title: string;
  chapter_title: string;
  instructions: string;
  context: string;
  constraints: string;
  expected_behavior: string;
  starter_code: string;
  expected_output: string;
  choices: ExerciseChoice[];
  test_cases?: TestCase[];
  xp_reward: number;
  max_attempts: number;
  order: number;
  hints: Hint[];
}

export interface ExerciseChoice {
  id: string;
  text: string;
  // Correctness is intentionally never sent to clients; grading is server-side.
  is_correct?: boolean;
}

export interface TestCase {
  input?: string;
  expected_output?: string;
  variable?: string;
  expected_value?: unknown;
}

export interface Hint {
  id: number;
  content: string;
  order: number;
  reveals_solution: boolean;
  xp_penalty: number;
}

export interface ExerciseResult {
  status: ExerciseStatus;
  feedback: string;
  output: string;
  error: string;
  test_results: TestResult[];
  xp_earned: number;
  correct_answer?: unknown;
  explain?: string;
  attempt_id: number;
  /** Badges unlocked by this action — drives the unlock toast. */
  awarded_badges?: BadgeUnlockPayload[];
}

export interface TestResult {
  test: number;
  status: string;
  message: string;
}

export interface Resource {
  id: number;
  title: string;
  description: string;
  resource_type: string;
  file_url: string;
  file_name: string;
  file_size_bytes: number;
  order: number;
}

export interface Enrollment {
  id: number;
  course: number;
  course_slug: string;
  course_title: string;
  track_title: string;
  enrolled_at: string;
  completed_at: string | null;
  last_activity_at: string | null;
  status: string;
  progress_percentage: number;
}

export interface PracticalClass {
  id: number;
  slug: string;
  title: string;
  board: "stb";
  is_published?: boolean;
  description: string;
  order: number;
  subject_count: number;
}

export interface PracticalSubject {
  id: number;
  slug: string;
  title: string;
  description: string;
  order: number;
  class_title: string;
  class_slug: string;
  practical_count: number;
}

export interface PracticalSummary {
  id: number;
  slug: string;
  title: string;
  description: string;
  practical_number: number;
  chapter_topic: string;
  subject_title: string;
  class_title: string;
  order: number;
  is_completed: boolean;
  is_bookmarked: boolean;
}

export interface PracticalDiagram {
  url: string;
  caption?: string;
}

export interface PracticalDetail extends PracticalSummary {
  aim: string;
  apparatus: string;
  theory: string;
  procedure: string;
  observations: string;
  calculations: string;
  result: string;
  precautions: string;
  diagrams: PracticalDiagram[];
}

export interface PracticalClassAdmin extends PracticalClass {
  thumbnail: string;
  is_active: boolean;
}

export interface PracticalSubjectAdmin extends PracticalSubject {
  practical_class: number;
  image: string;
  is_active: boolean;
}

export interface PracticalAdmin extends PracticalDetail {
  practical_class: number;
  subject: number;
  slug: string;
  is_published: boolean;
  is_active: boolean;
}
