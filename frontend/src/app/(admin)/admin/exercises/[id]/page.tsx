"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, Loader2, Plus, Save, Trash2 } from "lucide-react";
import Link from "next/link";
import { adminApi } from "@/lib/admin-api";
import type { ExerciseAdmin, LessonAdmin } from "@/lib/admin-api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input, Label, StudioError, StudioField, Textarea, Select } from "@/components/admin/studio/studio-fields";
import { Skeleton } from "@/components/ui/skeleton";

type ExerciseType = 'code' | 'multiple_choice' | 'multiple_select' | 'debugging' | 'output_prediction' | 'fill_blank';

const EXERCISE_TYPES: Array<{ value: ExerciseType; label: string }> = [
  { value: 'code', label: 'Code' },
  { value: 'multiple_choice', label: 'Multiple Choice' },
  { value: 'multiple_select', label: 'Multiple Select' },
  { value: 'debugging', label: 'Debugging' },
  { value: 'output_prediction', label: 'Output Prediction' },
  { value: 'fill_blank', label: 'Fill in the Blanks' },
];

export default function ExerciseDetailPage() {
  const params = useParams();
  const router = useRouter();
  const exerciseId = Number(params.id);

  const [exercise, setExercise] = useState<ExerciseAdmin | null>(null);
  const [lessons, setLessons] = useState<LessonAdmin[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [form, setForm] = useState({
    title: "",
    lesson: "",
    exercise_type: "code" as ExerciseType,
    difficulty: "easy",
    language: "python",
    instructions: "",
    context: "",
    constraints: "",
    expected_behavior: "",
    explain: "",
    starter_code: "",
    solution_code: "",
    expected_output: "",
    choices: "" as string,
    test_cases: "" as string,
    hints: "" as string,
    xp_reward: 50,
    max_attempts: 0,
    order: 1,
    is_active: true,
    is_final_assessment: false,
  });

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [exerciseData, lessonsData] = await Promise.all([
        adminApi.getExercise(exerciseId),
        adminApi.listLessons({ page_size: 100 }),
      ]);
      setExercise(exerciseData);
      setLessons((lessonsData.results || []));
      setForm({
        title: exerciseData.title,
        lesson: String(exerciseData.lesson),
        exercise_type: exerciseData.exercise_type as ExerciseType,
        difficulty: exerciseData.difficulty,
        language: exerciseData.language,
        instructions: exerciseData.instructions,
        context: exerciseData.context,
        constraints: exerciseData.constraints,
        expected_behavior: exerciseData.expected_behavior,
        explain: exerciseData.explain,
        starter_code: exerciseData.starter_code,
        solution_code: exerciseData.solution_code,
        expected_output: exerciseData.expected_output,
        choices: JSON.stringify(exerciseData.choices || []),
        test_cases: JSON.stringify(exerciseData.test_cases || []),
        hints: JSON.stringify([]),
        xp_reward: exerciseData.xp_reward,
        max_attempts: exerciseData.max_attempts,
        order: exerciseData.order,
        is_active: exerciseData.is_active,
        is_final_assessment: exerciseData.is_final_assessment,
      });
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not load exercise.");
    } finally {
      setLoading(false);
    }
  }, [exerciseId]);

  useEffect(() => {
    load();
  }, [exerciseId]);

  const update = (key: string, value: string | number | boolean) =>
    setForm((current) => ({ ...current, [key]: value }));

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setError("");
    try {
      let choices: unknown[] = [];
      let test_cases: unknown[] = [];
      try { choices = JSON.parse(form.choices as string) || []; } catch { choices = []; }
      try { test_cases = JSON.parse(form.test_cases as string) || []; } catch { test_cases = []; }

      await adminApi.updateExercise(exerciseId, {
        title: form.title.trim(),
        lesson: Number(form.lesson),
        exercise_type: form.exercise_type,
        difficulty: form.difficulty,
        language: form.language,
        instructions: form.instructions.trim(),
        context: form.context.trim(),
        constraints: form.constraints.trim(),
        expected_behavior: form.expected_behavior.trim(),
        explain: form.explain.trim(),
        starter_code: form.starter_code,
        solution_code: form.solution_code,
        expected_output: form.expected_output.trim(),
        choices: choices as unknown as { id: string; text: string; is_correct: boolean }[],
        test_cases: test_cases as unknown[],
        hidden_tests: [],
        xp_reward: Number(form.xp_reward) || 0,
        max_attempts: Number(form.max_attempts) || 0,
        order: Number(form.order) || 1,
        is_active: form.is_active,
        is_final_assessment: form.is_final_assessment,
      });
      router.replace("/admin/exercises");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Exercise could not be updated.");
      setSaving(false);
    }
  }

  async function handleDelete() {
    if (!confirm("Are you sure you want to delete this exercise?")) return;
    setSaving(true);
    try {
      await adminApi.deleteExercise(exerciseId);
      router.replace("/admin/exercises");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not delete exercise.");
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="animate-pulse space-y-6">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-96" />
      </div>
    );
  }

  if (!exercise) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
        <p className="text-center text-destructive">Exercise not found</p>
        <Link href="/admin/exercises"><Button variant="outline">Back to exercises</Button></Link>
      </div>
    );
  }

  const isChoiceType = form.exercise_type === 'multiple_choice' || form.exercise_type === 'multiple_select';
  const isCodeType = form.exercise_type === 'code' || form.exercise_type === 'debugging';
  const isOutputType = form.exercise_type === 'output_prediction';

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/admin/exercises"><Button variant="ghost" size="icon"><ArrowLeft className="h-4 w-4" /></Button></Link>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Edit Exercise</h1>
          <p className="mt-1 text-sm text-muted-foreground">Exercise ID: {exercise.id}</p>
        </div>
      </div>

      {error && <StudioError message={error} />}

      <Card>
        <CardHeader>
          <CardTitle>Exercise Details</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={submit} className="space-y-5">
            <div className="grid gap-4 sm:grid-cols-2">
              <StudioField label="Title" htmlFor="exercise-title" required>
                <Input id="exercise-title" value={form.title} onChange={(e) => update("title", e.target.value)} required />
              </StudioField>

              <StudioField label="Lesson" htmlFor="exercise-lesson" required>
                <Select id="exercise-lesson" value={form.lesson} onChange={(e) => update("lesson", e.target.value)} required>
                  <option value="">Select a lesson</option>
                  {lessons.map((lesson) => (
                    <option key={lesson.id} value={lesson.id}>{lesson.course_title} / {lesson.chapter_title} / {lesson.title}</option>
                  ))}
                </Select>
              </StudioField>
            </div>

            <div className="grid gap-4 sm:grid-cols-3">
              <StudioField label="Type" htmlFor="exercise-type">
                <Select id="exercise-type" value={form.exercise_type} onChange={(e) => update("exercise_type", e.target.value as ExerciseType)}>
                  {EXERCISE_TYPES.map((t) => (
                    <option key={t.value} value={t.value}>{t.label}</option>
                  ))}
                </Select>
              </StudioField>

              <StudioField label="Difficulty" htmlFor="exercise-difficulty">
                <Select id="exercise-difficulty" value={form.difficulty} onChange={(e) => update("difficulty", e.target.value)}>
                  <option value="easy">Easy</option>
                  <option value="medium">Medium</option>
                  <option value="hard">Hard</option>
                </Select>
              </StudioField>

              <StudioField label="Language" htmlFor="exercise-language">
                <Input id="exercise-language" value={form.language} onChange={(e) => update("language", e.target.value)} />
              </StudioField>
            </div>

            <StudioField label="Instructions" htmlFor="exercise-instructions" required>
              <Textarea id="exercise-instructions" value={form.instructions} onChange={(e) => update("instructions", e.target.value)} rows={5} required />
            </StudioField>

            <div className="grid gap-4 sm:grid-cols-2">
              <StudioField label="Context" htmlFor="exercise-context">
                <Textarea id="exercise-context" value={form.context} onChange={(e) => update("context", e.target.value)} rows={4} />
              </StudioField>
              <StudioField label="Constraints" htmlFor="exercise-constraints">
                <Textarea id="exercise-constraints" value={form.constraints} onChange={(e) => update("constraints", e.target.value)} rows={4} />
              </StudioField>
            </div>

            <StudioField label="Expected Behavior" htmlFor="exercise-expected">
              <Textarea id="exercise-expected" value={form.expected_behavior} onChange={(e) => update("expected_behavior", e.target.value)} rows={4} />
            </StudioField>

            {isChoiceType && (
              <StudioField label="Choices (JSON)" htmlFor="exercise-choices" hint='[{"id": "a", "text": "Option A", "is_correct": true}]'>
                <Textarea id="exercise-choices" value={form.choices} onChange={(e) => update("choices", e.target.value)} rows={6} className="font-mono" />
              </StudioField>
            )}

            {isCodeType || isOutputType && (
              <StudioField label="Starter Code" htmlFor="exercise-starter">
                <Textarea id="exercise-starter" value={form.starter_code} onChange={(e) => update("starter_code", e.target.value)} rows={8} className="font-mono" />
              </StudioField>
            )}

            {isOutputType && (
              <StudioField label="Expected Output" htmlFor="exercise-output">
                <Textarea id="exercise-output" value={form.expected_output} onChange={(e) => update("expected_output", e.target.value)} rows={4} />
              </StudioField>
            )}

            {!isChoiceType && (
              <StudioField label="Solution Code" htmlFor="exercise-solution">
                <Textarea id="exercise-solution" value={form.solution_code} onChange={(e) => update("solution_code", e.target.value)} rows={8} className="font-mono" />
              </StudioField>
            )}

            <StudioField label="Test Cases (JSON)" htmlFor="exercise-test-cases" hint='[{"input": "...", "expected_output": "..."}]'>
              <Textarea id="exercise-test-cases" value={form.test_cases} onChange={(e) => update("test_cases", e.target.value)} rows={6} className="font-mono" />
            </StudioField>

            <StudioField label="Explanation" htmlFor="exercise-explanation">
              <Textarea id="exercise-explanation" value={form.explain} onChange={(e) => update("explain", e.target.value)} rows={4} />
            </StudioField>

            <div className="grid gap-4 sm:grid-cols-3">
              <StudioField label="XP Reward" htmlFor="exercise-xp">
                <Input id="exercise-xp" type="number" min="0" value={form.xp_reward} onChange={(e) => update("xp_reward", Number(e.target.value))} />
              </StudioField>
              <StudioField label="Max Attempts (0 = unlimited)" htmlFor="exercise-attempts">
                <Input id="exercise-attempts" type="number" min="0" value={form.max_attempts} onChange={(e) => update("max_attempts", Number(e.target.value))} />
              </StudioField>
              <StudioField label="Order" htmlFor="exercise-order">
                <Input id="exercise-order" type="number" min="1" value={form.order} onChange={(e) => update("order", Number(e.target.value))} />
              </StudioField>
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <StudioField label="Active" htmlFor="exercise-active">
                <label className="flex items-center gap-2">
                  <input id="exercise-active" type="checkbox" checked={form.is_active} onChange={(e) => update("is_active", e.target.checked)} className="h-4 w-4 rounded border-input" />
                  Active
                </label>
              </StudioField>
              <StudioField label="Final Assessment" htmlFor="exercise-final">
                <label className="flex items-center gap-2">
                  <input id="exercise-final" type="checkbox" checked={form.is_final_assessment} onChange={(e) => update("is_final_assessment", e.target.checked)} className="h-4 w-4 rounded border-input" />
                  Final assessment
                </label>
              </StudioField>
            </div>

            {error && <StudioError message={error} />}

            <div className="flex justify-end gap-3 pt-4 border-t">
              <Button type="button" variant="outline" onClick={() => router.back()}>Cancel</Button>
              <Button type="submit" disabled={saving}>{saving ? "Saving..." : "Save changes"}</Button>
              <Button type="button" variant="destructive" onClick={handleDelete} disabled={saving}>Delete</Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
