'use client';

import type { ReactNode } from 'react';
import type { LessonDetail, TextbookReference } from '@/types';
import RunCodeBlock from './runnable-code-block';

interface LessonContentProps {
  lesson: LessonDetail;
  /**
   * Real snippet executor backed by the platform sandbox. Passed down to
   * every runnable fence; when absent, code blocks render statically without
   * a Run button (we never advertise execution that isn't wired up).
   */
  onRunSandbox?: (code: string, language: string) => Promise<string>;
}

/**
 * How a piece of content relates to the board textbook. The wording is
 * deliberate: only `official` material may be presented as Sindh Board
 * syllabus, and the badge makes the distinction visible on every lesson.
 */
const SOURCE_BADGES: Record<TextbookReference['source_type'], { label: string; className: string }> = {
  // State tints are token-driven (success/warning/info), so they stay legible
  // on both the light card and the dark navy surface.
  official: {
    label: 'Sindh Board textbook',
    className: 'bg-success/10 text-success ring-success/25',
  },
  supplementary: {
    label: 'Supplementary practice',
    className: 'bg-warning/10 text-warning ring-warning/25',
  },
  additional: {
    label: 'Beyond the textbook',
    className: 'bg-info/10 text-info ring-info/25',
  },
};

/** Inline markup: `code`, **bold**, *italic*. */
function renderInline(text: string, keyPrefix: string): ReactNode[] {
  return text.split(/(`[^`]+`)/g).flatMap((segment, i) => {
    if (segment.startsWith('`') && segment.endsWith('`') && segment.length > 2) {
      return [
        <code
          key={`${keyPrefix}-c${i}`}
          className="rounded bg-muted px-1.5 py-0.5 font-mono text-[0.85em] text-primary"
        >
          {segment.slice(1, -1)}
        </code>,
      ];
    }

    return segment.split(/(\*\*[^*]+\*\*|\*[^*]+\*)/g).map((part, j) => {
      const k = `${keyPrefix}-t${i}-${j}`;
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={k} className="font-semibold text-foreground">{part.slice(2, -2)}</strong>;
      }
      if (part.startsWith('*') && part.endsWith('*') && part.length > 2) {
        return <em key={k} className="italic">{part.slice(1, -1)}</em>;
      }
      return <span key={k}>{part}</span>;
    });
  });
}

/** Split a GFM-style table block into header cells and body rows. */
function parseTable(block: string[]) {
  const cells = (line: string) =>
    line.replace(/^\s*\|/, '').replace(/\|\s*$/, '').split('|').map((c) => c.trim());
  const header = cells(block[0]);
  const body = block.slice(2).filter((line) => !/^\s*\|?[\s:-]+\|[\s:|-]*$/.test(line)).map(cells);
  return { header, body };
}

/**
 * Block-level renderer for lesson content.
 *
 * Supports the subset of Markdown the curriculum actually uses: headings,
 * paragraphs, ordered/unordered lists, tables, blockquotes, rules and fenced
 * code. Fences in a language the sandbox executes get a Run button; `output`
 * fences render as a terminal panel showing the expected result.
 */
function renderContent(body: string, onRunSandbox?: (code: string, language: string) => Promise<string>) {
  const lines = body.split('\n');
  const elements: ReactNode[] = [];
  let key = 0;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // ── Fenced code ────────────────────────────────────────────────────────
    if (line.startsWith('```')) {
      const language = line.slice(3).trim();
      const code: string[] = [];
      i += 1;
      while (i < lines.length && !lines[i].startsWith('```')) {
        code.push(lines[i]);
        i += 1;
      }
      const text = code.join('\n').trim();

      if (language === 'output' || language === 'text') {
        elements.push(
          <div key={key++} className="my-3 overflow-hidden rounded-lg border border-[var(--editor-border)]">
            <div className="bg-[var(--editor-chrome)] px-3 py-1.5 text-[10px] font-medium uppercase tracking-wider text-white/40">
              {language === 'output' ? 'Expected output' : 'Note'}
            </div>
            <pre className="whitespace-pre-wrap bg-[var(--editor-bg)] px-3 py-2 font-mono text-xs text-[var(--syn-string)]">
              {text}
            </pre>
          </div>,
        );
      } else {
        elements.push(
          <RunCodeBlock key={key++} code={text} language={language} onRunSandbox={onRunSandbox} />
        );
      }
      continue;
    }

    // ── Headings ───────────────────────────────────────────────────────────
    const heading = /^(#{1,4})\s+(.*)$/.exec(line);
    if (heading) {
      const level = heading[1].length;
      const content = renderInline(heading[2], `h${key}`);
      if (level === 1) {
        elements.push(<h1 key={key++} className="mb-3 mt-6 text-2xl font-bold text-foreground">{content}</h1>);
      } else if (level === 2) {
        elements.push(<h2 key={key++} className="mb-2 mt-5 text-lg font-semibold text-foreground">{content}</h2>);
      } else if (level === 3) {
        elements.push(<h3 key={key++} className="mb-2 mt-4 text-base font-semibold text-foreground">{content}</h3>);
      } else {
        elements.push(<h4 key={key++} className="mb-1.5 mt-3 text-sm font-semibold text-foreground">{content}</h4>);
      }
      continue;
    }

    if (line.trim() === '') continue;

    // ── Horizontal rule ────────────────────────────────────────────────────
    if (/^\s*(-{3,}|\*{3,})\s*$/.test(line)) {
      elements.push(<hr key={key++} className="my-5 border-border" />);
      continue;
    }

    // ── Table ──────────────────────────────────────────────────────────────
    if (line.includes('|') && lines[i + 1] && /^[\s|:-]+$/.test(lines[i + 1]) && lines[i + 1].includes('-')) {
      const block: string[] = [line];
      j_loop: for (let j = i + 1; j < lines.length; j++) {
        if (!lines[j].includes('|') && block.length === 1) break j_loop;
        if (lines[j].trim() === '' && j + 1 < lines.length && !lines[j + 1].includes('|')) break j_loop;
        if (lines[j].trim() === '') continue;
        if (!lines[j].includes('|')) break j_loop;
        block.push(lines[j]);
        i = j;
      }
      const { header, body } = parseTable(block);
      elements.push(
        <div key={key++} className="my-4 overflow-x-auto rounded-lg border border-border bg-card text-card-foreground">
          <table className="w-full border-collapse text-sm">
            <thead>
              <tr className="bg-muted text-left">
                {header.map((cell, h) => (
                  <th key={h} className="border-b border-border px-3 py-2 font-semibold text-card-foreground">
                    {renderInline(cell, `th${h}`)}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {body.map((row, r) => (
                <tr key={r} className="align-top">
                  {row.map((cell, c) => (
                    <td key={c} className="border-b border-border/70 px-3 py-2 text-card-foreground">
                      {renderInline(cell, `td${r}-${c}`)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>,
      );
      continue;
    }

    // ── Blockquote ─────────────────────────────────────────────────────────
    if (line.startsWith('> ')) {
      const quote: string[] = [line.slice(2)];
      while (i + 1 < lines.length && lines[i + 1].startsWith('> ')) {
        quote.push(lines[i + 1].slice(2));
        i += 1;
      }
      elements.push(
        <blockquote key={key++} className="my-3 border-l-4 border-border bg-muted px-4 py-2 text-sm text-foreground/90">
          {renderInline(quote.join(' '), `bq${key}`)}
        </blockquote>,
      );
      continue;
    }

    // ── Lists ──────────────────────────────────────────────────────────────
    if (/^\s*[-*]\s+/.test(line) || /^\s*\d+\.\s+/.test(line)) {
      const ordered = /^\s*\d+\.\s+/.test(line);
      const items: string[] = [];
      while (i + 1 < lines.length && (ordered ? /^\s*\d+\.\s+/.test(lines[i + 1]) : /^\s*[-*]\s+/.test(lines[i + 1]))) {
        items.push(lines[i + 1].replace(/^\s*(?:[-*]|\d+\.)\s+/, ''));
        i += 1;
      }
      const ListTag = ordered ? 'ol' : 'ul';
      elements.push(
        <ListTag key={key++} className={`my-3 space-y-1.5 pl-5 text-sm text-foreground/90 ${ordered ? 'list-decimal' : 'list-disc'}`}>
          {items.map((item, n) => (
            <li key={n}>{renderInline(item, `li${n}`)}</li>
          ))}
        </ListTag>,
      );
      continue;
    }

    // ── Paragraph ──────────────────────────────────────────────────────────
    elements.push(
      <p key={key++} className="mb-3 text-sm leading-relaxed text-foreground/90">
        {renderInline(line, `p${key}`)}
      </p>,
    );
  }

  return elements;
}

export default function LessonContent({ lesson, onRunSandbox }: LessonContentProps) {
  const reference = lesson.textbook_reference;
  const badge = reference ? SOURCE_BADGES[reference.source_type] : null;

  return (
    <div className="px-6 py-6 max-w-2xl mx-auto">
      {/* Lesson Header */}
      <div className="mb-6">
        <div className="flex items-center gap-2 text-xs text-muted-foreground mb-2">
          <span>{lesson.chapter_title}</span>
          <span>·</span>
          <span>Lesson {lesson.order}</span>
        </div>
        <h1 className="text-2xl font-bold text-foreground mb-2">{lesson.title}</h1>

        {/* Curriculum provenance — what part of the printed book this is from */}
        {reference && badge && (
          <div className="mb-3 flex flex-wrap items-center gap-2 text-xs">
            <span className={`inline-flex items-center rounded-full px-2 py-0.5 font-medium ring-1 ${badge.className}`}>
              {badge.label}
            </span>
            {reference.pages && (
              <span className="text-muted-foreground">
                {reference.board} · {reference.class} · {reference.label}
              </span>
            )}
          </div>
        )}

        {lesson.learning_objective && (
          <p className="text-sm italic text-muted-foreground">
            By the end of this lesson you will be able to: {lesson.learning_objective}
          </p>
        )}
        <div className="mt-3 flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
          <span className="inline-flex items-center gap-1 rounded-full bg-success/10 px-2 py-0.5 font-medium text-success">
            +{lesson.xp_reward} XP
          </span>
          <span>{lesson.duration_minutes} min</span>
          <span>{lesson.exercise_count} exercises</span>
        </div>
      </div>

      {/* Lesson Body */}
      <div className="prose-learning">
        {renderContent(lesson.content_body, onRunSandbox)}
      </div>
    </div>
  );
}

/**
 * The learner-facing block renderer on its own, so the Course Creation Studio can
 * preview a lesson with exactly the code that renders it in the classroom. One
 * renderer, two hosts - a second preview implementation would drift.
 */
export function LessonBodyPreview({ body }: { body: string }) {
  return <div className="prose-learning">{renderContent(body)}</div>;
}
