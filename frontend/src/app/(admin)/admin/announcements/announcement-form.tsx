"use client";

import { Button } from "@/components/ui/button";
import type { AnnouncementAdmin } from "@/lib/admin-api";

export const ANNOUNCEMENT_CATEGORIES: Array<[AnnouncementAdmin["category"], string]> = [
  ["general", "General"],
  ["platform_updates", "Platform Updates"],
  ["hackathons", "Hackathons"],
  ["courses", "Courses"],
  ["competitions", "Competitions"],
  ["maintenance", "Maintenance"],
  ["important", "Important Notices"],
];

export const ANNOUNCEMENT_PRIORITIES: Array<[AnnouncementAdmin["priority"], string]> = [
  ["normal", "Normal"],
  ["important", "Important"],
  ["urgent", "Urgent"],
];

export const ANNOUNCEMENT_AUDIENCES: Array<[string, string]> = [
  ["all", "Everyone"],
  ["students", "Students"],
  ["instructors", "Instructors"],
  ["admins", "Administrators"],
];

export interface AnnouncementFormValues {
  title: string;
  short_description: string;
  body: string;
  category: string;
  priority: string;
  target_audience: string;
  scheduled_at: string;
  expires_at: string;
}

export const EMPTY_ANNOUNCEMENT_FORM: AnnouncementFormValues = {
  title: "",
  short_description: "",
  body: "",
  category: "general",
  priority: "normal",
  target_audience: "all",
  scheduled_at: "",
  expires_at: "",
};

const inputClass =
  "mt-1 w-full rounded-md border bg-background px-3 py-2 text-sm";

/**
 * Shared create/edit form for announcements. Publishing state is deliberately
 * not editable here: an announcement is saved as a draft and only goes live
 * through the Publish action in the list, which the server gates on role.
 */
export function AnnouncementForm({
  values,
  onChange,
  fieldErrors,
  disabled,
  submitLabel,
  onSubmit,
  onCancel,
  saving,
}: {
  values: AnnouncementFormValues;
  onChange: (next: AnnouncementFormValues) => void;
  fieldErrors?: Record<string, string>;
  disabled?: boolean;
  submitLabel: string;
  onSubmit: () => void;
  onCancel: () => void;
  saving: boolean;
}) {
  function set<K extends keyof AnnouncementFormValues>(key: K, value: AnnouncementFormValues[K]) {
    onChange({ ...values, [key]: value });
  }

  const error = (key: string) =>
    fieldErrors?.[key] ? <p className="mt-1 text-xs text-red-600">{fieldErrors[key]}</p> : null;

  return (
    <form
      className="space-y-5"
      onSubmit={(event) => {
        event.preventDefault();
        onSubmit();
      }}
    >
      <label className="block text-sm font-medium">
        Title
        <input
          required
          maxLength={200}
          disabled={disabled}
          value={values.title}
          onChange={(event) => set("title", event.target.value)}
          className={inputClass}
        />
        {error("title")}
      </label>

      <div className="grid gap-4 sm:grid-cols-3">
        <label className="block text-sm font-medium">
          Category
          <select
            disabled={disabled}
            value={values.category}
            onChange={(event) => set("category", event.target.value)}
            className={inputClass}
          >
            {ANNOUNCEMENT_CATEGORIES.map(([value, label]) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </select>
        </label>
        <label className="block text-sm font-medium">
          Priority
          <select
            disabled={disabled}
            value={values.priority}
            onChange={(event) => set("priority", event.target.value)}
            className={inputClass}
          >
            {ANNOUNCEMENT_PRIORITIES.map(([value, label]) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </select>
        </label>
        <label className="block text-sm font-medium">
          Audience
          <select
            disabled={disabled}
            value={values.target_audience}
            onChange={(event) => set("target_audience", event.target.value)}
            className={inputClass}
          >
            {ANNOUNCEMENT_AUDIENCES.map(([value, label]) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </select>
        </label>
      </div>

      <label className="block text-sm font-medium">
        Short description (shown in cards and email previews)
        <input
          maxLength={400}
          disabled={disabled}
          value={values.short_description}
          onChange={(event) => set("short_description", event.target.value)}
          className={inputClass}
        />
        {error("short_description")}
      </label>

      <label className="block text-sm font-medium">
        Message
        <textarea
          required
          rows={8}
          disabled={disabled}
          value={values.body}
          onChange={(event) => set("body", event.target.value)}
          className={inputClass}
        />
        {error("body")}
      </label>

      <div className="grid gap-4 sm:grid-cols-2">
        <label className="block text-sm font-medium">
          Publish date (optional — stays hidden until this time)
          <input
            type="datetime-local"
            disabled={disabled}
            value={values.scheduled_at}
            onChange={(event) => set("scheduled_at", event.target.value)}
            className={inputClass}
          />
          {error("scheduled_at")}
        </label>
        <label className="block text-sm font-medium">
          Expires (optional — leaves the feed after this time)
          <input
            type="datetime-local"
            disabled={disabled}
            value={values.expires_at}
            onChange={(event) => set("expires_at", event.target.value)}
            className={inputClass}
          />
          {error("expires_at")}
        </label>
      </div>

      <div className="flex justify-end gap-3">
        <Button type="button" variant="outline" onClick={onCancel} disabled={disabled}>
          Cancel
        </Button>
        <Button type="submit" disabled={saving || disabled}>
          {saving ? "Saving..." : submitLabel}
        </Button>
      </div>
    </form>
  );
}

export function toLocalInputValue(iso: string | null): string {
  if (!iso) return "";
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return "";
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}
