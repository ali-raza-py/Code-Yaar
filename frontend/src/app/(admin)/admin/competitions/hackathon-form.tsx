"use client";

import { Button } from "@/components/ui/button";
import type { CompetitionAdmin } from "@/lib/admin-api";

export interface HackathonFormValues {
  title: string;
  slug: string;
  short_description: string;
  description: string;
  category: string;
  tagsText: string;
  host_name: string;
  time_zone: string;
  difficulty: string;
  format: string;
  delivery_mode: string;
  location: string;
  registration_start: string;
  registration_deadline: string;
  competition_start: string;
  competition_end: string;
  submission_deadline: string;
  judging_end: string;
  results_announcement: string;
  participant_limit: string;
  minimum_team_size: string;
  maximum_team_size: string;
  registration_fee: string;
  eligibilityText: string;
  rulesText: string;
  problem_statement: string;
  participation_instructions: string;
  submission_requirements: string;
  evaluation_criteria: string;
  prize_information: string;
  contact_information: string;
  resourcesText: string;
}

export const EMPTY_HACKATHON_FORM: HackathonFormValues = {
  title: "", slug: "", short_description: "", description: "", category: "Programming",
  tagsText: "", host_name: "", time_zone: "UTC", difficulty: "beginner",
  format: "individual", delivery_mode: "online", location: "",
  registration_start: "", registration_deadline: "", competition_start: "",
  competition_end: "", submission_deadline: "", judging_end: "", results_announcement: "",
  participant_limit: "", minimum_team_size: "1", maximum_team_size: "4",
  registration_fee: "0",
  eligibilityText: "", rulesText: "", problem_statement: "",
  participation_instructions: "", submission_requirements: "", evaluation_criteria: "",
  prize_information: "", contact_information: "", resourcesText: "",
};

const inputClass = "mt-1 w-full rounded-md border bg-background px-3 py-2 text-sm";

const DATE_FIELDS = [
  "registration_start", "registration_deadline", "competition_start",
  "competition_end", "submission_deadline", "judging_end", "results_announcement",
] as const;

function toLocalInputValue(iso: string | null | undefined): string {
  if (!iso) return "";
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return "";
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

export function hackathonFromAdmin(data: CompetitionAdmin): HackathonFormValues {
  return {
    ...EMPTY_HACKATHON_FORM,
    title: data.title,
    slug: data.slug,
    short_description: data.short_description,
    description: data.description,
    category: data.category,
    tagsText: (data.tags || []).join(", "),
    host_name: data.host_name,
    time_zone: data.time_zone || "UTC",
    difficulty: data.difficulty,
    format: data.format,
    delivery_mode: data.delivery_mode,
    location: data.location,
    registration_start: toLocalInputValue(data.registration_start),
    registration_deadline: toLocalInputValue(data.registration_deadline),
    competition_start: toLocalInputValue(data.competition_start),
    competition_end: toLocalInputValue(data.competition_end),
    submission_deadline: toLocalInputValue(data.submission_deadline),
    judging_end: toLocalInputValue(data.judging_end),
    results_announcement: toLocalInputValue(data.results_announcement),
    participant_limit: data.participant_limit ? String(data.participant_limit) : "",
    minimum_team_size: String(data.minimum_team_size),
    maximum_team_size: String(data.maximum_team_size),
    registration_fee: String(data.registration_fee ?? "0"),
    eligibilityText: (data.eligibility_rules as string[] || []).join("\n"),
    rulesText: (data.competition_rules as string[] || []).join("\n"),
    problem_statement: data.problem_statement,
    participation_instructions: data.participation_instructions,
    submission_requirements: data.submission_requirements,
    evaluation_criteria: data.evaluation_criteria,
    prize_information: data.prize_information,
    contact_information: data.contact_information,
    resourcesText: (data.external_resources || [])
      .map((item) => `${item.title} | ${item.url}`)
      .join("\n"),
  };
}

function lines(text: string): string[] {
  return text.split("\n").map((line) => line.trim()).filter(Boolean);
}

export function hackathonToPayload(values: HackathonFormValues): Partial<CompetitionAdmin> {
  const payload: Record<string, unknown> = {
    title: values.title,
    slug: values.slug || values.title.toLowerCase().trim().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, ""),
    short_description: values.short_description,
    description: values.description,
    category: values.category,
    tags: values.tagsText.split(",").map((tag) => tag.trim()).filter(Boolean),
    host_name: values.host_name,
    time_zone: values.time_zone || "UTC",
    difficulty: values.difficulty,
    format: values.format,
    delivery_mode: values.delivery_mode,
    location: values.location,
    participant_limit: values.participant_limit ? Number(values.participant_limit) : null,
    minimum_team_size: Number(values.minimum_team_size) || 1,
    maximum_team_size: Number(values.maximum_team_size) || 2,
    registration_fee: values.registration_fee || "0",
    eligibility_rules: lines(values.eligibilityText),
    competition_rules: lines(values.rulesText),
    problem_statement: values.problem_statement,
    participation_instructions: values.participation_instructions,
    submission_requirements: values.submission_requirements,
    evaluation_criteria: values.evaluation_criteria,
    prize_information: values.prize_information,
    contact_information: values.contact_information,
    external_resources: lines(values.resourcesText)
      .map((row) => {
        const [title, ...rest] = row.split("|");
        return { title: (title || "").trim(), url: rest.join("|").trim() };
      })
      .filter((item) => item.url),
  };
  for (const key of DATE_FIELDS) {
    const value = values[key];
    if (value) payload[key] = new Date(value).toISOString();
  }
  return payload as Partial<CompetitionAdmin>;
}

function Field({
  label,
  children,
  className = "",
}: {
  label: string;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <label className={`block text-sm font-medium ${className}`}>
      {label}
      {children}
    </label>
  );
}

function SectionTitle({ children }: { children: React.ReactNode }) {
  return (
    <h2 className="border-b border-[var(--color-section-border)] pb-2 pt-2 text-xs font-bold uppercase tracking-wider text-muted-foreground">
      {children}
    </h2>
  );
}

export function HackathonForm({
  values,
  onChange,
  disabled,
  submitLabel,
  saving,
  onSubmit,
  onCancel,
}: {
  values: HackathonFormValues;
  onChange: (next: HackathonFormValues) => void;
  disabled?: boolean;
  submitLabel: string;
  saving: boolean;
  onSubmit: () => void;
  onCancel: () => void;
}) {
  function set<K extends keyof HackathonFormValues>(key: K, value: HackathonFormValues[K]) {
    onChange({ ...values, [key]: value });
  }

  const text = (key: keyof HackathonFormValues, label: string, extra?: { type?: string; placeholder?: string; required?: boolean }) => (
    <Field label={label}>
      <input
        type={extra?.type ?? "text"}
        required={extra?.required}
        disabled={disabled}
        placeholder={extra?.placeholder}
        value={values[key] as string}
        onChange={(event) => set(key, event.target.value)}
        className={inputClass}
      />
    </Field>
  );

  const area = (key: keyof HackathonFormValues, label: string, rows = 3, placeholder?: string) => (
    <Field label={label}>
      <textarea
        rows={rows}
        disabled={disabled}
        placeholder={placeholder}
        value={values[key] as string}
        onChange={(event) => set(key, event.target.value)}
        className={inputClass}
      />
    </Field>
  );

  return (
    <form
      className="space-y-6"
      onSubmit={(event) => {
        event.preventDefault();
        onSubmit();
      }}
    >
      <SectionTitle>Basics</SectionTitle>
      <div className="grid gap-4 md:grid-cols-2">
        {text("title", "Title", { required: true })}
        {text("slug", "Slug (optional)")}
        {text("category", "Category")}
        {text("host_name", "Host / organizer name")}
        {text("tagsText", "Tags (comma separated)", { placeholder: "hackathon, ai, students" })}
        {text("time_zone", "Time zone", { placeholder: "UTC" })}
      </div>
      {text("short_description", "Short description", { required: true })}
      {area("description", "Full description", 5)}

      <SectionTitle>Format</SectionTitle>
      <div className="grid gap-4 md:grid-cols-3">
        <Field label="Difficulty">
          <select disabled={disabled} value={values.difficulty} onChange={(e) => set("difficulty", e.target.value)} className={inputClass}>
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>
        </Field>
        <Field label="Format">
          <select disabled={disabled} value={values.format} onChange={(e) => set("format", e.target.value)} className={inputClass}>
            <option value="individual">Individual</option>
            <option value="team">Team</option>
            <option value="both">Individual or team</option>
          </select>
        </Field>
        <Field label="Delivery mode">
          <select disabled={disabled} value={values.delivery_mode} onChange={(e) => set("delivery_mode", e.target.value)} className={inputClass}>
            <option value="online">Online</option>
            <option value="offline">Offline</option>
            <option value="hybrid">Hybrid</option>
          </select>
        </Field>
      </div>
      <div className="grid gap-4 md:grid-cols-4">
        {text("location", "Location")}
        {text("minimum_team_size", "Minimum team size", { type: "number" })}
        {text("maximum_team_size", "Maximum team size", { type: "number" })}
        {text("participant_limit", "Maximum registrations (blank = unlimited)", { type: "number" })}
        {text("registration_fee", "Registration fee (0 = free)", { type: "number" })}
      </div>

      <SectionTitle>Dates</SectionTitle>
      <div className="grid gap-4 md:grid-cols-2">
        {text("registration_start", "Registration opens", { type: "datetime-local", required: true })}
        {text("registration_deadline", "Registration closes", { type: "datetime-local", required: true })}
        {text("competition_start", "Event starts", { type: "datetime-local", required: true })}
        {text("competition_end", "Event ends", { type: "datetime-local", required: true })}
        {text("submission_deadline", "Submission deadline", { type: "datetime-local", required: true })}
        {text("judging_end", "Judging ends", { type: "datetime-local" })}
        {text("results_announcement", "Results announcement", { type: "datetime-local" })}
      </div>

      <SectionTitle>Content & rules</SectionTitle>
      {area("problem_statement", "Problem statement", 4)}
      {area("eligibilityText", "Eligibility rules (one per line)", 3)}
      {area("rulesText", "Competition rules (one per line)", 4)}
      {area("participation_instructions", "Participation instructions", 4)}
      {area("submission_requirements", "Submission requirements", 3)}
      {area("evaluation_criteria", "Evaluation criteria", 3)}
      {area("prize_information", "Prizes", 3)}
      {area("contact_information", "Contact information", 2)}
      {area("resourcesText", "External resources (one per line: Title | URL)", 3, "Starter repo | https://github.com/...\nDiscord | https://discord.gg/...")}

      <div className="flex justify-end gap-3">
        <Button type="button" variant="outline" onClick={onCancel} disabled={disabled}>Cancel</Button>
        <Button type="submit" disabled={saving || disabled}>{saving ? "Saving..." : submitLabel}</Button>
      </div>
    </form>
  );
}
