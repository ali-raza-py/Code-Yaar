"use client";

import { useCallback, useEffect, useState } from "react";
import { adminApi } from "@/lib/admin-api";
import type { EmailTemplateAdmin } from "@/lib/admin-api";
import { useAuth } from "@/hooks/use-auth";
import EmailTemplateEditor from "@/components/admin/email-template-editor";
import { NetworkError } from "@/components/learning/workspace/error-states";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Copy,
  Eye,
  FileText,
  Pencil,
  Plus,
  Search,
  Star,
  Trash2,
  X,
} from "lucide-react";

const inputClass = "rounded-md border bg-background px-3 py-2 text-sm";

function relativeTime(iso: string): string {
  const then = new Date(iso).getTime();
  const days = Math.floor((Date.now() - then) / 86_400_000);
  if (days <= 0) return "today";
  if (days === 1) return "yesterday";
  if (days < 30) return `${days} days ago`;
  return new Date(iso).toLocaleDateString();
}

export default function EmailTemplatesPage() {
  const { user, loading: authLoading } = useAuth();
  const isSuperAdmin = Boolean(user?.is_super_admin);

  const [templates, setTemplates] = useState<EmailTemplateAdmin[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(false);
  const [forbidden, setForbidden] = useState(false);

  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");

  const [editing, setEditing] = useState<EmailTemplateAdmin | null>(null);
  const [creating, setCreating] = useState(false);
  const [previewing, setPreviewing] = useState<EmailTemplateAdmin | null>(null);
  const [busyId, setBusyId] = useState<number | null>(null);
  const [actionError, setActionError] = useState("");

  const load = useCallback(async () => {
    if (!user) return;
    try {
      const [list, cats] = await Promise.all([
        adminApi.listTemplates({
          page_size: 200,
          ordering: "-is_favorite,-updated_at",
          search: search || undefined,
          category: category || undefined,
        }),
        adminApi.templateCategories(),
      ]);
      setTemplates(list.results);
      setCategories(cats.categories);
      setLoadError(false);
      setForbidden(false);
    } catch (caught) {
      if (caught instanceof Error && /403|permission|Super Admin/i.test(caught.message)) {
        setForbidden(true);
      } else {
        setLoadError(true);
      }
    } finally {
      setLoading(false);
    }
  }, [user, search, category]);

  useEffect(() => {
    (async () => { await load(); })();
  }, [load]);

  async function handleDuplicate(template: EmailTemplateAdmin) {
    setBusyId(template.id);
    setActionError("");
    try {
      await adminApi.duplicateTemplate(template.id);
      await load();
    } catch (caught) {
      setActionError(caught instanceof Error ? caught.message : "The template could not be duplicated.");
    } finally {
      setBusyId(null);
    }
  }

  async function handleDelete(template: EmailTemplateAdmin) {
    if (!window.confirm(`Delete the template “${template.name}”? This cannot be undone.`)) return;
    setBusyId(template.id);
    setActionError("");
    try {
      await adminApi.deleteTemplate(template.id);
      await load();
    } catch (caught) {
      setActionError(caught instanceof Error ? caught.message : "The template could not be deleted.");
    } finally {
      setBusyId(null);
    }
  }

  async function toggleFavorite(template: EmailTemplateAdmin) {
    setBusyId(template.id);
    try {
      await adminApi.updateTemplate(template.id, { is_favorite: !template.is_favorite });
      await load();
    } catch (caught) {
      setActionError(caught instanceof Error ? caught.message : "The template could not be updated.");
    } finally {
      setBusyId(null);
    }
  }

  if (authLoading || loading) {
    return (
      <div className="animate-pulse space-y-4">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-24" />
        <Skeleton className="h-24" />
      </div>
    );
  }

  if (forbidden) {
    return (
      <Card className="mx-auto max-w-xl">
        <CardContent className="py-8 text-center">
          <p className="font-medium">Super Admin access required</p>
          <p className="mt-1 text-sm text-muted-foreground">
            Only Super Admins can manage the email templates library.
          </p>
        </CardContent>
      </Card>
    );
  }

  if (loadError) return <NetworkError onRetry={load} />;

  const favorites = templates.filter((t) => t.is_favorite);
  const recentlyUpdated = [...templates]
    .sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime())
    .slice(0, 4);

  function TemplateCard({ template }: { template: EmailTemplateAdmin }) {
    const busy = busyId === template.id;
    return (
      <Card className="flex flex-col overflow-hidden transition-shadow hover:shadow-md">
        <CardContent className="flex-1 space-y-2 py-4">
          <div className="flex items-start justify-between gap-2">
            <div className="flex items-center gap-1.5">
              <button
                type="button"
                aria-label={template.is_favorite ? "Remove from favorites" : "Mark as favorite"}
                onClick={() => toggleFavorite(template)}
                disabled={busy}
                className="text-muted-foreground transition-colors hover:text-amber-400"
              >
                <Star className={template.is_favorite ? "h-4 w-4 fill-amber-400 text-amber-400" : "h-4 w-4"} />
              </button>
              <h3 className="font-semibold leading-tight">{template.name}</h3>
            </div>
            <Badge variant="secondary" className="shrink-0 text-[11px]">{template.category}</Badge>
          </div>

          <p className="line-clamp-1 text-sm text-muted-foreground">{template.subject}</p>
          {template.description ? (
            <p className="line-clamp-2 text-xs text-muted-foreground/80">{template.description}</p>
          ) : null}

          <p className="text-xs text-muted-foreground">Updated {relativeTime(template.updated_at)}</p>
        </CardContent>

        <div className="flex items-center gap-1 border-t px-3 py-2">
          <Button variant="ghost" size="sm" onClick={() => setPreviewing(template)}>
            <Eye className="mr-1 h-4 w-4" /> Preview
          </Button>
          <Button variant="ghost" size="sm" onClick={() => setEditing(template)}>
            <Pencil className="mr-1 h-4 w-4" /> Edit
          </Button>
          <Button variant="ghost" size="sm" onClick={() => handleDuplicate(template)} disabled={busy}>
            <Copy className="mr-1 h-4 w-4" /> Duplicate
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="ml-auto text-destructive hover:bg-destructive/10 hover:text-destructive"
            onClick={() => handleDelete(template)}
            disabled={busy}
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="flex items-center gap-2 text-2xl font-bold">
            <FileText className="h-6 w-6" /> Email Templates
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            A reusable library of professional starting points. Choose one when composing an
            email — nothing is sent and the saved template is never changed automatically.
          </p>
        </div>
        {isSuperAdmin && (
          <Button size="sm" onClick={() => setCreating(true)}>
            <Plus className="mr-1 h-4 w-4" /> Create template
          </Button>
        )}
      </div>

      {actionError && (
        <p role="alert" className="rounded-md border border-destructive/40 bg-destructive/10 px-4 py-2 text-sm text-destructive">
          {actionError}
        </p>
      )}

      {templates.length === 0 ? (
        <Card className="mx-auto max-w-lg">
          <CardContent className="py-10 text-center">
            <FileText className="mx-auto h-10 w-10 text-muted-foreground/60" />
            <p className="mt-3 font-medium">No templates yet</p>
            <p className="mt-1 text-sm text-muted-foreground">
              Create your first template, or start from the built-in professional collection.
            </p>
            {isSuperAdmin && (
              <Button className="mt-4" size="sm" onClick={() => setCreating(true)}>
                <Plus className="mr-1 h-4 w-4" /> Create template
              </Button>
            )}
          </CardContent>
        </Card>
      ) : (
        <>
          <Card>
            <CardContent className="grid gap-3 py-4 md:grid-cols-[1fr_auto]">
              <div className="relative">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                <input
                  value={search}
                  onChange={(event) => setSearch(event.target.value)}
                  placeholder="Search templates by name, subject or description…"
                  className={`${inputClass} w-full pl-8`}
                />
              </div>
              <select
                value={category}
                onChange={(event) => setCategory(event.target.value)}
                className={inputClass}
              >
                <option value="">All categories</option>
                {categories.map((cat) => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
            </CardContent>
          </Card>

          {search === "" && category === "" && favorites.length > 0 && (
            <section className="space-y-3">
              <h2 className="flex items-center gap-1.5 text-sm font-semibold uppercase tracking-wide text-muted-foreground">
                <Star className="h-4 w-4 fill-amber-400 text-amber-400" /> Favorites
              </h2>
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {favorites.map((template) => (
                  <TemplateCard key={`fav-${template.id}`} template={template} />
                ))}
              </div>
            </section>
          )}

          {search === "" && category === "" && recentlyUpdated.length > 0 && (
            <section className="space-y-3">
              <h2 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">
                Recently updated
              </h2>
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {recentlyUpdated.map((template) => (
                  <TemplateCard key={`recent-${template.id}`} template={template} />
                ))}
              </div>
            </section>
          )}

          <section className="space-y-3">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">
              All templates ({templates.length})
            </h2>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {templates.map((template) => (
                <TemplateCard key={template.id} template={template} />
              ))}
            </div>
          </section>
        </>
      )}

      {(creating || editing) && (
        <EmailTemplateEditor
          template={editing}
          onClose={() => { setCreating(false); setEditing(null); }}
          onSaved={() => { setCreating(false); setEditing(null); void load(); }}
        />
      )}

      {previewing && (
        <TemplatePreviewModal template={previewing} onClose={() => setPreviewing(null)} />
      )}
    </div>
  );
}

function TemplatePreviewModal({
  template,
  onClose,
}: {
  template: EmailTemplateAdmin;
  onClose: () => void;
}) {
  const [html, setHtml] = useState("");
  const [subject, setSubject] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    adminApi
      .templatePreview(template.id)
      .then((data) => {
        if (cancelled) return;
        setHtml(data.html);
        setSubject(data.subject || template.subject);
      })
      .catch((caught) => !cancelled && setError(caught instanceof Error ? caught.message : "Preview failed."))
      .finally(() => !cancelled && setLoading(false));
    return () => { cancelled = true; };
  }, [template.id, template.subject]);

  useEffect(() => {
    function onKey(event: KeyboardEvent) {
      if (event.key === "Escape") onClose();
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-black/50 p-4 backdrop-blur-sm">
      <div className="my-8 w-full max-w-3xl rounded-xl border bg-card shadow-xl">
        <div className="flex items-center justify-between border-b px-6 py-4">
          <div>
            <h2 className="text-lg font-semibold">{template.name}</h2>
            <p className="text-xs text-muted-foreground">
              Preview as the signed-in admin. Variables are filled with your own details.
            </p>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose} aria-label="Close">
            <X className="h-4 w-4" />
          </Button>
        </div>
        <div className="space-y-3 px-6 py-4">
          {subject && <p className="text-sm font-medium">Subject: {subject}</p>}
          {loading ? (
            <Skeleton className="h-[420px]" />
          ) : error ? (
            <p className="py-10 text-center text-sm text-destructive">{error}</p>
          ) : (
            <iframe
              title={`Preview of ${template.name}`}
              srcDoc={html}
              className="h-[480px] w-full rounded-md border bg-white"
              sandbox=""
            />
          )}
        </div>
      </div>
    </div>
  );
}
