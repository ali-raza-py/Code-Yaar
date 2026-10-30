'use client';

import { ExerciseDetail, ExerciseResult, Hint } from '@/types';

interface ExercisePanelProps {
  exercise: ExerciseDetail;
  revealedHints: Hint[];
  hintsLoading: boolean;
  onHint: () => void;
  result: ExerciseResult | null;
  selectedAnswer: string | string[] | null;
  onAnswerChange: (answer: string | string[]) => void;
  textAnswer: string;
  onTextAnswerChange: (value: string) => void;
  authRequired: boolean;
}

export default function ExercisePanel({
  exercise,
  revealedHints,
  hintsLoading,
  onHint,
  result,
  selectedAnswer,
  onAnswerChange,
  textAnswer,
  onTextAnswerChange,
  authRequired,
}: ExercisePanelProps) {
  const isSuccess = result?.status === 'correct';
  const isFailure = result?.status === 'incorrect';
  const isPending = result?.status === 'running';
  const isChoiceType = exercise.exercise_type === 'multiple_choice' || exercise.exercise_type === 'multiple_select';
  const isTextAnswerType = exercise.exercise_type === 'output_prediction' || exercise.exercise_type === 'fill_blank';
  const hasMoreHints = revealedHints.length < exercise.hints.length;

  const toggleChoice = (id: string) => {
    if (exercise.exercise_type === 'multiple_choice') {
      onAnswerChange(id);
      return;
    }
    const current = Array.isArray(selectedAnswer) ? selectedAnswer : [];
    onAnswerChange(current.includes(id) ? current.filter((x) => x !== id) : [...current, id]);
  };

  return (
    <div className="max-h-[280px] overflow-y-auto border-b border-[var(--editor-border)] bg-[var(--editor-chrome)]">
      <div className="px-4 py-3">
        {/* Exercise Header */}
        <div className="mb-2 flex items-center justify-between">
          <h3 className="text-sm font-semibold text-white">{exercise.title}</h3>
          <span className="inline-flex items-center rounded-pill bg-success/15 px-2 py-0.5 text-xs font-medium text-success">
            +{exercise.xp_reward} XP
          </span>
        </div>

        {/* Instructions */}
        <div className="mb-2 text-sm text-white/80">
          <p className="mb-1 font-medium text-white">Your task</p>
          <p className="whitespace-pre-wrap">{exercise.instructions}</p>
        </div>

        {/* Context */}
        {exercise.context && (
          <p className="mb-2 text-xs text-white/55">{exercise.context}</p>
        )}

        {/* Constraints */}
        {exercise.constraints && (
          <div className="mb-2 text-xs text-white/55">
            <span className="font-medium">Constraints: </span>
            {exercise.constraints}
          </div>
        )}

        {/* Answer form for non-code exercises */}
        {isChoiceType && exercise.choices.length > 0 && (
          <fieldset className="mb-2 space-y-1.5">
            <legend className="sr-only">Choose your answer</legend>
            {exercise.choices.map((choice) => {
              const checked = isMultiSelect(exercise)
                ? Array.isArray(selectedAnswer) && selectedAnswer.includes(choice.id)
                : selectedAnswer === choice.id;
              return (
                <label
                  key={choice.id}
                  className={`flex cursor-pointer items-center gap-2 rounded-lg border px-3 py-2 text-sm transition-colors ${
                    checked
                      ? 'border-cta/50 bg-cta/10 text-white'
                      : 'border-[var(--overlay-border)] text-white/75 hover:bg-white/5'
                  }`}
                >
                  <input
                    type={isMultiSelect(exercise) ? 'checkbox' : 'radio'}
                    name="exercise-choice"
                    checked={checked}
                    onChange={() => toggleChoice(choice.id)}
                    className="accent-[var(--primary)]"
                  />
                  <span>{choice.text}</span>
                </label>
              );
            })}
          </fieldset>
        )}

        {isTextAnswerType && (
          <div className="mb-2">
            <label className="mb-1 block text-xs font-medium text-white/70">
              {exercise.exercise_type === 'output_prediction' ? 'Your predicted output' : 'Your answer'}
            </label>
            <textarea
              value={textAnswer}
              onChange={(e) => onTextAnswerChange(e.target.value)}
              rows={3}
              spellCheck={false}
              placeholder={exercise.exercise_type === 'output_prediction' ? 'What does the code print?' : 'Type your answer'}
              className="w-full resize-y rounded-lg border border-[var(--overlay-border)] bg-black/20 px-3 py-2 font-mono text-xs text-white placeholder:text-white/35 focus:border-cta/60 focus:outline-none"
            />
          </div>
        )}

        {authRequired && (
          <p className="mb-2 rounded-lg border border-info/25 bg-info/10 px-3 py-2 text-xs text-white/80">
            Sign in to run code and submit answers for grading.
          </p>
        )}

        {/* Hints (revealed one at a time via API) */}
        {revealedHints.length > 0 && (
          <div className="mt-3 space-y-2">
            {revealedHints.map((hint) => (
              <div
                key={hint.id ?? hint.order}
                className={`rounded-lg border px-3 py-2 text-xs ${
                  hint.reveals_solution
                    ? 'border-warning/30 bg-warning/10 text-white/85'
                    : 'border-info/25 bg-info/10 text-white/85'
                }`}
              >
                <span className="font-medium">
                  {hint.reveals_solution ? 'Solution: ' : `Hint ${hint.order}: `}
                </span>
                {hint.content}
              </div>
            ))}
            {!isSuccess && hasMoreHints && (
              <button
                onClick={onHint}
                disabled={hintsLoading}
                className="focus-ring rounded text-xs font-medium text-info transition-colors hover:text-white disabled:opacity-50"
              >
                {hintsLoading ? 'Loading…' : 'Show stronger hint'}
              </button>
            )}
          </div>
        )}

        {/* Feedback */}
        {isSuccess && (
          <div className="mt-3 rounded-lg border border-success/30 bg-success/10 px-3 py-2">
            <div className="flex items-center gap-2">
              <svg className="h-4 w-4 text-success" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="text-sm font-semibold text-success">Correct!</span>
            </div>
            <p className="mt-1 text-xs text-white/75">{result.feedback}</p>
            <p className="mt-1 text-xs font-medium text-success">+{result.xp_earned} XP</p>
          </div>
        )}

        {isFailure && (
          <div className="mt-3 rounded-lg border border-danger/30 bg-danger/10 px-3 py-2">
            <div className="flex items-center gap-2">
              <svg className="h-4 w-4 text-danger" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
              </svg>
              <span className="text-sm font-semibold text-danger">Not quite.</span>
            </div>
            <p className="mt-1 text-xs text-white/75">{result.feedback}</p>
          </div>
        )}

        {isPending && (
          <div className="mt-3 rounded-lg border border-warning/30 bg-warning/10 px-3 py-2">
            <div className="flex items-center gap-2">
              <svg className="h-4 w-4 text-warning" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="text-sm font-semibold text-warning">Recorded — not yet graded</span>
            </div>
            <p className="mt-1 text-xs text-white/75">
              {result.feedback || 'Your submission has been saved. Automated code evaluation is not available yet, so no XP was awarded.'}
            </p>
          </div>
        )}

        {/* Explanation — revealed only after the learner has attempted */}
        {result && result.explain && (
          <div className="mt-3 rounded-lg border border-[var(--overlay-border)] bg-white/5 px-3 py-2">
            <p className="text-xs font-medium text-white/85">Explanation</p>
            <p className="mt-1 whitespace-pre-wrap text-xs text-white/70">{result.explain}</p>
          </div>
        )}

        {/* Hint Button (if none revealed yet) */}
        {revealedHints.length === 0 && !result && hasMoreHints && (
          <button
            onClick={onHint}
            disabled={hintsLoading}
            className="focus-ring mt-2 rounded text-xs font-medium text-info transition-colors hover:text-white disabled:opacity-50"
          >
            {hintsLoading ? 'Loading…' : 'Need help? Get a hint'}
          </button>
        )}
      </div>
    </div>
  );
}

function isMultiSelect(exercise: ExerciseDetail): boolean {
  return exercise.exercise_type === 'multiple_select';
}
