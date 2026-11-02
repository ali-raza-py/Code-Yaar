"use client";

import { useCallback, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { AlertCircle, ImagePlus, Loader2, Star, Trash2 } from "lucide-react";
import {
  ApiError, studentProjects,
  PROJECT_CATEGORY_LABELS, PROJECT_STATUS_LABELS,
  type ProjectCategory, type ProjectStatus, type ProjectVisibility,
  type StudentProject, type StudentProjectInput,
} from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { MAX_FEATURED } from "./shared";

const CATEGORY_OPTIONS = Object.keys(PROJECT_CATEGORY_LABELS) as ProjectCategory[];
const STATUS_OPTIONS = Object.keys(PROJECT_STATUS_LABELS) as ProjectStatus[];

const ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"];
const MAX_IMAGE_BYTES = 5 * 1024 * 1024;

/** Shared create/edit form. Rich sections keep it scannable but every field is optional except the essentials. */
export function ProjectEditor({
  mode, project, alreadyFeatured = 0,
}: {
  mode: "create" | "edit";
  project?: StudentProject;
  /** Featured count excluding this project, so the editor can warn before submit. */
  alreadyFeatured?: number;
}) {
  const router = useRouter();

  const [title, setTitle] = useState(project?.title ?? "");
  const [shortDescription, setShortDescription] = useState(project?.short_description ?? "");
  const [overview, setOverview] = useState(project?.overview ?? "");
  const [category, setCategory] = useState<ProjectCategory>(project?.category ?? "web_development");
  const [status, setStatus] = useState<ProjectStatus>(project?.status ?? "completed");
  const [githubUrl, setGithubUrl] = useState(project?.github_url ?? "");
  const [liveDemoUrl, setLiveDemoUrl] = useState(project?.live_demo_url ?? "");
  const [docsUrl, setDocsUrl] = useState(project?.docs_url ?? "");
  const [problemStatement, setProblemStatement] = useState(project?.problem_statement ?? "");
  const [solution, setSolution] = useState(project?.solution ?? "");
  const [technicalDetails, setTechnicalDetails] = useState(project?.technical_details ?? "");
  const [challenges, setChallenges] = useState(project?.challenges ?? "");
  const [lessonsLearned, setLessonsLearned] = useState(project?.lessons_learned ?? "");
  const [contributions, setContributions] = useState(project?.contributions ?? "");
  const [technologiesText, setTechnologiesText] = useState((project?.technologies ?? []).join(", "));
  const [startDate, setStartDate] = useState(project?.start_date ?? "");
  const [completionDate, setCompletionDate] = useState(project?.completion_date ?? "");
  const [featured, setFeatured] = useState(project?.featured ?? false);
  const [visibility, setVisibility] = useState<ProjectVisibility>(project?.visibility ?? "public");
  const [coverFile, setCoverFile] = useState<File | null>(null);

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [banner, setBanner] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const technologies = useMemo(
    () => technologiesText.split(",").map((t) => t.trim()).filter(Boolean),
    [technologiesText],
  );

  const validate = useCallback((): Record<string, string> => {
    const next: Record<string, string> = {};
    if (!title.trim()) next.title = "A project needs a title.";
    if (!shortDescription.trim()) next.short_description = "Add a one-line summary of what this is.";
    for (const [key, value] of Object.entries({ githubUrl, liveDemoUrl, docsUrl })) {
      if (value && !/^https?:\/\/.+\..+/i.test(value)) {
        next[key === "githubUrl" ? "github_url" : key === "liveDemoUrl" ? "live_demo_url" : "docs_url"] =
          "Enter a full URL starting with http:// or https://.";
      }
    }
    if (coverFile && !ALLOWED_IMAGE_TYPES.includes(coverFile.type)) {
      next.cover_image = "Cover must be a JPEG, PNG or WebP image.";
    }
    if (coverFile && coverFile.size > MAX_IMAGE_BYTES) {
      next.cover_image = "Cover image must be under 5 MB.";
    }
    if (featured && mode === "create" && alreadyFeatured >= MAX_FEATURED) {
      next.featured = `You already have ${MAX_FEATURED} featured projects. Feature this one later by unfeaturing another.`;
    }
    return next;
  }, [title, shortDescription, githubUrl, liveDemoUrl, docsUrl, coverFile, featured, mode, alreadyFeatured]);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setBanner(null);
    const clientErrors = validate();
    setErrors(clientErrors);
    if (Object.keys(clientErrors).length > 0) {
      setBanner("Please fix the highlighted fields.");
      return;
    }

    const payload: StudentProjectInput = {
      title: title.trim(),
      short_description: shortDescription.trim(),
      overview: overview.trim(),
      category,
      status,
      github_url: githubUrl.trim(),
      live_demo_url: liveDemoUrl.trim(),
      docs_url: docsUrl.trim(),
      problem_statement: problemStatement.trim(),
      solution: solution.trim(),
      technical_details: technicalDetails.trim(),
      challenges: challenges.trim(),
      lessons_learned: lessonsLearned.trim(),
      contributions: contributions.trim(),
      technologies,
      start_date: startDate || null,
      completion_date: completionDate || null,
      featured,
      visibility,
    };

    setSaving(true);
    try {
      if (mode === "create") {
        await studentProjects.create(payload, coverFile);
      } else if (project) {
        await studentProjects.update(project.id, payload, coverFile);
      }
      router.push("/profile/portfolio");
      router.refresh();
    } catch (err) {
      // Surface server-side validation next to the offending fields; input is preserved.
      if (err instanceof ApiError && err.fieldErrors) {
        const mapped: Record<string, string> = {};
        for (const [field, messages] of Object.entries(err.fieldErrors)) {
          mapped[field] = messages.join(" ");
        }
        setErrors(mapped);
        setBanner(mapped.non_field_errors ?? "The portfolio service rejected these changes.");
      } else {
        setBanner(err instanceof Error ? err.message : "Something went wrong saving this project.");
      }
    } finally {
      setSaving(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="space-y-6" noValidate>
      {banner && (
        <div role="alert" className="flex items-start gap-2 rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
          <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
          <span>{banner}</span>
        </div>
      )}

      <EditorSection title="Basics" description="What the project is, at a glance.">
        <Field label="Title" error={errors.title} required>
          <TextInput value={title} onChange={setTitle} placeholder="Distributed rate limiter" invalid={!!errors.title} />
        </Field>
        <Field label="One-line summary" error={errors.short_description} required>
          <TextInput value={shortDescription} onChange={setShortDescription} placeholder="A Redis-backed limiter that survives restarts." maxLength={300} invalid={!!errors.short_description} />
        </Field>
        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="Category">
            <SelectInput value={category} onChange={(v) => setCategory(v as ProjectCategory)} options={CATEGORY_OPTIONS.map((c) => [c, PROJECT_CATEGORY_LABELS[c]])} />
          </Field>
          <Field label="Status">
            <SelectInput value={status} onChange={(v) => setStatus(v as ProjectStatus)} options={STATUS_OPTIONS.map((s) => [s, PROJECT_STATUS_LABELS[s]])} />
          </Field>
        </div>
        <Field label="Overview" hint="A short paragraph on the what and why.">
          <TextArea value={overview} onChange={setOverview} rows={3} />
        </Field>
      </EditorSection>

      <EditorSection title="Links" description="Point visitors to the real work. Only links you add are shown.">
        <Field label="Repository URL" error={errors.github_url}>
          <TextInput value={githubUrl} onChange={setGithubUrl} placeholder="https://github.com/you/project" invalid={!!errors.github_url} />
        </Field>
        <Field label="Live demo URL" error={errors.live_demo_url}>
          <TextInput value={liveDemoUrl} onChange={setLiveDemoUrl} placeholder="https://demo.example.com" invalid={!!errors.live_demo_url} />
        </Field>
        <Field label="Documentation URL" error={errors.docs_url}>
          <TextInput value={docsUrl} onChange={setDocsUrl} placeholder="https://you.dev/project/docs" invalid={!!errors.docs_url} />
        </Field>
      </EditorSection>

      <EditorSection title="The story" description="Show the thinking, not just the result — this is what makes a portfolio credible.">
        <Field label="Problem"><TextArea value={problemStatement} onChange={setProblemStatement} rows={3} /></Field>
        <Field label="Solution"><TextArea value={solution} onChange={setSolution} rows={3} /></Field>
        <Field label="Technical implementation"><TextArea value={technicalDetails} onChange={setTechnicalDetails} rows={4} /></Field>
        <Field label="Your role & contributions"><TextArea value={contributions} onChange={setContributions} rows={3} /></Field>
        <Field label="Challenges"><TextArea value={challenges} onChange={setChallenges} rows={3} /></Field>
        <Field label="What you learned"><TextArea value={lessonsLearned} onChange={setLessonsLearned} rows={3} /></Field>
      </EditorSection>

      <EditorSection title="Technology & timing" description="Stacks and dates are shown as tags, never as a fake proficiency score.">
        <Field label="Technologies" hint="Comma-separated, e.g. Python, Django, Redis">
          <TextInput value={technologiesText} onChange={setTechnologiesText} placeholder="React, TypeScript, Node.js" />
        </Field>
        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="Start date">
            <TextInput type="date" value={startDate} onChange={setStartDate} />
          </Field>
          <Field label="Completion date">
            <TextInput type="date" value={completionDate} onChange={setCompletionDate} />
          </Field>
        </div>
      </EditorSection>

      <EditorSection title="Cover, visibility & featuring">
        <Field label="Cover image" error={errors.cover_image} hint="JPEG, PNG or WebP, up to 5 MB.">
          <CoverPicker file={coverFile} onChange={setCoverFile} existing={project?.cover_image_url} />
        </Field>
        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="Visibility">
            <SelectInput
              value={visibility}
              onChange={(v) => setVisibility(v as ProjectVisibility)}
              options={[["public", "Public — visible on your portfolio"], ["private", "Private — only you"]]}
            />
          </Field>
          <Field label="Featured" error={errors.featured}>
            <label className={cn("flex min-h-11 cursor-pointer items-center gap-2 rounded-lg border px-3 py-2 text-sm", featured ? "border-primary bg-primary/5 text-foreground" : "border-border text-muted-foreground")}>
              <input type="checkbox" className="sr-only" checked={featured} onChange={(e) => setFeatured(e.target.checked)} />
              <Star className={cn("h-4 w-4", featured ? "fill-primary text-primary" : "")} aria-hidden="true" />
              {featured ? "Featured on your portfolio" : "Feature this project"}
            </label>
          </Field>
        </div>
      </EditorSection>

      <div className="flex flex-wrap items-center gap-3">
        <Button type="submit" disabled={saving}>
          {saving && <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />}
          {saving ? "Saving…" : mode === "create" ? "Create project" : "Save changes"}
        </Button>
        <Button type="button" variant="ghost" onClick={() => router.push("/profile/portfolio")} disabled={saving}>
          Cancel
        </Button>
      </div>
    </form>
  );
}

function EditorSection({ title, description, children }: { title: string; description?: string; children: React.ReactNode }) {
  return (
    <Card className="p-5 sm:p-6">
      <div className="mb-4">
        <h2 className="text-base font-semibold text-foreground">{title}</h2>
        {description && <p className="mt-1 text-sm text-muted-foreground">{description}</p>}
      </div>
      <div className="space-y-4">{children}</div>
    </Card>
  );
}

function Field({ label, hint, error, required, children }: { label: string; hint?: string; error?: string; required?: boolean; children: React.ReactNode }) {
  return (
    <label className="block">
      <span className="mb-1.5 flex items-center gap-1 text-sm font-medium text-foreground">
        {label}
        {required && <span className="text-destructive" aria-hidden="true">*</span>}
      </span>
      {children}
      {hint && !error && <span className="mt-1 block text-xs text-muted-foreground">{hint}</span>}
      {error && <span className="mt-1 block text-xs font-medium text-destructive">{error}</span>}
    </label>
  );
}

function TextInput({
  value, onChange, placeholder, type = "text", maxLength, invalid,
}: {
  value: string; onChange: (v: string) => void; placeholder?: string;
  type?: string; maxLength?: number; invalid?: boolean;
}) {
  return (
    <input
      type={type}
      value={value}
      maxLength={maxLength}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      className={cn(
        "min-h-11 w-full rounded-lg border bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring",
        invalid ? "border-destructive" : "border-border",
      )}
    />
  );
}

function TextArea({ value, onChange, rows = 3 }: { value: string; onChange: (v: string) => void; rows?: number }) {
  return (
    <textarea
      value={value}
      rows={rows}
      onChange={(e) => onChange(e.target.value)}
      className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
    />
  );
}

function SelectInput({
  value, onChange, options,
}: { value: string; onChange: (v: string) => void; options: Array<[string, string]> }) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="min-h-11 w-full rounded-lg border border-border bg-background px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
    >
      {options.map(([v, label]) => (
        <option key={v} value={v}>{label}</option>
      ))}
    </select>
  );
}

function CoverPicker({
  file, onChange, existing,
}: { file: File | null; onChange: (f: File | null) => void; existing?: string }) {
  const preview = file ? URL.createObjectURL(file) : existing || "";
  return (
    <div className="flex items-center gap-3">
      {preview ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img src={preview} alt="Cover preview" className="h-16 w-28 rounded-lg border border-border object-cover" />
      ) : (
        <div className="flex h-16 w-28 items-center justify-center rounded-lg border border-dashed border-border text-muted-foreground">
          <ImagePlus className="h-5 w-5" aria-hidden="true" />
        </div>
      )}
      <div className="flex flex-wrap gap-2">
        <label className="inline-flex min-h-9 cursor-pointer items-center gap-2 rounded-md border border-border bg-background px-3 text-xs font-semibold text-foreground hover:bg-secondary">
          <input
            type="file"
            accept="image/jpeg,image/png,image/webp"
            className="sr-only"
            onChange={(e) => onChange(e.target.files?.[0] ?? null)}
          />
          {file ? "Change" : "Choose image"}
        </label>
        {file && (
          <Button type="button" size="sm" variant="ghost" onClick={() => onChange(null)}>
            <Trash2 className="h-3.5 w-3.5" aria-hidden="true" /> Remove
          </Button>
        )}
      </div>
    </div>
  );
}
