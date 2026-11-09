"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { Award, X } from "lucide-react";
import {
  notifications as notificationsApi,
  type AppNotification,
  type BadgeUnlock,
} from "@/lib/api";

/**
 * Lightweight badge-unlock toasts. Completion responses carry an
 * `awarded_badges` array so a toast can appear instantly; on first mount we
 * also hydrate any unread badge notifications so nothing is missed after a
 * reload. Dismissing marks the backing notification read when there is one.
 */

interface Toast {
  key: string;
  title: string;
  description: string;
  notificationId?: number;
  visible: boolean;
}

interface BadgeToastApi {
  notify: (badges: BadgeUnlock[]) => void;
}

const BadgeToastContext = createContext<BadgeToastApi | null>(null);

export function useBadgeToasts(): BadgeToastApi {
  const ctx = useContext(BadgeToastContext);
  // Outside the provider (e.g. a stray consumer) degrade to a no-op.
  if (!ctx) return { notify: () => {} };
  return ctx;
}

let toastCounter = 0;

export function BadgeToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const seen = useRef<Set<string>>(new Set());

  const dismiss = useCallback((key: string, notificationId?: number) => {
    setToasts((prev) => prev.filter((t) => t.key !== key));
    if (notificationId) {
      void notificationsApi.markRead(notificationId).catch(() => {});
    }
  }, []);

  const push = useCallback(
    (toast: Omit<Toast, "visible">) => {
      if (seen.current.has(toast.key)) return;
      seen.current.add(toast.key);
      // Mount hidden, then slide in on the next frame for a subtle entrance.
      setToasts((prev) => [...prev, { ...toast, visible: false }]);
      requestAnimationFrame(() =>
        setToasts((prev) => prev.map((t) => (t.key === toast.key ? { ...t, visible: true } : t)))
      );
      window.setTimeout(() => dismiss(toast.key, toast.notificationId), 7000);
    },
    [dismiss]
  );

  const notify = useCallback(
    (badges: BadgeUnlock[]) => {
      for (const badge of badges) {
        push({
          key: `award-${badge.credential_id || badge.slug}-${toastCounter++}`,
          title: `Badge unlocked — ${badge.title}`,
          description: badge.description,
        });
      }
    },
    [push]
  );

  // Hydrate recent unread badge unlocks once on mount.
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await notificationsApi.list({ page_size: 10 });
        if (cancelled) return;
        res.results
          .filter((n: AppNotification) => n.unread && n.type === "badge_unlock")
          .slice(0, 3)
          .forEach((n: AppNotification) =>
            push({
              key: `notif-${n.id}`,
              title: n.title,
              description: n.body,
              notificationId: n.id,
            })
          );
      } catch {
        // Notifications are best-effort; a failure here must never break the UI.
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [push]);

  return (
    <BadgeToastContext.Provider value={{ notify }}>
      {children}
      <div className="pointer-events-none fixed bottom-4 right-4 z-[100] flex w-[min(22rem,calc(100vw-2rem))] flex-col gap-2">
        {toasts.map((toast) => (
          <div
            key={toast.key}
            role="status"
            className={`pointer-events-auto flex items-start gap-3 rounded-xl border border-border bg-card p-3 shadow-[var(--shadow-3)] transition-all duration-300 ${
              toast.visible ? "translate-y-0 opacity-100" : "translate-y-2 opacity-0"
            }`}
          >
            <span className="mt-0.5 grid h-8 w-8 shrink-0 place-items-center rounded-full bg-primary/10 text-primary">
              <Award className="h-4 w-4" aria-hidden="true" />
            </span>
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-semibold text-foreground">{toast.title}</p>
              <p className="mt-0.5 line-clamp-2 text-xs text-muted-foreground">
                {toast.description}
              </p>
            </div>
            <button
              type="button"
              onClick={() => dismiss(toast.key, toast.notificationId)}
              aria-label="Dismiss"
              className="shrink-0 rounded-md p-1 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
            >
              <X className="h-4 w-4" aria-hidden="true" />
            </button>
          </div>
        ))}
      </div>
    </BadgeToastContext.Provider>
  );
}
