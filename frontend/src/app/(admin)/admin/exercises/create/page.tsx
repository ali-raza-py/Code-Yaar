"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { adminApi } from "@/lib/admin-api";
import type { LessonAdmin } from "@/lib/admin-api";
import { Button } from "@/components/ui/button";
import { Input, Label, Textarea } from "@/components/admin/studio/studio-fields";

const initialForm = {
  title: "",
  lesson: "",
  exercise_type: "code",
  difficulty: "beginner",
  language: "python",
  instructions: "",
  context: "",
  constraints: "",
  expected_behavior: "",
  explain: "",
  starter_code: "",
  solution_code: "",
  expected_output: "",
  xp_reward: "50",
  max_attempts: "0",
  order: "1",
};

export default function CreateExercisePage() {
  const router = useRouter();
  const [lessons, setLessons] = useState<LessonAdmin[]>([]);
  const [form, setForm] = useState(initialForm);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    adminApi.listLessons({ page_size: 100 }).then((data) => {
      setLessons(data.results);
    }).catch(() => setError("Could not load lessons."));
  }, []);

  const update = (key: keyof typeof initialForm, value: string) => {
    setForm((current) => ({ ...current, [key]: value }));
  };

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setError("");
    try {
      await adminApi.createExercise({
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
        xp_reward: Number(form.xp_reward) || 0,
        max_attempts: Number(form.max_attempts) || 0,
        order: Number(form.order) || 1,
        is_active: true,
        choices: [],
        test_cases: [],
        hidden_tests: [],
      });
      router.replace("/admin/exercises");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Exercise could not be created.");
      setSaving(false);
    }
  }

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Create Exercise</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Add an exercise to an existing lesson.
        </p>
      </div>
      <form onSubmit={submit} className="space-y-5 rounded-xl border border-border bg-card p-6">
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <Label htmlFor="exercise-title">Title</Label>
            <Input id="exercise-title" value={form.title} onChange={(e) => update("title", e.target.value)} required />
          </div>
          <label className="text-sm font-medium">
            Lesson
            <select id="exercise-lesson" className="mt-1 w-full rounded-md border border-border bg-background px-3 py-2" value={form.lesson} onChange={(e) => update("lesson", e.target.value)} required>
              <option value="">Select a lesson</option>
              {lessons.map((lesson) => (
                <option key={lesson.id} value={lesson.id}>{lesson.course_title} / {lesson.chapter_title} / {lesson.title}</option>
              ))}
            </select>
          </label>
        </div>
        <div className="grid gap-4 sm:grid-cols-3">
          <label className="text-sm font-medium">Type<select className="mt-1 w-full rounded-md border border-border bg-background px-3 py-2" value={form.exercise_type} onChange={(e) => update("exercise_type", e.target.value)}><option value="code">Code</option><option value="mcq">Multiple choice</option><option value="true_false">True / false</option><option value="short_answer">Short answer</option></select></label>
          <label className="text-sm font-medium">Difficulty<select className="mt-1 w-full rounded-md border border-border bg-background px-3 py-2" value={form.difficulty} onChange={(e) => update("difficulty", e.target.value)}><option value="beginner">Beginner</option><option value="intermediate">Intermediate</option><option value="advanced">Advanced</option></select></label>
          <div><Label htmlFor="exercise-language">Language</Label><Input id="exercise-language" value={form.language} onChange={(e) => update("language", e.target.value)} /></div>
        </div>
        <div><Label htmlFor="exercise-instructions">Instructions</Label><Textarea id="exercise-instructions" value={form.instructions} onChange={(e) => update("instructions", e.target.value)} rows={5} required /></div>
        <div className="grid gap-4 sm:grid-cols-2">
          <div><Label htmlFor="exercise-context">Context</Label><Textarea id="exercise-context" value={form.context} onChange={(e) => update("context", e.target.value)} rows={4} /></div>
          <div><Label htmlFor="exercise-constraints">Constraints</Label><Textarea id="exercise-constraints" value={form.constraints} onChange={(e) => update("constraints", e.target.value)} rows={4} /></div>
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <div><Label htmlFor="exercise-starter">Starter code</Label><Textarea id="exercise-starter" value={form.starter_code} onChange={(e) => update("starter_code", e.target.value)} rows={8} className="font-mono" /></div>
          <div><Label htmlFor="exercise-solution">Reference solution</Label><Textarea id="exercise-solution" value={form.solution_code} onChange={(e) => update("solution_code", e.target.value)} rows={8} className="font-mono" /></div>
        </div>
        <div><Label htmlFor="exercise-output">Expected output</Label><Textarea id="exercise-output" value={form.expected_output} onChange={(e) => update("expected_output", e.target.value)} rows={3} /></div>
        <div className="grid gap-4 sm:grid-cols-3">
          <div><Label htmlFor="exercise-xp">XP reward</Label><Input id="exercise-xp" type="number" min="0" value={form.xp_reward} onChange={(e) => update("xp_reward", e.target.value)} /></div>
          <div><Label htmlFor="exercise-attempts">Max attempts (0 = unlimited)</Label><Input id="exercise-attempts" type="number" min="0" value={form.max_attempts} onChange={(e) => update("max_attempts", e.target.value)} /></div>
          <div><Label htmlFor="exercise-order">Order</Label><Input id="exercise-order" type="number" min="1" value={form.order} onChange={(e) => update("order", e.target.value)} /></div>
        </div>
        <div><Label htmlFor="exercise-explanation">Explanation</Label><Textarea id="exercise-explanation" value={form.explain} onChange={(e) => update("explain", e.target.value)} rows={4} /></div>
        {error && <p className="text-sm text-destructive">{error}</p>}
        <div className="flex justify-end gap-3">
          <Button type="button" variant="outline" onClick={() => router.back()}>Cancel</Button>
          <Button type="submit" disabled={saving}>{saving ? "Creating..." : "Create exercise"}</Button>
        </div>
      </form>
    </div>
  );
}
