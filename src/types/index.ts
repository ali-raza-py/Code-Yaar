export interface Project {
  id: string;
  slug: string;
  title: string;
  description: string;
  difficulty: "beginner" | "intermediate" | "advanced";
  technologies: string[];
  estimatedHours: number;
  skillsDeveloped: string[];
  milestones: ProjectMilestone[];
  status: "available" | "coming-soon";
}

export interface ProjectMilestone {
  id: string;
  title: string;
  description: string;
  completed: boolean;
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
  progress_percentage: number;
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
  learning_objective: string;
  content_body: string;
  video_url: string;
  video_duration_seconds: number;
  is_free_preview: boolean;
  exercises: ExerciseSummary[];
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
  solution_code: string;
  expected_output: string;
  choices: ExerciseChoice[];
  test_cases: TestCase[];
  xp_reward: number;
  max_attempts: number;
  order: number;
  hints: Hint[];
}

export interface ExerciseChoice {
  id: string;
  text: string;
  is_correct: boolean;
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
  attempt_id: number;
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
