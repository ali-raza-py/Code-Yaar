'use client';

import { useState, useCallback } from 'react';
import CodeEditor from './code-editor';
import type { RunnableLanguage } from '@/lib/api';

/** Fence languages the server sandbox actually executes, normalised. */
const RUNNABLE: Record<string, RunnableLanguage> = {
  python: 'python',
  py: 'python',
  cpp: 'cpp',
  'c++': 'cpp',
  cxx: 'cpp',
};

interface RunCodeBlockProps {
  code: string;
  language: string;
  /**
   * Real executor (platform sandbox). When absent — or when the language
   * cannot be executed server-side — the block renders as static code.
   * A Run button is never shown unless execution genuinely works.
   */
  onRunSandbox?: (code: string, language: string) => Promise<string>;
}

/**
 * A C++ fence is only runnable if it is a complete program. Textbooks show
 * syntax fragments (`if (x) statement;`) that compile to confusing errors,
 * so fragments stay static — every real board program has `main()`.
 */
function isRunnableCode(executable: RunnableLanguage | undefined, code: string): boolean {
  if (!executable) return false;
  if (executable === 'cpp') return /\bmain\s*\(/.test(code);
  return true;
}

/**
 * Runnable code block embedded directly in lesson prose.
 * Collapses "read → run" to a single click for languages the sandbox
 * actually executes (Python and C++). Everything else stays a plain
 * code fence. Runnable samples also offer "Try it yourself": the fence
 * becomes an editable working copy the learner can run and reset.
 */
export default function RunCodeBlock({ code, language, onRunSandbox }: RunCodeBlockProps) {
  const [output, setOutput] = useState<string | null>(null);
  const [running, setRunning] = useState(false);
  // null = pristine textbook sample; a string = the learner's working copy.
  const [draft, setDraft] = useState<string | null>(null);
  const executable = RUNNABLE[language.toLowerCase()];
  const runnable = !!onRunSandbox && isRunnableCode(executable, code);
  const editable = draft !== null;
  const displayCode = draft ?? code;

  const handleRun = useCallback(async () => {
    if (!onRunSandbox || !executable) return;
    setRunning(true);
    setOutput('');
    try {
      setOutput(await onRunSandbox(displayCode, executable));
    } catch (err) {
      setOutput(`Error: ${(err as Error).message}`);
    } finally {
      setRunning(false);
    }
  }, [displayCode, executable, onRunSandbox]);

  return (
    <div className="code-block-runnable my-3">
      <div className="flex items-center gap-2 border-b border-[var(--editor-border)] bg-[var(--editor-chrome)] px-3 py-1.5">
        <span className="text-[10px] font-medium uppercase tracking-wider text-white/50">
          {runnable ? executable : (language ? language.replace(/-static$/, '') : 'code')}
        </span>
        {editable && (
          <span className="text-[10px] font-medium uppercase tracking-wider text-[var(--sidebar-accent-soft)]">
            Your working copy
          </span>
        )}
        {runnable && (
          <div className="ml-auto flex items-center gap-2">
            {editable ? (
              <button
                type="button"
                onClick={() => { setDraft(null); setOutput(null); }}
                disabled={running}
                className="inline-flex items-center rounded-[var(--radius-tool)] border border-white/20 px-3 py-1 text-xs font-semibold text-white/70 transition-colors hover:border-white/40 hover:text-white disabled:opacity-50"
              >
                Reset
              </button>
            ) : (
              <button
                type="button"
                onClick={() => { setDraft(code); setOutput(null); }}
                disabled={running}
                className="inline-flex items-center rounded-[var(--radius-tool)] border border-white/20 px-3 py-1 text-xs font-semibold text-white/70 transition-colors hover:border-white/40 hover:text-white disabled:opacity-50"
              >
                Try it yourself
              </button>
            )}
            <button
              type="button"
              onClick={handleRun}
              disabled={running}
              className="editor-run-btn inline-flex items-center justify-center gap-1 rounded-[var(--radius-tool)] bg-cta px-3 py-1 text-xs font-semibold text-cta-fg transition-colors hover:bg-cta-hover disabled:opacity-50"
            >
              {running ? 'Running…' : 'Run Code'}
            </button>
          </div>
        )}
      </div>

      {/* Shared CodeMirror fence — same governed syntax theme as the workspace.
          The gutter stays off because CodeMirror builds it once at mount. */}
      <CodeEditor
        code={displayCode}
        onChange={(next) => setDraft((current) => (current === null ? current : next))}
        language={language}
        readOnly={!editable}
        showChrome={false}
        showGutter={false}
      />

      {output !== null && (
        <div className="border-t border-[var(--editor-border)] bg-[var(--editor-chrome)] px-3 py-2">
          <div className="mb-1 text-[10px] font-medium uppercase tracking-wider text-white/40">
            Output
          </div>
          <pre className="whitespace-pre-wrap font-mono text-xs text-[var(--syn-string)]">{output}</pre>
        </div>
      )}
    </div>
  );
}
