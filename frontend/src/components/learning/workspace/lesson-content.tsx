'use client';

import React from 'react';
import { LessonDetail } from '@/types';
import RunCodeBlock from './runnable-code-block';

interface LessonContentProps {
  lesson: LessonDetail;
  /**
   * Real snippet executor backed by the platform sandbox. Passed down to
   * every Python fence; when absent, code blocks render statically without
   * a Run button (we never advertise execution that isn't wired up).
   */
  onRunSandbox?: (code: string, language: string) => Promise<string>;
}

/**
 * Simple markdown-like renderer for lesson content.
 * Handles headings, paragraphs, code blocks, inline code, and lists.
 */
function renderContent(body: string, onRunSandbox?: (code: string, language: string) => Promise<string>) {
  const lines = body.split('\n');
  const elements: React.ReactNode[] = [];
  let inCodeBlock = false;
  let codeContent = '';
  let codeLanguage = '';
  let key = 0;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Code block start/end
    if (line.startsWith('```')) {
      if (inCodeBlock) {
        elements.push(
          <RunCodeBlock key={key++} code={codeContent.trim()} language={codeLanguage} onRunSandbox={onRunSandbox} />
        );
        codeContent = '';
        codeLanguage = '';
        inCodeBlock = false;
      } else {
        inCodeBlock = true;
        codeLanguage = line.slice(3).trim();
      }
      continue;
    }

    if (inCodeBlock) {
      codeContent += line + '\n';
      continue;
    }

    // Headings
    if (line.startsWith('# ')) {
      elements.push(
        <h1 key={key++} className="text-2xl font-bold text-gray-900 mt-6 mb-3">
          {line.slice(2)}
        </h1>
      );
      continue;
    }
    if (line.startsWith('## ')) {
      elements.push(
        <h2 key={key++} className="text-lg font-semibold text-gray-900 mt-5 mb-2">
          {line.slice(3)}
        </h2>
      );
      continue;
    }
    if (line.startsWith('### ')) {
      elements.push(
        <h3 key={key++} className="text-base font-semibold text-gray-900 mt-4 mb-2">
          {line.slice(4)}
        </h3>
      );
      continue;
    }

    // Empty line
    if (line.trim() === '') {
      continue;
    }

    // Paragraph with inline code
    const parts = line.split(/(`[^`]+`)/g);
    const rendered = parts.map((part, j) => {
      if (part.startsWith('`') && part.endsWith('`')) {
        return (
          <code key={j} className="rounded bg-gray-100 px-1.5 py-0.5 text-sm font-mono text-pink-600">
            {part.slice(1, -1)}
          </code>
        );
      }
      // Bold
      const boldParts = part.split(/(\*\*[^*]+\*\*)/g);
      return boldParts.map((bp, k) => {
        if (bp.startsWith('**') && bp.endsWith('**')) {
          return <strong key={`${j}-${k}`} className="font-semibold text-gray-900">{bp.slice(2, -2)}</strong>;
        }
        return <span key={`${j}-${k}`}>{bp}</span>;
      });
    });

    elements.push(
      <p key={key++} className="text-sm leading-relaxed text-gray-700 mb-3">
        {rendered}
      </p>
    );
  }

  return elements;
}

export default function LessonContent({ lesson, onRunSandbox }: LessonContentProps) {
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
        {lesson.learning_objective && (
          <p className="text-sm text-gray-600 italic">
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
