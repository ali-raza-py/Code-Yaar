"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import {
  BookOpen,
  ChevronDown,
  ClipboardCheck,
  Code2,
  Dumbbell,
  FolderGit2,
  Home,
  Layers,
  LogOut,
  Medal,
  Menu,
  Settings,
  Swords,
  User,
  X,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/hooks/use-auth";

type QueryKey = "mode" | "view";

interface NavItem {
  href: string;
  label: string;
  icon: LucideIcon;
  query?: Partial<Record<QueryKey, string>>;
  badge?: string;
}

interface NavGroup {
  label: string;
  items: NavItem[];
}

const primaryItems: NavItem[] = [
  { href: "/dashboard", label: "Dashboard", icon: Home },
];

const navGroups: NavGroup[] = [
  {
    label: "Learn",
    items: [
      { href: "/learn?view=tracks", label: "Tracks", icon: Layers, query: { view: "tracks" } },
      { href: "/learn?view=courses", label: "Courses", icon: BookOpen, query: { view: "courses" } },
      { href: "/challenges", label: "Practice", icon: Dumbbell },
      {
        href: "/challenges?mode=assessments",
        label: "Assessments",
        icon: ClipboardCheck,
        query: { mode: "assessments" },
      },
    ],
  },
  {
    label: "Apply",
    items: [
      { href: "/projects", label: "Real World Projects", icon: FolderGit2 },
      { href: "/projects?mode=sandbox", label: "Sandbox", icon: Code2, query: { mode: "sandbox" } },
      {
        href: "/challenges?mode=competitions",
        label: "Competitions",
        icon: Swords,
        query: { mode: "competitions" },
      },
    ],
  },
];

const secondaryItems: NavItem[] = [
  { href: "/leaderboard", label: "Leaderboard", icon: Medal, badge: "NEW" },
  { href: "/profile", label: "Profile", icon: User },
  { href: "/settings", label: "Settings", icon: Settings },
];

function isNavItemActive(
  item: NavItem,
  pathname: string,
  searchParams: URLSearchParams
) {
  if (pathname !== item.href.split("?")[0]) return false;

  if (!item.query) {
    return !searchParams.has("mode") && !searchParams.has("view");
  }

  return Object.entries(item.query).every(
    ([key, value]) => searchParams.get(key) === value
  );
}

function SidebarLink({
  item,
  active,
  onNavigate,
}: {
  item: NavItem;
  active: boolean;
  onNavigate: () => void;
}) {
  const Icon = item.icon;

  return (
    <li>
      <Link
        href={item.href}
        onClick={onNavigate}
        aria-current={active ? "page" : undefined}
        className={cn(
          "group relative flex min-h-10 items-center gap-3 rounded-lg px-3 text-sm font-medium transition-colors duration-150",
          "before:absolute before:inset-y-2 before:left-0 before:w-0.5 before:rounded-r-full before:transition-colors",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#c4b5fd] focus-visible:ring-offset-2 focus-visible:ring-offset-[#0b1220]",
          active
            ? "bg-[#8b5cf6]/[0.16] text-white before:bg-[#c4b5fd]"
            : "text-white/75 hover:bg-white/[0.07] hover:text-white before:bg-transparent"
        )}
      >
        <Icon
          aria-hidden="true"
          className={cn(
            "h-5 w-5 shrink-0 stroke-[1.7] transition-colors",
            active ? "text-[#c4b5fd]" : "text-white/65 group-hover:text-white"
          )}
        />
        <span className="min-w-0 truncate">{item.label}</span>
        {item.badge && (
          <span className="ml-auto rounded-full border border-[#c4b5fd]/30 bg-[#8b5cf6]/20 px-1.5 py-0.5 text-[10px] font-bold tracking-wide text-[#ddd6fe]">
            {item.badge}
          </span>
        )}
      </Link>
    </li>
  );
}

function SidebarGroup({
  group,
  expanded,
  onToggle,
  pathname,
  searchParams,
  onNavigate,
}: {
  group: NavGroup;
  expanded: boolean;
  onToggle: () => void;
  pathname: string;
  searchParams: URLSearchParams;
  onNavigate: () => void;
}) {
  const contentId = `sidebar-${group.label.toLowerCase()}-links`;

  return (
    <section className="mt-5 first:mt-4">
      <button
        type="button"
        aria-expanded={expanded}
        aria-controls={contentId}
        onClick={onToggle}
        className="flex min-h-8 w-full items-center justify-between rounded-md px-3 text-[11px] font-bold uppercase tracking-[0.12em] text-white/75 transition-colors hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#c4b5fd]"
      >
        {group.label}
        <ChevronDown
          aria-hidden="true"
          className={cn(
            "h-4 w-4 stroke-[1.7] transition-transform duration-200",
            !expanded && "-rotate-90"
          )}
        />
      </button>

      <AnimatePresence initial={false}>
        {expanded && (
          <motion.ul
            id={contentId}
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.18, ease: "easeOut" }}
            className="mt-1 space-y-0.5 overflow-hidden"
          >
            {group.items.map((item) => (
              <SidebarLink
                key={item.label}
                item={item}
                active={isNavItemActive(item, pathname, searchParams)}
                onNavigate={onNavigate}
              />
            ))}
          </motion.ul>
        )}
      </AnimatePresence>
    </section>
  );
}

function SidebarPanel({
  pathname,
  searchParams,
  expandedGroups,
  onToggleGroup,
  onNavigate,
  onSignOut,
}: {
  pathname: string;
  searchParams: URLSearchParams;
  expandedGroups: Record<string, boolean>;
  onToggleGroup: (label: string) => void;
  onNavigate: () => void;
  onSignOut: () => void;
}) {
  const { user } = useAuth();
  const displayName = user?.first_name || user?.username || "Your profile";
  const initials = displayName.slice(0, 1).toUpperCase();

  return (
    <div className="flex h-full min-h-0 flex-col bg-[#0b1220] text-white">
      <div className="flex h-14 shrink-0 items-center gap-2.5 border-b border-white/10 px-4">
        <div className="relative h-6 w-6 shrink-0">
          <Image
            src="/logo-light.png"
            alt=""
            fill
            sizes="24px"
            className="object-contain"
            priority
          />
        </div>
        <span className="text-sm font-bold tracking-tight">Code-Yaar</span>
      </div>

      <nav
        aria-label="Application navigation"
        className="min-h-0 flex-1 overflow-y-auto px-3 py-2 [scrollbar-color:rgba(255,255,255,0.28)_transparent] [scrollbar-width:thin] [&::-webkit-scrollbar]:w-1 [&::-webkit-scrollbar-thumb]:rounded-full [&::-webkit-scrollbar-thumb]:bg-white/25 [&::-webkit-scrollbar-track]:bg-transparent"
      >
        <ul className="space-y-0.5">
          {primaryItems.map((item) => (
            <SidebarLink
              key={item.label}
              item={item}
              active={isNavItemActive(item, pathname, searchParams)}
              onNavigate={onNavigate}
            />
          ))}
        </ul>

        {navGroups.map((group) => (
          <SidebarGroup
            key={group.label}
            group={group}
            expanded={expandedGroups[group.label]}
            onToggle={() => onToggleGroup(group.label)}
            pathname={pathname}
            searchParams={searchParams}
            onNavigate={onNavigate}
          />
        ))}

        <ul className="mt-5 space-y-0.5 border-t border-white/10 pt-3">
          {secondaryItems.map((item) => (
            <SidebarLink
              key={item.label}
              item={item}
              active={isNavItemActive(item, pathname, searchParams)}
              onNavigate={onNavigate}
            />
          ))}
        </ul>
      </nav>

      <div className="shrink-0 border-t border-white/10 p-3">
        <div className="rounded-lg border border-white/10 bg-white/[0.045] p-3">
          <div className="flex items-start justify-between gap-3 text-xs">
            <div>
              <p className="font-semibold text-white">Getting started</p>
              <p className="mt-1 text-[11px] text-white/65">One small win today.</p>
            </div>
            <span className="font-bold text-[#ddd6fe]">0/4</span>
          </div>
          <div className="mt-3 h-1 overflow-hidden rounded-full bg-white/10">
            <div className="h-full min-w-1.5 w-0 rounded-full bg-[#a78bfa]" />
          </div>
        </div>

        <div className="mt-3 border-t border-white/10 pt-3">
          <Link
            href="/profile"
            onClick={onNavigate}
            className="flex items-center gap-3 rounded-lg p-2 text-white transition-colors hover:bg-white/[0.07] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#c4b5fd]"
          >
            <span className="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-[#5b4bb7] text-xs font-bold">
              {initials}
            </span>
            <span className="min-w-0">
              <span className="block truncate text-xs font-semibold">{displayName}</span>
              <span className="block text-[11px] text-white/65">View profile</span>
            </span>
          </Link>

          <button
            type="button"
            onClick={onSignOut}
            className="mt-1 flex min-h-10 w-full items-center gap-3 rounded-lg px-2 text-sm font-medium text-red-200 transition-colors hover:bg-red-400/10 hover:text-red-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-200"
          >
            <LogOut aria-hidden="true" className="h-5 w-5 stroke-[1.7]" />
            <span>Sign out</span>
          </button>
        </div>
      </div>
    </div>
  );
}

export function AppSidebar() {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const router = useRouter();
  const { signOut } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>({
    Learn: true,
    Apply: true,
  });

  const closeMobile = () => setMobileOpen(false);
  const toggleGroup = (label: string) => {
    setExpandedGroups((current) => ({ ...current, [label]: !current[label] }));
  };

  useEffect(() => {
    if (!mobileOpen) return;

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") closeMobile();
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [mobileOpen]);

  const handleSignOut = async () => {
    await signOut();
    closeMobile();
    router.push("/");
  };

  return (
    <>
      <aside className="fixed inset-y-0 left-0 z-40 hidden w-[272px] md:flex">
        <SidebarPanel
          pathname={pathname}
          searchParams={searchParams}
          expandedGroups={expandedGroups}
          onToggleGroup={toggleGroup}
          onNavigate={closeMobile}
          onSignOut={handleSignOut}
        />
      </aside>

      <header className="fixed inset-x-0 top-0 z-30 flex h-14 items-center border-b border-[var(--color-section-border)] bg-white px-4 md:hidden">
        <button
          type="button"
          aria-label="Open navigation"
          aria-expanded={mobileOpen}
          onClick={() => setMobileOpen(true)}
          className="flex h-10 w-10 items-center justify-center rounded-lg text-foreground transition-colors hover:bg-secondary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)]"
        >
          <Menu aria-hidden="true" className="h-5 w-5" />
        </button>
        <span className="ml-2 text-sm font-semibold text-foreground">Code-Yaar</span>
      </header>

      <AnimatePresence>
        {mobileOpen && (
          <>
            <motion.button
              type="button"
              aria-label="Close navigation"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={closeMobile}
              className="fixed inset-0 z-40 bg-slate-950/60 md:hidden"
            />
            <motion.aside
              initial={{ x: "-100%" }}
              animate={{ x: 0 }}
              exit={{ x: "-100%" }}
              transition={{ duration: 0.2, ease: "easeOut" }}
              className="fixed inset-y-0 left-0 z-50 w-[min(86vw,272px)] shadow-2xl md:hidden"
              aria-label="Mobile navigation"
            >
              <button
                type="button"
                aria-label="Close navigation"
                onClick={closeMobile}
                className="absolute right-3 top-3 z-10 flex h-8 w-8 items-center justify-center rounded-lg text-white/70 transition-colors hover:bg-white/10 hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#c4b5fd]"
              >
                <X aria-hidden="true" className="h-4 w-4" />
              </button>
              <SidebarPanel
                pathname={pathname}
                searchParams={searchParams}
                expandedGroups={expandedGroups}
                onToggleGroup={toggleGroup}
                onNavigate={closeMobile}
                onSignOut={handleSignOut}
              />
            </motion.aside>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
