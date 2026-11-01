"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { ArrowLeft, Loader2, Pencil, Plus, Search, Trash2 } from "lucide-react";
import { practicalAdmin } from "@/lib/api";
import { useAuth } from "@/hooks/use-auth";
import type { PracticalAdmin, PracticalClassAdmin, PracticalSubjectAdmin } from "@/types";

type Tab = "classes" | "subjects" | "practicals";
type Notice = { kind: "success" | "error"; text: string } | null;

const inputClass = "w-full rounded-lg border border-[var(--color-section-border)] bg-white px-3 py-2 text-sm outline-none focus:border-[var(--primary)]";
const textFields = ["description", "aim", "apparatus", "theory", "procedure", "observations", "calculations", "result", "precautions"] as const;

function slugify(value: string) {
  return value.trim().toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");
}

export default function PracticalManagementPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialMode = searchParams.get("mode");
  const [tab, setTab] = useState<Tab>(initialMode === "subjects" ? "subjects" : initialMode === "practicals" ? "practicals" : "classes");
  const [classes, setClasses] = useState<PracticalClassAdmin[]>([]);
  const [subjects, setSubjects] = useState<PracticalSubjectAdmin[]>([]);
  const [practicals, setPracticals] = useState<PracticalAdmin[]>([]);
  const [search, setSearch] = useState("");
  const [editing, setEditing] = useState<PracticalClassAdmin | PracticalSubjectAdmin | PracticalAdmin | null | undefined>(null);
  const [notice, setNotice] = useState<Notice>(null);
  const [busy, setBusy] = useState(false);

  const load = async () => {
    try {
      const [nextClasses, nextSubjects, nextPracticals] = await Promise.all([
        practicalAdmin.classes(search),
        practicalAdmin.subjects(),
        practicalAdmin.practicals(search),
      ]);
      setClasses(nextClasses);
      setSubjects(nextSubjects);
      setPracticals(nextPracticals);
    } catch (error) {
      setNotice({ kind: "error", text: error instanceof Error ? error.message : "Content could not be loaded." });
    }
  };

  useEffect(() => {
    if (!authLoading && user?.role !== "administrator") router.replace("/learn/practicals");
  }, [authLoading, router, user?.role]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    if (user?.role === "administrator") void load();
    // Loading is intentionally tied to the role, not the search box.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user?.role]);

  const visibleSubjects = useMemo(() => {
    if (!search.trim()) return subjects;
    const query = search.toLowerCase();
    return subjects.filter((item) => `${item.title} ${item.description}`.toLowerCase().includes(query));
  }, [search, subjects]);

  async function remove(kind: Tab, id: number) {
    if (!window.confirm("Delete this item? This action cannot be undone.")) return;
    setBusy(true);
    try {
      if (kind === "classes") await practicalAdmin.deleteClass(id);
      if (kind === "subjects") await practicalAdmin.deleteSubject(id);
      if (kind === "practicals") await practicalAdmin.deletePractical(id);
      setNotice({ kind: "success", text: "Content deleted." });
      await load();
    } catch (error) {
      setNotice({ kind: "error", text: error instanceof Error ? error.message : "Delete failed." });
    } finally {
      setBusy(false);
    }
  }

  if (authLoading || user?.role !== "administrator") {
    return <main className="mx-auto max-w-7xl px-4 py-12 text-center text-muted-foreground">Checking administrator access...</main>;
  }

  return (
    <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <Link href="/learn/practicals" className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground"><ArrowLeft className="h-4 w-4" /> Practicals</Link>
      <div className="mt-5 flex flex-wrap items-end justify-between gap-4">
        <div><p className="text-xs font-bold uppercase tracking-widest text-cta">Administrator</p><h1 className="mt-1 text-3xl font-bold">Manage practical content</h1><p className="mt-2 text-muted-foreground">Create, edit, publish, and organize classes, subjects, and practicals.</p></div>
        <button type="button" onClick={() => setEditing(null)} className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-bold text-primary-foreground"><Plus className="h-4 w-4" /> Add {tab === "classes" ? "Course" : tab === "subjects" ? "Subject" : "Practical"}</button>
      </div>
      {notice && <div role="status" className={`mt-5 rounded-lg border px-4 py-3 text-sm ${notice.kind === "error" ? "border-red-200 bg-red-50 text-red-700" : "border-green-200 bg-green-50 text-green-700"}`}>{notice.text}</div>}
      <div className="mt-8 flex flex-wrap gap-2 border-b border-[var(--color-section-border)]">
        {(["classes", "subjects", "practicals"] as Tab[]).map((item) => <button key={item} type="button" onClick={() => { setTab(item); setEditing(null); }} className={`border-b-2 px-4 py-3 text-sm font-semibold capitalize ${tab === item ? "border-[var(--primary)] text-foreground" : "border-transparent text-muted-foreground"}`}>{item === "classes" ? "Courses / Classes" : item}</button>)}
      </div>
      <div className="mt-5 flex items-center gap-2"><Search className="h-4 w-4 text-muted-foreground" /><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search content..." className={`${inputClass} max-w-sm`} /></div>
      {editing !== undefined && <Editor tab={tab} item={editing} classes={classes} subjects={subjects} busy={busy} onCancel={() => setEditing(undefined)} onSaved={async () => { setEditing(undefined); setNotice({ kind: "success", text: "Content saved." }); await load(); }} onError={(text) => setNotice({ kind: "error", text })} />}
      <section className="mt-6 overflow-hidden rounded-xl border border-[var(--color-section-border)] bg-white">
        {tab === "classes" && <ClassList items={classes} onEdit={setEditing} onDelete={(id) => void remove("classes", id)} />}
        {tab === "subjects" && <SubjectList items={visibleSubjects} onEdit={setEditing} onDelete={(id) => void remove("subjects", id)} />}
        {tab === "practicals" && <PracticalList items={practicals} onEdit={setEditing} onDelete={(id) => void remove("practicals", id)} />}
        {busy && <div className="p-4 text-sm text-muted-foreground">Working...</div>}
      </section>
    </main>
  );
}

function RowActions({ onEdit, onDelete }: { onEdit: () => void; onDelete: () => void }) {
  return <div className="flex gap-2"><button type="button" aria-label="Edit" onClick={onEdit} className="rounded p-2 text-muted-foreground hover:bg-secondary hover:text-foreground"><Pencil className="h-4 w-4" /></button><button type="button" aria-label="Delete" onClick={onDelete} className="rounded p-2 text-red-600 hover:bg-red-50"><Trash2 className="h-4 w-4" /></button></div>;
}

function ClassList({ items, onEdit, onDelete }: { items: PracticalClassAdmin[]; onEdit: (item: PracticalClassAdmin) => void; onDelete: (id: number) => void }) {
  return <div>{items.map((item) => <div key={item.id} className="flex items-center justify-between border-b p-4 last:border-0"><div><p className="font-semibold">{item.title}</p><p className="text-sm text-muted-foreground">{item.slug} · {item.is_published ? "Published" : "Draft"}</p></div><RowActions onEdit={() => onEdit(item)} onDelete={() => onDelete(item.id)} /></div>)}</div>;
}

function SubjectList({ items, onEdit, onDelete }: { items: PracticalSubjectAdmin[]; onEdit: (item: PracticalSubjectAdmin) => void; onDelete: (id: number) => void }) {
  return <div>{items.map((item) => <div key={item.id} className="flex items-center justify-between border-b p-4 last:border-0"><div><p className="font-semibold">{item.title}</p><p className="text-sm text-muted-foreground">{item.practical_class} · {item.description || "No description"}</p></div><RowActions onEdit={() => onEdit(item)} onDelete={() => onDelete(item.id)} /></div>)}</div>;
}

function PracticalList({ items, onEdit, onDelete }: { items: PracticalAdmin[]; onEdit: (item: PracticalAdmin) => void; onDelete: (id: number) => void }) {
  return <div>{items.map((item) => <div key={item.id} className="flex items-center justify-between border-b p-4 last:border-0"><div><p className="font-semibold">{item.practical_number}. {item.title}</p><p className="text-sm text-muted-foreground">{item.subject} · {item.is_published ? "Published" : "Draft"}</p></div><RowActions onEdit={() => onEdit(item)} onDelete={() => onDelete(item.id)} /></div>)}</div>;
}

function Editor({ tab, item, classes, subjects, busy, onCancel, onSaved, onError }: { tab: Tab; item: PracticalClassAdmin | PracticalSubjectAdmin | PracticalAdmin | null | undefined; classes: PracticalClassAdmin[]; subjects: PracticalSubjectAdmin[]; busy: boolean; onCancel: () => void; onSaved: () => Promise<void>; onError: (text: string) => void }) {
  const [values, setValues] = useState<Record<string, string | number | boolean | unknown[]>>(() => {
    if (item) return { ...item } as unknown as Record<string, string | number | boolean | unknown[]>;
    if (tab === "classes") return { title: "", slug: "", description: "", thumbnail: "", is_published: false, is_active: true };
    if (tab === "subjects") return { practical_class: classes[0]?.id ?? "", title: "", slug: "", description: "", image: "", is_active: true };
    return { practical_class: classes[0]?.id ?? "", subject: subjects[0]?.id ?? "", slug: "", title: "", practical_number: 1, description: "", aim: "", apparatus: "", theory: "", procedure: "", observations: "", calculations: "", result: "", precautions: "", is_published: false, is_active: true, diagrams: [] };
  });
  const set = (key: string, value: string | number | boolean | unknown[]) => setValues((current) => ({ ...current, [key]: value }));
  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      const payload = { ...values };
      if (tab === "classes") await practicalAdmin.saveClass(payload as Partial<PracticalClassAdmin>, item?.id);
      if (tab === "subjects") await practicalAdmin.saveSubject(payload as Partial<PracticalSubjectAdmin>, item?.id);
      if (tab === "practicals") await practicalAdmin.savePractical(payload as Partial<PracticalAdmin>, item?.id);
      await onSaved();
    } catch (error) { onError(error instanceof Error ? error.message : "Could not save content."); }
  };
  const text = (key: string, label: string, multiline = false) => <label className="block text-sm font-semibold">{label}{multiline ? <textarea rows={3} value={String(values[key] ?? "")} onChange={(event) => set(key, event.target.value)} className={`${inputClass} mt-1`} /> : <input required={key === "title"} value={String(values[key] ?? "")} onChange={(event) => set(key, event.target.value)} onBlur={() => key === "title" && !item && set("slug", slugify(String(values.title ?? "")))} className={`${inputClass} mt-1`} />}</label>;
  return <form onSubmit={submit} className="mt-6 rounded-xl border border-cta/40 bg-cta/5 p-5"><div className="grid gap-4 md:grid-cols-2">{text("title", tab === "classes" ? "Course / class name" : tab === "subjects" ? "Subject name" : "Practical title")}{text("slug", "Slug")}{tab === "classes" && text("thumbnail", "Thumbnail URL")}{tab === "subjects" && text("image", "Subject image URL")}{tab === "practicals" && <><label className="block text-sm font-semibold">Course / class<select value={String(values.practical_class)} onChange={(event) => set("practical_class", Number(event.target.value))} className={`${inputClass} mt-1`}>{classes.map((entry) => <option key={entry.id} value={entry.id}>{entry.title}</option>)}</select></label><label className="block text-sm font-semibold">Subject<select value={String(values.subject)} onChange={(event) => set("subject", Number(event.target.value))} className={`${inputClass} mt-1`}>{subjects.filter((entry) => !values.practical_class || entry.practical_class === Number(values.practical_class)).map((entry) => <option key={entry.id} value={entry.id}>{entry.title}</option>)}</select></label></>}{tab === "practicals" && <label className="block text-sm font-semibold">Practical number<input type="number" min="1" value={String(values.practical_number)} onChange={(event) => set("practical_number", Number(event.target.value))} className={`${inputClass} mt-1`} /></label>}{text("description", "Short description", true)}{tab === "practicals" && textFields.slice(1).map((key) => text(key, key[0].toUpperCase() + key.slice(1), true))}</div><label className="mt-4 flex items-center gap-2 text-sm font-semibold"><input type="checkbox" checked={Boolean(values.is_published)} onChange={(event) => set("is_published", event.target.checked)} /> Published</label><div className="mt-5 flex gap-2"><button disabled={busy} className="rounded-lg bg-primary px-4 py-2 text-sm font-bold text-primary-foreground">{busy ? <Loader2 className="h-4 w-4 animate-spin" /> : "Save"}</button><button type="button" onClick={onCancel} className="rounded-lg border px-4 py-2 text-sm font-semibold">Cancel</button></div></form>;
}
