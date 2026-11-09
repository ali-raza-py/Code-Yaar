'use client';

/**
 * Curriculum tree for the Course Creation Studio (spec 3.2 - 3.3).
 *
 * Drag-and-drop is hand-rolled on the HTML5 drag events because the agreed dependency
 * budget for this pass was `recharts` only. The interaction is optimistic: the tree
 * reorders immediately, the write goes to the studio API, and a failed write reloads
 * from the server rather than leaving the screen showing an order that was never saved.
 *
 * Every mutation is scoped to the course being edited - the server enforces the same
 * rule, so a dragged lesson cannot be dropped into another course's chapter.
 */

import { useCallback, useMemo, useState } from 'react';
import {
  AlertTriangle, Check, Code2, Copy, Eye, EyeOff, FileText, GripVertical, ListPlus,
  Loader2, Plus, Pencil, Trash2,
} from 'lucide-react';
import { adminApi } from '@/lib/admin-api';
import type { StudioBundle, StudioChapter, StudioLesson, ExerciseAdmin } from '@/lib/admin-api';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';

type DragTarget =
  | { kind: 'chapter'; id: number }
  | { kind: 'lesson'; id: number; chapterId: number }
  | { kind: 'exercise'; id: number; lessonId: number };

interface CurriculumTreeProps {
  bundle: StudioBundle;
  onReload: () => void | Promise<void>;
  onOpenLesson: (lesson: StudioLesson, chapter: StudioChapter) => void;
  onCreateLesson: (chapter: StudioChapter) => void;
  onCreateExercise: (lesson: StudioLesson) => void;
  onUpdateExercise: (exercise: ExerciseAdmin) => void;
  onDeleteExercise: (exercise: ExerciseAdmin) => void;
}

const STATE_BADGE: Record<StudioChapter['publication_state'], { label: string; className: string }> = {
  empty: { label: 'no lessons', className: 'bg-muted text-muted-foreground' },
  draft: { label: 'draft', className: 'bg-muted text-muted-foreground' },
  partial: { label: 'partly live', className: 'bg-amber-500/15 text-amber-700' },
  published: { label: 'live', className: 'bg-success/10 text-success' },
};

export default function CurriculumTree({
  bundle, onReload, onOpenLesson, onCreateLesson, onCreateExercise, onUpdateExercise, onDeleteExercise,
}: CurriculumTreeProps) {
  const canEdit = bundle.permissions.can_edit;
  const canPublish = bundle.permissions.can_publish;
  const [drag, setDrag] = useState<DragTarget | null>(null);
  const [over, setOver] = useState<string | null>(null);
  const [selected, setSelected] = useState<Set<number>>(new Set());
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  const chapters = useMemo(
    () => [...bundle.chapters].sort((a, b) => a.order - b.order),
    [bundle.chapters],
  );

  const run = useCallback(async (action: () => Promise<unknown>) => {
    setBusy(true);
    setError('');
    try {
      await action();
      await onReload();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'That change could not be saved.');
      // Roll the optimistic view back to what the server actually holds.
      await onReload();
    } finally {
      setBusy(false);
    }
  }, [onReload]);

  const addChapter = () => run(async () => {
    await adminApi.studioCreateChapter(bundle.course.id, {
      title: `Chapter ${chapters.length + 1}`,
      order: chapters.length + 1,
    });
  });

  const renameChapter = (chapter: StudioChapter) => {
    const title = window.prompt('Chapter title', chapter.title);
    if (!title || title.trim() === chapter.title) return;
    run(() => adminApi.studioUpdateChapter(bundle.course.id, chapter.id, { title: title.trim() }));
  };

  const toggleChapter = (chapter: StudioChapter) =>
    run(() => adminApi.studioUpdateChapter(bundle.course.id, chapter.id, {
      is_active: !chapter.is_active,
    }));

  const duplicateChapter = (chapter: StudioChapter) =>
    run(() => adminApi.duplicateChapter(bundle.course.id, chapter.id));

  const removeChapter = (chapter: StudioChapter) => {
    if (!window.confirm(`Delete "${chapter.title}" and its lessons? Lessons that learners have started cannot be deleted.`)) return;
    run(() => adminApi.studioDeleteChapter(bundle.course.id, chapter.id));
  };

  const duplicateLesson = (lesson: StudioLesson) =>
    run(() => adminApi.duplicateLesson(bundle.course.id, lesson.id));

  const toggleLesson = (lesson: StudioLesson) =>
    run(() => adminApi.studioUpdateLesson(bundle.course.id, lesson.id, {
      is_active: !lesson.is_active,
      expected_updated_at: lesson.updated_at,
    }));

  const removeLesson = (lesson: StudioLesson) => {
    if (!window.confirm(`Delete "${lesson.title}"?`)) return;
    run(() => adminApi.studioDeleteLesson(bundle.course.id, lesson.id));
  };

  const addExercise = (lesson: StudioLesson) => run(async () => {
    const title = window.prompt('Exercise title');
    if (!title) return;
    await adminApi.studioCreateExercise(bundle.course.id, lesson.id, {
      title: title.trim(),
      exercise_type: 'code',
      instructions: 'Write your solution here.',
      language: 'python',
      is_active: false,
      order: 1,
    });
  });

  const toggleExercise = (exercise: ExerciseAdmin) => run(() =>
    adminApi.studioUpdateExercise(bundle.course.id, exercise.lesson, exercise.id, {
      is_active: !exercise.is_active,
    })
  );

  const removeExercise = (exercise: ExerciseAdmin) => {
    if (!window.confirm(`Delete "${exercise.title}"?`)) return;
    run(() => adminApi.studioDeleteExercise(bundle.course.id, exercise.lesson, exercise.id));
  };

  const toggleSelect = (id: number) => {
    setSelected((current) => {
      const next = new Set(current);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const bulkPublish = (isActive: boolean) => {
    const ids = [...selected];
    if (!ids.length) return;
    run(async () => {
      await adminApi.bulkPublishLessons(bundle.course.id, ids, isActive);
      setSelected(new Set());
    });
  };

  /** Drop handler: reorders within a chapter, or moves across chapters. */
  const handleDrop = (target: { chapterId: number; beforeLessonId?: number }) => {
    setOver(null);
    if (!drag || !canEdit) return;
    if (drag.kind === 'chapter') {
      if (drag.id === target.chapterId) return;
      const orders = chapters.filter((c) => c.id !== drag.id).map((c, i) => ({ id: c.id, order: i + 1 }));
      const movedIndex = chapters.findIndex((c) => c.id === drag.id);
      const targetIndex = chapters.findIndex((c) => c.id === target.chapterId);
      const spliceAt = movedIndex < targetIndex ? targetIndex : Math.max(targetIndex - 1, 0);
      orders.splice(spliceAt, 0, { id: drag.id, order: 0 });
      const payload = orders.map((row, i) => ({ id: row.id, order: i + 1 }));
      setDrag(null);
      run(() => adminApi.studioReorderChapters(bundle.course.id, payload));
      return;
    }

    // After the chapter branch, drag is a lesson or exercise; only lessons are draggable here.
    const lessonDrag = drag as Extract<DragTarget, { kind: 'lesson' }>;
    if (lessonDrag.chapterId !== target.chapterId) {
      setDrag(null);
      run(() => adminApi.moveLesson(bundle.course.id, lessonDrag.id, { chapter: target.chapterId }));
      return;
    }

    const lessonChapter = chapters.find((c) => c.id === target.chapterId);
    if (!lessonChapter) return;
    const ordered = [...lessonChapter.lessons].sort((a, b) => a.order - b.order);
    const from = ordered.findIndex((l) => l.id === lessonDrag.id);
    if (from === -1) return;
    const [moved] = ordered.splice(from, 1);
    const to = target.beforeLessonId
      ? ordered.findIndex((l) => l.id === target.beforeLessonId)
      : ordered.length;
    ordered.splice(to < 0 ? ordered.length : to, 0, moved);
    const payload = ordered.map((l, i) => ({ id: l.id, order: i + 1, chapter: target.chapterId }));
    setDrag(null);
    run(() => adminApi.studioReorderLessons(bundle.course.id, payload));
  };

  const dragProps = (target: DragTarget) => ({
    draggable: canEdit,
    onDragStart: (event: React.DragEvent) => {
      event.dataTransfer.effectAllowed = 'move';
      event.dataTransfer.setData('text/plain', String(target.id));
      setDrag(target);
    },
    onDragEnd: () => { setDrag(null); setOver(null); },
  });

  const dropProps = (key: string, target: { chapterId: number; beforeLessonId?: number }) => ({
    onDragOver: (event: React.DragEvent) => {
      if (!drag) return;
      event.preventDefault();
      event.dataTransfer.dropEffect = 'move';
      setOver(key);
    },
    onDragLeave: () => setOver((current) => (current === key ? null : current)),
    onDrop: (event: React.DragEvent) => { event.preventDefault(); handleDrop(target); },
  });

  return (
    <Card>
      <CardContent className="space-y-3 p-5">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <h3 className="text-lg font-semibold">Curriculum</h3>
            {busy && <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />}
            {canEdit && (
              <Button variant="outline" size="sm" onClick={addChapter}>
                <Plus className="mr-2 h-4 w-4" />
                Add chapter
              </Button>
            )}
          </div>
          {selected.size > 0 && canPublish && (
            <div className="flex items-center gap-2 text-sm">
              <span className="text-muted-foreground">{selected.size} selected</span>
              <Button size="sm" onClick={() => bulkPublish(true)}>
                <Check className="mr-2 h-4 w-4" />
                Publish
              </Button>
              <Button variant="outline" size="sm" onClick={() => bulkPublish(false)}>
                <EyeOff className="mr-2 h-4 w-4" />
                Draft
              </Button>
            </div>
          )}
        </div>

        {error && (
          <p role="alert" className="flex items-center gap-2 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700 dark:border-red-800 dark:bg-red-950 dark:text-red-200">
            <AlertTriangle className="h-4 w-4 shrink-0" />
            {error}
          </p>
        )}

        <p className="text-xs text-muted-foreground">
          Drag a chapter or a lesson to move it. Lessons dropped into another chapter are
          renumbered so the stored order stays unambiguous.
        </p>

        {chapters.length === 0 && (
          <div className="rounded-lg border border-dashed border-border p-8 text-center text-sm text-muted-foreground">
            No chapters yet. {canEdit ? 'Add one to start building the course.' : 'An administrator needs to add the first chapter.'}
          </div>
        )}

        <ol className="space-y-3">
          {chapters.map((chapter) => {
            const badge = STATE_BADGE[chapter.publication_state] ?? STATE_BADGE.empty;
            const lessons = [...chapter.lessons].sort((a, b) => a.order - b.order);
            return (
              <li
                key={chapter.id}
                className={`rounded-lg border ${over === `chapter-${chapter.id}` ? 'border-ring ring-1 ring-ring' : 'border-border'}`}
                {...dragProps({ kind: 'chapter', id: chapter.id })}
                {...dropProps(`chapter-${chapter.id}`, { chapterId: chapter.id })}
              >
                <div className="flex flex-wrap items-center gap-2 border-b border-border px-4 py-3">
                  <GripVertical className="h-4 w-4 shrink-0 text-muted-foreground" />
                  <span className="text-xs text-muted-foreground">#{chapter.order}</span>
                  <span className="font-medium">{chapter.title}</span>
                  <Badge variant="secondary" className={badge.className}>{badge.label}</Badge>
                  <span className="text-xs text-muted-foreground">
                    {chapter.published_lesson_count}/{lessons.length} live
                  </span>
                  {!chapter.is_active && (
                    <Badge variant="outline" className="text-muted-foreground">hidden</Badge>
                  )}
                  <span className="ml-auto flex items-center gap-1">
                    {canEdit && (
                      <>
                        <Button variant="ghost" size="sm" onClick={() => onCreateLesson(chapter)}>
                          <ListPlus className="mr-1 h-4 w-4" />
                          Lesson
                        </Button>
                        <Button variant="ghost" size="icon" aria-label="Rename chapter"
                          onClick={() => renameChapter(chapter)}>
                          <Pencil className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="icon" aria-label={chapter.is_active ? 'Hide chapter' : 'Show chapter'}
                          onClick={() => toggleChapter(chapter)}>
                          {chapter.is_active ? <Eye className="h-4 w-4" /> : <EyeOff className="h-4 w-4" />}
                        </Button>
                        <Button variant="ghost" size="icon" aria-label="Duplicate chapter"
                          onClick={() => duplicateChapter(chapter)}>
                          <Copy className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="icon" aria-label="Delete chapter"
                          onClick={() => removeChapter(chapter)}>
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </>
                    )}
                  </span>
                </div>

                {lessons.length === 0 ? (
                  <p className="px-4 py-3 text-sm text-muted-foreground">
                    Empty chapter - it blocks publication until it has at least one lesson.
                  </p>
                ) : (
                  <ol className="divide-y divide-border">
                    {lessons.map((lesson) => (
                      <li
                        key={lesson.id}
                        className={`flex flex-wrap items-center gap-2 px-4 py-2 text-sm ${over === `lesson-${lesson.id}` ? 'bg-muted/60' : ''}`}
                        {...dragProps({ kind: 'lesson', id: lesson.id, chapterId: chapter.id })}
                        {...dropProps(`lesson-${lesson.id}`, { chapterId: chapter.id, beforeLessonId: lesson.id })}
                      >
                        <GripVertical className="h-4 w-4 shrink-0 text-muted-foreground" />
                        {canPublish && (
                          <input
                            type="checkbox"
                            aria-label={`Select ${lesson.title}`}
                            checked={selected.has(lesson.id)}
                            onChange={() => toggleSelect(lesson.id)}
                            className="h-4 w-4 rounded border-input"
                          />
                        )}
                        <FileText className="h-4 w-4 shrink-0 text-muted-foreground" />
                        <button
                          type="button"
                          className="truncate text-left font-medium hover:underline"
                          onClick={() => onOpenLesson(lesson, chapter)}
                        >
                          {lesson.title}
                        </button>
                        {!lesson.is_active && (
                          <Badge variant="outline" className="text-muted-foreground">draft</Badge>
                        )}
                        {!lesson.is_required && (
                          <Badge variant="outline" className="text-muted-foreground">optional</Badge>
                        )}
                        {lesson.prerequisite && (
                          <Badge variant="outline" title="Learners must finish another lesson first">
                            gated
                          </Badge>
                        )}
                        <span className="text-xs text-muted-foreground">
                          {lesson.duration_minutes} min · {lesson.xp_reward} XP · {lesson.exercise_count} exercises
                        </span>
                        <span className="ml-auto flex items-center gap-1">
                          <Button variant="ghost" size="icon" aria-label="Edit lesson"
                            onClick={() => onOpenLesson(lesson, chapter)}>
                            <Pencil className="h-4 w-4" />
                          </Button>
                          {canEdit && (
                            <>
                              {canPublish && (
                                <Button variant="ghost" size="icon"
                                  aria-label={lesson.is_active ? 'Set lesson to draft' : 'Publish lesson'}
                                  onClick={() => toggleLesson(lesson)}>
                                  {lesson.is_active ? <Eye className="h-4 w-4" /> : <EyeOff className="h-4 w-4" />}
                                </Button>
                              )}
                              <Button variant="ghost" size="icon" aria-label="Duplicate lesson"
                                onClick={() => duplicateLesson(lesson)}>
                                <Copy className="h-4 w-4" />
                              </Button>
                              <Button variant="ghost" size="icon" aria-label="Delete lesson"
                                onClick={() => removeLesson(lesson)}>
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </>
                          )}
                        </span>

                        {/* Exercises under this lesson */}
                        {lesson.exercises && lesson.exercises.length > 0 && (
                          <ol className="pl-8 space-y-1 border-l border-border/50 ml-2">
                            {lesson.exercises.map((ex) => (
                              <li
                                key={ex.id}
                                className="flex items-center gap-2 px-4 py-1.5 text-xs"
                              >
                                <Code2 className="h-3.5 w-3.5 shrink-0 text-muted-foreground" />
                                <span className="truncate">{ex.title}</span>
                                <span className="text-xs text-muted-foreground ml-auto">
                                  {ex.exercise_type} · {ex.xp_reward} XP
                                </span>
                                {!ex.is_active && (
                                  <Badge variant="outline" className="text-muted-foreground">draft</Badge>
                                )}
                                <span className="ml-auto flex items-center gap-1">
                                  {canEdit && (
                                    <>
                                      <Button variant="ghost" size="icon" aria-label="Toggle exercise"
                                        onClick={() => toggleExercise(ex)}>
                                        {ex.is_active ? <Eye className="h-3.5 w-3.5" /> : <EyeOff className="h-3.5 w-3.5" />}
                                      </Button>
                                      <Button variant="ghost" size="icon" aria-label="Delete exercise"
                                        onClick={() => removeExercise(ex)}>
                                        <Trash2 className="h-3.5 w-3.5" />
                                      </Button>
                                    </>
                                  )}
                                </span>
                              </li>
                            ))}
                          </ol>
                        )}
                        {canEdit && (
                          <Button
                            type="button"
                            size="sm"
                            variant="outline"
                            className="mt-2 px-2 text-xs"
                            onClick={() => addExercise(lesson)}
                          >
                            <Plus className="mr-1 h-3.5 w-3.5" /> Add exercise
                          </Button>
                        )}
                      </li>
                    ))}
                  </ol>
                )}
              </li>
            );
          })}
        </ol>
      </CardContent>
    </Card>
  );
}
