'use client';

import { useState, useCallback } from 'react';
import CodeEditor from './code-editor';

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
 * Runnable code block embedded directly in lesson prose.
 * Collapses "read → run" to a single click for languages the sandbox
 * actually executes (Python). Everything else stays a plain code fence.
 */
export default function RunCodeBlock({ code, language, onRunSandbox }: RunCodeBlockProps) {
  const [output, setOutput] = useState<string | null>(null);
  const [running, setRunning] = useState(false);
  const runnable = language === 'python' && !!onRunSandbox;

  const handleRun = useCallback(async () => {
    if (!onRunSandbox) return;
    setRunning(true);
    setOutput('');
    try {
      setOutput(await onRunSandbox(code, language));
    } catch (err) {
      setOutput(`Error: ${(err as Error).message}`);
    } finally {
      setRunning(false);
    }
  }, [code, language, onRunSandbox]);

  return (
    <div className="code-block-runnable my-3">
      <div className="flex items-center gap-2 border-b border-[var(--editor-border)] bg-[var(--editor-chrome)] px-3 py-1.5">
        <span className="text-[10px] font-medium uppercase tracking-wider text-white/50">
          {language || 'code'}
        </span>
        {runnable && (
          <button
            type="button"
            onClick={handleRun}
            disabled={running}
            className="editor-run-btn ml-auto inline-flex items-center justify-center gap-1 rounded-[var(--radius-tool)] bg-cta px-3 py-1 text-xs font-semibold text-cta-fg transition-colors hover:bg-cta-hover disabled:opacity-50"
          >
            {running ? 'Running…' : 'Run Code'}
          </button>
        )}
      </div>

      {/* Shared read-only CodeMirror fence — same governed syntax theme as the workspace */}
      <CodeEditor
        code={code}
        onChange={() => {}}
        language={language}
        readOnly
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
