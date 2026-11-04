"use client";

import { Button } from "@/components/ui/button";
import type { EmailCampaignAdmin } from "@/lib/admin-api";

export interface CampaignFormValues {
  name: string;
  subject: string;
  heading: string;
  body: string;
  template: EmailCampaignAdmin["template"];
  cta_label: string;
  cta_url: string;
  audience: string;
  competition: string;
  essential: boolean;
}

export const EMPTY_CAMPAIGN_FORM: CampaignFormValues = {
  name: "",
  subject: "",
  heading: "",
  body: "",
  template: "general",
  cta_label: "",
  cta_url: "",
  audience: "all",
  competition: "",
  essential: false,
};

export function campaignFromAdmin(data: EmailCampaignAdmin): CampaignFormValues {
  return {
    name: data.name,
    subject: data.subject,
    heading: data.heading,
    body: data.body,
    template: data.template,
    cta_label: data.cta_label,
    cta_url: data.cta_url,
    audience: data.audience,
    competition: data.competition ? String(data.competition) : "",
    essential: data.essential,
  };
}

export function campaignToPayload(values: CampaignFormValues): Partial<EmailCampaignAdmin> {
  return {
    name: values.name,
    subject: values.subject,
    heading: values.heading,
    body: values.body,
    template: values.template,
    cta_label: values.cta_label,
    cta_url: absoluteCtaUrl(values.cta_url),
    audience: values.audience,
    competition: values.audience.startsWith("comp_") ? Number(values.competition) : null,
    essential: values.essential,
  };
}

/**
 * The backend stores the button link as a real URL, so a site path typed by an
 * admin ("/updates") is resolved against the app origin before it is sent.
 */
function absoluteCtaUrl(value: string): string {
  const trimmed = value.trim();
  if (!trimmed.startsWith("/")) return trimmed;
  return typeof window === "undefined" ? trimmed : `${window.location.origin}${trimmed}`;
}

const TEMPLATE_LABELS: Record<CampaignFormValues["template"], string> = {
  general: "General announcement",
  notice: "Important platform notice",
  platform_update: "Platform update",
  new_course: "New course announcement",
};

const AUDIENCE_GROUPS: Array<{ label: string; options: Array<{ value: string; label: string }> }> = [
  {
    label: "Everyone by role",
    options: [
      { value: "all", label: "All registered users" },
      { value: "students", label: "Students" },
      { value: "instructors", label: "Instructors" },
      { value: "admins", label: "Administrators" },
    ],
  },
  {
    label: "Hackathon audience (pick a hackathon below)",
    options: [
      { value: "comp_participants", label: "All registered participants" },
      { value: "comp_approved", label: "Approved applicants" },
      { value: "comp_pending", label: "Pending applicants" },
      { value: "comp_waitlisted", label: "Waitlisted applicants" },
    ],
  },
];

const inputClass = "mt-1 w-full rounded-md border bg-background px-3 py-2 text-sm";

function Field({ label, children, className = "" }: { label: string; children: React.ReactNode; className?: string }) {
  return (
    <label className={`block text-sm font-medium ${className}`}>
      {label}
      {children}
    </label>
  );
}

export function CampaignForm({
  values,
  onChange,
  disabled,
  competitions,
  submitLabel,
  saving,
  onSubmit,
  onCancel,
  extraActions,
}: {
  values: CampaignFormValues;
  onChange: (next: CampaignFormValues) => void;
  disabled?: boolean;
  competitions: Array<{ id: number; title: string }>;
  submitLabel: string;
  saving: boolean;
  onSubmit: () => void;
  onCancel: () => void;
  extraActions?: React.ReactNode;
}) {
  function set<K extends keyof CampaignFormValues>(key: K, value: CampaignFormValues[K]) {
    onChange({ ...values, [key]: value });
  }

  const isHackathonAudience = values.audience.startsWith("comp_");

  return (
    <form
      className="space-y-4"
      onSubmit={(event) => {
        event.preventDefault();
        onSubmit();
      }}
    >
      <div className="grid gap-4 md:grid-cols-2">
        <Field label="Internal name (never shown to recipients)">
          <input required disabled={disabled} value={values.name} onChange={(e) => set("name", e.target.value)} placeholder="Nov platform update mail" className={inputClass} />
        </Field>
        <Field label="Email template">
          <select disabled={disabled} value={values.template} onChange={(e) => set("template", e.target.value as CampaignFormValues["template"])} className={inputClass}>
            {Object.entries(TEMPLATE_LABELS).map(([value, label]) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </select>
        </Field>
      </div>

      <Field label="Subject line">
        <input required disabled={disabled} value={values.subject} onChange={(e) => set("subject", e.target.value)} className={inputClass} />
      </Field>

      <Field label="Heading shown at the top of the email (optional — falls back to the campaign name)">
        <input disabled={disabled} value={values.heading} onChange={(e) => set("heading", e.target.value)} className={inputClass} />
      </Field>

      <Field label="Message — one paragraph per line">
        <textarea
          required
          rows={7}
          disabled={disabled}
          value={values.body}
          onChange={(e) => set("body", e.target.value)}
          placeholder={"We just shipped something new for you.\n\nHere is what changed and why it matters."}
          className={inputClass}
        />
      </Field>

      <div className="grid gap-4 md:grid-cols-2">
        <Field label="Button label (optional)">
          <input disabled={disabled} value={values.cta_label} onChange={(e) => set("cta_label", e.target.value)} placeholder="View updates" className={inputClass} />
        </Field>
        <Field label="Button link (optional, site path or full URL)">
          <input disabled={disabled} value={values.cta_url} onChange={(e) => set("cta_url", e.target.value)} placeholder="/updates" className={inputClass} />
        </Field>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Field label="Audience">
          <select disabled={disabled} value={values.audience} onChange={(e) => set("audience", e.target.value)} className={inputClass}>
            {AUDIENCE_GROUPS.map((group) => (
              <optgroup key={group.label} label={group.label}>
                {group.options.map((option) => (
                  <option key={option.value} value={option.value}>{option.label}</option>
                ))}
              </optgroup>
            ))}
          </select>
        </Field>
        {isHackathonAudience && (
          <Field label="Hackathon">
            <select required disabled={disabled} value={values.competition} onChange={(e) => set("competition", e.target.value)} className={inputClass}>
              <option value="">Choose a hackathon…</option>
              {competitions.map((c) => (
                <option key={c.id} value={c.id}>{c.title}</option>
              ))}
            </select>
          </Field>
        )}
      </div>

      <label className="flex items-start gap-2 text-sm">
        <input
          type="checkbox"
          disabled={disabled || isHackathonAudience}
          checked={values.essential || isHackathonAudience}
          onChange={(e) => set("essential", e.target.checked)}
          className="mt-0.5"
        />
        <span>
          Essential mail (ignores “announcement emails” unsubscribes)
          {isHackathonAudience && <span className="block text-xs text-muted-foreground">Forced on: application decisions are transactional mail, not marketing.</span>}
        </span>
      </label>

      <div className="flex flex-wrap justify-end gap-3">
        <Button type="button" variant="outline" onClick={onCancel} disabled={disabled}>Cancel</Button>
        {extraActions}
        <button
          type="submit"
          disabled={saving || disabled || (isHackathonAudience && !values.competition)}
          className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
        >
          {saving ? "Saving..." : submitLabel}
        </button>
      </div>
    </form>
  );
}
