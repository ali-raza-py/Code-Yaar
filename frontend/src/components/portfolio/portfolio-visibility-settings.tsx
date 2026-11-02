"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Globe, GlobeOff, Loader2 } from "lucide-react";
import { ApiError, portfolio, type PortfolioData } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

const TOGGLES: Array<{ key: keyof ToggleMap; label: string; hint: string }> = [
  { key: "show_skills", label: "Technical skills", hint: "Self-reported and demonstrated skills, grouped by area." },
  { key: "show_achievements", label: "Achievements", hint: "Badges you've earned, honouring your profile's badge privacy." },
  { key: "show_learning_progress", label: "Learning journey", hint: "Completed tracks and courses." },
  { key: "show_social_links", label: "Social links", hint: "GitHub, LinkedIn and website from your profile." },
  { key: "show_location", label: "Location", hint: "Show the location on your profile." },
  { key: "show_contact", label: "Contact link", hint: "Let visitors reach you. Off by default." },
];

type ToggleMap = Pick<
  PortfolioData,
  "show_skills" | "show_achievements" | "show_learning_progress" | "show_social_links" | "show_location" | "show_contact"
>;

/**
 * Publish control + per-section visibility. Every toggle persists immediately
 * against `/portfolio/me/`, so there's no separate "save" to forget; publish /
 * unpublish hit the dedicated endpoints so the state is unambiguous.
 */
export function PortfolioVisibilitySettings({ portfolio: data }: { portfolio: PortfolioData }) {
  const router = useRouter();
  const [state, setState] = useState<ToggleMap>({
    show_skills: data.show_skills,
    show_achievements: data.show_achievements,
    show_learning_progress: data.show_learning_progress,
    show_social_links: data.show_social_links,
    show_location: data.show_location,
    show_contact: data.show_contact,
  });
  const [busy, setBusy] = useState<string | null>(null);
  const [published, setPublished] = useState(data.is_published);
  const [error, setError] = useState<string | null>(null);

  async function persist(key: keyof ToggleMap, value: boolean) {
    const previous = state[key];
    setState((s) => ({ ...s, [key]: value }));
    setBusy(key);
    setError(null);
    try {
      await portfolio.patchMy({ [key]: value });
    } catch (err) {
      setState((s) => ({ ...s, [key]: previous })); // revert optimistic change
      setError(err instanceof Error ? err.message : "Couldn't update that setting.");
    } finally {
      setBusy(null);
    }
  }

  async function togglePublish() {
    setBusy("publish");
    setError(null);
    try {
      if (published) {
        await portfolio.unpublish();
        setPublished(false);
      } else {
        await portfolio.publish();
        setPublished(true);
      }
      router.refresh();
    } catch (err) {
      setError(
        err instanceof ApiError && err.status === 400
          ? "Add a headline and publishable projects before going live."
          : err instanceof Error ? err.message : "Couldn't change publish state.",
      );
    } finally {
      setBusy(null);
    }
  }

  return (
    <Card className="overflow-hidden">
      <div className="border-b border-border bg-muted/30 px-5 py-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="min-w-0">
            <h2 className="text-base font-semibold text-foreground">
              {published ? "Portfolio is public" : "Portfolio is private"}
            </h2>
            <p className="mt-0.5 text-sm text-muted-foreground">
              {published
                ? "Anyone with your link can view published sections and public projects."
                : "Only you can see this. Publish when you're ready to share."}
            </p>
          </div>
          <Button
            type="button"
            variant={published ? "outline" : "default"}
            onClick={togglePublish}
            disabled={busy === "publish"}
          >
            {busy === "publish"
              ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
              : published ? <GlobeOff className="h-4 w-4" aria-hidden="true" /> : <Globe className="h-4 w-4" aria-hidden="true" />}
            {published ? "Unpublish" : "Publish"}
          </Button>
        </div>
      </div>

      {error && <p className="bg-destructive/10 px-5 py-2 text-sm text-destructive">{error}</p>}

      <ul className="divide-y divide-border">
        {TOGGLES.map(({ key, label, hint }) => (
          <li key={key} className="flex items-center justify-between gap-4 px-5 py-3.5">
            <div className="min-w-0">
              <p className="text-sm font-medium text-foreground">{label}</p>
              <p className="text-xs text-muted-foreground">{hint}</p>
            </div>
            <button
              type="button"
              role="switch"
              aria-checked={state[key]}
              aria-label={label}
              disabled={busy === key}
              onClick={() => persist(key, !state[key])}
              className={cn(
                "relative h-6 w-11 shrink-0 rounded-full border transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:opacity-60",
                state[key] ? "border-primary bg-primary" : "border-border bg-muted",
              )}
            >
              <span
                className={cn(
                  "absolute top-0.5 rounded-full bg-white shadow transition-transform",
                  state[key] ? "translate-x-5" : "translate-x-0.5",
                )}
                style={{ height: 18, width: 18 }}
              />
            </button>
          </li>
        ))}
      </ul>
    </Card>
  );
}
