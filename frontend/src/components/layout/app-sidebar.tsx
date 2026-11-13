"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import {
  Activity,
  BookOpen,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
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
import { Avatar } from "@/components/ui/avatar";
import { tracks as tracksApi, type TrackSummary } from "@/lib/api";
import { canonicalClassSlug } from "@/components/learning/tracks/shared";
import {
  restoreSidebarExpansion,
  sidebarNode,
  useSidebarNodeExpansion,
} from "@/lib/sidebar-expansion";

const EXPAND_TRANSITION = { duration: 0.2, ease: [0.22, 0.61, 0.36, 1] } as const;

type QueryKey = "mode" | "view" | "track";

interface NavItem {
  href: string;
  label: string;
  icon: LucideIcon;
  query?: Partial<Record<QueryKey, string>>;
  badge?: string;
}

const primaryItems: NavItem[] = [
  { href: "/dashboard", label: "Dashboard", icon: Home },
];

const exploreCoursesItem: NavItem = {
  href: "/learn?view=courses",
  label: "Explore Courses",
  icon: BookOpen,
  query: { view: "courses" },
};

const applyItems: NavItem[] = [
  { href: "/challenges", label: "Practice", icon: Dumbbell },
  { href: "/projects", label: "Real World Projects", icon: FolderGit2 },
  { href: "/competitions", label: "Competitions", icon: Swords },
];

const secondaryItems: NavItem[] = [
  { href: "/progress", label: "My Progress", icon: Activity },
  { href: "/leaderboard", label: "Leaderboard", icon: Medal, badge: "NEW" },
  { href: "/profile", label: "My Profile", icon: User },
  { href: "/settings", label: "Settings", icon: Settings },
];

function routeIsActive(
  href: string,
  pathname: string,
  searchParams: URLSearchParams,
) {
  const [base, rawQuery] = href.split("?");

  if (rawQuery) {
    if (pathname !== base) return false;
    const pairs = new URLSearchParams(rawQuery);
    return Array.from(pairs.entries()).every(
      ([key, value]) => searchParams.get(key) === value,
    );
  }

  const matches = pathname === base || pathname.startsWith(`${base}/`);
  if (!matches) return false;
  return !searchParams.has("mode") && !searchParams.has("view");
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
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--sidebar-accent)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--sidebar-bg)]",
          active
            ? "bg-[var(--sidebar-active-bg)] text-[var(--sidebar-accent-strong)] before:bg-[var(--sidebar-accent)] font-semibold"
            : "text-[var(--sidebar-text)] hover:bg-[var(--sidebar-hover-bg)] before:bg-transparent"
        )}
      >
        <Icon
          aria-hidden="true"
          className={cn(
            "h-5 w-5 shrink-0 stroke-[1.7] transition-colors",
            active ? "text-[var(--sidebar-accent-strong)]" : "text-[var(--sidebar-icon)] group-hover:text-[var(--sidebar-accent-strong)]"
          )}
        />
        <span className="min-w-0 truncate">{item.label}</span>
        {item.badge && (
          <span className="ml-auto rounded-pill border border-[var(--sidebar-badge-border)] bg-[var(--sidebar-badge-bg)] px-1.5 py-0.5 text-[10px] font-semibold tracking-wide text-[var(--sidebar-accent-strong)]">
            {item.badge}
          </span>
        )}
      </Link>
    </li>
  );
}

function NavSection({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  const [expanded, onToggle] = useSidebarNodeExpansion(sidebarNode.section(label));
  const contentId = `sidebar-${label.toLowerCase()}-links`;

  return (
    <section className="mt-5 first:mt-4">
      <button
        type="button"
        aria-expanded={expanded}
        aria-controls={contentId}
        onClick={onToggle}
        className="flex min-h-8 w-full items-center justify-between rounded-md px-3 text-[11px] font-bold uppercase tracking-[0.12em] text-[var(--sidebar-section-text)] transition-colors hover:text-[var(--sidebar-accent-strong)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--sidebar-accent)]"
      >
        {label}
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
          <motion.div
            id={contentId}
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={EXPAND_TRANSITION}
            className="mt-1 overflow-hidden"
          >
            <ul className="space-y-0.5">{children}</ul>
          </motion.div>
        )}
      </AnimatePresence>
    </section>
  );
}

function TreeRow({
  item,
  active,
  depth,
  hasChildren,
  expanded,
  onToggle,
  activeDescendant = false,
  onNavigate,
  children,
}: {
  item: NavItem;
  active: boolean;
  depth: number;
  hasChildren?: boolean;
  expanded?: boolean;
  onToggle?: () => void;
  activeDescendant?: boolean;
  onNavigate: () => void;
  children?: React.ReactNode;
}) {
  const Icon = item.icon;
  const indent = 12 + depth * 14;

  return (
    <li>
      <div className="relative">
        <Link
          href={item.href}
          onClick={onNavigate}
          aria-current={active ? "page" : undefined}
          style={{
            paddingLeft: `${indent}px`,
            paddingRight: hasChildren ? "2.5rem" : undefined,
          }}
          className={cn(
            "group relative flex min-h-10 items-center gap-3 rounded-lg text-sm font-medium transition-colors duration-150",
            "before:absolute before:inset-y-2 before:left-0 before:w-0.5 before:rounded-r-full before:transition-colors",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--sidebar-accent)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--sidebar-bg)]",
            active
              ? "bg-[var(--sidebar-active-bg)] text-[var(--sidebar-accent-strong)] before:bg-[var(--sidebar-accent)] font-semibold"
              : "text-[var(--sidebar-text)] hover:bg-[var(--sidebar-hover-bg)] before:bg-transparent"
          )}
        >
          <Icon
            aria-hidden="true"
            className={cn(
              "h-5 w-5 shrink-0 stroke-[1.7] transition-colors",
              active ? "text-[var(--sidebar-accent-strong)]" : "text-[var(--sidebar-icon)] group-hover:text-[var(--sidebar-accent-strong)]"
            )}
          />
          <span className="min-w-0 truncate">{item.label}</span>
        </Link>
        {hasChildren && (
          <button
            type="button"
            onClick={onToggle}
            aria-label={`${expanded ? "Collapse" : "Expand"} ${item.label}`}
            aria-expanded={expanded}
            className={cn(
              "absolute right-1 top-1/2 flex h-7 w-7 -translate-y-1/2 items-center justify-center rounded-md transition-colors hover:bg-[var(--sidebar-hover-bg)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--sidebar-accent)]",
              activeDescendant
                ? "text-[var(--sidebar-accent-strong)]"
                : "text-[var(--sidebar-icon)]"
            )}
          >
            <ChevronDown
              aria-hidden="true"
              className={cn(
                "h-4 w-4 transition-transform duration-200 ease-out",
                !expanded && "-rotate-90"
              )}
            />
          </button>
        )}
      </div>

      <AnimatePresence initial={false}>
        {expanded && hasChildren && (
          <motion.ul
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={EXPAND_TRANSITION}
            className="mt-0.5 space-y-0.5 overflow-hidden"
          >
            {children}
          </motion.ul>
        )}
      </AnimatePresence>
    </li>
  );
}

function ClassNode({
  trackSlug,
  classSlug,
  label,
  depth,
  pathname,
  searchParams,
  onNavigate,
}: {
  trackSlug: string;
  classSlug: string;
  label: string;
  depth: number;
  pathname: string;
  searchParams: URLSearchParams;
  onNavigate: () => void;
}) {
  const href = `/tracks/${trackSlug}/${classSlug}`;
  return (
    <TreeRow
      item={{ href, label, icon: BookOpen }}
      active={routeIsActive(href, pathname, searchParams)}
      depth={depth}
      onNavigate={onNavigate}
    />
  );
}

const classesByTrack = new Map<string, { slug: string; label: string }[]>();

function TrackNode({
  track,
  depth,
  pathname,
  searchParams,
  onNavigate,
}: {
  track: TrackSummary;
  depth: number;
  pathname: string;
  searchParams: URLSearchParams;
  onNavigate: () => void;
}) {
  const isBoard = track.category === "school_board";
  const [open, toggleOpen] = useSidebarNodeExpansion(sidebarNode.track(track.slug));
  const [classes, setClasses] = useState(
    () => classesByTrack.get(track.slug) ?? null,
  );
  const [error, setError] = useState(false);

  const href = `/tracks/${track.slug}`;
  const active = routeIsActive(href, pathname, searchParams);
  const loading = isBoard && open && classes === null && !error;

  useEffect(() => {
    if (!isBoard || !open || classes !== null) return;
    let alive = true;
    (async () => {
      try {
        const detail = await tracksApi.detail(track.slug);
        if (!alive) return;
        const seen = new Map<string, string>();
        for (const course of detail.courses) {
          const label = course.academic_class;
          if (!label) continue;
          const slug = canonicalClassSlug(label);
          if (slug && !seen.has(slug)) seen.set(slug, label);
        }
        const entries = Array.from(seen, ([slug, label]) => ({ slug, label }));
        classesByTrack.set(track.slug, entries);
        setClasses(entries);
      } catch {
        if (alive) setError(true);
      }
    })();
    return () => {
      alive = false;
    };
  }, [isBoard, open, classes, track.slug]);

  return (
    <TreeRow
      item={{ href, label: track.title, icon: Layers }}
      active={active}
      depth={depth}
      hasChildren={isBoard}
      expanded={open}
      onToggle={toggleOpen}
      activeDescendant={isBoard && active && !open}
      onNavigate={onNavigate}
    >
      {loading && (
        <li style={{ paddingLeft: `${12 + (depth + 1) * 14}px` }} className="py-1 text-xs text-[var(--sidebar-muted)]">
          Loading classes...
        </li>
      )}
      {error && (
        <li style={{ paddingLeft: `${12 + (depth + 1) * 14}px` }} className="py-1 text-xs text-[var(--sidebar-muted)]">
          Classes could not be loaded.
        </li>
      )}
      {classes?.map((cls) => (
        <ClassNode
          key={cls.slug}
          trackSlug={track.slug}
          classSlug={cls.slug}
          label={cls.label}
          depth={depth + 1}
          pathname={pathname}
          searchParams={searchParams}
          onNavigate={onNavigate}
        />
      ))}
    </TreeRow>
  );
}

let cachedTracks: TrackSummary[] | null = null;

function LearningTracksNav({
  pathname,
  searchParams,
  onNavigate,
}: {
  pathname: string;
  searchParams: URLSearchParams;
  onNavigate: () => void;
}) {
  const [open, toggleOpen] = useSidebarNodeExpansion(sidebarNode.tracksRoot);
  const [tracks, setTracks] = useState<TrackSummary[] | null>(cachedTracks);
  const [error, setError] = useState(false);
  const loading = open && tracks === null && !error;
  const hiddenActiveTrack = pathname.startsWith("/tracks/") && !open;

  useEffect(() => {
    if (!open || tracks !== null) return;
    let alive = true;
    (async () => {
      try {
        const data = await tracksApi.list();
        if (!alive) return;
        cachedTracks = data;
        setTracks(data);
      } catch {
        if (alive) setError(true);
      }
    })();
    return () => {
      alive = false;
    };
  }, [open, tracks]);

  return (
    <TreeRow
      item={{ href: "/tracks", label: "Learning Tracks", icon: Layers }}
      active={routeIsActive("/tracks", pathname, searchParams)}
      depth={0}
      hasChildren
      expanded={open}
      onToggle={toggleOpen}
      activeDescendant={hiddenActiveTrack}
      onNavigate={onNavigate}
    >
      {loading && (
        <li style={{ paddingLeft: "26px" }} className="py-1 text-xs text-[var(--sidebar-muted)]">
          Loading tracks...
        </li>
      )}
      {error && (
        <li style={{ paddingLeft: "26px" }} className="py-1 text-xs text-[var(--sidebar-muted)]">
          Tracks could not be loaded.
        </li>
      )}
      {tracks?.map((track) => (
        <TrackNode
          key={track.slug}
          track={track}
          depth={1}
          pathname={pathname}
          searchParams={searchParams}
          onNavigate={onNavigate}
        />
      ))}
    </TreeRow>
  );
}

function SidebarPanel({
  pathname,
  searchParams,
  onNavigate,
  onSignOut,
  onCollapse,
}: {
  pathname: string;
  searchParams: URLSearchParams;
  onNavigate: () => void;
  onSignOut: () => void;
  onCollapse?: () => void;
}) {
  const { user, profile } = useAuth();
  const displayName = user?.first_name || user?.username || "Your profile";

  return (
    <div className="flex h-full min-h-0 flex-col bg-[var(--sidebar-bg)] text-[var(--sidebar-text)] border-r border-[var(--sidebar-border)]">
      <div className="flex h-14 shrink-0 items-center gap-2.5 border-b border-[var(--sidebar-border)] px-4">
        <div className="relative h-6 w-6 shrink-0">
          <Image
            src="/brand/logo-mark.png"
            alt=""
            fill
            sizes="24px"
            className="object-contain"
            priority
          />
        </div>
        <span className="text-sm font-semibold tracking-tight text-[var(--sidebar-text)]">Code Yaar</span>
        {onCollapse && (
          <button
            type="button"
            onClick={onCollapse}
            aria-label="Collapse navigation"
            className="ml-auto flex h-8 w-8 shrink-0 items-center justify-center rounded-md text-[var(--sidebar-icon)] transition-colors hover:bg-[var(--sidebar-hover-bg)] hover:text-[var(--sidebar-accent-strong)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--sidebar-accent)]"
          >
            <ChevronLeft aria-hidden="true" className="h-4 w-4" />
          </button>
        )}
      </div>

      <nav
        aria-label="Application navigation"
        className="min-h-0 flex-1 overflow-y-auto px-3 py-2 [scrollbar-width:thin]"
      >
        <ul className="space-y-0.5">
          {primaryItems.map((item) => (
            <SidebarLink
              key={item.label}
              item={item}
              active={routeIsActive(item.href, pathname, searchParams)}
              onNavigate={onNavigate}
            />
          ))}
        </ul>

        <NavSection label="Learn">
          <LearningTracksNav
            pathname={pathname}
            searchParams={searchParams}
            onNavigate={onNavigate}
          />
          <SidebarLink
            item={exploreCoursesItem}
            active={routeIsActive(exploreCoursesItem.href, pathname, searchParams)}
            onNavigate={onNavigate}
          />
        </NavSection>

        <NavSection label="Apply">
          {applyItems.map((item) => (
            <SidebarLink
              key={item.href}
              item={item}
              active={routeIsActive(item.href, pathname, searchParams)}
              onNavigate={onNavigate}
            />
          ))}
        </NavSection>

        <ul className="mt-5 space-y-0.5 border-t border-[var(--sidebar-border)] pt-3">
          {secondaryItems.map((item) => (
            <SidebarLink
              key={item.label}
              item={item}
              active={routeIsActive(item.href, pathname, searchParams)}
              onNavigate={onNavigate}
            />
          ))}
          {user?.role === "administrator" && (
            <SidebarLink
              item={{ href: "/admin/dashboard", label: "Admin Panel", icon: Settings }}
              active={pathname.startsWith("/admin")}
              onNavigate={onNavigate}
            />
          )}
        </ul>
      </nav>

      <div className="shrink-0 border-t border-[var(--sidebar-border)] p-3">
        <Link
          href="/profile"
          onClick={onNavigate}
          className="flex items-center gap-3 rounded-lg p-2 text-[var(--sidebar-text)] transition-colors hover:bg-[var(--sidebar-hover-bg)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--sidebar-accent)]"
        >
          <Avatar
            src={profile?.avatar}
            name={displayName}
            username={user?.username}
            size={32}
            className="shrink-0 ring-1 ring-[var(--sidebar-border)]"
          />
          <span className="min-w-0">
            <span className="block truncate text-xs font-semibold text-[var(--sidebar-text)]">{displayName}</span>
            <span className="block text-[11px] text-[var(--sidebar-muted)]">View profile</span>
          </span>
        </Link>

        <button
          type="button"
          onClick={onSignOut}
          className="mt-1 flex min-h-10 w-full items-center gap-3 rounded-lg px-2 text-sm font-medium text-destructive transition-colors hover:bg-destructive/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-destructive/30"
        >
          <LogOut aria-hidden="true" className="h-5 w-5 stroke-[1.7]" />
          <span>Sign out</span>
        </button>
      </div>
    </div>
  );
}

export function AppSidebar({
  collapsed,
  onToggle,
}: {
  collapsed: boolean;
  onToggle: () => void;
}) {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const router = useRouter();
  const { signOut } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);

  const closeMobile = () => setMobileOpen(false);

  useEffect(() => {
    restoreSidebarExpansion();
  }, []);

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
      {collapsed ? (
        <div className="fixed left-0 top-1/2 z-40 hidden -translate-y-1/2 md:block">
          <button
            type="button"
            onClick={onToggle}
            aria-label="Open navigation"
            className="flex h-16 w-6 items-center justify-center rounded-r-lg border border-l-0 border-[var(--sidebar-border)] bg-[var(--sidebar-bg)] text-[var(--sidebar-text)] shadow-sm transition-colors hover:bg-[var(--sidebar-hover-bg)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--sidebar-accent)]"
          >
            <ChevronRight aria-hidden="true" className="h-4 w-4" />
          </button>
        </div>
      ) : (
        <aside className="fixed inset-y-0 left-0 z-40 hidden w-[272px] md:flex">
          <SidebarPanel
            pathname={pathname}
            searchParams={searchParams}
            onNavigate={closeMobile}
            onSignOut={handleSignOut}
            onCollapse={onToggle}
          />
        </aside>
      )}

      <header className="fixed inset-x-0 top-0 z-30 flex h-14 items-center border-b border-border bg-background/95 px-4 backdrop-blur supports-[backdrop-filter]:bg-background/80 md:hidden">
        <button
          type="button"
          aria-label="Open navigation"
          aria-expanded={mobileOpen}
          onClick={() => setMobileOpen(true)}
          className="flex h-10 w-10 items-center justify-center rounded-lg text-foreground transition-colors hover:bg-secondary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        >
          <Menu aria-hidden="true" className="h-5 w-5" />
        </button>
        <span className="ml-2 text-sm font-semibold text-foreground">Code Yaar</span>
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
              className="fixed inset-0 z-40 bg-black/50 md:hidden"
            />
            <motion.aside
              initial={{ x: "-100%" }}
              animate={{ x: 0 }}
              exit={{ x: "-100%" }}
              transition={{ duration: 0.2, ease: "easeOut" }}
              className="fixed inset-y-0 left-0 z-50 w-[min(86vw,272px)] shadow-xl md:hidden"
              aria-label="Mobile navigation"
            >
              <button
                type="button"
                aria-label="Close navigation"
                onClick={closeMobile}
                className="absolute right-3 top-3 z-10 flex h-8 w-8 items-center justify-center rounded-lg text-foreground/70 transition-colors hover:bg-secondary hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)]"
              >
                <X aria-hidden="true" className="h-4 w-4" />
              </button>
              <SidebarPanel
                pathname={pathname}
                searchParams={searchParams}
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




