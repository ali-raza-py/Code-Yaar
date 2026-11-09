"use client";

import { useEffect, useMemo, useState } from "react";
import { adminApi } from "@/lib/admin-api";
import type { EmailTemplateAdmin } from "@/lib/admin-api";
import RichTextEditor from "@/components/admin/rich-text-editor";
import { Button } from "@/components/ui/button";

// Personalization tokens supported by the backend composer. Kept in sync with
// ``email_composer.PERSONALIZATION_KEYS`` server-side; a template stores these
// literally and they are rendered per recipient only when the template is used.
const VARIABLE_TOKENS = [
  "{{student_name}}",
  "{{student_email}}",
  "{{student_id}}",
  "{{current_date}}",
  "{{organization_name}}",
];

const PRESET_CATEGORIES = [
  "Welcome & Onboarding",
  "Account Verification",
  "Password Reset",
  "Student Communications",
  "Course Enrollment",
  "Course Completion",
  "Certificates & Achievements",
  "Internship Opportunities",
  "Hackathons & Competitions",
  "Ambassador Programs",
  "Team Communications",
  "Partnership & Collaboration",
  "Important Announcements",
  "Custom Templates",
];

const inputClass = "w-full rounded-md border bg-background px-3 py-2 text-sm";

interface Draft {
  name: string;
  category: string;
  description: string;
  subject: string;
  heading: string;
  preview_text: string;
  body_html: string;
  cta_label: string;
  cta_url: string;
  footer_content: string;
  is_favorite: boolean;
}

const EMPTY_DRAFT: Draft = {
  name: "",
  category: "Custom Templates",
  description: "",
  subject: "",
  heading: "",
  preview_text: "",
  body_html: "",
  cta_label: "",
  cta_url: "",
  footer_content: "",
  is_favorite: false,
};

function draftFromTemplate(template: EmailTemplateAdmin): Draft {
  return {
    name: template.name,
    category: template.category,
    description: template.description,
    subject: template.subject,
    heading: template.heading,
    preview_text: template.preview_text,
    body_html: template.body_html,
    cta_label: template.cta_label,
    cta_url: template.cta_url,
    footer_content: template.footer_content,
    is_favorite: template.is_favorite,
  };
}

function Field({ label, children, hint }: { label: string; children: React.ReactNode; hint?: string }) {
  return (
    <label className="block text-sm font-medium">
      <span>{label}</span>
      {hint && <span className="block text-xs font-normal text-muted-foreground">{hint}</span>}
      {children}
    </label>
  );
}

/** A small token picker for plain-text fields (subject, heading, footer). */
function VariableRow({ onInsert }: { onInsert: (token: string) => void }) {
  return (
    <div className="flex flex-wrap items-center gap-1.5">
      <span className="text-xs text-muted-foreground">Insert variable:</span>
      {VARIABLE_TOKENS.map((token) => (
        <button
          key={token}
          type="button"
          onClick={() => onInsert(token)}
          className="rounded-full border bg-muted/40 px-2 py-0.5 font-mono text-[11px] text-muted-foreground transition-colors hover:border-primary/40 hover:text-foreground"
        >
          {token.replace(/[{}]/g, "")}
        </button>
      ))}
    </div>
  );
}

/**
 * Create / edit dialog for a single email template. Content-only by design:
 * it never carries recipients or send state, and saving here never mails
 * anyone. The body reuses the composer's {@link RichTextEditor} so there is
 * exactly one rich-text editor in the product, and its variable insertion
 * behaves identically.
 */
export default function EmailTemplateEditor({
  template,
  onClose,
  onSaved,
}: {
  template: EmailTemplateAdmin | null;
  onClose: () => void;
  onSaved: (saved: EmailTemplateAdmin) => void;
}) {
  const [draft, setDraft] = useState<Draft>(template ? draftFromTemplate(template) : EMPTY_DRAFT);
  const [categories, setCategories] = useState<string[]>(PRESET_CATEGORIES);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    adminApi.templateCategories().then((data) => setCategories(data.categories)).catch(() => undefined);
  }, []);

  // Escape closes the dialog unless a save is mid-flight.
  useEffect(() => {
    function onKey(event: KeyboardEvent) {
      if (event.key === "Escape" && !saving) onClose();
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose, saving]);

  const canSave = draft.name.trim() !== "" && draft.subject.trim() !== "" && draft.body_html.trim() !== "";

  const customCategory = useMemo(
    () => !categories.includes(draft.category) && draft.category.trim() !== "",
    [categories, draft.category],
  );

  async function save() {
    setError("");
    if (!canSave) {
      setError("Name, subject and body are required.");
      return;
    }
    setSaving(true);
    try {
      const payload: Partial<EmailTemplateAdmin> = { ...draft };
      const saved = template
        ? await adminApi.updateTemplate(template.id, payload)
        : await adminApi.createTemplate(payload);
      onSaved(saved);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "The template could not be saved.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-black/50 p-4 backdrop-blur-sm">
      <div className="my-8 w-full max-w-3xl rounded-xl border bg-card shadow-xl">
        <div className="flex items-center justify-between border-b px-6 py-4">
          <div>
            <h2 className="text-lg font-semibold">{template ? "Edit template" : "Create template"}</h2>
            <p className="text-xs text-muted-foreground">
              Saved for reuse. Nothing is sent until you choose it on the Send Email page.
            </p>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose} disabled={saving}>Close</Button>
        </div>

        <div className="space-y-4 px-6 py-5">
          {error && (
            <p role="alert" className="rounded-md border border-destructive/40 bg-destructive/10 px-4 py-2 text-sm text-destructive">
              {error}
            </p>
          )}

          <div className="grid gap-4 md:grid-cols-2">
            <Field label="Template name">
              <input
                value={draft.name}
                onChange={(e) => setDraft({ ...draft, name: e.target.value })}
                placeholder="Welcome to Code Yaar"
                className={inputClass}
              />
            </Field>
            <Field label="Category" hint={customCategory ? "New category — it appears once this template is saved." : undefined}>
              <input
                list="email-template-categories"
                value={draft.category}
                onChange={(e) => setDraft({ ...draft, category: e.target.value })}
                placeholder="Choose or type a category"
                className={inputClass}
              />
              <datalist id="email-template-categories">
                {categories.map((category) => (
                  <option key={category} value={category} />
                ))}
              </datalist>
            </Field>
          </div>

          <Field label="Internal description" hint="Only administrators see this.">
            <textarea
              rows={2}
              value={draft.description}
              onChange={(e) => setDraft({ ...draft, description: e.target.value })}
              placeholder="When should the team reach for this template?"
              className={inputClass}
            />
          </Field>

          <div className="space-y-1.5">
            <Field label="Email subject">
              <input
                value={draft.subject}
                onChange={(e) => setDraft({ ...draft, subject: e.target.value })}
                placeholder="Welcome aboard, {{student_name}}"
                className={inputClass}
              />
            </Field>
            <VariableRow onInsert={(token) => setDraft({ ...draft, subject: draft.subject + token })} />
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-1.5">
              <Field label="Email heading">
                <input
                  value={draft.heading}
                  onChange={(e) => setDraft({ ...draft, heading: e.target.value })}
                  className={inputClass}
                />
              </Field>
              <VariableRow onInsert={(token) => setDraft({ ...draft, heading: draft.heading + token })} />
            </div>
            <Field label="Preview text" hint="Short preheader shown in inbox previews.">
              <input
                value={draft.preview_text}
                onChange={(e) => setDraft({ ...draft, preview_text: e.target.value })}
                className={inputClass}
              />
            </Field>
          </div>

          <Field label="Email body" hint="Use the toolbar to insert personalization variables — they render per recipient.">
            <RichTextEditor
              key={template ? `edit-${template.id}` : "create"}
              value={draft.body_html}
              onChange={(html) => setDraft({ ...draft, body_html: html })}
            />
          </Field>

          <div className="grid gap-4 md:grid-cols-2">
            <Field label="CTA button label">
              <input
                value={draft.cta_label}
                onChange={(e) => setDraft({ ...draft, cta_label: e.target.value })}
                placeholder="Open Code Yaar"
                className={inputClass}
              />
            </Field>
            <Field label="CTA button link" hint="A site path (/dashboard) or a full URL.">
              <input
                value={draft.cta_url}
                onChange={(e) => setDraft({ ...draft, cta_url: e.target.value })}
                placeholder="/dashboard"
                className={inputClass}
              />
            </Field>
          </div>

          <div className="space-y-1.5">
            <Field label="Footer content" hint="A closing line appended to the body when the template is used.">
              <textarea
                rows={2}
                value={draft.footer_content}
                onChange={(e) => setDraft({ ...draft, footer_content: e.target.value })}
                className={inputClass}
              />
            </Field>
            <VariableRow onInsert={(token) => setDraft({ ...draft, footer_content: draft.footer_content + token })} />
          </div>

          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={draft.is_favorite}
              onChange={(e) => setDraft({ ...draft, is_favorite: e.target.checked })}
              className="mt-0.5"
            />
            <span>Mark as favorite (pins it to the top of the library)</span>
          </label>
        </div>

        <div className="flex justify-end gap-3 border-t px-6 py-4">
          <Button variant="outline" onClick={onClose} disabled={saving}>Cancel</Button>
          <Button onClick={save} disabled={saving || !canSave}>
            {saving ? "Saving…" : template ? "Save changes" : "Create template"}
          </Button>
        </div>
      </div>
    </div>
  );
}
