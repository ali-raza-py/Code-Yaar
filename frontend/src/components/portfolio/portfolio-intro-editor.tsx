"use client";

import { useState } from "react";
import { Check, Loader2 } from "lucide-react";
import { ApiError, portfolio, type PortfolioData, type PortfolioPatch } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

/**
 * The owner-controlled narrative fields (headline, about, interests, focus).
 * Edited as one form so the intro stays coherent; saved with a single PATCH.
 */
export function PortfolioIntroEditor({ portfolio: data }: { portfolio: PortfolioData }) {
  const [headline, setHeadline] = useState(data.headline);
  const [about, setAbout] = useState(data.about);
  const [interestsText, setInterestsText] = useState(data.interests.join(", "));
  const [currentlyLearning, setCurrentlyLearning] = useState(data.currently_learning);
  const [enjoysBuilding, setEnjoysBuilding] = useState(data.enjoys_building);

  const [saving, setSaving] = useState(false);
  const [savedAt, setSavedAt] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  const dirty =
    headline !== data.headline ||
    about !== data.about ||
    interestsText !== data.interests.join(", ") ||
    currentlyLearning !== data.currently_learning ||
    enjoysBuilding !== data.enjoys_building;

  async function save() {
    setSaving(true);
    setError(null);
    setFieldErrors({});
    const patch: PortfolioPatch = {
      headline: headline.trim(),
      about: about.trim(),
      interests: interestsText.split(",").map((s) => s.trim()).filter(Boolean),
      currently_learning: currentlyLearning.trim(),
      enjoys_building: enjoysBuilding.trim(),
    };
    try {
      await portfolio.patchMy(patch);
      setSavedAt(Date.now());
    } catch (err) {
      if (err instanceof ApiError && err.fieldErrors) {
        setFieldErrors(Object.fromEntries(Object.entries(err.fieldErrors).map(([k, v]) => [k, v.join(" ")])));
      }
      setError(err instanceof Error ? err.message : "Couldn't save your intro.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <Card className="p-5 sm:p-6">
      <div className="mb-4">
        <h2 className="text-base font-semibold text-foreground">Portfolio intro</h2>
        <p className="mt-1 text-sm text-muted-foreground">How visitors and recruiters first read who you are.</p>
      </div>

      <div className="space-y-4">
        <Field label="Headline" error={fieldErrors.headline} hint="One line, e.g. “Backend engineer who likes making systems boring.”">
          <input
            value={headline}
            maxLength={160}
            onChange={(e) => setHeadline(e.target.value)}
            className={inputClass(!!fieldErrors.headline)}
            placeholder="Your professional headline"
          />
        </Field>

        <Field label="About you" error={fieldErrors.about}>
          <textarea
            value={about}
            rows={4}
            onChange={(e) => setAbout(e.target.value)}
            className={inputClass(!!fieldErrors.about)}
            placeholder="A short paragraph about what you build and why."
          />
        </Field>

        <Field label="Interests" hint="Comma-separated topics you care about.">
          <input
            value={interestsText}
            onChange={(e) => setInterestsText(e.target.value)}
            className={inputClass(false)}
            placeholder="Distributed systems, developer experience, RL"
          />
        </Field>

        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="Currently learning">
            <input
              value={currentlyLearning}
              maxLength={200}
              onChange={(e) => setCurrentlyLearning(e.target.value)}
              className={inputClass(false)}
              placeholder="Rust async internals"
            />
          </Field>
          <Field label="Enjoys building">
            <input
              value={enjoysBuilding}
              maxLength={200}
              onChange={(e) => setEnjoysBuilding(e.target.value)}
              className={inputClass(false)}
              placeholder="Tools that remove friction"
            />
          </Field>
        </div>
      </div>

      {error && <p className="mt-3 text-sm font-medium text-destructive">{error}</p>}

      <div className="mt-5 flex items-center gap-3">
        <Button type="button" onClick={save} disabled={saving || !dirty}>
          {saving && <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />}
          {saving ? "Saving…" : "Save intro"}
        </Button>
        {savedAt && !dirty && (
          <span className="inline-flex items-center gap-1 text-sm text-success">
            <Check className="h-4 w-4" aria-hidden="true" /> Saved
          </span>
        )}
      </div>
    </Card>
  );
}

function Field({ label, hint, error, children }: { label: string; hint?: string; error?: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-sm font-medium text-foreground">{label}</span>
      {children}
      {hint && !error && <span className="mt-1 block text-xs text-muted-foreground">{hint}</span>}
      {error && <span className="mt-1 block text-xs font-medium text-destructive">{error}</span>}
    </label>
  );
}

function inputClass(invalid: boolean) {
  return cn(
    "w-full rounded-lg border bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring",
    invalid ? "border-destructive" : "border-border",
  );
}
