"use client";

import { Bell, Menu, Moon, Search, Sun, User } from "lucide-react";
import { useAuth } from "@/hooks/use-auth";
import { useTheme } from "@/hooks/use-theme";
import { Avatar } from "@/components/ui/avatar";

export function AdminTopNav({ onMenuClick }: { onMenuClick: () => void }) {
  const { user, profile } = useAuth();
  const { theme, setTheme } = useTheme();
  const displayName = user?.first_name || user?.username || "Admin";

  return (
    <header className="sticky top-0 z-20 flex h-14 shrink-0 items-center gap-4 border-b border-[var(--color-section-border)] bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 px-4 md:px-6 lg:px-8">
      <button
        type="button"
        onClick={onMenuClick}
        aria-label="Open navigation"
        className="flex h-10 w-10 items-center justify-center rounded-lg text-foreground transition-colors hover:bg-secondary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)] md:hidden"
      >
        <Menu className="h-5 w-5" />
      </button>

      <div className="flex h-10 flex-1 items-center gap-2 bg-[var(--color-section-light)] rounded-lg px-3 text-sm placeholder:text-muted-foreground md:max-w-md">
        <Search className="h-4 w-4 text-muted-foreground" aria-hidden="true" />
        <input
          type="search"
          placeholder="Search courses, students, tracks..."
          className="flex h-full w-full bg-transparent border-none outline-none text-foreground placeholder:text-muted-foreground"
          aria-label="Global search"
        />
      </div>

      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          aria-label={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
          className="flex h-10 w-10 items-center justify-center rounded-lg text-foreground transition-colors hover:bg-secondary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)]"
        >
          {theme === "dark" ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
        </button>

        <button
          type="button"
          aria-label="Notifications"
          className="relative flex h-10 w-10 items-center justify-center rounded-lg text-foreground transition-colors hover:bg-secondary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)]"
        >
          <Bell className="h-5 w-5" />
        </button>

        <div className="relative ml-2">
          <button
            type="button"
            aria-label="User menu"
            aria-expanded="false"
            className="flex items-center gap-2 rounded-lg px-3 py-1.5 text-sm font-medium text-foreground transition-colors hover:bg-secondary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)]"
          >
            <Avatar
              src={profile?.avatar}
              name={displayName}
              username={user?.username}
              size={32}
              className="shrink-0 ring-1 ring-[var(--color-section-border)]"
            />
            <span className="hidden truncate md:block">{displayName}</span>
            <User className="h-4 w-4 md:hidden" aria-hidden="true" />
          </button>
        </div>
      </div>
    </header>
  );
}