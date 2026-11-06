'use client';

/**
 * Block-based lesson editor (spec section 4).
 *
 * The document is a list of typed blocks the author adds, edits, reorders and removes;
 * on save it serializes to the markdown subset the classroom renderer already understands
 * (see `lib/lesson-blocks.ts`), so nothing about the 800+ existing lessons changes. Code
 * blocks reuse the learner-side CodeMirror component, which means the editor highlights a
 * Python fence exactly the way the student will see it.
 *
 * Saving sends `expected_updated_at`. A 409 means somebody else wrote this lesson while
 * the tab was open; the editor keeps the draft on screen and offers to reload instead of
 * overwriting their work silently.
 */

import { useCallback, useMemo, useRef, useState } from 'react';
import {
  ArrowDown, ArrowUp, Code2, GripVertical, Heading, Image as ImageIcon, Link2,
  List, Loader2, Minus, Quote, RotateCcw, Save, Table, Type,
} from 'lucide-react';
import CodeEditor from '@/components/learning/workspace/code-editor-lazy';
import { LessonBodyPreview } from '@/components/learning/workspace/lesson-content';
import { adminApi } from '@/lib/admin-api';
import type { StudioLesson } from '@/lib/admin-api';
import { ApiError } from '@/lib/api';
import {
  BLOCK_LANGUAGE_OPTIONS, NEW_BLOCK_DEFAULTS, countBlockWords, parseLessonBlocks,
  serializeLessonBlocks, type LessonBlock,
} from '@/lib/lesson-blocks';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Input, Label, Textarea } from '@/components/admin/studio/studio-fields';

interface LessonEditorProps {
  courseId: number;
  lesson: StudioLesson;
  /** Other lessons in the same chapter - a prerequisite must live there. */
  chapterLessons: StudioLesson[];
  onSaved: (lesson: StudioLesson) => void;
  onClose: () => void;
}

const BLOCK_ICONS: Record<LessonBlock['kind'], typeof Type> = {
  heading: Heading,
  paragraph: Type,
  list: List,
  code: Code2,
  quote: Quote,
  table: Table,
  rule: Minus,
};

const BLOCK_LABELS: Record<LessonBlock['kind'], string> = {
  heading: 'Heading',
  paragraph: 'Text',
  list: 'Bullet list',
  code: 'Code',
  quote: 'Callout',
  table: 'Table',
  rule: 'Divider',
};

function blockKeyPrefix(block: LessonBlock, index: number): string {
  return `${index}-${block.kind}`;
}

function LessonEditorForm({
  courseId, lesson, chapterLessons, onSaved, onClose,
}: LessonEditorProps) {
  const [title, setTitle] = useState(lesson.title);
  const [objective, setObjective] = useState(lesson.learning_objective);
  const [notes, setNotes] = useState(lesson.instructor_notes || '');
  const [duration, setDuration] = useState(lesson.duration_minutes);
  const [xp, setXp] = useState(lesson.xp_reward);
  const [isActive, setIsActive] = useState(lesson.is_active);
  const [isRequired, setIsRequired] = useState(lesson.is_required);
  const [prerequisite, setPrerequisite] = useState<number | null>(lesson.prerequisite);
  const [blocks, setBlocks] = useState<LessonBlock[]>(() => parseLessonBlocks(lesson.content_body));
  const [dirty, setDirty] = useState(false);
  const [saving, setSaving] = useState(false);
  const [conflict, setConflict] = useState(false);
  const [error, setError] = useState('');
  const [showPreview, setShowPreview] = useState(true);
  const updatedRef = useRef(lesson.updated_at);

  const markdown = useMemo(() => serializeLessonBlocks(blocks), [blocks]);
  const wordCount = useMemo(() => countBlockWords(blocks), [blocks]);

  const patch = useCallback((next: (blocks: LessonBlock[]) => LessonBlock[]) => {
    setBlocks((current) => next(current));
    setDirty(true);
  }, []);

  const updateBlock = useCallback((index: number, block: LessonBlock) => {
    patch((current) => current.map((row, i) => (i === index ? block : row)));
  }, [patch]);

  const addBlock = useCallback((kind: LessonBlock['kind'], after?: number) => {
    patch((current) => {
      const copy = [...current];
      copy.splice((after ?? copy.length - 1) + 1, 0, NEW_BLOCK_DEFAULTS[kind]());
      return copy;
    });
  }, [patch]);

  const moveBlock = useCallback((index: number, delta: number) => {
    patch((current) => {
      const target = index + delta;
      if (target < 0 || target >= current.length) return current;
      const copy = [...current];
      const [row] = copy.splice(index, 1);
      copy.splice(target, 0, row);
      return copy;
    });
  }, [patch]);

  const removeBlock = useCallback((index: number) => {
    patch((current) => current.filter((_, i) => i !== index));
  }, [patch]);

  const save = useCallback(async () => {
    setSaving(true);
    setError('');
    try {
      const saved = await adminApi.studioUpdateLesson(courseId, lesson.id, {
        title,
        learning_objective: objective,
        instructor_notes: notes,
        duration_minutes: duration,
        xp_reward: xp,
        is_active: isActive,
        is_required: isRequired,
        prerequisite,
        content_body: markdown,
        expected_updated_at: updatedRef.current,
      });
      updatedRef.current = saved.updated_at;
      setDirty(false);
      onSaved(saved);
    } catch (err) {
      if (err instanceof ApiError && err.status === 409) {
        setConflict(true);
      } else {
        setError(err instanceof ApiError ? err.message : 'Could not save the lesson.');
      }
    } finally {
      setSaving(false);
    }
  }, [courseId, duration, isActive, isRequired, markdown, lesson.id, notes, objective, onSaved, prerequisite, title, xp]);

  const renderBlock = (block: LessonBlock, index: number) => {
    const key = blockKeyPrefix(block, index);
    switch (block.kind) {
      case 'heading':
        return (
          <div key={key} className="flex gap-2">
            <select
              className="h-9 rounded-md border border-input bg-transparent px-2 text-sm"
              value={block.level}
              onChange={(e) => updateBlock(index, { ...block, level: Number(e.target.value) as 1 | 2 | 3 | 4 })}
              aria-label="Heading level"
            >
              <option value={1}>H1</option>
              <option value={2}>H2</option>
              <option value={3}>H3</option>
              <option value={4}>H4</option>
            </select>
            <Input
              value={block.text}
              placeholder="Section heading"
              onChange={(e) => updateBlock(index, { ...block, text: e.target.value })}
            />
          </div>
        );
      case 'paragraph':
        return (
          <Textarea
            key={key}
            rows={3}
            value={block.text}
            placeholder="Explain the idea. Inline markup works: **bold**, *italic*, `code`."
            onChange={(e) => updateBlock(index, { ...block, text: e.target.value })}
          />
        );
      case 'list':
        return (
          <div key={key} className="space-y-2">
            {block.items.map((item, itemIndex) => (
              <div key={`${key}-${itemIndex}`} className="flex gap-2">
                <Input
                  value={item}
                  placeholder={block.ordered ? `Step ${itemIndex + 1}` : 'List item'}
                  onChange={(e) => updateBlock(index, {
                    ...block,
                    items: block.items.map((row, i) => (i === itemIndex ? e.target.value : row)),
                  })}
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  aria-label="Remove item"
                  onClick={() => updateBlock(index, { ...block, items: block.items.filter((_, i) => i !== itemIndex) })}
                >
                  <Minus className="h-4 w-4" />
                </Button>
              </div>
            ))}
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => updateBlock(index, { ...block, items: [...block.items, ''] })}
            >
              Add item
            </Button>
          </div>
        );
      case 'code':
        return (
          <div key={key} className="space-y-2">
            <div className="flex gap-2">
              <select
                className="h-9 rounded-md border border-input bg-transparent px-2 text-sm"
                value={block.language}
                onChange={(e) => updateBlock(index, { ...block, language: e.target.value })}
                aria-label="Code language"
              >
                {BLOCK_LANGUAGE_OPTIONS.map((option) => (
                  <option key={option || 'none'} value={option}>
                    {option || 'no language'}
                  </option>
                ))}
              </select>
              {block.language === 'output' && (
                <p className="self-center text-xs text-muted-foreground">
                  Rendered as a terminal panel showing the expected result.
                </p>
              )}
            </div>
            <div className="overflow-hidden rounded-lg border border-border">
              <CodeEditor
                code={block.code}
                language={block.language || 'python'}
                onChange={(code) => updateBlock(index, { ...block, code })}
                showChrome={false}
                fileName=""
              />
            </div>
          </div>
        );
      case 'quote':
        return (
          <Textarea
            key={key}
            rows={2}
            value={block.text}
            placeholder="A note the learner should not miss."
            onChange={(e) => updateBlock(index, { ...block, text: e.target.value })}
          />
        );
      case 'table':
        return (
          <div key={key} className="space-y-2 rounded-lg border border-dashed border-border p-3">
            <div className="grid grid-cols-2 gap-2">
              {block.header.map((cell, columnIndex) => (
                <Input
                  key={`${key}-h${columnIndex}`}
                  value={cell}
                  aria-label={`Column ${columnIndex + 1}`}
                  onChange={(e) => updateBlock(index, {
                    ...block,
                    header: block.header.map((row, i) => (i === columnIndex ? e.target.value : row)),
                  })}
                />
              ))}
            </div>
            {block.rows.map((row, rowIndex) => (
              <div key={`${key}-r${rowIndex}`} className="grid grid-cols-2 gap-2">
                {block.header.map((_, columnIndex) => (
                  <Input
                    key={`${key}-r${rowIndex}-${columnIndex}`}
                    value={row[columnIndex] ?? ''}
                    onChange={(e) => updateBlock(index, {
                      ...block,
                      rows: block.rows.map((existing, i) => {
                        if (i !== rowIndex) return existing;
                        const cells = [...existing];
                        cells[columnIndex] = e.target.value;
                        return cells;
                      }),
                    })}
                  />
                ))}
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  aria-label="Remove row"
                  onClick={() => updateBlock(index, { ...block, rows: block.rows.filter((_, i) => i !== rowIndex) })}
                >
                  <Minus className="h-4 w-4" />
                </Button>
              </div>
            ))}
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => updateBlock(index, { ...block, rows: [...block.rows, block.header.map(() => '')] })}
            >
              Add row
            </Button>
          </div>
        );
      case 'rule':
        return (
          <p key={key} className="text-xs uppercase tracking-wide text-muted-foreground">
            Horizontal divider
          </p>
        );
      default:
        return null;
    }
  };

  return (
    <Card>
      <CardContent className="space-y-5 p-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <h3 className="text-lg font-semibold">Lesson editor</h3>
            {dirty && <Badge variant="secondary">unsaved</Badge>}
            {conflict && <Badge className="bg-amber-500/15 text-amber-700">conflict</Badge>}
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={() => setShowPreview((v) => !v)}>
              <ImageIcon className="mr-2 h-4 w-4" />
              {showPreview ? 'Hide preview' : 'Show preview'}
            </Button>
            <Button variant="outline" size="sm" onClick={onClose}>Close</Button>
            <Button size="sm" onClick={save} disabled={saving || !dirty}>
              {saving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Save className="mr-2 h-4 w-4" />}
              Save lesson
            </Button>
          </div>
        </div>

        {conflict && (
          <div className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-amber-500/40 bg-amber-500/10 p-3 text-sm">
            <span>
              This lesson was changed elsewhere while you were editing. Your draft is kept on
              screen; reload to start from the saved version before saving again.
            </span>
            <Button variant="outline" size="sm" onClick={onClose}>
              <RotateCcw className="mr-2 h-4 w-4" />
              Reload saved version
            </Button>
          </div>
        )}
        {error && <p className="text-sm text-destructive">{error}</p>}

        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-1.5">
            <Label htmlFor="lesson-title">Title</Label>
            <Input
              id="lesson-title"
              value={title}
              onChange={(e) => { setTitle(e.target.value); setDirty(true); }}
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="lesson-objective">Learning objective</Label>
            <Input
              id="lesson-objective"
              value={objective}
              placeholder="By the end you will be able toâ€¦"
              onChange={(e) => { setObjective(e.target.value); setDirty(true); }}
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="lesson-duration">Duration (minutes)</Label>
            <Input
              id="lesson-duration"
              type="number"
              min={0}
              value={duration}
              onChange={(e) => { setDuration(Number(e.target.value) || 0); setDirty(true); }}
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="lesson-xp">XP reward</Label>
            <Input
              id="lesson-xp"
              type="number"
              min={0}
              value={xp}
              onChange={(e) => { setXp(Number(e.target.value) || 0); setDirty(true); }}
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="lesson-prerequisite">Required lesson (same chapter)</Label>
            <select
              id="lesson-prerequisite"
              className="h-9 w-full rounded-md border border-input bg-transparent px-3 text-sm"
              value={prerequisite ?? ''}
              onChange={(e) => {
                setPrerequisite(e.target.value ? Number(e.target.value) : null);
                setDirty(true);
              }}
            >
              <option value="">None</option>
              {chapterLessons
                .filter((row) => row.id !== lesson.id)
                .map((row) => (
                  <option key={row.id} value={row.id}>{row.title}</option>
                ))}
            </select>
          </div>
          <div className="flex flex-col justify-end gap-2 text-sm">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={isActive}
                onChange={(e) => { setIsActive(e.target.checked); setDirty(true); }}
                className="h-4 w-4 rounded border-input"
              />
              Published to learners
            </label>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={isRequired}
                onChange={(e) => { setIsRequired(e.target.checked); setDirty(true); }}
                className="h-4 w-4 rounded border-input"
              />
              Required for completion
            </label>
          </div>
        </div>

        <div className="space-y-1.5">
          <Label>Instructor notes (never shown to learners)</Label>
          <Textarea
            rows={2}
            value={notes}
            onChange={(e) => { setNotes(e.target.value); setDirty(true); }}
          />
        </div>

        <div className="space-y-3">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <Label>Content blocks Â· {wordCount} words</Label>
            <div className="flex flex-wrap gap-1">
              {(Object.keys(NEW_BLOCK_DEFAULTS) as LessonBlock['kind'][]).map((kind) => {
                const Icon = BLOCK_ICONS[kind];
                return (
                  <Button
                    key={kind}
                    type="button"
                    variant="ghost"
                    size="sm"
                    title={`Add ${BLOCK_LABELS[kind]}`}
                    onClick={() => addBlock(kind)}
                  >
                    <Icon className="mr-1 h-4 w-4" />
                    {BLOCK_LABELS[kind]}
                  </Button>
                );
              })}
            </div>
          </div>

          {blocks.length === 0 && (
            <p className="rounded-lg border border-dashed border-border p-6 text-center text-sm text-muted-foreground">
              Empty lesson. Add a text block to start writing.
            </p>
          )}

          <ol className="space-y-3">
            {blocks.map((block, index) => {
              const Icon = BLOCK_ICONS[block.kind];
              return (
                <li key={`${block.kind}-${index}`} className="rounded-lg border border-border p-3">
                  <div className="mb-2 flex items-center gap-2 text-xs text-muted-foreground">
                    <GripVertical className="h-4 w-4" />
                    <Icon className="h-4 w-4" />
                    <span className="font-medium uppercase tracking-wide">{BLOCK_LABELS[block.kind]}</span>
                    <span className="ml-auto flex items-center gap-1">
                      <Button type="button" variant="ghost" size="icon" aria-label="Move up"
                        onClick={() => moveBlock(index, -1)} disabled={index === 0}>
                        <ArrowUp className="h-4 w-4" />
                      </Button>
                      <Button type="button" variant="ghost" size="icon" aria-label="Move down"
                        onClick={() => moveBlock(index, 1)} disabled={index === blocks.length - 1}>
                        <ArrowDown className="h-4 w-4" />
                      </Button>
                      <Button type="button" variant="ghost" size="icon" aria-label="Insert below"
                        onClick={() => addBlock('paragraph', index)}>
                        <Link2 className="h-4 w-4" />
                      </Button>
                      <Button type="button" variant="ghost" size="icon" aria-label="Delete block"
                        onClick={() => removeBlock(index)}>
                        <Minus className="h-4 w-4" />
                      </Button>
                    </span>
                  </div>
                  {renderBlock(block, index)}
                </li>
              );
            })}
          </ol>
        </div>

        {showPreview && (
          <div className="space-y-2">
            <Label>Learner preview</Label>
            <div className="rounded-lg border border-border bg-background">
              <LessonBodyPreview body={markdown} />
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default function LessonEditor(props: LessonEditorProps) {
  return <LessonEditorForm key={`${props.lesson.id}:${props.lesson.updated_at}`} {...props} />;
}
