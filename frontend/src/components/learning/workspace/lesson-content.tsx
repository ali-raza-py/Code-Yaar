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
  official: {
    label: 'Sindh Board textbook',
    className: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
  },
  supplementary: {
    label: 'Supplementary practice',
    className: 'bg-amber-50 text-amber-700 ring-amber-200',
  },
  additional: {
    label: 'Beyond the textbook',
    className: 'bg-sky-50 text-sky-700 ring-sky-200',
  },
};

/** Inline markup: `code`, **bold**, *italic*. */
function renderInline(text: string, keyPrefix: string): ReactNode[] {
  return text.split(/(`[^`]+`)/g).flatMap((segment, i) => {
    if (segment.startsWith('`') && segment.endsWith('`') && segment.length > 2) {
      return [
        <code
          key={`${keyPrefix}-c${i}`}
          className="rounded bg-gray-100 px-1.5 py-0.5 font-mono text-[0.85em] text-pink-600"
        >
          {segment.slice(1, -1)}
        </code>,
      ];
    }

    return segment.split(/(\*\*[^*]+\*\*|\*[^*]+\*)/g).map((part, j) => {
      const k = `${keyPrefix}-t${i}-${j}`;
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={k} className="font-semibold text-gray-900">{part.slice(2, -2)}</strong>;
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
        elements.push(<h1 key={key++} className="mb-3 mt-6 text-2xl font-bold text-gray-900">{content}</h1>);
      } else if (level === 2) {
        elements.push(<h2 key={key++} className="mb-2 mt-5 text-lg font-semibold text-gray-900">{content}</h2>);
      } else if (level === 3) {
        elements.push(<h3 key={key++} className="mb-2 mt-4 text-base font-semibold text-gray-900">{content}</h3>);
      } else {
        elements.push(<h4 key={key++} className="mb-1.5 mt-3 text-sm font-semibold text-gray-900">{content}</h4>);
      }
      continue;
    }

    if (line.trim() === '') continue;

    // ── Horizontal rule ────────────────────────────────────────────────────
    if (/^\s*(-{3,}|\*{3,})\s*$/.test(line)) {
      elements.push(<hr key={key++} className="my-5 border-gray-200" />);
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
        <div key={key++} className="my-4 overflow-x-auto rounded-lg border border-gray-200">
          <table className="w-full border-collapse text-sm">
            <thead>
              <tr className="bg-gray-50 text-left">
                {header.map((cell, h) => (
                  <th key={h} className="border-b border-gray-200 px-3 py-2 font-semibold text-gray-900">
                    {renderInline(cell, `th${h}`)}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {body.map((row, r) => (
                <tr key={r} className="align-top">
                  {row.map((cell, c) => (
                    <td key={c} className="border-b border-gray-100 px-3 py-2 text-gray-700">
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
        <blockquote key={key++} className="my-3 border-l-4 border-gray-200 bg-gray-50 px-4 py-2 text-sm text-gray-700">
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
        <ListTag key={key++} className={`my-3 space-y-1.5 pl-5 text-sm text-gray-700 ${ordered ? 'list-decimal' : 'list-disc'}`}>
          {items.map((item, n) => (
            <li key={n}>{renderInline(item, `li${n}`)}</li>
          ))}
        </ListTag>,
      );
      continue;
    }

    // ── Paragraph ──────────────────────────────────────────────────────────
    elements.push(
      <p key={key++} className="mb-3 text-sm leading-relaxed text-gray-700">
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
        <div className="flex items-center gap-2 text-xs text-gray-500 mb-2">
          <span>{lesson.chapter_title}</span>
          <span>·</span>
          <span>Lesson {lesson.order}</span>
        </div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">{lesson.title}</h1>

        {/* Curriculum provenance — what part of the printed book this is from */}
        {reference && badge && (
          <div className="mb-3 flex flex-wrap items-center gap-2 text-xs">
            <span className={`inline-flex items-center rounded-full px-2 py-0.5 font-medium ring-1 ${badge.className}`}>
              {badge.label}
            </span>
            {reference.pages && (
              <span className="text-gray-500">
                {reference.board} · {reference.class} · {reference.label}
              </span>
            )}
          </div>
        )}

        {lesson.learning_objective && (
          <p className="text-sm italic text-gray-600">
            By the end of this lesson you will be able to: {lesson.learning_objective}
          </p>
        )}
        <div className="mt-3 flex items-center gap-3 text-xs text-gray-500">
          <span className="inline-flex items-center gap-1 rounded-full bg-green-50 px-2 py-0.5 font-medium text-green-700">
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
