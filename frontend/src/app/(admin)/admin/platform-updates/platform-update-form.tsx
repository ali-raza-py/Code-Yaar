"use client";

import { Button } from "@/components/ui/button";

export const UPDATE_CATEGORIES: Array<[string, string]> = [
  ["feature", "New Feature"],
  ["course", "Courses & Tracks"],
  ["improvement", "Improvement"],
  ["bug_fix", "Bug Fix"],
  ["performance", "Performance"],
  ["certificate", "Certificates"],
  ["other", "Other"],
];

export const UPDATE_AUDIENCES: Array<[string, string]> = [
  ["all", "Everyone"],
  ["students", "Students"],
  ["instructors", "Instructors"],
];

export interface PlatformUpdateFormValues {
  title: string;
  version: string;
  category: string;
  summary: string;
  content: string;
  changeListText: string;
  target_audience: string;
}

export const EMPTY_PLATFORM_UPDATE_FORM: PlatformUpdateFormValues = {
  title: "",
  version: "",
  category: "feature",
  summary: "",
  content: "",
  changeListText: "",
  target_audience: "all",
};

const inputClass = "mt-1 w-full rounded-md border bg-background px-3 py-2 text-sm";

/** One change bullet per line in the textarea; stored as a JSON list. */
export function parseChangeList(text: string): string[] {
  return text
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);
}

export function PlatformUpdateForm({
  values,
  onChange,
  disabled,
  submitLabel,
  onSubmit,
  onCancel,
  saving,
}: {
  values: PlatformUpdateFormValues;
  onChange: (next: PlatformUpdateFormValues) => void;
  disabled?: boolean;
  submitLabel: string;
  onSubmit: () => void;
  onCancel: () => void;
  saving: boolean;
}) {
  function set<K extends keyof PlatformUpdateFormValues>(key: K, value: PlatformUpdateFormValues[K]) {
    onChange({ ...values, [key]: value });
  }

  return (
    <form
      className="space-y-5"
      onSubmit={(event) => {
        event.preventDefault();
        onSubmit();
      }}
    >
      <div className="grid gap-4 sm:grid-cols-[1fr_160px]">
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
        </label>
        <label className="block text-sm font-medium">
          Version (optional)
          <input
            maxLength={40}
            disabled={disabled}
            placeholder="e.g. 1.4.0"
            value={values.version}
            onChange={(event) => set("version", event.target.value)}
            className={inputClass}
          />
        </label>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <label className="block text-sm font-medium">
          Category
          <select
            disabled={disabled}
            value={values.category}
            onChange={(event) => set("category", event.target.value)}
            className={inputClass}
          >
            {UPDATE_CATEGORIES.map(([value, label]) => (
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
            {UPDATE_AUDIENCES.map(([value, label]) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </select>
        </label>
      </div>

      <label className="block text-sm font-medium">
        Summary (one or two sentences for the list view)
        <input
          maxLength={500}
          disabled={disabled}
          value={values.summary}
          onChange={(event) => set("summary", event.target.value)}
          className={inputClass}
        />
      </label>

      <label className="block text-sm font-medium">
        Details
        <textarea
          required
          rows={6}
          disabled={disabled}
          value={values.content}
          onChange={(event) => set("content", event.target.value)}
          className={inputClass}
        />
      </label>

      <label className="block text-sm font-medium">
        Change list (one item per line)
        <textarea
          rows={6}
          disabled={disabled}
          placeholder={"Added ...\nFixed ...\nImproved ..."}
          value={values.changeListText}
          onChange={(event) => set("changeListText", event.target.value)}
          className={inputClass}
        />
      </label>

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
