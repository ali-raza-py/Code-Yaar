"use client";

import { useCallback, useEffect, useState } from "react";
import { adminApi } from "@/lib/admin-api";
import type { EmailTemplateAdmin } from "@/lib/admin-api";
import { NetworkError } from "@/components/learning/workspace/error-states";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Star, Search, X } from "lucide-react";

/**
 * A searchable, filterable modal of saved email templates. Picking one hands
 * the template back to the caller (the composer) to populate its fields — it
 * never sends anything and never edits the saved template. Search and the
 * category filter are shared with the library page so the two surfaces behave
 * identically.
 */
export default function EmailTemplatePicker({
  open,
  onClose,
  onChoose,
}: {
  open: boolean;
  onClose: () => void;
  onChoose: (template: EmailTemplateAdmin) => void;
}) {
  const [templates, setTemplates] = useState<EmailTemplateAdmin[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const load = useCallback(async () => {
    if (!open) return;
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
      setError(false);
    } catch {
      setError(true);
    } finally {
      setLoading(false);
    }
  }, [open, search, category]);

  useEffect(() => {
    (async () => { await load(); })();
  }, [load]);

  useEffect(() => {
    if (!open) return;
    function onKey(event: KeyboardEvent) {
      if (event.key === "Escape") onClose();
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-black/50 p-4 backdrop-blur-sm">
      <div className="my-8 flex max-h-[88vh] w-full max-w-2xl flex-col rounded-xl border bg-card shadow-xl">
        <div className="flex items-center justify-between border-b px-6 py-4">
          <div>
            <h2 className="text-lg font-semibold">Choose Email Template</h2>
            <p className="text-xs text-muted-foreground">
              Selecting fills the email below. The saved template is never changed.
            </p>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose} aria-label="Close">
            <X className="h-4 w-4" />
          </Button>
        </div>

        <div className="grid gap-2 border-b px-6 py-3 sm:grid-cols-[1fr_auto]">
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search templates by name…"
              className="w-full rounded-md border bg-background py-2 pl-8 pr-3 text-sm"
            />
          </div>
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="rounded-md border bg-background px-3 py-2 text-sm"
          >
            <option value="">All categories</option>
            {categories.map((cat) => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
        </div>

        <div className="flex-1 overflow-y-auto px-6 py-4">
          {loading ? (
            <div className="space-y-3">
              {[0, 1, 2].map((n) => (
                <div key={n} className="h-20 animate-pulse rounded-lg bg-muted/50" />
              ))}
            </div>
          ) : error ? (
            <NetworkError onRetry={load} />
          ) : templates.length === 0 ? (
            <p className="py-10 text-center text-sm text-muted-foreground">
              No templates match your search.
            </p>
          ) : (
            <div className="space-y-2">
              {templates.map((template) => (
                <button
                  key={template.id}
                  type="button"
                  onClick={() => onChoose(template)}
                  className="block w-full rounded-lg border p-4 text-left transition-colors hover:border-primary/40 hover:bg-muted/40"
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="flex items-center gap-1.5 font-medium">
                      {template.is_favorite && <Star className="h-4 w-4 fill-amber-400 text-amber-400" />}
                      {template.name}
                    </span>
                    <Badge variant="secondary" className="shrink-0">{template.category}</Badge>
                  </div>
                  <p className="mt-1 line-clamp-1 text-sm text-muted-foreground">{template.subject}</p>
                  {template.description && (
                    <p className="mt-1 line-clamp-1 text-xs text-muted-foreground/80">{template.description}</p>
                  )}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
