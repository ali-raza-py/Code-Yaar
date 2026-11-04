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

// Shared, height-driven ease for every expand/collapse so branches open and
// shut with the same feel. Framer-motion honours `prefers-reduced-motion`
// through the app-wide MotionConfig, so this stays a polish, not a requirement.
const EXPAND_TRANSITION = { duration: 0.2, ease: [0.22, 0.61, 0.36, 1] } as const;

type QueryKey = "mode" | "view" | "track";

interface NavItem {
  href: string;
  label: string;
  icon: LucideIcon;
  /** Legacy marker kept for type compatibility with query-driven links. */
  query?: Partial<Record<QueryKey, string>>;
  badge?: string;
}

const primaryItems: NavItem[] = [
  { href: "/dashboard", label: "Dashboard", icon: Home },
];

// Explore Courses is a flat Learn leaf. Learning Tracks is the nested,
// API-driven subtree rendered by <LearningTracksNav/>.
const exploreCoursesItem: NavItem = {
  href: "/learn?view=courses",
  label: "Explore Courses",
  icon: BookOpen,
  query: { view: "courses" },
};

// Apply holds general skill work only. Sindh Board practicals live inside
// their class curriculum (Learn), and the standalone Sandbox entry is gone —
// the editor now surfaces within Practice and Projects where it is needed.
const applyItems: NavItem[] = [
  { href: "/challenges", label: "Practice", icon: Dumbbell },
  { href: "/projects", label: "Real World Projects", icon: FolderGit2 },
  {
    href: "/competitions",
    label: "Competitions",
    icon: Swords,
  },
];

// Student destinations, simplified to four entries: Progress and Profile
// carry Achievements/Certificates and Portfolio as in-page tabs, so the
// sidebar stays minimal while every experience remains one click away.
const secondaryItems: NavItem[] = [
  { href: "/progress", label: "My Progress", icon: Activity },
  { href: "/leaderboard", label: "Leaderboard", icon: Medal, badge: "NEW" },
  { href: "/profile", label: "My Profile", icon: User },
  { href: "/settings", label: "Settings", icon: Settings },
];

// Resolve a nav target to an active flag. A href carrying a query string
// (e.g. "/challenges?mode=competitions") must match path + params exactly;
// a plain href also claims nested routes (a class page lights its parent
// track), while ignoring pages that are on a query-driven sibling view.
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
            ? "bg-[var(--sidebar-active-bg)] text-white before:bg-[var(--sidebar-accent)]"
            : "text-white/75 hover:bg-white/[0.07] hover:text-white before:bg-transparent"
        )}
      >
        <Icon
          aria-hidden="true"
          className={cn(
            "h-5 w-5 shrink-0 stroke-[1.7] transition-colors",
            active ? "text-[var(--sidebar-accent)]" : "text-white/65 group-hover:text-white"
          )}
        />
        <span className="min-w-0 truncate">{item.label}</span>
        {item.badge && (
          <span className="ml-auto rounded-pill border border-[var(--sidebar-badge-border)] bg-[var(--sidebar-badge-bg)] px-1.5 py-0.5 text-[10px] font-bold tracking-wide text-[var(--sidebar-accent-soft)]">
            {item.badge}
          </span>
        )}
      </Link>
    </li>
  );
}

/**
 * A collapsible section group. Expansion lives in the shared sidebar store,
 * keyed by the label, so a click is the only thing that ever changes it —
 * navigation and remounts restore the learner's last arrangement instead.
 */
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
        className="flex min-h-8 w-full items-center justify-between rounded-md px-3 text-[11px] font-bold uppercase tracking-[0.12em] text-white/75 transition-colors hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--sidebar-accent)]"
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

// A single tree row: the whole label is a Link, and when it has children a
// trailing chevron button toggles them. `depth` drives the left inset so the
// Learning Tracks > track > class nesting stays visually legible. Expansion is
// owned by the caller (and through the shared store), never by this row, so a
// remount can't quietly reopen — or close — something the learner set.
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
  /**
   * The route lives among this row's children while the row is shut. The
   * chevron keeps the accent colour so the branch still reads as the current
   * one without being forced open.
   */
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
              ? "bg-[var(--sidebar-active-bg)] text-white before:bg-[var(--sidebar-accent)]"
              : "text-white/75 hover:bg-white/[0.07] hover:text-white before:bg-transparent"
          )}
        >
          <Icon
            aria-hidden="true"
            className={cn(
              "h-5 w-5 shrink-0 stroke-[1.7] transition-colors",
              active ? "text-[var(--sidebar-accent)]" : "text-white/65 group-hover:text-white"
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
              "absolute right-1 top-1/2 flex h-7 w-7 -translate-y-1/2 items-center justify-center rounded-md transition-colors hover:bg-white/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--sidebar-accent)]",
              activeDescendant
                ? "text-[var(--sidebar-accent)] hover:text-white"
                : "text-white/60 hover:text-white"
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

// A published class (Class X / XI / XII) under a board track — the deepest
// nav level, linking to the class overview page that unifies Theory+Practicals.
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

// A track inside Learning Tracks. Board tracks are expandable and lazily load
// their class levels (from the courses' academic_class labels) on first open.
//
// Loaded lists are kept at module scope: the shell is mounted by two route
// groups, so crossing from Learn to Leaderboard remounts this row. Reading the
// cache back into state makes that return instant and silent instead of a
// "Loading classes..." flash plus a duplicate request.
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
    // Guard on `classes === null` (state), not a persistent ref: under a
    // StrictMode double-invoke the first cleanup cancels its own result, so
    // the second run must be free to re-fetch and actually apply the data.
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
        <li style={{ paddingLeft: `${12 + (depth + 1) * 14}px` }} className="py-1 text-xs text-white/50">
          Loading classes...
        </li>
      )}
      {error && (
        <li style={{ paddingLeft: `${12 + (depth + 1) * 14}px` }} className="py-1 text-xs text-white/50">
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

// The nested "Learning Tracks" subtree. Children come from the tracks API so
// an admin publishing a new track needs no frontend change; board tracks
// expand to their classes.
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
  // A specific track page is open while the branch is shut — keep the chevron
  // accented so the current location is still visible, without forcing it open.
  const hiddenActiveTrack = pathname.startsWith("/tracks/") && !open;

  useEffect(() => {
    // Same StrictMode-safe guard as TrackNode: rely on state, not a ref, so a
    // re-mounted effect re-fetches instead of stranding the row on "Loading".
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
        <li style={{ paddingLeft: "26px" }} className="py-1 text-xs text-white/50">
          Loading tracks...
        </li>
      )}
      {error && (
        <li style={{ paddingLeft: "26px" }} className="py-1 text-xs text-white/50">
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
  /** Present on desktop only; the mobile drawer closes with its own button. */
  onCollapse?: () => void;
}) {
  const { user, profile } = useAuth();
  const displayName = user?.first_name || user?.username || "Your profile";

  return (
    <div className="flex h-full min-h-0 flex-col bg-[var(--sidebar-bg)] text-white">
      <div className="flex h-14 shrink-0 items-center gap-2.5 border-b border-white/10 px-4">
        <div className="relative h-6 w-6 shrink-0">
          <Image
            src="/brand/logo-mark.png"
            alt=""
            fill
            sizes="24px"
            className="object-contain brightness-0 invert"
            priority
          />
        </div>
        <span className="text-sm font-bold tracking-tight">Code-Yaar</span>
        {onCollapse && (
          <button
            type="button"
            onClick={onCollapse}
            aria-label="Collapse navigation"
            className="ml-auto flex h-8 w-8 shrink-0 items-center justify-center rounded-md text-white/70 transition-colors hover:bg-white/10 hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--sidebar-accent)]"
          >
            <ChevronLeft aria-hidden="true" className="h-4 w-4" />
          </button>
        )}
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
              active={routeIsActive(item.href, pathname, searchParams)}
              onNavigate={onNavigate}
            />
          ))}
        </ul>

        {/* Learn: the nested Learning Tracks subtree plus the flat Explore
            Courses leaf. Sindh Board classes live here, alongside their
            practicals — never in Apply. */}
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

        {/* Apply: general skill work only. No Sandbox, no Assessments. */}
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

        <ul className="mt-5 space-y-0.5 border-t border-white/10 pt-3">
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

      <div className="shrink-0 border-t border-white/10 p-3">
        <Link
          href="/profile"
          onClick={onNavigate}
          className="flex items-center gap-3 rounded-lg p-2 text-white transition-colors hover:bg-white/[0.07] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--sidebar-accent)]"
        >
          <Avatar
            src={profile?.avatar}
            name={displayName}
            username={user?.username}
            size={32}
            className="shrink-0 ring-1 ring-white/25"
          />
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

  // Branch expansion is click-driven and lives in the shared store, so it
  // outlives this component. The stored arrangement is lifted in after mount
  // (never during render) to keep the first paint identical to the server HTML.
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
        // Wrapper owns the responsive display so the hidden handle is never a
        // focus target on mobile, where the header button handles navigation.
        <div className="fixed left-0 top-1/2 z-40 hidden -translate-y-1/2 md:block">
          <button
            type="button"
            onClick={onToggle}
            aria-label="Open navigation"
            className="flex h-16 w-6 items-center justify-center rounded-r-lg bg-[var(--sidebar-bg)] text-white shadow-lg transition-colors hover:bg-[var(--sidebar-active-bg)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--sidebar-accent)]"
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

      <header className="fixed inset-x-0 top-0 z-30 flex h-14 items-center border-b border-[var(--color-section-border)] bg-background px-4 md:hidden">
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
                className="absolute right-3 top-3 z-10 flex h-8 w-8 items-center justify-center rounded-lg text-white/70 transition-colors hover:bg-white/10 hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--sidebar-accent)]"
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
