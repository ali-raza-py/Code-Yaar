"use client";

import Link from "next/link";
import Image from "next/image";

const footerLinks = [
  {
    title: "Platform",
    links: [
      { label: "Learn", href: "/learn" },
      { label: "Projects", href: "/projects" },
      { label: "Challenges", href: "/challenges" },
      { label: "Leaderboard", href: "/leaderboard" },
      { label: "Dashboard", href: "/dashboard" },
    ],
  },
  {
    title: "Resources",
    links: [
      { label: "Documentation", href: "/learn" },
      { label: "Blog", href: "/learn" },
      { label: "Community", href: "/leaderboard" },
      { label: "FAQ", href: "/about#faq" },
    ],
  },
  {
    title: "Company",
    links: [
      { label: "About", href: "/about" },
      { label: "Careers", href: "/about#careers" },
      { label: "Contact", href: "/about#contact" },
      { label: "Privacy Policy", href: "/about#privacy" },
      { label: "Terms of Service", href: "/about#terms" },
    ],
  },
];

export function Footer() {
  return (
    <footer className="border-t border-[var(--color-section-border)] bg-white">
      <div className="mx-auto max-w-6xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 gap-8 md:grid-cols-5">
          {/* Brand */}
          <div className="col-span-2">
            <Link
              href="/"
              className="inline-flex items-center gap-2"
              aria-label="Code-Yaar Home"
            >
              <div className="relative h-6 w-6">
                <Image
                  src="/logo-light.png"
                  alt="Code-Yaar"
                  fill
                  className="object-contain"
                />
              </div>
              <span className="text-sm font-bold tracking-tight">Code-Yaar</span>
            </Link>
            <p className="mt-3 max-w-xs text-sm leading-relaxed text-muted-foreground">
              Learn to code, build real projects, and prove your skills.
              The engineering path from concept to proof.
            </p>

            {/* Social links */}
            <div className="mt-4 flex gap-3">
              {[
                ["Twitter", "https://x.com"],
                ["GitHub", "https://github.com"],
                ["LinkedIn", "https://linkedin.com"],
                ["YouTube", "https://youtube.com"],
              ].map(([social, href]) => (
                <a
                  key={social}
                  href={href}
                  target="_blank"
                  rel="noreferrer"
                  className="flex h-8 w-8 items-center justify-center rounded-full bg-[var(--color-section-light)] text-xs font-medium text-muted-foreground transition-colors hover:bg-foreground hover:text-white"
                  aria-label={social}
                >
                  {social[0]}
                </a>
              ))}
            </div>
          </div>

          {/* Link columns */}
          {footerLinks.map((group) => (
            <div key={group.title}>
              <h3 className="text-xs font-semibold uppercase tracking-wider text-foreground">
                {group.title}
              </h3>
              <ul className="mt-3 space-y-2">
                {group.links.map((link) => (
                  <li key={link.label}>
                    <Link
                      href={link.href}
                      className="text-sm text-muted-foreground transition-colors hover:text-foreground"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom */}
        <div className="mt-10 flex flex-col items-center justify-between gap-3 border-t border-[var(--color-section-border)] pt-6 sm:flex-row">
          <p className="text-xs text-muted-foreground/60">
            &copy; {new Date().getFullYear()} Code-Yaar. All rights reserved.
          </p>
          <p className="text-xs text-muted-foreground/40">
            Think. Build. Evolve.
          </p>
        </div>
      </div>
    </footer>
  );
}
