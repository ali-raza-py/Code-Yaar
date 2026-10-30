'use client';

import { ExerciseResult } from '@/types';

interface OutputPanelProps {
  output: string;
  isRunning: boolean;
  result: ExerciseResult | null;
}

export default function OutputPanel({ output, isRunning, result }: OutputPanelProps) {
  const hasOutput = output || isRunning;
  const isError = result?.status === 'error' || Boolean(result?.error);

  return (
    <div className="flex min-h-0 flex-1 flex-col overflow-hidden editor-surface">
      {/* Tab — matches editor chrome */}
      <div className="flex shrink-0 items-center gap-3 border-b editor-chrome px-3 py-1">
        <span className="seg-tab">Output</span>
        {isRunning && (
          <span className="flex items-center gap-1 text-[10px] text-amber">
            <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-amber" />
            Running...
          </span>
        )}
      </div>

      {/* Content */}
      <div className="min-h-0 flex-1 overflow-auto p-3" role="log" aria-live="polite">
        {!hasOutput && !result && (
          <p className="font-mono text-xs text-white/60">
            Run your code to see output.
          </p>
        )}

        {hasOutput && (
          <pre className={`whitespace-pre-wrap font-mono text-xs ${isError ? 'text-[var(--syn-invalid)]' : 'text-[var(--syn-string)]'}`}>
            {output}
          </pre>
        )}

        {result?.error && (
          <pre className="whitespace-pre-wrap font-mono text-xs text-[var(--syn-invalid)]">
            {result.error}
          </pre>
        )}

        {result?.test_results && result.test_results.length > 0 && (
          <div className="mt-2 space-y-1">
            {result.test_results.map((tr, i) => (
              <div key={i} className="flex items-center gap-2 font-mono text-xs">
                <span className={tr.status === 'passed' ? 'text-success' : 'text-danger'}>
                  {tr.status === 'passed' ? '✓' : '✗'}
                </span>
                <span className="text-white/60">Test {tr.test}:</span>
                <span className={tr.status === 'passed' ? 'text-[var(--syn-string)]' : 'text-[var(--syn-invalid)]'}>
                  {tr.message}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
