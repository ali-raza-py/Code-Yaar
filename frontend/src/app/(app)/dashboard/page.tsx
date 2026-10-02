import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRight, Zap, Trophy, Sparkles } from "lucide-react";

export const metadata: Metadata = {
  title: "Dashboard",
  description: "Your learning dashboard. Track your progress and continue building.",
};

export default function DashboardPage() {
  return (
    <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
      {/* Top bar */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">My Activity</h1>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-sm font-medium text-muted-foreground">
            Premium &middot;{" "}
            <Link href="#" className="text-[#7c3aed] hover:underline">
              Upgrade
            </Link>
          </span>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* LEFT — Main content (2/3) */}
        <div className="lg:col-span-2 space-y-6">
          {/* Continue Learning card */}
          <div className="overflow-hidden rounded-xl bg-[#0f1d32] text-white">
            <div className="p-6 sm:p-8">
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <div className="text-xs font-semibold uppercase tracking-wider text-white/50">
                    Course
                  </div>
                  <h2 className="mt-1 text-2xl font-bold sm:text-3xl">
                    Working with the OpenAI API
                  </h2>
                  <p className="mt-2 text-sm text-white/60">
                    Part of the{" "}
                    <Link href="#" className="text-[#60a5fa] hover:underline">
                      Full Stack Developer
                    </Link>{" "}
                    track
                  </p>
                </div>
                <Link
                  href="/learn"
                  className="inline-flex items-center justify-center gap-2 rounded-lg bg-[#2dbe52] px-6 py-3 text-sm font-bold text-white transition-colors hover:bg-[#25a848] whitespace-nowrap"
                >
                  Continue Learning
                </Link>
              </div>
            </div>
          </div>

          {/* Sandbox / Practice section */}
          <div>
            <h2 className="mb-4 flex items-center gap-2 text-lg font-bold text-foreground">
              <Sparkles className="h-5 w-5 text-[#7c3aed]" />
              Sandbox
            </h2>
            <div className="rounded-xl border border-[var(--color-section-border)] bg-white p-6">
              <div className="flex flex-col gap-6 sm:flex-row sm:items-center">
                {/* Token circle */}
                <div className="flex h-28 w-28 shrink-0 items-center justify-center rounded-full border-4 border-[#facc15]">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-foreground">2,500</div>
                    <div className="text-xs text-muted-foreground">/2,500</div>
                  </div>
                </div>
                <div className="flex-1">
                  <h3 className="font-bold text-foreground">
                    You have 2500 unused tokens to practice your skills!
                  </h3>
                  <p className="mt-1 text-sm text-muted-foreground">
                    Step into Sandbox that provides a simple, low-risk environment for practicing
                    coding, web development, and system design without the complexity of setting up.
                  </p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {["Python", "React", "Node.js", "SQL"].map((tech) => (
                      <span
                        key={tech}
                        className="inline-flex items-center gap-1 rounded-lg border border-[var(--color-section-border)] bg-[var(--color-section-light)] px-3 py-1.5 text-sm font-medium text-foreground"
                      >
                        {tech}
                      </span>
                    ))}
                    <Link
                      href="/challenges"
                      className="inline-flex items-center gap-1 text-sm font-medium text-[#4f46e5] hover:underline"
                    >
                      View All <ArrowRight className="h-3.5 w-3.5" />
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Quick access grid */}
          <div className="grid gap-4 sm:grid-cols-2">
            <Link
              href="/learn"
              className="group rounded-xl border border-[var(--color-section-border)] bg-white p-5 transition-all hover:border-[var(--primary)] hover:shadow-md"
            >
              <h3 className="font-semibold text-foreground group-hover:text-[var(--primary)]">
                Courses
              </h3>
              <p className="mt-1 text-sm text-muted-foreground">
                Interactive courses combining short videos with hands-on exercises.
              </p>
              <div className="mt-3 text-sm font-medium text-[#4f46e5]">
                Browse courses <ArrowRight className="ml-1 inline h-3.5 w-3.5" />
              </div>
            </Link>
            <Link
              href="/projects"
              className="group rounded-xl border border-[var(--color-section-border)] bg-white p-5 transition-all hover:border-[var(--primary)] hover:shadow-md"
            >
              <h3 className="font-semibold text-foreground group-hover:text-[var(--primary)]">
                Real World Projects
              </h3>
              <p className="mt-1 text-sm text-muted-foreground">
                Engage with real-world challenges. Apply your knowledge to practical scenarios.
              </p>
              <div className="mt-3 text-sm font-medium text-[#4f46e5]">
                Browse projects <ArrowRight className="ml-1 inline h-3.5 w-3.5" />
              </div>
            </Link>
          </div>
        </div>

        {/* RIGHT — Sidebar (1/3) */}
        <div className="space-y-6">
          {/* Daily Streak + XP */}
          <div className="rounded-xl border border-[var(--color-section-border)] bg-white p-6">
            <div className="flex items-center gap-4">
              {/* Avatar */}
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-[#7c3aed] to-[#2dbe52] text-xl font-bold text-white">
                U
              </div>
              <div>
                <div className="text-lg font-bold text-foreground">User</div>
                <div className="mt-2">
                  <div className="text-xs text-muted-foreground">Daily Streak</div>
                  <div className="flex items-center gap-1.5">
                    <Zap className="h-4 w-4 text-[#f59e0b]" />
                    <span className="text-lg font-bold text-foreground">0 days</span>
                  </div>
                </div>
                <div className="mt-2">
                  <div className="text-xs text-muted-foreground">Total XP</div>
                  <div className="text-lg font-bold text-foreground">0 XP</div>
                </div>
              </div>
            </div>
          </div>

          {/* Leaderboard */}
          <div className="rounded-xl border border-[var(--color-section-border)] bg-white p-6">
            <div className="flex items-center justify-between">
              <h3 className="flex items-center gap-2 font-bold text-foreground">
                <Trophy className="h-5 w-5 text-[#f59e0b]" />
                Leaderboard
              </h3>
              <span className="rounded-full bg-blue-50 px-2.5 py-0.5 text-xs font-semibold text-blue-600">
                9 HOURS LEFT TO JOIN
              </span>
            </div>
            <div className="mt-4 flex flex-col items-center text-center">
              <div className="flex h-20 w-20 items-center justify-center rounded-2xl bg-[#f5f0e0]">
                <Trophy className="h-10 w-10 text-[#c9a84c]" />
              </div>
              <p className="mt-3 text-sm font-medium text-foreground">
                Gain 250XP to enter this week&apos;s leaderboard
              </p>
              <Link
                href="/challenges"
                className="mt-3 text-sm font-medium text-[#4f46e5] hover:underline"
              >
                Start a challenge <ArrowRight className="ml-1 inline h-3.5 w-3.5" />
              </Link>
            </div>
          </div>

          {/* Getting Started */}
          <div className="rounded-xl bg-[#7c3aed] p-6 text-white">
            <h3 className="font-bold">Getting Started (0/4)</h3>
            <div className="mt-3 space-y-2">
              {[
                "Complete your profile",
                "Start your first course",
                "Solve a challenge",
                "Build a project",
              ].map((task, i) => (
                <div key={task} className="flex items-center gap-2 text-sm text-white/80">
                  <div className="flex h-5 w-5 items-center justify-center rounded-full border border-white/30 text-xs">
                    {i + 1}
                  </div>
                  {task}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
