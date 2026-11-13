"use client";

import Link from "next/link";
import Image from "next/image";

const footerLinks = [
  {
    title: "Platform",
    links: [
      { label: "Courses", href: "/courses" },
      { label: "Learning Tracks", href: "/tracks" },
      { label: "Challenges", href: "/challenges" },
      { label: "Hackathons", href: "/competitions" },
      { label: "Announcements", href: "/announcements" },
      { label: "Updates", href: "/updates" },
      { label: "Leaderboard", href: "/leaderboard" },
      { label: "Dashboard", href: "/dashboard" },
    ],
  },
  {
    title: "Credentials",
    links: [
      { label: "Verify a certificate", href: "/verify/certificate/" },
      { label: "Verify a badge", href: "/verify/badge/" },
      { label: "Certificates", href: "/certificates" },
      { label: "Achievements", href: "/achievements" },
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
    <footer className="border-t border-border bg-background">
      <div className="mx-auto max-w-6xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 gap-8 md:grid-cols-5">
          {/* Brand */}
          <div className="col-span-2">
            <Link
              href="/"
              className="inline-flex items-center gap-2.5 rounded-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background"
              aria-label="Code Yaar Home"
            >
              <div className="relative h-6 w-6">
                <Image
                  src="/brand/logo-mark.png"
                  alt="Code Yaar"
                  fill
                  sizes="24px"
                  className="object-contain"
                />
              </div>
              <span className="text-sm font-semibold tracking-tight text-foreground">Code Yaar</span>
            </Link>
            <p className="mt-3 max-w-xs text-sm leading-relaxed text-muted-foreground">
              Learn to code, build real projects, and prove your skills.
              The engineering path from concept to proof.
            </p>

            {/* Social links */}
            <div className="mt-4 flex gap-2.5">
              {[
                ["X", "https://x.com"],
                ["GitHub", "https://github.com"],
                ["LinkedIn", "https://linkedin.com"],
                ["YouTube", "https://youtube.com"],
              ].map(([social, href]) => (
                <a
                  key={social}
                  href={href}
                  target="_blank"
                  rel="noreferrer"
                  className="flex h-9 w-9 items-center justify-center rounded-full border border-border bg-secondary text-xs font-medium text-muted-foreground transition-colors duration-200 hover:border-primary/30 hover:bg-primary hover:text-primary-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
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
                      className="text-sm text-muted-foreground transition-colors duration-200 hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded-sm"
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
        <div className="mt-10 flex flex-col items-center justify-between gap-3 border-t border-border pt-6 sm:flex-row">
          <p className="text-xs text-muted-foreground">
            &copy; {new Date().getFullYear()} Code Yaar. All rights reserved.
          </p>
          <p className="text-xs text-muted-foreground/70">
            Think. Build. Evolve.
          </p>
        </div>
      </div>
    </footer>
  );
}
