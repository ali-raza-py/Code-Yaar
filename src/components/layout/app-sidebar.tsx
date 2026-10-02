"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Home,
  BookOpen,
  Trophy,
  FolderGit2,
  Medal,
  User,
  Settings,
  LogOut,
  Menu,
  X,
  ChevronDown,
  ChevronRight,
  Layers,
  Target,
  Lightbulb,
  Dumbbell,
  ClipboardCheck,
  Sparkles,
  Code2,
  Swords,
  Rocket,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/hooks/use-auth";
import Image from "next/image";

const MotionLink = motion.create(Link);

interface NavItem {
  href: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: string;
}

interface NavGroup {
  title: string;
  items: NavItem[];
}

const navGroups: NavGroup[] = [
  {
    title: "LEARN",
    items: [
      { href: "/learn", label: "Tracks", icon: Layers },
      { href: "/learn", label: "Courses", icon: Lightbulb },
      { href: "/challenges", label: "Practice", icon: Dumbbell },
      { href: "/challenges", label: "Assessments", icon: ClipboardCheck },
    ],
  },
  {
    title: "APPLY",
    items: [
      { href: "/projects", label: "Real World Projects", icon: FolderGit2 },
      { href: "/projects", label: "Sandbox", icon: Code2 },
      { href: "/challenges", label: "Competitions", icon: Swords },
    ],
  },
];

const bottomItems: NavItem[] = [
  { href: "/dashboard", label: "Dashboard", icon: Home },
  { href: "/leaderboard", label: "Leaderboard", icon: Medal, badge: "NEW" },
  { href: "/profile", label: "Profile", icon: User },
  { href: "/settings", label: "Settings", icon: Settings },
];

export function AppSidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, signOut } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>({
    LEARN: true,
    APPLY: true,
  });

  const handleSignOut = async () => {
    await signOut();
    router.push("/");
  };

  const toggleGroup = (title: string) => {
    setExpandedGroups((prev) => ({ ...prev, [title]: !prev[title] }));
  };

  const NavContent = (
    <div className="flex h-full flex-col bg-[#0a1628] text-white">
      {/* Logo */}
      <div className="flex h-14 items-center gap-2.5 border-b border-white/10 px-4">
        <div className="relative h-6 w-6 shrink-0">
          <Image
            src="/logo-light.png"
            alt=""
            fill
            className="object-contain"
            priority
          />
        </div>
        <span className="text-sm font-bold tracking-tight">Code-Yaar</span>
      </div>

      {/* Navigation Groups */}
      <nav className="flex-1 overflow-y-auto px-2 py-3">
        {navGroups.map((group) => {
          const isExpanded = expandedGroups[group.title];
          return (
            <div key={group.title} className="mb-2">
              <button
                onClick={() => toggleGroup(group.title)}
                className="flex w-full items-center justify-between px-3 py-2 text-xs font-bold uppercase tracking-wider text-white/40 hover:text-white/60"
              >
                {group.title}
                {isExpanded ? (
                  <ChevronDown className="h-3.5 w-3.5" />
                ) : (
                  <ChevronRight className="h-3.5 w-3.5" />
                )}
              </button>
              <AnimatePresence>
                {isExpanded && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                    className="overflow-hidden"
                  >
                    {group.items.map((item) => {
                      const isActive = pathname === item.href;
                      return (
                        <Link
                          key={item.href + item.label}
                          href={item.href}
                          onClick={() => setMobileOpen(false)}
                          className={cn(
                            "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                            isActive
                              ? "bg-white/10 text-white"
                              : "text-white/60 hover:bg-white/5 hover:text-white"
                          )}
                        >
                          <item.icon className="h-4 w-4 shrink-0" />
                          <span>{item.label}</span>
                          {item.badge && (
                            <span className="ml-auto rounded bg-[#2dbe52] px-1.5 py-0.5 text-[10px] font-bold text-white">
                              {item.badge}
                            </span>
                          )}
                        </Link>
                      );
                    })}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          );
        })}

        {/* Bottom items */}
        <div className="mt-4 space-y-1 border-t border-white/10 pt-3">
          {bottomItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setMobileOpen(false)}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-white/10 text-white"
                    : "text-white/60 hover:bg-white/5 hover:text-white"
                )}
              >
                <item.icon className="h-4 w-4 shrink-0" />
                <span>{item.label}</span>
                {item.badge && (
                  <span className="ml-auto rounded bg-[#2dbe52] px-1.5 py-0.5 text-[10px] font-bold text-white">
                    {item.badge}
                  </span>
                )}
              </Link>
            );
          })}
        </div>
      </nav>

      {/* Getting Started */}
      <div className="border-t border-white/10 p-3">
        <div className="rounded-lg bg-[#7c3aed] px-3 py-2.5 text-center text-sm font-bold">
          Getting Started (0/4)
        </div>
      </div>

      {/* Logout */}
      <div className="border-t border-white/10 p-2">
        <button
          onClick={handleSignOut}
          className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-white/50 transition-colors hover:bg-white/5 hover:text-white"
        >
          <LogOut className="h-4 w-4" />
          <span>Sign Out</span>
        </button>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop sidebar */}
      <aside className="hidden lg:flex lg:flex-col lg:fixed lg:inset-y-0 lg:left-0 lg:z-40 lg:w-60">
        {NavContent}
      </aside>

      {/* Mobile header */}
      <div className="lg:hidden fixed top-0 left-0 right-0 z-50 flex h-14 items-center justify-between border-b border-[var(--color-section-border)] bg-white px-4">
        <button
          onClick={() => setMobileOpen(true)}
          className="flex items-center gap-2"
          aria-label="Open navigation"
        >
          <Menu className="h-5 w-5" />
          <div className="relative h-6 w-6">
            <Image
              src="/logo-light.png"
              alt=""
              fill
              className="object-contain"
            />
          </div>
        </button>
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-muted-foreground">Code-Yaar</span>
        </div>
      </div>

      {/* Mobile overlay */}
      <AnimatePresence>
        {mobileOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 z-50 bg-black/50 lg:hidden"
              onClick={() => setMobileOpen(false)}
            />
            <motion.aside
              initial={{ x: -280 }}
              animate={{ x: 0 }}
              exit={{ x: -280 }}
              transition={{ type: "spring", stiffness: 300, damping: 30 }}
              className="fixed inset-y-0 left-0 z-50 w-64 shadow-xl lg:hidden"
            >
              <div className="absolute right-2 top-3 z-10">
                <button
                  onClick={() => setMobileOpen(false)}
                  className="flex h-8 w-8 items-center justify-center rounded-full text-white/60 hover:text-white"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
              {NavContent}
            </motion.aside>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
