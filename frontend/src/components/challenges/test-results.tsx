import { CheckCircle2, XCircle, AlertTriangle, Clock } from "lucide-react";
import type { ChallengeTestResult } from "@/types";

interface TestResultsProps {
  results: ChallengeTestResult[];
}

const STATUS_META: Record<string, { icon: typeof CheckCircle2; className: string; label: string }> = {
  passed: { icon: CheckCircle2, className: "text-success", label: "Passed" },
  failed: { icon: XCircle, className: "text-danger", label: "Failed" },
  error: { icon: AlertTriangle, className: "text-danger", label: "Error" },
  pending: { icon: Clock, className: "text-[var(--challenge-muted)]", label: "Pending" },
};

/** Readable pass/fail breakdown for a run or submit. */
export function TestResults({ results }: TestResultsProps) {
  if (results.length === 0) {
    return <p className="text-xs text-[var(--challenge-muted)]">No test cases were executed.</p>;
  }

  const passed = results.filter((r) => r.status === "passed").length;
  return (
    <div className="space-y-2">
      <p className="text-xs font-semibold text-[var(--challenge-text-soft)]">
        {passed}/{results.length} tests passed
      </p>
      <ul className="space-y-2">
        {results.map((result) => {
          const meta = STATUS_META[result.status] ?? STATUS_META.pending;
          const Icon = meta.icon;
          return (
            <li key={result.test} className="rounded-md border border-[var(--challenge-border)] bg-[var(--challenge-surface-muted)] p-2.5">
              <div className="flex items-center gap-2">
                <Icon aria-hidden="true" className={`h-4 w-4 shrink-0 ${meta.className}`} />
                <span className="text-xs font-bold text-[var(--challenge-text)]">Test {result.test}</span>
                <span className={`ml-auto text-[11px] font-semibold uppercase tracking-wide ${meta.className}`}>{meta.label}</span>
              </div>
              {result.message && (
                <p className="mt-1.5 text-xs leading-5 text-[var(--challenge-muted)]">{result.message}</p>
              )}
              {(result.status === "failed" || result.status === "error") && (
                <div className="mt-2 grid gap-2 sm:grid-cols-2">
                  <div>
                    <p className="text-[10px] font-bold uppercase tracking-wide text-[var(--challenge-muted)]">Expected</p>
                    <pre className="mt-1 overflow-auto whitespace-pre-wrap rounded bg-[var(--editor-bg)] p-2 font-mono text-[11px] text-[var(--syn-string)]">{result.expected || "(empty)"}</pre>
                  </div>
                  <div>
                    <p className="text-[10px] font-bold uppercase tracking-wide text-[var(--challenge-muted)]">Your output</p>
                    <pre className="mt-1 overflow-auto whitespace-pre-wrap rounded bg-[var(--editor-bg)] p-2 font-mono text-[11px] text-[var(--syn-invalid)]">{result.actual || "(empty)"}</pre>
                  </div>
                </div>
              )}
            </li>
          );
        })}
      </ul>
    </div>
  );
}
