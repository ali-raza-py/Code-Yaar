"use client";

import { useCallback, Suspense, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { adminApi } from "@/lib/admin-api";
import type { EmailTemplateAdmin } from "@/lib/admin-api";
import { useAuth } from "@/hooks/use-auth";
import RichTextEditor from "@/components/admin/rich-text-editor";
import EmailTemplatePicker from "@/components/admin/email-template-picker";
import { NetworkError } from "@/components/learning/workspace/error-states";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { FileText, Mail, Plus, Search, Send, ShieldCheck, X } from "lucide-react";

type RecipientMode = "single" | "multiple" | "custom";

interface StudentHit {
  id: number;
  name: string;
  email: string;
  student_id: string;
}

interface VerifiedRow {
  id: number | null;
  name: string;
  email: string;
  student_id: string;
  registered: boolean;
}

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const MODE_LABELS: Record<RecipientMode, string> = {
  single: "One registered student",
  multiple: "Multiple students",
  custom: "Custom email addresses",
};

const inputClass = "w-full rounded-md border bg-background px-3 py-2 text-sm";

function Field({ label, children, hint }: { label: string; children: React.ReactNode; hint?: string }) {
  return (
    <label className="block text-sm font-medium">
      <span>{label}</span>
      {hint && <span className="block text-xs font-normal text-muted-foreground">{hint}</span>}
      {children}
    </label>
  );
}

function EmailChips({
  emails,
  onRemove,
}: {
  emails: string[];
  onRemove: (email: string) => void;
}) {
  return (
    <div className="flex flex-wrap gap-1.5">
      {emails.map((email) => (
        <Badge key={email} variant="secondary" className="gap-1 font-normal">
          {email}
          <button type="button" aria-label={`Remove ${email}`} onClick={() => onRemove(email)}>
            <X className="h-3 w-3" />
          </button>
        </Badge>
      ))}
    </div>
  );
}

function ComposerPageInner() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { user, loading: authLoading } = useAuth();
  const isSuperAdmin = Boolean(user?.is_super_admin);

  // Recipients
  const [mode, setMode] = useState<RecipientMode>("single");
  const [searchTerm, setSearchTerm] = useState("");
  const [searchResults, setSearchResults] = useState<StudentHit[]>([]);
  const [searching, setSearching] = useState(false);
  const [selectedStudents, setSelectedStudents] = useState<StudentHit[]>([]);
  const [customEmails, setCustomEmails] = useState<string[]>([]);
  const [customInput, setCustomInput] = useState("");
  const [customError, setCustomError] = useState("");
  const [ccInput, setCcInput] = useState("");
  const [ccEmails, setCcEmails] = useState<string[]>([]);
  const [bccInput, setBccInput] = useState("");
  const [bccEmails, setBccEmails] = useState<string[]>([]);

  // Composition
  const [name, setName] = useState("");
  const [subject, setSubject] = useState("");
  const [heading, setHeading] = useState("");
  const [bodyHtml, setBodyHtml] = useState("");
  const [plainText, setPlainText] = useState("");
  const [ctaLabel, setCtaLabel] = useState("");
  const [ctaUrl, setCtaUrl] = useState("");
  const [essential, setEssential] = useState(true);

  // Email Templates integration: the chosen template seeds the fields above.
  // The saved template is never mutated by composing — only an explicit
  // "Save changes to template" writes back. The template footer is kept
  // separate and appended to the composed body at payload-build time, so
  // writing back preserves the template's body/footer split (no double-append).
  const [templatePickerOpen, setTemplatePickerOpen] = useState(false);
  const [sourceTemplate, setSourceTemplate] = useState<EmailTemplateAdmin | null>(null);
  const [templateFooter, setTemplateFooter] = useState("");

  // Flow state
  const [sender, setSender] = useState<{ sender_name: string; sender_email: string; reply_to: string } | null>(null);
  const [draftId, setDraftId] = useState<number | null>(null);
  const [draftLoaded, setDraftLoaded] = useState(false);
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [verified, setVerified] = useState<VerifiedRow[] | null>(null);
  const [invalidEmails, setInvalidEmails] = useState<string[]>([]);
  const [preview, setPreview] = useState<{ html: string; text: string; subject?: string } | null>(null);
  const [testAddress, setTestAddress] = useState("");
  const [testResult, setTestResult] = useState("");
  const [results, setResults] = useState<{ status: string; sent: number; failed: number; pending: number } | null>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (!user) return;
    adminApi.composerSenderIdentity().then(setSender).catch(() => setSender(null));
  }, [user]);

  // Open as a draft when arriving from "Duplicate" or an edit link.
  useEffect(() => {
    const draftParam = searchParams.get("draft");
    // Fresh composer: nothing to load, so the page renders immediately.
    if (!draftParam) {
      setDraftLoaded(true);
      return;
    }
    if (!user) return;
    const id = Number(draftParam);
    if (!Number.isInteger(id)) {
      setDraftLoaded(true);
      return;
    }
    let cancelled = false;
    adminApi
      .getCampaign(id)
      .then((data) => {
        if (cancelled || data.audience !== "specific") return;
        setDraftId(data.id);
        setName(data.name);
        setSubject(data.subject);
        setHeading(data.heading);
        setBodyHtml(data.body_html || "");
        setPlainText(data.plain_text_alternative || "");
        setCtaLabel(data.cta_label);
        setCtaUrl(data.cta_url);
        setEssential(data.essential);
        setCustomEmails(data.custom_emails || []);
        setCcEmails(data.cc_emails || []);
        setBccEmails(data.bcc_emails || []);
        if ((data.custom_emails || []).length && !(data.selected_users || []).length) setMode("custom");
        else if ((data.selected_users || []).length > 1) setMode("multiple");
        setDraftLoaded(true);
      })
      .catch(() => setDraftLoaded(true));
    return () => {
      cancelled = true;
    };
  }, [searchParams, user]);

  // Live student search against the real Django endpoint, debounced.
  const searchTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  function runSearch(term: string) {
    setSearchTerm(term);
    if (searchTimer.current) clearTimeout(searchTimer.current);
    if (term.trim().length < 2) {
      setSearchResults([]);
      return;
    }
    searchTimer.current = setTimeout(async () => {
      setSearching(true);
      try {
        const data = await adminApi.searchComposerStudents(term.trim());
        setSearchResults(data.results);
      } catch {
        setSearchResults([]);
      } finally {
        setSearching(false);
      }
    }, 300);
  }

  function addStudent(student: StudentHit) {
    const max = mode === "single" ? 1 : Infinity;
    setSelectedStudents((current) => {
      if (current.some((s) => s.id === student.id)) return current;
      const next = [...current, student];
      return next.slice(0, max === Infinity ? undefined : max);
    });
    setSearchResults([]);
    setSearchTerm("");
    setVerified(null);
  }

  function addCustomEmail(raw: string) {
    const email = raw.trim().toLowerCase();
    if (!email) return;
    if (!EMAIL_RE.test(email)) {
      setCustomError(`"${raw.trim()}" is not a valid email address.`);
      return;
    }
    setCustomError("");
    setCustomEmails((current) => (current.includes(email) ? current : [...current, email]));
    setCustomInput("");
    setVerified(null);
  }

  function addListEmail(field: "cc" | "bcc", raw: string) {
    const email = raw.trim().toLowerCase();
    if (!email) return;
    if (!EMAIL_RE.test(email)) {
      setError(`"${raw.trim()}" is not a valid ${field.toUpperCase()} address.`);
      return;
    }
    setError("");
    const setter = field === "cc" ? setCcEmails : setBccEmails;
    setter((current) => (current.includes(email) ? current : [...current, email]));
    (field === "cc" ? setCcInput : setBccInput)("");
  }

  const recipientCount =
    mode === "custom" ? customEmails.length : selectedStudents.length + (mode === "multiple" ? customEmails.length : 0);

  function buildPayload() {
    const emails = mode === "custom" ? customEmails : mode === "multiple" ? Array.from(new Set([...customEmails])) : [];
    // Append the chosen template's footer (kept separate from the editable
    // body) so it renders in the sent email without polluting the draft body.
    const footerHtml = templateFooter
      .split("\n")
      .map((line) => line.trim())
      .filter(Boolean)
      .map((line) => `<p>${line}</p>`)
      .join("");
    return {
      name: name.trim() || subject.trim() || "Official email",
      subject: subject.trim(),
      heading: heading.trim(),
      body: "",
      body_html: bodyHtml + footerHtml,
      plain_text_alternative: plainText,
      audience: "specific",
      template: "general" as const,
      selected_users: mode === "single" || mode === "multiple" ? selectedStudents.map((s) => s.id) : [],
      custom_emails: emails,
      cc_emails: ccEmails,
      bcc_emails: bccEmails,
      cta_label: ctaLabel.trim(),
      // Relative site paths become absolute URLs server-side, like campaigns.
      cta_url: ctaUrl.trim().startsWith("/") && typeof window !== "undefined"
        ? `${window.location.origin}${ctaUrl.trim()}`
        : ctaUrl.trim(),
      essential,
    };
  }

  async function saveDraft(): Promise<number | null> {
    setError("");
    setNotice("");
    if (recipientCount === 0) {
      setError("Choose at least one recipient first.");
      return null;
    }
    if (!subject.trim()) {
      setError("A subject line is required.");
      return null;
    }
    setBusy("saving");
    try {
      const payload = buildPayload();
      const data = draftId
        ? await adminApi.updateCampaign(draftId, payload)
        : await adminApi.createCampaign(payload);
      setDraftId(data.id);
      setNotice(`Draft saved (#${data.id}). Nothing has been sent yet.`);
      return data.id;
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "The draft could not be saved.");
      return null;
    } finally {
      setBusy("");
    }
  }

  async function verifyRecipients() {
    setError("");
    setInvalidEmails([]);
    setVerified(null);
    setBusy("verify");
    try {
      const payload = buildPayload();
      const data = await adminApi.validateComposerRecipients({
        user_ids: payload.selected_users,
        emails: payload.custom_emails,
      });
      setVerified(data.recipients);
      setInvalidEmails(data.invalid);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "The recipients could not be verified.");
    } finally {
      setBusy("");
    }
  }

  async function showPreview() {
    setError("");
    const id = await saveDraft();
    if (!id) return;
    setBusy("preview");
    try {
      const firstStudent = verified?.[0] ?? selectedStudents[0];
      const data = await adminApi.campaignPreview(id, firstStudent && "id" in firstStudent && firstStudent.id ? firstStudent.id : undefined);
      setPreview(data);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "The preview could not be rendered.");
    } finally {
      setBusy("");
    }
  }

  async function sendTest() {
    setError("");
    setTestResult("");
    const id = draftId ?? (await saveDraft());
    if (!id) return;
    setBusy("test");
    try {
      const data = await adminApi.campaignTest(id, testAddress.trim() || undefined);
      setTestResult(
        data.ok
          ? data.status === "sent"
            ? `Test delivered to ${testAddress.trim() || "your address"} — the SMTP server accepted it.`
            : "Test rendered only: the configured transport is not a live SMTP backend, so nothing left the server."
          : `Test failed: ${data.error}`,
      );
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "The test email could not be sent.");
    } finally {
      setBusy("");
    }
  }

  const pollResults = useCallback(async (id: number) => {
    try {
      const [campaign, rows] = await Promise.all([
        adminApi.getCampaign(id),
        adminApi.campaignRecipients(id, { page_size: 100 }),
      ]);
      const counts = { sent: 0, failed: 0, pending: 0 };
      for (const row of rows.results) {
        if (row.status === "sent" || row.status === "render_only") counts.sent += 1;
        else if (row.status === "failed") counts.failed += 1;
        else if (row.status === "pending") counts.pending += 1;
      }
      setResults({ status: campaign.status, ...counts });
      if (campaign.status !== "sending" && campaign.status !== "queued" && counts.pending === 0) {
        if (pollRef.current) clearInterval(pollRef.current);
        pollRef.current = null;
      }
    } catch {
      // Keep polling; a transient failure should not lose the results panel.
    }
  }, []);

  async function sendNow() {
    setError("");
    const id = await saveDraft();
    if (!id) return;
    if (recipientCount === 0) {
      setError("Choose at least one recipient first.");
      return;
    }
    const confirmed = window.confirm(
      `Send this email to ${recipientCount} recipient${recipientCount === 1 ? "" : "s"} now?\n\n` +
        "Each recipient receives a personal, individual copy — nobody sees anyone else's address. " +
        "This cannot be undone from here.",
    );
    if (!confirmed) return;
    setBusy("send");
    try {
      await adminApi.campaignSend(id);
      setNotice("Send accepted. Delivery results appear below as each copy is attempted.");
      setResults({ status: "queued", sent: 0, failed: 0, pending: recipientCount });
      if (!pollRef.current) {
        pollRef.current = setInterval(() => void pollResults(id), 2500);
      }
      void pollResults(id);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "The email could not be sent.");
    } finally {
      setBusy("");
    }
  }

  // Apply a chosen template to the composer. This only fills fields; it does
  // not save, send, or touch the stored template. The draft is detached so the
  // composed edits go to a new campaign rather than overwriting an existing one.
  function chooseTemplate(template: EmailTemplateAdmin) {
    setError("");
    setNotice("");
    setDraftId(null);
    setSourceTemplate(template);
    setTemplateFooter(template.footer_content || "");
    setName(template.name);
    setSubject(template.subject);
    setHeading(template.heading);
    setBodyHtml(template.body_html);
    setPlainText(template.plain_text || "");
    setCtaLabel(template.cta_label);
    setCtaUrl(template.cta_url);
    setTemplatePickerOpen(false);
    setNotice(`Template “${template.name}” applied. Edit freely — the saved template is unchanged.`);
  }

  // Explicit write-back: updates the saved template with the current fields.
  // Never triggered automatically; the admin chooses to overwrite.
  async function saveChangesToTemplate() {
    if (!sourceTemplate) return;
    setError("");
    setBusy("save-template");
    try {
      const saved = await adminApi.updateTemplate(sourceTemplate.id, {
        subject: subject.trim(),
        heading: heading.trim(),
        // Store the editable body without the appended footer, preserving the
        // template's body/footer split so re-applying never double-appends.
        body_html: bodyHtml,
        cta_label: ctaLabel.trim(),
        cta_url: ctaUrl.trim(),
        footer_content: templateFooter,
      });
      setSourceTemplate(saved);
      setNotice(`Template “${saved.name}” updated with your changes.`);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "The template could not be updated.");
    } finally {
      setBusy("");
    }
  }

  useEffect(() => () => {
    if (pollRef.current) clearInterval(pollRef.current);
  }, []);

  if (authLoading || !draftLoaded) {
    return (
      <div className="animate-pulse space-y-4">
        <Skeleton className="h-8 w-72" />
        <Skeleton className="h-96" />
      </div>
    );
  }

  if (!isSuperAdmin) {
    return (
      <Card className="mx-auto max-w-lg">
        <CardHeader>
          <CardTitle>Super Admin required</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Only authorized Super Administrators can send official emails from the Code Yaar account.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="flex items-center gap-2 text-2xl font-bold">
            <Mail className="h-6 w-6" /> Send Official Email
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Write a completely custom message and deliver it to specific people through the existing
            Code Yaar email system.
          </p>
        </div>
        <Link href="/admin/email-campaigns">
          <Button variant="outline" size="sm">Sent emails history</Button>
        </Link>
      </div>

      {sender && (
        <Card>
          <CardContent className="flex flex-wrap items-center gap-x-6 gap-y-1 py-4 text-sm">
            <span className="flex items-center gap-1.5 font-medium">
              <ShieldCheck className="h-4 w-4 text-primary" /> Sending as {sender.sender_name}
            </span>
            <span className="text-muted-foreground">{sender.sender_email}</span>
            <span className="text-muted-foreground">Reply-to: {sender.reply_to}</span>
            <Badge variant="outline">Sender identity is fixed by the server</Badge>
          </CardContent>
        </Card>
      )}

      {error && (
        <p role="alert" className="rounded-md border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700 dark:border-red-800 dark:bg-red-950 dark:text-red-200">
          {error}
        </p>
      )}
      {notice && (
        <p className="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-2 text-sm text-emerald-800 dark:border-emerald-800 dark:bg-emerald-950 dark:text-emerald-200">
          {notice}
        </p>
      )}

      {/* ── Recipients ─────────────────────────────────────────────── */}
      <Card>
        <CardHeader>
          <CardTitle>1 — Recipients</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-wrap gap-2">
            {(Object.keys(MODE_LABELS) as RecipientMode[]).map((option) => (
              <Button
                key={option}
                size="sm"
                variant={mode === option ? "default" : "outline"}
                onClick={() => setMode(option)}
              >
                {MODE_LABELS[option]}
              </Button>
            ))}
          </div>

          {mode !== "custom" && (
            <div className="space-y-3">
              <Field label="Search registered students" hint="Matches name, registered email address or student ID.">
                <div className="relative">
                  <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                  <input
                    value={searchTerm}
                    onChange={(event) => runSearch(event.target.value)}
                    placeholder="Name, email or student ID…"
                    className={`${inputClass} pl-8`}
                  />
                </div>
              </Field>
              {searching && <p className="text-xs text-muted-foreground">Searching…</p>}
              {searchResults.length > 0 && (
                <div className="divide-y rounded-md border">
                  {searchResults.map((student) => (
                    <button
                      key={student.id}
                      type="button"
                      onClick={() => addStudent(student)}
                      className="flex w-full items-center justify-between gap-2 px-3 py-2 text-left text-sm hover:bg-muted/50"
                    >
                      <span>
                        <span className="font-medium">{student.name}</span>{" "}
                        <span className="text-muted-foreground">{student.email}</span>
                      </span>
                      <Badge variant="outline">{student.student_id}</Badge>
                    </button>
                  ))}
                </div>
              )}
              {selectedStudents.length > 0 && (
                <div className="space-y-2">
                  <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                    Selected — {selectedStudents.length} student{selectedStudents.length === 1 ? "" : "s"}
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {selectedStudents.map((student) => (
                      <Badge key={student.id} variant="secondary" className="gap-1 py-1 font-normal">
                        {student.name} · {student.email}
                        <button
                          type="button"
                          aria-label={`Remove ${student.email}`}
                          onClick={() => setSelectedStudents((c) => c.filter((s) => s.id !== student.id))}
                        >
                          <X className="h-3 w-3" />
                        </button>
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {mode !== "single" && (
            <div className="space-y-2">
              <Field label="Custom email addresses (people without a Code Yaar account)" hint="Press Enter or Add to append; duplicates are ignored.">
                <div className="flex gap-2">
                  <input
                    value={mode === "custom" ? customInput : ""}
                    onChange={(event) => setCustomInput(event.target.value)}
                    onKeyDown={(event) => {
                      if (event.key === "Enter") {
                        event.preventDefault();
                        addCustomEmail(customInput);
                      }
                    }}
                    disabled={mode !== "custom"}
                    placeholder="name@example.org"
                    className={inputClass}
                  />
                  <Button type="button" variant="outline" size="sm" disabled={mode !== "custom"} onClick={() => addCustomEmail(customInput)}>
                    <Plus className="mr-1 h-4 w-4" /> Add
                  </Button>
                </div>
              </Field>
              {customError && <p className="text-sm text-red-600 dark:text-red-400">{customError}</p>}
              {customEmails.length > 0 && (
                <EmailChips
                  emails={customEmails}
                  onRemove={(email) => setCustomEmails((c) => c.filter((e) => e !== email))}
                />
              )}
            </div>
          )}

          <div className="grid gap-4 md:grid-cols-2">
            <Field label="CC (optional)">
              <div className="flex gap-2">
                <input
                  value={ccInput}
                  onChange={(event) => setCcInput(event.target.value)}
                  onKeyDown={(event) => {
                    if (event.key === "Enter") {
                      event.preventDefault();
                      addListEmail("cc", ccInput);
                    }
                  }}
                  placeholder="boss@codeyaar.dev"
                  className={inputClass}
                />
                <Button type="button" variant="outline" size="sm" onClick={() => addListEmail("cc", ccInput)}>Add</Button>
              </div>
              {ccEmails.length > 0 && (
                <div className="mt-2">
                  <EmailChips emails={ccEmails} onRemove={(e) => setCcEmails((c) => c.filter((x) => x !== e))} />
                </div>
              )}
            </Field>
            <Field label="BCC (optional)">
              <div className="flex gap-2">
                <input
                  value={bccInput}
                  onChange={(event) => setBccInput(event.target.value)}
                  onKeyDown={(event) => {
                    if (event.key === "Enter") {
                      event.preventDefault();
                      addListEmail("bcc", bccInput);
                    }
                  }}
                  placeholder="archive@codeyaar.dev"
                  className={inputClass}
                />
                <Button type="button" variant="outline" size="sm" onClick={() => addListEmail("bcc", bccInput)}>Add</Button>
              </div>
              {bccEmails.length > 0 && (
                <div className="mt-2">
                  <EmailChips emails={bccEmails} onRemove={(e) => setBccEmails((c) => c.filter((x) => x !== e))} />
                </div>
              )}
            </Field>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <Badge variant="secondary">{recipientCount} recipient{recipientCount === 1 ? "" : "s"}</Badge>
            <Button variant="outline" size="sm" disabled={busy !== "" || recipientCount === 0} onClick={verifyRecipients}>
              {busy === "verify" ? "Verifying…" : "Verify recipients"}
            </Button>
          </div>

          {verified && (
            <div className="space-y-1.5">
              {invalidEmails.length > 0 && (
                <p className="text-sm text-red-600 dark:text-red-400">
                  Invalid and not included: {invalidEmails.join(", ")}
                </p>
              )}
              <p className="text-sm font-medium">Verified recipient list — {verified.length} total:</p>
              <div className="divide-y rounded-md border">
                {verified.map((row) => (
                  <div key={row.email} className="flex flex-wrap items-center justify-between gap-2 px-3 py-1.5 text-sm">
                    <span>
                      <span className="font-medium">{row.name}</span>{" "}
                      <span className="text-muted-foreground">{row.email}</span>
                    </span>
                    <Badge variant={row.registered ? "outline" : "secondary"}>
                      {row.registered ? `Student ID: ${row.student_id}` : "External address"}
                    </Badge>
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* ── Compose ────────────────────────────────────────────────── */}
      <Card>
        <CardHeader className="flex flex-wrap items-center justify-between gap-2">
          <CardTitle>2 — Write the email</CardTitle>
          <div className="flex flex-wrap items-center gap-2">
            <Button variant="outline" size="sm" onClick={() => setTemplatePickerOpen(true)}>
              <FileText className="mr-1 h-4 w-4" /> Choose Email Template
            </Button>
            {sourceTemplate && (
              <Button
                variant="outline"
                size="sm"
                disabled={busy !== ""}
                onClick={saveChangesToTemplate}
              >
                {busy === "save-template" ? "Saving…" : `Save changes to “${sourceTemplate.name}”`}
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {sourceTemplate && (
            <p className="rounded-md border bg-muted/40 px-3 py-2 text-xs text-muted-foreground">
              Composing from template “{sourceTemplate.name}”. Editing here does not change the
              saved template unless you use “Save changes”.
            </p>
          )}
          <Field label="Subject" hint="Variables like {{student_name}} personalize each recipient's subject separately.">
            <input value={subject} onChange={(event) => setSubject(event.target.value)} className={inputClass} />
          </Field>
          <Field label="Email heading (optional)" hint="Shown as the headline inside the branded layout.">
            <input value={heading} onChange={(event) => setHeading(event.target.value)} className={inputClass} />
          </Field>
          <Field label="Message body">
            <RichTextEditor value={bodyHtml} onChange={setBodyHtml} />
          </Field>
          <div className="grid gap-4 md:grid-cols-2">
            <Field label="CTA button label (optional)">
              <input value={ctaLabel} onChange={(event) => setCtaLabel(event.target.value)} placeholder="Open Code Yaar" className={inputClass} />
            </Field>
            <Field label="CTA button link (optional)">
              <input value={ctaUrl} onChange={(event) => setCtaUrl(event.target.value)} placeholder="/dashboard or https://…" className={inputClass} />
            </Field>
          </div>
          <Field label="Plain-text alternative (optional)" hint="Automatically derived from the formatted body when left empty.">
            <textarea rows={4} value={plainText} onChange={(event) => setPlainText(event.target.value)} className={inputClass} />
          </Field>
          <label className="flex items-start gap-2 text-sm">
            <input type="checkbox" checked={essential} onChange={(event) => setEssential(event.target.checked)} className="mt-0.5" />
            <span>
              Essential notice (ignores recipients&apos; “announcement emails” preference — use sparingly)
            </span>
          </label>
          <Field label="Internal reference (optional)" hint="Only visible to administrators in the sent-emails history.">
            <input value={name} onChange={(event) => setName(event.target.value)} placeholder="Nov fee reminder" className={inputClass} />
          </Field>
        </CardContent>
      </Card>

      {/* ── Review & send ──────────────────────────────────────────── */}
      <Card>
        <CardHeader>
          <CardTitle>3 — Preview, test and send</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-muted-foreground">
            Saving only stores a draft. Nobody receives anything until “Send now” is confirmed below.
          </p>
          <div className="flex flex-wrap gap-2">
            <Button variant="outline" size="sm" disabled={busy !== ""} onClick={() => void saveDraft()}>
              {busy === "saving" ? "Saving…" : draftId ? "Update draft" : "Save draft"}
            </Button>
            <Button variant="outline" size="sm" disabled={busy !== "" || recipientCount === 0} onClick={showPreview}>
              {busy === "preview" ? "Rendering…" : "Preview email"}
            </Button>
            <div className="flex items-center gap-2">
              <input
                value={testAddress}
                onChange={(event) => setTestAddress(event.target.value)}
                placeholder="Test address (defaults to yours)"
                className={`${inputClass} max-w-[220px]`}
              />
              <Button variant="outline" size="sm" disabled={busy !== ""} onClick={sendTest}>
                {busy === "test" ? "Sending test…" : "Send test"}
              </Button>
            </div>
            <Button size="sm" disabled={busy !== "" || recipientCount === 0} onClick={sendNow}>
              <Send className="mr-1 h-4 w-4" />
              {busy === "send" ? "Sending…" : `Send to ${recipientCount} recipient${recipientCount === 1 ? "" : "s"}`}
            </Button>
          </div>
          {testResult && <p className="text-sm text-muted-foreground">{testResult}</p>}
          {draftId && (
            <Link href={`/admin/email-campaigns/${draftId}`} className="inline-block text-sm text-primary hover:underline">
              Open this email&apos;s draft detail (campaign #{draftId})
            </Link>
          )}

          {results && (
            <div className="rounded-lg border p-4">
              <p className="mb-2 text-sm font-semibold">
                Sending {results.status === "sending" || results.status === "queued" ? "in progress…" : `finished (${results.status})`}
              </p>
              <div className="grid gap-2 text-sm sm:grid-cols-3">
                <span>Submitted: <strong>{results.sent}</strong></span>
                <span>Failed: <strong>{results.failed}</strong></span>
                <span>Pending: <strong>{results.pending}</strong></span>
              </div>
              <p className="mt-2 text-xs text-muted-foreground">
                “Submitted” means the configured mail server accepted the copy — delivery to the final
                inbox is only confirmed when the provider reports it, so nothing here is ever marked delivered.
              </p>
            </div>
          )}

          {preview && (
            <div className="space-y-2 border-t pt-4">
              <p className="text-sm font-medium">Preview{preview.subject ? ` — subject: “${preview.subject}”` : ""}</p>
              <iframe
                title="Email preview"
                srcDoc={preview.html}
                className="h-[480px] w-full rounded-md border bg-white"
                sandbox=""
              />
              <details className="text-sm">
                <summary className="cursor-pointer text-muted-foreground">Plain-text version</summary>
                <pre className="mt-2 max-h-72 overflow-auto rounded-md border bg-muted p-3 text-xs whitespace-pre-wrap">
                  {preview.text}
                </pre>
              </details>
            </div>
          )}
        </CardContent>
      </Card>

      <EmailTemplatePicker
        open={templatePickerOpen}
        onClose={() => setTemplatePickerOpen(false)}
        onChoose={chooseTemplate}
      />

      {authLoading ? null : !user ? <NetworkError onRetry={() => router.refresh()} /> : null}
    </div>
  );
}

// useSearchParams needs a Suspense boundary for the static prerender pass.
export default function SendOfficialEmailPage() {
  return (
    <Suspense
      fallback={
        <div className="animate-pulse space-y-4">
          <Skeleton className="h-8 w-72" />
          <Skeleton className="h-96" />
        </div>
      }
    >
      <ComposerPageInner />
    </Suspense>
  );
}
