'use client';

import { useState, useCallback } from 'react';
import Link from 'next/link';
import { Chapter, LessonDetail, ExerciseDetail, ExerciseResult, LessonStatus } from '@/types';
import CourseSidebar from '@/components/learning/workspace/course-sidebar';
import LessonContent from '@/components/learning/workspace/lesson-content';
import ExercisePanel from '@/components/learning/workspace/exercise-panel';
import CodeEditor from '@/components/learning/workspace/code-editor';
import OutputPanel from '@/components/learning/workspace/output-panel';
import XPBadge from '@/components/learning/workspace/xp-badge';

// ─── Mock data (will be replaced by API calls) ──────────────────────────────

const mockChapters: Chapter[] = [
  {
    id: 1, title: 'Python Basics', slug: 'python-basics', order: 1, xp_reward: 500,
    progress_percentage: 100,
    lessons: [
      { id: 1, title: 'Hello Python', slug: 'hello-python', content_type: 'text', order: 1, duration_minutes: 10, xp_reward: 50, exercise_count: 1, progress_status: 'completed' },
      { id: 2, title: 'Variables', slug: 'variables', content_type: 'text', order: 2, duration_minutes: 15, xp_reward: 50, exercise_count: 2, progress_status: 'completed' },
    ],
  },
  {
    id: 2, title: 'Control Flow', slug: 'control-flow', order: 2, xp_reward: 500,
    progress_percentage: 50,
    lessons: [
      { id: 3, title: 'Conditions', slug: 'conditions', content_type: 'text', order: 1, duration_minutes: 15, xp_reward: 50, exercise_count: 1, progress_status: 'completed' },
      { id: 4, title: 'Loops', slug: 'loops', content_type: 'text', order: 2, duration_minutes: 15, xp_reward: 50, exercise_count: 1, progress_status: 'in_progress' },
    ],
  },
  {
    id: 3, title: 'Functions', slug: 'functions', order: 3, xp_reward: 500,
    progress_percentage: 0,
    lessons: [
      { id: 5, title: 'Defining Functions', slug: 'defining-functions', content_type: 'text', order: 1, duration_minutes: 15, xp_reward: 50, exercise_count: 1, progress_status: 'not_started' },
    ],
  },
  {
    id: 4, title: 'Data Structures', slug: 'data-structures', order: 4, xp_reward: 500,
    progress_percentage: 0,
    lessons: [
      { id: 6, title: 'Lists', slug: 'lists', content_type: 'text', order: 1, duration_minutes: 15, xp_reward: 50, exercise_count: 1, progress_status: 'not_started' },
      { id: 7, title: 'Dictionaries', slug: 'dictionaries', content_type: 'text', order: 2, duration_minutes: 15, xp_reward: 50, exercise_count: 1, progress_status: 'not_started' },
    ],
  },
];

const mockLesson: LessonDetail = {
  id: 4, title: 'Loops', slug: 'loops', content_type: 'text', order: 2,
  duration_minutes: 15, xp_reward: 50, exercise_count: 1, progress_status: 'in_progress',
  chapter_title: 'Control Flow', course_title: 'Python Foundations',
  learning_objective: 'Use for loops to iterate over sequences.',
  content_body: `# For Loops

A \`for\` loop lets you repeat code for each item in a sequence:

\`\`\`python
fruits = ["apple", "banana", "cherry"]

for fruit in fruits:
    print(fruit)
\`\`\`

## The range() Function

Use \`range()\` to loop a specific number of times:

\`\`\`python
for i in range(5):
    print(i)  # Prints 0, 1, 2, 3, 4
\`\`\`

## Try it yourself

Now write a loop that prints each number from 0 to 4.`,
  video_url: '',
  video_duration_seconds: 0,
  is_free_preview: false,
  exercises: [
    {
      id: 1, title: 'Print Numbers', slug: 'print-numbers',
      exercise_type: 'code', difficulty: 'easy', language: 'python',
      xp_reward: 100, order: 1, hint_count: 3,
    },
  ],
};

const mockExercise: ExerciseDetail = {
  id: 1, title: 'Print Numbers', slug: 'print-numbers',
  exercise_type: 'code', difficulty: 'easy', language: 'python',
  lesson_title: 'Loops', chapter_title: 'Control Flow',
  instructions: 'Write a for loop that prints each number from 0 to 4, each on a new line.',
  context: 'Loops are fundamental to programming. They let you automate repetitive tasks.',
  constraints: 'Use a for loop with range().',
  expected_behavior: 'Output should be:\n0\n1\n2\n3\n4',
  starter_code: '# Write a for loop that prints numbers 0 through 4\n',
  solution_code: 'for i in range(5):\n    print(i)',
  expected_output: '0\n1\n2\n3\n4',
  choices: [],
  test_cases: [
    { expected_output: '0\n1\n2\n3\n4' },
  ],
  xp_reward: 100,
  max_attempts: 0,
  order: 1,
  hints: [
    { id: 1, content: 'Think about how range(5) generates numbers.', order: 1, reveals_solution: false, xp_penalty: 10 },
    { id: 2, content: 'Use print() inside your loop.', order: 2, reveals_solution: false, xp_penalty: 20 },
    { id: 3, content: 'Solution: for i in range(5): print(i)', order: 3, reveals_solution: true, xp_penalty: 50 },
  ],
};

// ─── Page ───────────────────────────────────────────────────────────────────

export default function LearningWorkspacePage() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [code, setCode] = useState(mockExercise.starter_code);
  const [output, setOutput] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const [exerciseResult, setExerciseResult] = useState<ExerciseResult | null>(null);
  const [currentExerciseIndex, setCurrentExerciseIndex] = useState(0);
  const [xpAnimation, setXpAnimation] = useState<number | null>(null);
  const [hintsRevealed, setHintsRevealed] = useState(0);

  const handleRun = useCallback(() => {
    setIsRunning(true);
    setOutput('Running...');
    setExerciseResult(null);

    // Simulate code execution
    setTimeout(() => {
      setOutput('Execution completed.\n\nOutput:\n0\n1\n2\n3\n4');
      setIsRunning(false);
    }, 800);
  }, []);

  const handleSubmit = useCallback(() => {
    setIsRunning(true);
    setExerciseResult(null);

    setTimeout(() => {
      const result: ExerciseResult = {
        status: 'correct',
        feedback: 'Your solution passed all checks.',
        output: '0\n1\n2\n3\n4',
        error: '',
        test_results: [
          { test: 1, status: 'passed', message: 'Output matches expected.' },
        ],
        xp_earned: mockExercise.xp_reward,
        attempt_id: 1,
      };
      setExerciseResult(result);
      setOutput('');
      setIsRunning(false);

      // Trigger XP animation
      setXpAnimation(result.xp_earned);
      setTimeout(() => setXpAnimation(null), 2000);
    }, 1200);
  }, []);

  const handleHint = useCallback(() => {
    if (hintsRevealed < mockExercise.hints.length) {
      setHintsRevealed(prev => prev + 1);
    }
  }, [hintsRevealed, mockExercise.hints.length]);

  const handleReset = useCallback(() => {
    setCode(mockExercise.starter_code);
    setOutput('');
    setExerciseResult(null);
    setHintsRevealed(0);
  }, [mockExercise.starter_code]);

  const totalLessons = mockChapters.reduce((sum, ch) => sum + ch.lessons.length, 0);
  const completedLessons = mockChapters.reduce(
    (sum, ch) => sum + ch.lessons.filter(l => l.progress_status === 'completed').length, 0
  );
  const progressPercent = Math.round((completedLessons / totalLessons) * 100);

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      {/* ── Left: Course Sidebar ────────────────────────────────── */}
      <CourseSidebar
        chapters={mockChapters}
        currentLessonId={mockLesson.id}
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
        courseProgress={progressPercent}
        courseTitle="Python Foundations"
      />

      {/* ── Main Content Area ───────────────────────────────────── */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Top Bar */}
        <header className="flex h-12 shrink-0 items-center justify-between border-b border-gray-200 bg-white px-4">
          <div className="flex items-center gap-3">
            {!sidebarOpen && (
              <button
                onClick={() => setSidebarOpen(true)}
                className="rounded p-1 text-gray-500 hover:bg-gray-100"
              >
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
                </svg>
              </button>
            )}
            <Link href="/learn" className="text-sm text-gray-500 hover:text-gray-900">
              ← Course
            </Link>
            <span className="text-gray-300">|</span>
            <span className="text-sm text-gray-600">
              Chapter 2 / Lesson 4
            </span>
          </div>
          <div className="flex items-center gap-3">
            {xpAnimation && <XPBadge amount={xpAnimation} />}
            <span className="text-sm font-medium text-gray-700">
              XP 420
            </span>
          </div>
        </header>

        {/* Content: Lesson + Editor */}
        <div className="flex flex-1 overflow-hidden">
          {/* Center: Lesson Content */}
          <div className="flex-1 overflow-y-auto border-r border-gray-200">
            <LessonContent lesson={mockLesson} />
          </div>

          {/* Right: Code Editor + Output */}
          <div className="hidden lg:flex w-[480px] flex-col overflow-hidden">
            {/* Exercise Instructions */}
            <ExercisePanel
              exercise={mockExercise}
              hintsRevealed={hintsRevealed}
              onHint={handleHint}
              result={exerciseResult}
            />

            {/* Code Editor */}
            <div className="flex-1 overflow-hidden">
              <CodeEditor
                code={code}
                onChange={setCode}
                language={mockExercise.language}
                fileName="main.py"
              />
            </div>

            {/* Output Panel */}
            <OutputPanel
              output={output}
              isRunning={isRunning}
              result={exerciseResult}
            />

            {/* Action Bar */}
            <div className="flex items-center gap-2 border-t border-gray-200 bg-white px-4 py-3">
              <button
                onClick={handleHint}
                className="rounded-lg border border-gray-300 px-3 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50 transition-colors"
              >
                Hint
              </button>
              <button
                onClick={handleReset}
                className="rounded-lg border border-gray-300 px-3 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50 transition-colors"
              >
                Reset
              </button>
              <div className="flex-1" />
              <button
                onClick={handleRun}
                disabled={isRunning}
                className="rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors disabled:opacity-50"
              >
                {isRunning ? 'Running...' : 'Run Code'}
              </button>
              <button
                onClick={handleSubmit}
                disabled={isRunning}
                className="rounded-lg bg-green-600 px-4 py-2 text-sm font-semibold text-white hover:bg-green-700 transition-colors disabled:opacity-50"
              >
                Submit Answer
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
