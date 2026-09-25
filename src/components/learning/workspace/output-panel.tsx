'use client';

import { ExerciseResult } from '@/types';

interface OutputPanelProps {
  output: string;
  isRunning: boolean;
  result: ExerciseResult | null;
}

export default function OutputPanel({ output, isRunning, result }: OutputPanelProps) {
  const hasOutput = output || isRunning;
  const isError = result?.status === 'error' || (output && output.includes('Error'));

  return (
    <div className="h-28 shrink-0 border-t border-gray-200 bg-[#1e1e2e] overflow-hidden flex flex-col">
      {/* Tab */}
      <div className="flex items-center gap-3 border-b border-gray-700 bg-[#181825] px-3 py-1">
        <span className="text-[10px] font-medium text-gray-400 uppercase tracking-wider">Output</span>
        {isRunning && (
          <span className="flex items-center gap-1 text-[10px] text-yellow-400">
            <span className="h-1.5 w-1.5 rounded-full bg-yellow-400 animate-pulse" />
            Running...
          </span>
        )}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-3">
        {!hasOutput && !result && (
          <p className="text-xs text-gray-500 font-mono">
            Run your code to see output.
          </p>
        )}

        {hasOutput && (
          <pre className={`text-xs font-mono whitespace-pre-wrap ${isError ? 'text-red-400' : 'text-green-300'}`}>
            {output}
          </pre>
        )}

        {result?.error && (
          <pre className="text-xs font-mono text-red-400 whitespace-pre-wrap">
            {result.error}
          </pre>
        )}

        {result?.test_results && result.test_results.length > 0 && (
          <div className="mt-2 space-y-1">
            {result.test_results.map((tr, i) => (
              <div key={i} className="flex items-center gap-2 text-xs font-mono">
                <span className={tr.status === 'passed' ? 'text-green-400' : 'text-red-400'}>
                  {tr.status === 'passed' ? '✓' : '✗'}
                </span>
                <span className="text-gray-400">Test {tr.test}:</span>
                <span className={tr.status === 'passed' ? 'text-green-300' : 'text-red-300'}>
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
