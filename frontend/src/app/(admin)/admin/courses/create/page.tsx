"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { adminApi } from "@/lib/admin-api";
import type { CareerTrackAdmin } from "@/lib/admin-api";
import { Button } from "@/components/ui/button";
import { Input, Label, Textarea } from "@/components/admin/studio/studio-fields";

export default function CreateCoursePage() {
  const router = useRouter();
  const [tracks, setTracks] = useState<CareerTrackAdmin[]>([]);
  const [form, setForm] = useState({
    title: "", subtitle: "", description: "", track: "", difficulty: "beginner",
    language: "python", academic_class: "", instructor: "", prerequisites: "",
    objectives: "", is_free: true, certification_enabled: true,
    require_all_lessons: true, require_final_assessment: true,
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    adminApi.listTracks({ page_size: 100 })
      .then((data) => setTracks(data.results))
      .catch(() => setError("Could not load learning tracks."));
  }, []);
  const update = (key: string, value: string | boolean) => setForm((current) => ({ ...current, [key]: value }));

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setError("");
    try {
      const bundle = await adminApi.createStudioCourse({
        title: form.title.trim(),
        subtitle: form.subtitle.trim(),
        description: form.description.trim(),
        track: form.track ? Number(form.track) : null,
        difficulty: form.difficulty,
        language: form.language,
        academic_class: form.academic_class.trim(),
        instructor: form.instructor.trim(),
        prerequisites: form.prerequisites.trim() || "None",
        learning_objectives: form.objectives.split("\n").map((item) => item.trim()).filter(Boolean),
        is_free: form.is_free,
        certification_enabled: form.certification_enabled,
        require_all_lessons: form.require_all_lessons,
        require_final_assessment: form.require_final_assessment,
      });
      router.replace(`/admin/courses?created=${bundle.course.id}`);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Course could not be created.");
      setSaving(false);
    }
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-foreground">Create Course</h1>
        <p className="mt-1 text-sm text-muted-foreground">Create a draft course, then add chapters and lessons.</p>
      </div>
      <form onSubmit={submit} className="space-y-6 rounded-xl border border-border bg-card p-6">
        <div>
          <Label htmlFor="course-title">Title</Label>
          <Input id="course-title" value={form.title} onChange={(event) => update("title", event.target.value)} placeholder="e.g. Python Foundations" required />
          <p className="mt-1 text-xs text-muted-foreground">Use a clear name learners will recognize.</p>
        </div>
        <div><Label htmlFor="course-subtitle">Short subtitle</Label><Input id="course-subtitle" value={form.subtitle} onChange={(event) => update("subtitle", event.target.value)} placeholder="A practical introduction to Python programming" /></div>
        <div>
          <Label htmlFor="course-description">Description</Label>
          <Textarea id="course-description" value={form.description} onChange={(event) => update("description", event.target.value)} placeholder="Explain what learners will build, practice, and achieve." required rows={5} />
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <label className="text-sm font-medium">Track
            <select className="mt-1 w-full rounded-md border border-border bg-background px-3 py-2" value={form.track} onChange={(event) => update("track", event.target.value)} required>
              <option value="">Select a track</option>
              {tracks.map((item) => <option key={item.id} value={item.id}>{item.title}</option>)}
            </select>
          </label>
          <label className="text-sm font-medium">Difficulty
            <select className="mt-1 w-full rounded-md border border-border bg-background px-3 py-2" value={form.difficulty} onChange={(event) => update("difficulty", event.target.value)}>
              {["beginner", "elementary", "intermediate", "advanced", "expert"].map((item) => <option key={item} value={item}>{item}</option>)}
            </select>
          </label>
          <label className="text-sm font-medium">Language
            <select className="mt-1 w-full rounded-md border border-border bg-background px-3 py-2" value={form.language} onChange={(event) => update("language", event.target.value)}>
              {["python", "javascript", "cpp", "java", "other"].map((item) => <option key={item} value={item}>{item}</option>)}
            </select>
          </label>
          <div><Label htmlFor="course-class">Academic class (optional)</Label><Input id="course-class" value={form.academic_class} onChange={(event) => update("academic_class", event.target.value)} placeholder="e.g. Class X" /></div>
          <div><Label htmlFor="course-instructor">Instructor display name</Label><Input id="course-instructor" value={form.instructor} onChange={(event) => update("instructor", event.target.value)} placeholder="e.g. Code Yaar Team" /></div>
        </div>
        <div><Label htmlFor="course-objectives">Learning objectives (one per line)</Label><Textarea id="course-objectives" value={form.objectives} onChange={(event) => update("objectives", event.target.value)} placeholder={"Write readable outcomes for learners\nBuild and run Python programs\nSolve beginner coding exercises"} rows={4} /></div>
        <div><Label htmlFor="course-prerequisites">Prerequisites</Label><Textarea id="course-prerequisites" value={form.prerequisites} onChange={(event) => update("prerequisites", event.target.value)} placeholder="No prior experience required" rows={3} /></div>
        <fieldset className="space-y-3 rounded-lg bg-muted/40 p-4"><legend className="font-semibold">Course settings</legend>
          {([["is_free", "Free course"], ["certification_enabled", "Offer a certificate on completion"], ["require_all_lessons", "Require all lessons before completion"], ["require_final_assessment", "Require the final assessment"]] as const).map(([key, label]) => <label key={key} className="flex items-center gap-2 text-sm"><input type="checkbox" checked={form[key]} onChange={(event) => update(key, event.target.checked)} />{label}</label>)}
        </fieldset>
        {error && <p className="text-sm text-destructive">{error}</p>}
        <div className="flex justify-end gap-3">
          <Button type="button" variant="outline" onClick={() => router.back()}>Cancel</Button>
          <Button type="submit" disabled={saving}>{saving ? "Creating..." : "Create draft course"}</Button>
        </div>
      </form>
    </div>
  );
}
