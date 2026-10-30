"use client";

import { Suspense, useEffect, useRef, useState, type ReactNode } from "react";
import { usePathname } from "next/navigation";
import { AppSidebar } from "@/components/layout/app-sidebar";
import { cn } from "@/lib/utils";

const NAV_STORAGE_KEY = "codeyaar:nav-collapsed";
// A course workspace is /learn/<course-slug> (the catalogue lives at /learn).
const COURSE_WORKSPACE = /^\/learn\/[^/]+\/?$/;

function persistCollapsed(collapsed: boolean) {
  try {
    window.localStorage.setItem(NAV_STORAGE_KEY, String(collapsed));
  } catch {
    // Storage can be blocked (private mode); the toggle still works for this visit.
  }
}

/**
 * Client shell around the app navigation. Owns the sidebar's collapsed state so
 * the content offset and the sidebar itself always agree, remembers the
 * learner's choice, and gets the main navigation out of the way when a course
 * workspace opens.
 */
export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);
  // The learner's saved choice, so a temporary auto-collapse inside a course
  // never overwrites how they like the navigation everywhere else.
  const preference = useRef(false);
  const wasInCourse = useRef(false);

  // Restore the last explicit choice once mounted (localStorage is unavailable
  // during server rendering).
  useEffect(() => {
    (async () => {
      try {
        const stored = window.localStorage.getItem(NAV_STORAGE_KEY) === "true";
        preference.current = stored;
        setCollapsed(stored);
      } catch {
        // Keep the expanded default when storage is unavailable.
      }
    })();
  }, []);

  // Starting a course collapses the main navigation so the lesson and the
  // workspace get the full width; leaving the course restores the saved choice.
  useEffect(() => {
    (async () => {
      const inCourse = COURSE_WORKSPACE.test(pathname);
      if (inCourse && !wasInCourse.current) setCollapsed(true);
      else if (!inCourse && wasInCourse.current) setCollapsed(preference.current);
      wasInCourse.current = inCourse;
    })();
  }, [pathname]);

  const toggle = () => {
    const next = !collapsed;
    setCollapsed(next);
    // Inside a course the collapse is automatic, so a manual toggle there only
    // affects this visit; everywhere else it becomes the saved preference.
    if (!wasInCourse.current) {
      preference.current = next;
      persistCollapsed(next);
    }
  };

  return (
    <div className="flex min-h-dvh flex-col bg-[#f5f7fa]">
      <Suspense fallback={null}>
        <AppSidebar collapsed={collapsed} onToggle={toggle} />
      </Suspense>
      {/* Main content area — offset for the sidebar on desktop, and for the
          mobile header below md. */}
      <div
        className={cn(
          "flex min-h-0 flex-1 flex-col pt-14 md:pt-0",
          collapsed ? "md:pl-0" : "md:pl-[272px]"
        )}
      >
        <main className="min-h-0 flex-1">
          <Suspense fallback={null}>{children}</Suspense>
        </main>
      </div>
    </div>
  );
}
