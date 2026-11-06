"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { adminApi } from "@/lib/admin-api";
import type { CourseAdmin } from "@/lib/admin-api";
import { Button } from "@/components/ui/button";
import { Input, Label, Textarea } from "@/components/admin/studio/studio-fields";

export default function CreateChapterPage() {
  const router = useRouter();
  const [courses, setCourses] = useState<CourseAdmin[]>([]);
  const [form, setForm] = useState({ title: "", description: "", course: "", order: "1", xp_reward: "0" });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  useEffect(() => {
    adminApi.listCourses({ page_size: 100 }).then((data) => setCourses(data.results)).catch(() => setError("Could not load courses."));
  }, []);
  const update = (key: string, value: string) => setForm((current) => ({ ...current, [key]: value }));
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setSaving(true); setError("");
    try {
      await adminApi.createChapter({ title: form.title.trim(), description: form.description.trim(), course: Number(form.course), order: Number(form.order) || 1, xp_reward: Number(form.xp_reward) || 0, is_active: true });
      router.replace("/admin/chapters");
    } catch (caught) { setError(caught instanceof Error ? caught.message : "Chapter could not be created."); setSaving(false); }
  }
  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div><h1 className="text-3xl font-bold tracking-tight">Create Chapter</h1><p className="mt-1 text-sm text-muted-foreground">A chapter groups related lessons inside one course.</p></div>
      <form onSubmit={submit} className="space-y-5 rounded-xl border border-border bg-card p-6">
        <div><Label htmlFor="chapter-title">Chapter title</Label><Input id="chapter-title" value={form.title} onChange={(e) => update("title", e.target.value)} placeholder="e.g. Variables and Data Types" required /></div>
        <label className="text-sm font-medium">Course<select id="chapter-course" className="mt-1 w-full rounded-md border border-border bg-background px-3 py-2" value={form.course} onChange={(e) => update("course", e.target.value)} required><option value="">Select a course</option>{courses.map((course) => <option key={course.id} value={course.id}>{course.title}</option>)}</select></label>
        <div><Label htmlFor="chapter-description">Description</Label><Textarea id="chapter-description" value={form.description} onChange={(e) => update("description", e.target.value)} placeholder="What will learners study in this chapter?" rows={4} required /></div>
        <div className="grid gap-4 sm:grid-cols-2"><div><Label htmlFor="chapter-order">Order</Label><Input id="chapter-order" type="number" min="1" value={form.order} onChange={(e) => update("order", e.target.value)} /></div><div><Label htmlFor="chapter-xp">XP reward</Label><Input id="chapter-xp" type="number" min="0" value={form.xp_reward} onChange={(e) => update("xp_reward", e.target.value)} /></div></div>
        {error && <p className="text-sm text-destructive">{error}</p>}
        <div className="flex justify-end gap-3"><Button type="button" variant="outline" onClick={() => router.back()}>Cancel</Button><Button type="submit" disabled={saving}>{saving ? "Creating..." : "Create chapter"}</Button></div>
      </form>
    </div>
  );
}
