'use client';

import { ExerciseDetail, ExerciseResult } from '@/types';

interface ExercisePanelProps {
  exercise: ExerciseDetail;
  hintsRevealed: number;
  onHint: () => void;
  result: ExerciseResult | null;
}

export default function ExercisePanel({ exercise, hintsRevealed, onHint, result }: ExercisePanelProps) {
  const isSuccess = result?.status === 'correct';
  const isFailure = result?.status === 'incorrect';

  return (
    <div className="border-b border-gray-200 bg-white overflow-y-auto max-h-[240px]">
      <div className="px-4 py-3">
        {/* Exercise Header */}
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-semibold text-gray-900">{exercise.title}</h3>
          <span className="inline-flex items-center rounded-full bg-green-50 px-2 py-0.5 text-xs font-medium text-green-700">
            +{exercise.xp_reward} XP
          </span>
        </div>

        {/* Instructions */}
        <div className="text-sm text-gray-700 mb-2">
          <p className="font-medium text-gray-900 mb-1">Your task</p>
          <p className="whitespace-pre-wrap">{exercise.instructions}</p>
        </div>

        {/* Context */}
        {exercise.context && (
          <p className="text-xs text-gray-500 mb-2">{exercise.context}</p>
        )}

        {/* Constraints */}
        {exercise.constraints && (
          <div className="text-xs text-gray-500 mb-2">
            <span className="font-medium">Constraints: </span>
            {exercise.constraints}
          </div>
        )}

        {/* Hints */}
        {hintsRevealed > 0 && (
          <div className="mt-3 space-y-2">
            {exercise.hints.slice(0, hintsRevealed).map((hint) => (
              <div
                key={hint.id}
                className={`rounded-lg border px-3 py-2 text-xs ${
                  hint.reveals_solution
                    ? 'border-amber-200 bg-amber-50 text-amber-800'
                    : 'border-blue-200 bg-blue-50 text-blue-800'
                }`}
              >
                <span className="font-medium">
                  {hint.reveals_solution ? 'Solution: ' : `Hint ${hint.order}: `}
                </span>
                {hint.content}
              </div>
            ))}
            {!isSuccess && hintsRevealed < exercise.hints.length && (
              <button
                onClick={onHint}
                className="text-xs font-medium text-blue-600 hover:text-blue-800"
              >
                Show stronger hint
              </button>
            )}
          </div>
        )}

        {/* Feedback */}
        {isSuccess && (
          <div className="mt-3 rounded-lg border border-green-200 bg-green-50 px-3 py-2">
            <div className="flex items-center gap-2">
              <svg className="h-4 w-4 text-green-600" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="text-sm font-semibold text-green-800">Correct!</span>
            </div>
            <p className="mt-1 text-xs text-green-700">{result.feedback}</p>
            <p className="mt-1 text-xs font-medium text-green-700">+{result.xp_earned} XP</p>
          </div>
        )}

        {isFailure && (
          <div className="mt-3 rounded-lg border border-red-200 bg-red-50 px-3 py-2">
            <div className="flex items-center gap-2">
              <svg className="h-4 w-4 text-red-500" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
              </svg>
              <span className="text-sm font-semibold text-red-800">Not quite.</span>
            </div>
            <p className="mt-1 text-xs text-red-700">{result.feedback}</p>
          </div>
        )}

        {/* Hint Button (if none revealed yet) */}
        {hintsRevealed === 0 && !result && (
          <button
            onClick={onHint}
            className="mt-2 text-xs font-medium text-blue-600 hover:text-blue-800"
          >
            Need help? Get a hint
          </button>
        )}
      </div>
    </div>
  );
}
