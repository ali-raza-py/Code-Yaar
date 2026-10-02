"use client";

import Link from "next/link";
import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Menu, X } from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/hooks/use-auth";
import Image from "next/image";

const MotionLink = motion.create(Link);

const navItems = [
  { href: "/learn", label: "Learn" },
  { href: "/projects", label: "Projects" },
  { href: "/challenges", label: "Challenges" },
  { href: "/leaderboard", label: "Leaderboard" },
];

export function PublicHeader() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const { user } = useAuth();

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    setMobileOpen(false);
  }, []);

  return (
    <header
      className={cn(
        "sticky top-0 z-50 w-full transition-all duration-300",
        scrolled
          ? "border-b border-[var(--color-section-border)] bg-white/95 backdrop-blur-sm shadow-sm"
          : "bg-white"
      )}
    >
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Logo */}
        <Link
          href="/"
          className="flex items-center gap-2"
          aria-label="Code-Yaar Home"
        >
          <div className="relative h-7 w-7">
            <Image
              src="/logo-light.png"
              alt=""
              fill
              className="object-contain"
              priority
            />
          </div>
          <span className="text-[15px] font-bold tracking-tight text-foreground">
            Code-Yaar
          </span>
        </Link>

        {/* Desktop Nav */}
        <nav className="hidden md:block">
          <div className="flex items-center gap-1">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="rounded-md px-3.5 py-2 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground hover:bg-secondary/50"
              >
                {item.label}
              </Link>
            ))}
          </div>
        </nav>

        {/* Right actions */}
        <div className="flex items-center gap-2">
          <button
            className="h-9 w-9 md:hidden flex items-center justify-center"
            onClick={() => setMobileOpen(!mobileOpen)}
            aria-label="Toggle menu"
          >
            <AnimatePresence mode="wait" initial={false}>
              {mobileOpen ? (
                <motion.div
                  key="close"
                  initial={{ rotate: -90, opacity: 0 }}
                  animate={{ rotate: 0, opacity: 1 }}
                  exit={{ rotate: 90, opacity: 0 }}
                  transition={{ duration: 0.15 }}
                >
                  <X className="h-4 w-4" />
                </motion.div>
              ) : (
                <motion.div
                  key="menu"
                  initial={{ rotate: 90, opacity: 0 }}
                  animate={{ rotate: 0, opacity: 1 }}
                  exit={{ rotate: -90, opacity: 0 }}
                  transition={{ duration: 0.15 }}
                >
                  <Menu className="h-4 w-4" />
                </motion.div>
              )}
            </AnimatePresence>
          </button>

          <div className="hidden items-center gap-2 md:flex">
            {user ? (
              <Link href="/dashboard" className="rounded-lg bg-foreground px-4 py-2 text-sm font-medium text-white transition-colors hover:opacity-90">
                Dashboard
              </Link>
            ) : (
              <>
                <Link href="/sign-in" className="rounded-md px-3.5 py-2 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground">
                  Sign in
                </Link>
                <Link href="/sign-up" className="dc-btn-primary !py-2 !px-4 !text-sm">
                  Get started
                </Link>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Mobile Nav */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.25, ease: [0.25, 0.1, 0.25, 1] }}
            className="overflow-hidden border-t border-[var(--color-section-border)] md:hidden"
          >
            <nav className="flex flex-col gap-1 px-4 py-4">
              {navItems.map((item, i) => (
                <MotionLink
                  key={item.href}
                  href={item.href}
                  initial={{ opacity: 0, x: -12 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.05, duration: 0.2 }}
                  className="rounded-lg px-3 py-2.5 text-sm font-medium text-muted-foreground transition-colors hover:bg-secondary/50 hover:text-foreground"
                >
                  {item.label}
                </MotionLink>
              ))}
              <div className="mt-3 flex flex-col gap-2 border-t border-[var(--color-section-border)] pt-3">
                {user ? (
                  <Link href="/dashboard" className="dc-btn-primary w-full justify-center">
                    Dashboard
                  </Link>
                ) : (
                  <>
                    <Link href="/sign-in" className="dc-btn-outline w-full justify-center">
                      Sign in
                    </Link>
                    <Link href="/sign-up" className="dc-btn-primary w-full justify-center">
                      Get started
                    </Link>
                  </>
                )}
              </div>
            </nav>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}
