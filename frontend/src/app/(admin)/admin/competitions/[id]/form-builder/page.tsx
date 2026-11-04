"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { adminApi } from "@/lib/admin-api";
import type { RegistrationFormFieldAdmin, RegistrationFieldType } from "@/lib/admin-api";
import { NetworkError } from "@/components/learning/workspace/error-states";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { ArrowDown, ArrowUp, Plus, RotateCcw, Trash2 } from "lucide-react";

const FIELD_TYPE_LABELS: Record<RegistrationFieldType, string> = {
  short_text: "Short text",
  long_text: "Long text",
  email: "Email",
  phone: "Phone",
  number: "Number",
  dropdown: "Dropdown",
  multiple_choice: "Multiple choice (pick one)",
  checkboxes: "Checkboxes (pick many)",
  url: "URL",
  date: "Date",
};

const CHOICE_TYPES = new Set<RegistrationFieldType>(["dropdown", "multiple_choice", "checkboxes"]);

const inputClass = "mt-1 w-full rounded-md border bg-background px-3 py-2 text-sm";

function slugKey(label: string): string {
  return label
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "")
    .slice(0, 48);
}

function FieldEditor({
  field,
  index,
  total,
  disabled,
  onSave,
  onMove,
  onToggleActive,
  onDelete,
}: {
  field: RegistrationFormFieldAdmin;
  index: number;
  total: number;
  disabled: boolean;
  onSave: (id: number, patch: Partial<RegistrationFormFieldAdmin>) => Promise<void>;
  onMove: (index: number, direction: -1 | 1) => void;
  onToggleActive: (field: RegistrationFormFieldAdmin) => void;
  onDelete: (field: RegistrationFormFieldAdmin) => void;
}) {
  const [editing, setEditing] = useState(false);
  const [label, setLabel] = useState(field.label);
  const [description, setDescription] = useState(field.description);
  const [placeholder, setPlaceholder] = useState(field.placeholder);
  const [required, setRequired] = useState(field.required);
  const [optionsText, setOptionsText] = useState(field.options.join("\n"));
  const [minLength, setMinLength] = useState(field.validation.min_length != null ? String(field.validation.min_length) : "");
  const [maxLength, setMaxLength] = useState(field.validation.max_length != null ? String(field.validation.max_length) : "");
  const [min, setMin] = useState(field.validation.min != null ? String(field.validation.min) : "");
  const [max, setMax] = useState(field.validation.max != null ? String(field.validation.max) : "");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const isChoice = CHOICE_TYPES.has(field.field_type);
  const isText = field.field_type === "short_text" || field.field_type === "long_text";
  const isNumber = field.field_type === "number";

  async function save() {
    setSaving(true);
    setError("");
    try {
      const validation: Record<string, number> = {};
      if (minLength) validation.min_length = Number(minLength);
      if (maxLength) validation.max_length = Number(maxLength);
      if (min) validation.min = Number(min);
      if (max) validation.max = Number(max);
      await onSave(field.id, {
        label,
        description,
        placeholder,
        required,
        validation,
        ...(isChoice ? { options: optionsText.split("\n").map((line) => line.trim()).filter(Boolean) } : {}),
      });
      setEditing(false);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "The field could not be saved.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="rounded-lg border p-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold text-muted-foreground">#{index + 1}</span>
          <p className="font-medium">{field.label}</p>
          <Badge variant="outline">{FIELD_TYPE_LABELS[field.field_type]}</Badge>
          {field.required && <Badge variant="outline">Required</Badge>}
          {field.is_default && <Badge variant="secondary">Default</Badge>}
          {!field.is_active && <Badge variant="destructive">Hidden</Badge>}
        </div>
        <div className="flex items-center gap-1">
          <Button size="sm" variant="ghost" disabled={disabled || index === 0} onClick={() => onMove(index, -1)} aria-label="Move up">
            <ArrowUp className="h-4 w-4" />
          </Button>
          <Button size="sm" variant="ghost" disabled={disabled || index === total - 1} onClick={() => onMove(index, 1)} aria-label="Move down">
            <ArrowDown className="h-4 w-4" />
          </Button>
          <Button size="sm" variant="ghost" disabled={disabled} onClick={() => setEditing((v) => !v)}>
            {editing ? "Close" : "Edit"}
          </Button>
          <Button size="sm" variant="outline" disabled={disabled} onClick={() => onToggleActive(field)}>
            {field.is_active ? "Hide" : "Show"}
          </Button>
          <Button size="sm" variant="outline" disabled={disabled} onClick={() => onDelete(field)}>
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </div>
      {field.description && !editing && (
        <p className="mt-1 text-sm text-muted-foreground">{field.description}</p>
      )}
      {editing && (
        <div className="mt-4 space-y-4 border-t pt-4">
          {error && (
            <p role="alert" className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700 dark:border-red-800 dark:bg-red-950 dark:text-red-200">
              {error}
            </p>
          )}
          <div className="grid gap-4 md:grid-cols-2">
            <label className="block text-sm font-medium">
              Label
              <input value={label} onChange={(e) => setLabel(e.target.value)} className={inputClass} />
            </label>
            <label className="block text-sm font-medium">
              Field key (read-only)
              <input value={field.field_key} readOnly className={`${inputClass} opacity-60`} />
            </label>
          </div>
          <label className="block text-sm font-medium">
            Help text shown under the question
            <textarea rows={2} value={description} onChange={(e) => setDescription(e.target.value)} className={inputClass} />
          </label>
          {!isChoice && (
            <label className="block text-sm font-medium">
              Placeholder
              <input value={placeholder} onChange={(e) => setPlaceholder(e.target.value)} className={inputClass} />
            </label>
          )}
          {isChoice && (
            <label className="block text-sm font-medium">
              Options (one per line)
              <textarea rows={4} value={optionsText} onChange={(e) => setOptionsText(e.target.value)} className={inputClass} />
            </label>
          )}
          {isText && (
            <div className="grid gap-4 md:grid-cols-2">
              <label className="block text-sm font-medium">
                Minimum length
                <input type="number" min={0} value={minLength} onChange={(e) => setMinLength(e.target.value)} className={inputClass} />
              </label>
              <label className="block text-sm font-medium">
                Maximum length
                <input type="number" min={0} value={maxLength} onChange={(e) => setMaxLength(e.target.value)} className={inputClass} />
              </label>
            </div>
          )}
          {isNumber && (
            <div className="grid gap-4 md:grid-cols-2">
              <label className="block text-sm font-medium">
                Minimum value
                <input type="number" value={min} onChange={(e) => setMin(e.target.value)} className={inputClass} />
              </label>
              <label className="block text-sm font-medium">
                Maximum value
                <input type="number" value={max} onChange={(e) => setMax(e.target.value)} className={inputClass} />
              </label>
            </div>
          )}
          <label className="flex items-center gap-2 text-sm font-medium">
            <input type="checkbox" checked={required} onChange={(e) => setRequired(e.target.checked)} />
            Required question
          </label>
          <div className="flex justify-end gap-2">
            <Button size="sm" variant="outline" disabled={saving} onClick={() => setEditing(false)}>Cancel</Button>
            <Button size="sm" disabled={saving || !label.trim() || (isChoice && !optionsText.split("\n").some((line) => line.trim()))} onClick={save}>
              {saving ? "Saving..." : "Save field"}
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}

export default function FormBuilderPage() {
  const params = useParams<{ id: string }>();
  const competitionId = Number(params.id);

  const [fields, setFields] = useState<RegistrationFormFieldAdmin[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(false);
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");

  // New-field draft
  const [newLabel, setNewLabel] = useState("");
  const [newType, setNewType] = useState<RegistrationFieldType>("short_text");
  const [newDescription, setNewDescription] = useState("");
  const [newRequired, setNewRequired] = useState(false);
  const [newOptions, setNewOptions] = useState("");

  const load = useCallback(async () => {
    try {
      const data = await adminApi.listFormFields({ competition: competitionId, page_size: 100 });
      setFields(data.results);
      setLoadError(false);
    } catch {
      setLoadError(true);
    } finally {
      setLoading(false);
    }
  }, [competitionId]);

  useEffect(() => {
    (async () => { await load(); })();
  }, [load]);

  async function runAction(action: () => Promise<unknown>, successMessage: string) {
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await action();
      setNotice(successMessage);
      await load();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "That action did not complete.");
    } finally {
      setBusy(false);
    }
  }

  function move(index: number, direction: -1 | 1) {
    const next = [...fields];
    const target = index + direction;
    if (target < 0 || target >= next.length) return;
    [next[index], next[target]] = [next[target], next[index]];
    setFields(next);
    void runAction(
      () => adminApi.reorderFormFields(next.map((field, i) => ({ id: field.id, order: i }))),
      "Field order saved.",
    );
  }

  function saveField(id: number, patch: Partial<RegistrationFormFieldAdmin>) {
    return runAction(() => adminApi.updateFormField(id, patch), "Field saved.");
  }

  function toggleActive(field: RegistrationFormFieldAdmin) {
    return runAction(
      () => adminApi.updateFormField(field.id, { is_active: !field.is_active }),
      field.is_active ? `Question "${field.label}" is now hidden from the public form.` : `Question "${field.label}" is visible again.`,
    );
  }

  function removeField(field: RegistrationFormFieldAdmin) {
    const warning = field.is_default
      ? `Remove the standard question "${field.label}"? Registrants will no longer see it. You can restore all standard questions with Reset defaults.`
      : `Remove the custom question "${field.label}"? Existing answers stay in received applications.`;
    if (!confirm(warning)) return;
    void runAction(() => adminApi.deleteFormField(field.id), "Question removed.");
  }

  function resetDefaults() {
    if (!confirm("Re-add any missing standard questions? Existing questions and edits are kept; nothing is deleted.")) return;
    void runAction(async () => {
      const result = await adminApi.resetFormDefaults(competitionId);
      return result;
    }, "Standard questions restored.");
  }

  async function addField() {
    const key = slugKey(newLabel);
    if (!key) {
      setError("Give the new question a label first.");
      return;
    }
    const options = newOptions.split("\n").map((line) => line.trim()).filter(Boolean);
    if (CHOICE_TYPES.has(newType) && options.length === 0) {
      setError("Choice fields need at least one option (one per line).");
      return;
    }
    await runAction(() => adminApi.createFormField({
      competition: competitionId,
      label: newLabel.trim(),
      field_key: key,
      field_type: newType,
      description: newDescription.trim(),
      placeholder: "",
      required: newRequired,
      options,
      validation: {},
      order: fields.length,
      is_active: true,
    }), "Question added.");
    setNewLabel("");
    setNewDescription("");
    setNewOptions("");
    setNewRequired(false);
    setNewType("short_text");
  }

  if (loading) {
    return (
      <div className="animate-pulse space-y-4">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-24" />
        <Skeleton className="h-24" />
      </div>
    );
  }

  if (loadError) return <NetworkError onRetry={load} />;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold">Registration Form Builder</h1>
          <p className="mt-1 max-w-2xl text-sm text-muted-foreground">
            Customize the questions applicants answer when they register for this
            hackathon. Changes apply to the public form immediately. The page you
            publish lives at <code className="rounded bg-muted px-1 py-0.5">/hackathons/&lt;slug&gt;/register</code>.
          </p>
        </div>
        <div className="flex gap-2">
          <Link href={`/admin/competitions/${competitionId}`}>
            <Button variant="outline" size="sm">Back to hackathon</Button>
          </Link>
          <Button variant="outline" size="sm" disabled={busy} onClick={resetDefaults}>
            <RotateCcw className="mr-1 h-4 w-4" /> Reset defaults
          </Button>
        </div>
      </div>

      {notice && (
        <p className="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-2 text-sm text-emerald-800 dark:border-emerald-800 dark:bg-emerald-950 dark:text-emerald-200">
          {notice}
        </p>
      )}
      {error && (
        <p role="alert" className="rounded-md border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700 dark:border-red-800 dark:bg-red-950 dark:text-red-200">
          {error}
        </p>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Questions ({fields.filter((f) => f.is_active).length} shown · {fields.length} total)</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {fields.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No questions yet. Use Reset defaults to seed the standard
              registration questions, or add a custom question below.
            </p>
          ) : (
            fields.map((field, index) => (
              <FieldEditor
                key={field.id}
                field={field}
                index={index}
                total={fields.length}
                disabled={busy}
                onSave={saveField}
                onMove={move}
                onToggleActive={toggleActive}
                onDelete={removeField}
              />
            ))
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Plus className="h-4 w-4" /> Add a custom question
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            <label className="block text-sm font-medium">
              Question label
              <input value={newLabel} onChange={(e) => setNewLabel(e.target.value)} placeholder="e.g. Which technology will you build with?" className={inputClass} />
            </label>
            <label className="block text-sm font-medium">
              Field type
              <select value={newType} onChange={(e) => setNewType(e.target.value as RegistrationFieldType)} className={inputClass}>
                {Object.entries(FIELD_TYPE_LABELS).map(([value, labelText]) => (
                  <option key={value} value={value}>{labelText}</option>
                ))}
              </select>
            </label>
          </div>
          <label className="mt-4 block text-sm font-medium">
            Help text (optional)
            <textarea rows={2} value={newDescription} onChange={(e) => setNewDescription(e.target.value)} className={inputClass} />
          </label>
          {CHOICE_TYPES.has(newType) && (
            <label className="mt-4 block text-sm font-medium">
              Options (one per line)
              <textarea rows={4} value={newOptions} onChange={(e) => setNewOptions(e.target.value)} placeholder={"Web\nMobile\nAI/ML"} className={inputClass} />
            </label>
          )}
          <label className="mt-4 flex items-center gap-2 text-sm font-medium">
            <input type="checkbox" checked={newRequired} onChange={(e) => setNewRequired(e.target.checked)} />
            Required question
          </label>
          <div className="mt-4">
            <Button
              size="sm"
              disabled={busy || !newLabel.trim() || (CHOICE_TYPES.has(newType) && !newOptions.split("\n").some((line) => line.trim()))}
              onClick={addField}
            >
              {busy ? "Adding..." : "Add question"}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
