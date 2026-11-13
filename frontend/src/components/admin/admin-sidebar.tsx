"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import {
  Activity,
  Award,
  BookOpen,
  ClipboardList,
  History,
  Mail,
  MailPlus,
  Megaphone,
  Rocket,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  Code2,
  FileText,
  FolderGit2,
  GraduationCap,
  Home,
  LogOut,
  Layers,
  ListTodo,
  Menu,
  Settings,
  Shield,
  Users,
  X,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/hooks/use-auth";

const EXPAND_TRANSITION = { duration: 0.2, ease: [0.22, 0.61, 0.36, 1] } as const;

interface NavItem {
  href?: string;
  label: string;
  icon: LucideIcon;
  badge?: string;
  children?: NavItem[];
  roles?: string[];
}

const adminNavItems: NavItem[] = [
  {
    href: "/admin/dashboard",
    label: "Dashboard",
    icon: Home,
    roles: ["administrator", "content_admin", "instructor", "moderator"],
  },
  {
    label: "Content Management",
    icon: GraduationCap,
    roles: ["administrator", "content_admin"],
    children: [
      { href: "/admin/tracks", label: "Learning Tracks", icon: Layers },
      { href: "/admin/courses", label: "Courses", icon: BookOpen },
      { href: "/admin/chapters", label: "Chapters", icon: FolderGit2 },
      { href: "/admin/lessons", label: "Lessons", icon: FileText },
      { href: "/admin/exercises", label: "Exercises & Quizzes", icon: ListTodo },
      { href: "/admin/practicals", label: "Practicals", icon: Code2 },
      { href: "/admin/platform-updates", label: "Platform Updates", icon: History },
    ],
  },
  {
    label: "Events",
    icon: Rocket,
    roles: ["administrator", "content_admin", "instructor"],
    children: [
      { href: "/admin/competitions", label: "Hackathons", icon: Rocket },
      { href: "/admin/applications", label: "Applications", icon: ClipboardList },
      { href: "/admin/achievements", label: "Achievements", icon: Award },
      { href: "/admin/certificates", label: "Certificates", icon: FileText },
    ],
  },
  {
    label: "Email Studio",
    icon: Mail,
    roles: ["administrator", "content_admin", "instructor"],
    children: [
      { href: "/admin/email-studio", label: "Overview", icon: Home },
      { href: "/admin/email-templates", label: "Email Templates", icon: FileText },
      { href: "/admin/email-themes", label: "Theme Gallery", icon: Layers },
      { href: "/admin/email-automations", label: "Automation Rules", icon: Activity },
      { href: "/admin/email-campaigns", label: "Campaign Manager", icon: Mail },
      { href: "/admin/email-logs", label: "Delivery Logs", icon: History },
      { href: "/admin/email-settings", label: "Email Settings", icon: Settings },
    ],
  },
  {
    label: "Messaging",
    icon: Megaphone,
    roles: ["administrator", "content_admin", "instructor"],
    children: [
      { href: "/admin/send-email", label: "Send Official Email", icon: MailPlus },
      { href: "/admin/announcements", label: "Announcements", icon: Megaphone },
      { href: "/admin/notifications", label: "Notifications", icon: Activity },
    ],
  },
  {
    label: "People",
    icon: Users,
    roles: ["administrator", "content_admin", "instructor"],
    children: [
      { href: "/admin/students", label: "Students", icon: Users },
      { href: "/admin/instructors", label: "Instructors", icon: Award },
      { href: "/admin/enrollments", label: "Enrollments", icon: Activity },
      { href: "/admin/roles", label: "Roles & Permissions", icon: Shield },
    ],
  },
  {
    label: "System",
    icon: Settings,
    roles: ["administrator"],
    children: [
      { href: "/admin/audit-logs", label: "Audit Logs", icon: Activity },
      { href: "/admin/settings", label: "Platform Settings", icon: Settings },
    ],
  },
];

function routeIsActive(href: string, pathname: string) {
  const [base] = href.split("?");
  if (!base) return false;
  return pathname === base || pathname.startsWith(`${base}/`);
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
        href={item.href!}
        onClick={onNavigate}
        aria-current={active ? "page" : undefined}
        className={cn(
          "group relative flex min-h-10 items-center gap-3 rounded-lg px-3 text-sm font-medium transition-colors duration-150",
          "before:absolute before:inset-y-2 before:left-0 before:w-0.5 before:rounded-r-full before:transition-colors",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--sidebar-accent)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--sidebar-bg)]",
          active
            ? "bg-[var(--sidebar-active-bg)] text-[var(--sidebar-accent-strong)] before:bg-[var(--sidebar-accent)]"
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
        {item.href ? (
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
              ? "bg-[var(--sidebar-active-bg)] text-[var(--sidebar-accent-strong)] before:bg-[var(--sidebar-accent)]"
              : "text-[var(--sidebar-text)] hover:bg-[var(--sidebar-hover-bg)] hover:text-[var(--sidebar-accent-strong)] before:bg-transparent"
          )}
        >
          <Icon
            aria-hidden="true"
            className={cn(
              "h-5 w-5 shrink-0 stroke-[1.7] transition-colors",
              active ? "text-[var(--sidebar-accent)]" : "text-[var(--sidebar-icon)] group-hover:text-[var(--sidebar-accent-strong)]"
            )}
          />
          <span className="min-w-0 truncate">{item.label}</span>
        </Link>
        ) : (
        <div
          style={{
            paddingLeft: `${indent}px`,
            paddingRight: hasChildren ? "2.5rem" : undefined,
          }}
          className={cn(
            "group relative flex min-h-10 items-center gap-3 rounded-lg text-sm font-medium text-[var(--sidebar-text)]"
          )}
        >
          <Icon aria-hidden="true" className="h-5 w-5 shrink-0 stroke-[1.7] text-[var(--sidebar-icon)]" />
          <span className="min-w-0 truncate">{item.label}</span>
        </div>
        )}
        {hasChildren && (
          <button
            type="button"
            onClick={onToggle}
            aria-label={`${expanded ? "Collapse" : "Expand"} ${item.label}`}
            aria-expanded={expanded}
            className={cn(
              "absolute right-1 top-1/2 flex h-7 w-7 -translate-y-1/2 items-center justify-center rounded-md transition-colors hover:bg-[var(--sidebar-hover-bg)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--sidebar-accent)]",
              activeDescendant
                ? "text-[var(--sidebar-accent)] hover:text-[var(--sidebar-accent-strong)]"
                : "text-[var(--sidebar-icon)] hover:text-[var(--sidebar-accent-strong)]"
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

function ExpandableNavItem({
  item,
  active,
  depth,
  pathname,
  onNavigate,
}: {
  item: NavItem;
  active: boolean;
  depth: number;
  pathname: string;
  onNavigate: () => void;
}) {
  const [expanded, setExpanded] = useState(false);
  const childActive = (item.children || []).some((child) =>
    routeIsActive(child.href!, pathname)
  );
  const activeDescendant = childActive && !expanded;

  return (
    <TreeRow
      item={item}
      active={active}
      depth={depth}
      hasChildren
      expanded={expanded}
      onToggle={() => setExpanded(!expanded)}
      activeDescendant={activeDescendant}
      onNavigate={onNavigate}
    >
      {item.children!.map((child) => (
        <SidebarLink
          key={child.href}
          item={child}
          active={routeIsActive(child.href!, pathname)}
          onNavigate={onNavigate}
        />
      ))}
    </TreeRow>
  );
}

function RenderNavItems({
  items,
  depth = 0,
  pathname,
  onNavigate,
}: {
  items: NavItem[];
  depth?: number;
  pathname: string;
  onNavigate: () => void;
}) {
  const { user, profile } = useAuth();
  // `AuthUser.role` is the canonical effective role (`administrator`);
  // profile.role is the storage value (`admin`) and is kept only as a
  // fallback for older session payloads.
  const userRole = user?.role || (
    profile?.role === "admin" ? "administrator" :
    profile?.role === "mentor" ? "instructor" :
    profile?.role || "student"
  );

  const filteredItems = items.filter((item) => {
    if (!item.roles) return true;
    return item.roles.includes(userRole);
  });

  return (
    <ul className="space-y-0.5">
      {filteredItems.map((item) => {
        const active = item.href ? routeIsActive(item.href, pathname) : false;
        const hasChildren = Boolean(item.children && item.children.length > 0);

        if (hasChildren) {
          return (
            <ExpandableNavItem
              key={item.label}
              item={item}
              active={active}
              depth={depth}
              pathname={pathname}
              onNavigate={onNavigate}
            />
          );
        }

        return (
          <SidebarLink
            key={item.href}
            item={item}
            active={active}
            onNavigate={onNavigate}
          />
        );
      })}
    </ul>
  );
}

function SidebarPanel({
  pathname,
  onNavigate,
  onSignOut,
  onCollapse,
}: {
  pathname: string;
  onNavigate: () => void;
  onSignOut: () => void;
  onCollapse?: () => void;
}) {
  const { user, profile, signOut } = useAuth();
  const displayName = user?.first_name || user?.username || "Admin";
  const userRole = user?.role || (
    profile?.role === "admin" ? "administrator" :
    profile?.role === "mentor" ? "instructor" :
    profile?.role || "student"
  );

  const handleSignOut = async () => {
    await signOut();
    onSignOut();
  };

  return (
    <div className="flex h-full min-h-0 flex-col border-r border-[var(--sidebar-border)] bg-[var(--sidebar-bg)] text-[var(--sidebar-text)]">
      <div className="flex h-14 shrink-0 items-center gap-2.5 border-b border-[var(--sidebar-border)] px-4">
        <div className="relative h-6 w-6 shrink-0">
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            className="h-6 w-6 text-[var(--sidebar-accent-strong)]"
            aria-hidden="true"
          >
            <path d="M12 2L2 7l10 5 10-5-10-5z" />
            <path d="M2 17l10 5 10-5" />
            <path d="M2 12l10 5 10-5" />
          </svg>
        </div>
        <span className="text-sm font-bold tracking-tight">Code Yaar Admin</span>
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
        aria-label="Admin navigation"
        className="min-h-0 flex-1 overflow-y-auto px-3 py-2 [scrollbar-width:thin] [&::-webkit-scrollbar-track]:bg-transparent"
      >
        <RenderNavItems
          items={adminNavItems}
          pathname={pathname}
          onNavigate={onNavigate}
        />
      </nav>

      <div className="shrink-0 border-t border-[var(--sidebar-border)] p-3">
        <div className="flex items-center gap-3 rounded-lg p-2 text-[var(--sidebar-text)] transition-colors hover:bg-[var(--sidebar-hover-bg)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--sidebar-accent)]">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/20 text-primary font-medium text-sm">
            {(displayName || "A").charAt(0).toUpperCase()}
          </div>
          <span className="min-w-0">
            <span className="block truncate text-xs font-semibold">{displayName}</span>
            <span className="block text-[11px] text-[var(--sidebar-muted)]">{userRole}</span>
          </span>
        </div>

        <button
          type="button"
          onClick={handleSignOut}
          className="mt-1 flex min-h-10 w-full items-center gap-3 rounded-lg px-2 text-sm font-medium text-destructive transition-colors hover:bg-destructive/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-destructive/30"
        >
          <LogOut aria-hidden="true" className="h-5 w-5 stroke-[1.7]" />
          <span>Sign out</span>
        </button>
        <Link
          href="/dashboard"
          onClick={onNavigate}
          className="mt-1 flex min-h-10 w-full items-center gap-3 rounded-lg px-2 text-sm font-medium text-[var(--sidebar-text)] transition-colors hover:bg-[var(--sidebar-hover-bg)] hover:text-[var(--sidebar-accent-strong)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--sidebar-accent)]"
        >
          <Home aria-hidden="true" className="h-5 w-5 stroke-[1.7]" />
          <span>User experience</span>
        </Link>
      </div>
    </div>
  );
}

export function AdminSidebar({
  collapsed,
  onToggle,
}: {
  collapsed: boolean;
  onToggle: (collapsed: boolean) => void;
}) {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);

  const closeMobile = () => setMobileOpen(false);

  return (
    <>
      {collapsed ? (
        <div className="fixed left-0 top-1/2 z-40 hidden -translate-y-1/2 md:block">
          <button
            type="button"
            onClick={() => onToggle(false)}
            aria-label="Open navigation"
            className="flex h-16 w-6 items-center justify-center rounded-r-lg border border-l-0 border-[var(--sidebar-border)] bg-[var(--sidebar-bg)] text-[var(--sidebar-text)] shadow-sm transition-colors hover:bg-[var(--sidebar-hover-bg)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--sidebar-accent)]"
          >
            <ChevronRight aria-hidden="true" className="h-4 w-4" />
          </button>
        </div>
      ) : (
        <aside className="fixed inset-y-0 left-0 z-40 hidden w-[280px] md:flex">
          <SidebarPanel
            pathname={pathname}
            onNavigate={closeMobile}
            onSignOut={closeMobile}
            onCollapse={() => onToggle(true)}
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
        <span className="ml-2 text-sm font-semibold text-foreground">Code Yaar Admin</span>
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
              className="fixed inset-y-0 left-0 z-50 w-[min(86vw,280px)] shadow-2xl md:hidden"
              aria-label="Mobile navigation"
            >
              <button
                type="button"
                aria-label="Close navigation"
                onClick={closeMobile}
                className="absolute right-3 top-3 z-10 flex h-8 w-8 items-center justify-center rounded-lg text-[var(--sidebar-icon)] transition-colors hover:bg-[var(--sidebar-hover-bg)] hover:text-[var(--sidebar-accent-strong)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--sidebar-accent)]"
              >
                <X aria-hidden="true" className="h-4 w-4" />
              </button>
              <SidebarPanel
                pathname={pathname}
                onNavigate={closeMobile}
                onSignOut={closeMobile}
              />
            </motion.aside>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
