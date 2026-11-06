"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { adminApi } from "@/lib/admin-api";
import { Button } from "@/components/ui/button";
import { Input, Label, Textarea } from "@/components/admin/studio/studio-fields";

export default function CreateTrackPage() {
  const router = useRouter();
  const [form, setForm] = useState({
    title: "", description: "", category: "programming", difficulty: "beginner",
    estimated_hours: "10", icon: "", learning_objectives: "",
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const update = (key: string, value: string) => setForm((current) => ({ ...current, [key]: value }));

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setError("");
    try {
      await adminApi.createTrack({
        title: form.title.trim(),
        description: form.description.trim(),
        category: form.category,
        difficulty: form.difficulty,
        estimated_hours: Number(form.estimated_hours) || 0,
        icon: form.icon.trim(),
        learning_objectives: form.learning_objectives.split("\n").map((item) => item.trim()).filter(Boolean),
        is_active: true,
        is_published: false,
      });
      router.replace("/admin/tracks");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Track could not be created.");
      setSaving(false);
    }
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div><h1 className="text-3xl font-bold tracking-tight">Create Learning Track</h1><p className="mt-1 text-sm text-muted-foreground">Define the learner journey first; courses can be added afterward.</p></div>
      <form onSubmit={submit} className="space-y-5 rounded-xl border border-border bg-card p-6">
        <div><Label htmlFor="track-title">Track name</Label><Input id="track-title" value={form.title} onChange={(e) => update("title", e.target.value)} placeholder="e.g. Python Development" required /></div>
        <div><Label htmlFor="track-description">Description</Label><Textarea id="track-description" value={form.description} onChange={(e) => update("description", e.target.value)} placeholder="Explain who this track is for and what learners will achieve." rows={5} required /></div>
        <div className="grid gap-4 sm:grid-cols-3">
          <label className="text-sm font-medium">Category<select className="mt-1 w-full rounded-md border border-border bg-background px-3 py-2" value={form.category} onChange={(e) => update("category", e.target.value)}>{[["programming","Programming"],["school_board","School & Board Education"],["web","Web Development"],["ai","Artificial Intelligence"],["other","Other"]].map(([value,label]) => <option key={value} value={value}>{label}</option>)}</select></label>
          <label className="text-sm font-medium">Difficulty<select className="mt-1 w-full rounded-md border border-border bg-background px-3 py-2" value={form.difficulty} onChange={(e) => update("difficulty", e.target.value)}>{["beginner","intermediate","advanced"].map((item) => <option key={item}>{item}</option>)}</select></label>
          <div><Label htmlFor="track-hours">Estimated hours</Label><Input id="track-hours" type="number" min="0" value={form.estimated_hours} onChange={(e) => update("estimated_hours", e.target.value)} /></div>
        </div>
        <div><Label htmlFor="track-icon">Icon name (optional)</Label><Input id="track-icon" value={form.icon} onChange={(e) => update("icon", e.target.value)} placeholder="code, brain, graduation-cap" /></div>
        <div><Label htmlFor="track-objectives">Learning objectives (one per line)</Label><Textarea id="track-objectives" value={form.learning_objectives} onChange={(e) => update("learning_objectives", e.target.value)} placeholder={"Build real projects\nUnderstand core concepts\nPrepare for assessments"} rows={4} /></div>
        {error && <p className="text-sm text-destructive">{error}</p>}
        <div className="flex justify-end gap-3"><Button type="button" variant="outline" onClick={() => router.back()}>Cancel</Button><Button type="submit" disabled={saving}>{saving ? "Creating..." : "Create draft track"}</Button></div>
      </form>
    </div>
  );
}
