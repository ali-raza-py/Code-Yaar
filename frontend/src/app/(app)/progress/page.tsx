"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import {
  ArrowUpRight, Award, BookOpen, ChevronRight, Code2, Flame, GitBranch,
  Layers3, LockKeyhole, Sparkles, Target, Trophy, Zap,
} from "lucide-react";
import { ProgressBar } from "@/components/progress/progress-bar";
import { useAuth } from "@/hooks/use-auth";
import { NetworkError } from "@/components/learning/workspace/error-states";
import {
  profileStats,
  progressDashboard,
  type ProfileStatsData,
  type ProgressDashboardData,
} from "@/lib/api";

const XP_PER_LEVEL = 500;

function clamp(value: number) {
  return Math.min(100, Math.max(0, value));
}

function formatTime(seconds: number) {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  return hours ? `${hours}h ${minutes}m` : `${minutes}m`;
}

function formatDate(value: string) {
  return new Date(value).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function createDemoProgress(progress: ProgressDashboardData): ProgressDashboardData {
  const today = new Date();
  const contributionData = Array.from({ length: 365 }, (_, index) => {
    const date = new Date(today);
    date.setDate(today.getDate() - (364 - index));
    const total = index % 17 === 0 ? 0 : (index % 5) + (index % 3 === 0 ? 2 : 0);
    return {
      date: date.toISOString().slice(0, 10),
      lessons_completed: Math.ceil(total * 0.55),
      practicals_completed: Math.floor(total * 0.2),
      quizzes_completed: total - Math.ceil(total * 0.55) - Math.floor(total * 0.2),
      total_activities: total,
      intensity: Math.min(4, Math.ceil(total / 2)) as 0 | 1 | 2 | 3 | 4,
    };
  });
  const weeklyActivity = contributionData.slice(-7).map((day) => ({
    date: day.date,
    count: day.total_activities,
  }));
  const demoDate = (daysAgo: number) => {
    const date = new Date(today);
    date.setDate(today.getDate() - daysAgo);
    return date.toISOString();
  };

  return {
    ...progress,
    overview: {
      ...progress.overview,
      overall_percentage: 68,
      total_courses: 4,
      completed_courses: 1,
      in_progress_courses: 3,
      lessons_completed: 84,
      lessons_total: 124,
      practicals_completed: 19,
      practicals_total: 28,
      quizzes_attempted: 32,
      average_quiz_score: 86,
      highest_quiz_score: 100,
      learning_time_seconds: 327600,
      current_streak: 12,
      longest_streak: 27,
    },
    courses: [
      { id: 1, slug: "python-foundations", title: "Python Foundations", status: "active", total_lessons: 32, completed_lessons: 29, remaining_lessons: 3, total_practicals: 8, completed_practicals: 6, progress_percentage: 82, last_accessed_at: demoDate(0) },
      { id: 2, slug: "javascript-essentials", title: "JavaScript Essentials", status: "active", total_lessons: 40, completed_lessons: 27, remaining_lessons: 13, total_practicals: 10, completed_practicals: 6, progress_percentage: 63, last_accessed_at: demoDate(2) },
      { id: 3, slug: "react-development", title: "React Development", status: "active", total_lessons: 28, completed_lessons: 17, remaining_lessons: 11, total_practicals: 6, completed_practicals: 3, progress_percentage: 54, last_accessed_at: demoDate(4) },
      { id: 4, slug: "git-and-github", title: "Git & GitHub", status: "completed", total_lessons: 24, completed_lessons: 24, remaining_lessons: 0, total_practicals: 4, completed_practicals: 4, progress_percentage: 100, last_accessed_at: demoDate(18) },
    ],
    weekly_activity: weeklyActivity,
    contribution_data: contributionData,
    active_dates: contributionData.filter((day) => day.total_activities > 0).map((day) => day.date),
    total_learning_activities: 248,
    active_learning_days: contributionData.filter((day) => day.total_activities > 0).length,
    activities: [
      { id: 1, type: "lesson_completed", title: "Completed async programming lesson", status: "completed", associated_title: "JavaScript Essentials", date: demoDate(0), activity_date: demoDate(0).slice(0, 10) },
      { id: 2, type: "practical_completed", title: "Finished a data parsing practical", status: "completed", associated_title: "Python Foundations", date: demoDate(1), activity_date: demoDate(1).slice(0, 10) },
      { id: 3, type: "quiz_attempted", title: "Scored 92% on the React quiz", status: "completed", associated_title: "React Development", date: demoDate(2), activity_date: demoDate(2).slice(0, 10) },
      { id: 4, type: "lesson_completed", title: "Learned component composition", status: "completed", associated_title: "React Development", date: demoDate(4), activity_date: demoDate(4).slice(0, 10) },
    ],
  };
}

function createDemoStats(stats: ProfileStatsData): ProfileStatsData {
  return {
    ...stats,
    profile: { ...stats.profile, xp_points: 4250, streak_days: 12, longest_streak: 27, level: 8 },
    stats: { ...stats.stats, total_enrollments: 4, active_enrollments: 3, completed_courses: 1, total_attempts: 32, correct_attempts: 28, unique_exercises_solved: 76, lessons_completed: 84, lessons_in_progress: 23, achievements_earned: 6, total_achievements: 10 },
    skills: [
      { id: 1, name: "Python", category: "Programming", proficiency: 86, icon: "python" },
      { id: 2, name: "JavaScript", category: "Programming", proficiency: 74, icon: "javascript" },
      { id: 3, name: "React", category: "Frontend", proficiency: 68, icon: "react" },
      { id: 4, name: "TypeScript", category: "Programming", proficiency: 61, icon: "typescript" },
      { id: 5, name: "Problem Solving", category: "Core", proficiency: 79, icon: "target" },
    ],
    achievements: [
      { id: 1, slug: "first-steps", title: "First Steps", description: "Complete your first lesson.", icon: "sparkles", category: "learning", category_label: "Learning", difficulty: "easy", difficulty_label: "Easy", how_to_earn: "Complete one lesson.", level_label: "Beginner", xp_bonus: 50, earned: true, earned_at: new Date().toISOString(), public_id: null, credential_id: null, recipient_name: null, verification_url: null, status: "earned", progress: { current: 1, target: 1, complete: true } },
      { id: 2, slug: "consistent-learner", title: "Consistent Learner", description: "Maintain a seven-day learning streak.", icon: "flame", category: "streak", category_label: "Streak", difficulty: "medium", difficulty_label: "Medium", how_to_earn: "Learn for seven consecutive days.", level_label: "Intermediate", xp_bonus: 150, earned: true, earned_at: new Date().toISOString(), public_id: null, credential_id: null, recipient_name: null, verification_url: null, status: "earned", progress: { current: 7, target: 7, complete: true } },
      { id: 3, slug: "quiz-master", title: "Quiz Master", description: "Answer 25 quiz questions correctly.", icon: "trophy", category: "assessment", category_label: "Assessment", difficulty: "medium", difficulty_label: "Medium", how_to_earn: "Answer 25 questions correctly.", level_label: "Intermediate", xp_bonus: 200, earned: true, earned_at: new Date().toISOString(), public_id: null, credential_id: null, recipient_name: null, verification_url: null, status: "earned", progress: { current: 25, target: 25, complete: true } },
      { id: 4, slug: "course-finisher", title: "Course Finisher", description: "Complete your first course.", icon: "award", category: "courses", category_label: "Courses", difficulty: "hard", difficulty_label: "Hard", how_to_earn: "Complete one course.", level_label: "Advanced", xp_bonus: 300, earned: true, earned_at: new Date().toISOString(), public_id: null, credential_id: null, recipient_name: null, verification_url: null, status: "earned", progress: { current: 1, target: 1, complete: true } },
    ],
    next_badge: { slug: "streak-champion", title: "Streak Champion", description: "Build a 30-day learning streak.", how_to_earn: "Learn for 30 consecutive days.", difficulty: "hard", difficulty_label: "Hard", progress: { current: 12, target: 30 } },
  };
}

function Panel({
  title,
  subtitle,
  children,
  action,
  className = "",
}: {
  title: string;
  subtitle?: string;
  children: ReactNode;
  action?: ReactNode;
  className?: string;
}) {
  return (
    <section className={`rounded-2xl border border-border bg-card p-5 shadow-sm sm:p-6 ${className}`}>
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-base font-bold tracking-tight">{title}</h2>
          {subtitle && <p className="mt-1 text-xs text-muted-foreground">{subtitle}</p>}
        </div>
        {action}
      </div>
      <div className="mt-5">{children}</div>
    </section>
  );
}

function Metric({
  icon: Icon,
  label,
  value,
  detail,
  tone = "text-primary",
}: {
  icon: typeof Zap;
  label: string;
  value: string;
  detail: string;
  tone?: string;
}) {
  return (
    <div className="rounded-xl border border-border bg-background/60 p-4">
      <Icon className={`h-4 w-4 ${tone}`} aria-hidden="true" />
      <p className="mt-3 text-xl font-bold">{value}</p>
      <p className="mt-1 text-xs font-medium">{label}</p>
      <p className="mt-1 text-[11px] text-muted-foreground">{detail}</p>
    </div>
  );
}

function EmptyState({ text, href, linkText }: { text: string; href?: string; linkText?: string }) {
  return (
    <div className="rounded-xl border border-dashed border-border p-6 text-center text-sm text-muted-foreground">
      <p>{text}</p>
      {href && <Link href={href} className="mt-2 inline-flex items-center gap-1 font-semibold text-primary hover:underline">{linkText}<ArrowUpRight className="h-3 w-3" /></Link>}
    </div>
  );
}

function SkillRadar({ values }: { values: number[] }) {
  const points = values.slice(0, 5);
  while (points.length < 5) points.push(0);
  const center = 100;
  const radius = 72;
  const coordinates = points.map((value, index) => {
    const angle = -Math.PI / 2 + (index * 2 * Math.PI) / 5;
    const distance = radius * clamp(value) / 100;
    return `${center + Math.cos(angle) * distance},${center + Math.sin(angle) * distance}`;
  }).join(" ");
  const outline = Array.from({ length: 5 }, (_, index) => {
    const angle = -Math.PI / 2 + (index * 2 * Math.PI) / 5;
    return `${center + Math.cos(angle) * radius},${center + Math.sin(angle) * radius}`;
  }).join(" ");
  return (
    <svg viewBox="0 0 200 200" className="h-44 w-44" role="img" aria-label="Skill mastery overview">
      <polygon points={outline} fill="none" stroke="currentColor" strokeOpacity=".15" strokeWidth="1" />
      <polygon points="100,28 168,78 142,158 58,158 32,78" fill="none" stroke="currentColor" strokeOpacity=".1" strokeWidth="1" />
      <polygon points={coordinates} fill="currentColor" fillOpacity=".2" stroke="currentColor" strokeWidth="2" className="text-primary" />
      {points.map((_, index) => {
        const angle = -Math.PI / 2 + (index * 2 * Math.PI) / 5;
        return <circle key={index} cx={center + Math.cos(angle) * radius} cy={center + Math.sin(angle) * radius} r="3" className="fill-primary" />;
      })}
    </svg>
  );
}

function ActivityPulse({
  days,
  weekly,
}: {
  days: ProgressDashboardData["contribution_data"];
  weekly: ProgressDashboardData["weekly_activity"];
}) {
  const months = useMemo(() => {
    const grouped = new Map<string, number>();
    days.forEach((day) => {
      const month = day.date.slice(0, 7);
      grouped.set(month, (grouped.get(month) ?? 0) + day.total_activities);
    });
    return Array.from(grouped.entries()).slice(-8).map(([month, count]) => ({
      month,
      count,
      label: new Date(`${month}-15T12:00:00`).toLocaleDateString(undefined, { month: "short" }),
    }));
  }, [days]);
  const maxMonthly = Math.max(...months.map((item) => item.count), 1);
  const totalThisWeek = weekly.reduce((sum, item) => sum + item.count, 0);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="text-3xl font-bold tracking-tight">{totalThisWeek}</p>
          <p className="mt-1 text-xs text-muted-foreground">learning actions this week</p>
        </div>
        <span className="rounded-full bg-primary/10 px-2.5 py-1 text-xs font-semibold text-primary">
          {days.filter((day) => day.total_activities > 0).length} active days this year
        </span>
      </div>
      <div>
        <div className="mb-3 flex items-center justify-between text-xs text-muted-foreground">
          <span>Monthly momentum</span>
          <span>Last 8 months</span>
        </div>
        <div className="grid h-32 grid-cols-8 items-end gap-2 sm:gap-3">
          {months.map((item) => (
            <div key={item.month} className="flex h-full min-w-0 flex-col items-center justify-end gap-2">
              <div
                className="w-full max-w-8 rounded-t-lg bg-gradient-to-t from-primary/80 to-sky-400 transition-[height] duration-700 motion-reduce:transition-none"
                style={{ height: `${Math.max(item.count ? 10 : 3, item.count / maxMonthly * 100)}%` }}
                title={`${item.count} activities in ${item.label}`}
                role="img"
                aria-label={`${item.count} activities in ${item.label}`}
              />
              <span className="text-[10px] text-muted-foreground">{item.label}</span>
            </div>
          ))}
        </div>
      </div>
      <div className="border-t border-border pt-4">
        <div className="mb-3 flex items-center justify-between text-xs text-muted-foreground">
          <span>Daily rhythm</span>
          <span>Mon – Sun</span>
        </div>
        <div className="grid grid-cols-7 gap-2">
          {weekly.map((item) => (
            <div key={item.date} className="min-w-0">
              <div className="mb-2 flex h-10 items-end">
                <div
                  className="w-full rounded-md bg-primary/70"
                  style={{ height: `${Math.max(item.count ? 12 : 4, item.count / Math.max(...weekly.map((day) => day.count), 1) * 100)}%` }}
                  title={`${item.count} activities`}
                  role="img"
                  aria-label={`${item.count} activities`}
                />
              </div>
              <p className="truncate text-center text-[10px] text-muted-foreground">
                {new Date(`${item.date}T12:00:00`).toLocaleDateString(undefined, { weekday: "short" }).slice(0, 3)}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default function ProgressPage() {
  const { user, loading: authLoading } = useAuth();
  const [progressData, setProgressData] = useState<ProgressDashboardData | null>(null);
  const [statsData, setStatsData] = useState<ProfileStatsData | null>(null);
  const [demoMode, setDemoMode] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const load = useCallback(async () => {
    if (!user) return;
    setLoading(true);
    try {
      const [progressData, statsData] = await Promise.all([
        progressDashboard.get(),
        profileStats.get(),
      ]);
      setProgressData(progressData);
      setStatsData(statsData);
      setError(false);
    } catch {
      setError(true);
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    // The request is the synchronization boundary for server-derived state.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void load();
  }, [load]);

  const progress = demoMode && progressData ? createDemoProgress(progressData) : progressData;
  const stats = demoMode && statsData ? createDemoStats(statsData) : statsData;

  const courses = useMemo(() => {
    if (!progress) return [];
    const rank = { active: 0, completed: 2, dropped: 3 };
    return [...progress.courses]
      .sort((a, b) => (rank[a.status as keyof typeof rank] ?? 1) - (rank[b.status as keyof typeof rank] ?? 1))
      .slice(0, 6);
  }, [progress]);

  if (authLoading || loading) {
    return <main className="mx-auto max-w-7xl animate-pulse space-y-5 px-4 py-8 sm:px-6 lg:px-8"><div className="h-72 rounded-2xl bg-card" /><div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">{[1, 2, 3, 4].map((item) => <div key={item} className="h-32 rounded-2xl bg-card" />)}</div><div className="h-64 rounded-2xl bg-card" /></main>;
  }
  if (error || !progress || !stats) return <NetworkError onRetry={load} />;

  const { overview } = progress;
  const currentXp = stats.profile.xp_points % XP_PER_LEVEL;
  const xpPercentage = currentXp / XP_PER_LEVEL * 100;
  const skills = stats.skills.slice(0, 5);
  const averageSkill = stats.skills.length ? stats.skills.reduce((sum, skill) => sum + skill.proficiency, 0) / stats.skills.length : 0;
  const latestAchievement = stats.achievements.find((achievement) => achievement.earned);
  const isAdmin = user?.role === "administrator";

  return (
    <main className="mx-auto max-w-7xl overflow-x-hidden px-4 py-7 sm:px-6 lg:px-8">
      <header className="mb-6 flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="font-mono text-[10px] font-bold uppercase tracking-[0.2em] text-primary">Developer analytics</p>
          <h1 className="mt-2 text-3xl font-bold tracking-tight">My progress</h1>
          <p className="mt-1 text-sm text-muted-foreground">A clear view of your learning momentum and next steps.</p>
        </div>
        <div className="flex flex-wrap gap-2">
          {isAdmin && <button type="button" aria-pressed={demoMode} onClick={() => setDemoMode((enabled) => !enabled)} className={`inline-flex items-center gap-2 rounded-lg border px-3 py-2 text-sm font-semibold transition-colors ${demoMode ? "border-primary/40 bg-primary/10 text-primary" : "border-border bg-card hover:bg-muted"}`}><Sparkles className="h-4 w-4" /> {demoMode ? "Exit demo stats" : "Preview demo stats"}</button>}
          <Link href="/learn" className="inline-flex items-center gap-2 rounded-lg border border-border bg-card px-3 py-2 text-sm font-semibold hover:bg-muted"><BookOpen className="h-4 w-4 text-primary" /> Explore academy</Link>
        </div>
      </header>
      {isAdmin && demoMode && <div role="status" className="mb-5 rounded-xl border border-primary/20 bg-primary/5 px-4 py-3 text-sm text-primary"><strong>Admin preview:</strong> showing illustrative progress data. No learning records were changed.</div>}

      <section className="overflow-hidden rounded-2xl border border-border bg-card shadow-sm">
        <div className="grid lg:grid-cols-[1.05fr_.95fr]">
          <div className="p-6 sm:p-8">
            <div className="flex items-start gap-4">
              {stats.profile.avatar ? (
                // Avatar URLs are user-provided and may be hosted outside Next.js image domains.
                // eslint-disable-next-line @next/next/no-img-element
                <img src={stats.profile.avatar} alt="" className="h-16 w-16 rounded-full object-cover ring-4 ring-primary/10" />
              ) : <div className="grid h-16 w-16 place-items-center rounded-full bg-primary/10 text-xl font-bold text-primary ring-4 ring-primary/5">{(stats.user.first_name || stats.user.username).slice(0, 1).toUpperCase()}</div>}
              <div><p className="text-xs text-muted-foreground">Welcome back</p><h2 className="mt-1 text-xl font-bold">{stats.user.first_name || stats.user.username}</h2><p className="mt-1 text-xs text-muted-foreground">{stats.profile.level >= 5 ? "Code Craftsman" : "Code Explorer"} · Level {stats.profile.level}</p></div>
            </div>
            <div className="mt-8 flex items-end justify-between"><div><p className="text-5xl font-bold tracking-tight">{overview.overall_percentage}<span className="text-2xl text-muted-foreground">%</span></p><p className="mt-1 text-sm text-muted-foreground">Overall learning progress</p></div><div className="text-right"><p className="text-sm font-bold">{stats.profile.xp_points.toLocaleString()} XP</p><p className="text-xs text-muted-foreground">total earned</p></div></div>
            <div className="mt-4"><div className="mb-2 flex justify-between text-xs"><span className="font-medium">Level {stats.profile.level} progress</span><span className="font-mono text-primary">{currentXp} / {XP_PER_LEVEL} XP</span></div><div className="h-2.5 overflow-hidden rounded-full bg-muted"><div className="h-full rounded-full bg-primary transition-[width] duration-700 motion-reduce:transition-none" style={{ width: `${xpPercentage}%` }} /></div><p className="mt-2 text-xs text-muted-foreground">{XP_PER_LEVEL - currentXp} XP until Level {stats.profile.level + 1}</p></div>
            <div className="mt-7 grid grid-cols-2 gap-3 sm:grid-cols-4"><Metric icon={BookOpen} label="Lessons" value={`${overview.lessons_completed}`} detail={`of ${overview.lessons_total}`} /><Metric icon={Target} label="Exercises" value={`${stats.stats.unique_exercises_solved}`} detail="solved" tone="text-sky-500" /><Metric icon={Flame} label="Streak" value={`${overview.current_streak}d`} detail={`best ${overview.longest_streak}`} tone="text-amber-500" /><Metric icon={Award} label="Badges" value={`${stats.stats.achievements_earned}`} detail={`of ${stats.stats.total_achievements}`} tone="text-violet-500" /></div>
          </div>
          <div className="border-t border-border bg-muted/20 p-6 sm:p-8 lg:border-l lg:border-t-0">
            <div className="flex items-center justify-between"><div><p className="text-xs font-semibold text-muted-foreground">Skill overview</p><h3 className="mt-1 font-bold">Your developer profile</h3></div><span className="rounded-full bg-primary/10 px-2.5 py-1 text-xs font-semibold text-primary">{Math.round(averageSkill)}% avg.</span></div>
            <div className="mt-4 flex items-center justify-center"><SkillRadar values={skills.map((skill) => skill.proficiency)} /></div>
            <div className="mt-2 grid grid-cols-2 gap-x-5 gap-y-3">{skills.map((skill) => <div key={skill.id}><div className="mb-1 flex justify-between text-[11px]"><span className="truncate">{skill.name}</span><span className="font-mono text-muted-foreground">{skill.proficiency}%</span></div><div className="h-1.5 overflow-hidden rounded-full bg-muted"><div className="h-full rounded-full bg-primary" style={{ width: `${clamp(skill.proficiency)}%` }} /></div></div>)}</div>
            {!skills.length && <p className="text-center text-sm text-muted-foreground">Complete learning content to build your skill profile.</p>}
          </div>
        </div>
      </section>

      <div className="mt-5 grid gap-5 lg:grid-cols-[1.35fr_.65fr]">
        <Panel title="Learning momentum" subtitle="A clearer view of your activity over time" action={<span className="font-mono text-xs text-primary">{progress.total_learning_activities} total actions</span>}><ActivityPulse days={progress.contribution_data} weekly={progress.weekly_activity} /></Panel>
        <Panel title="Focus snapshot" subtitle="The habits behind your progress"><div className="grid gap-3 sm:grid-cols-2"><Metric icon={Flame} label="Current streak" value={`${overview.current_streak} days`} detail={`Best: ${overview.longest_streak} days`} tone="text-amber-500" /><Metric icon={Zap} label="Learning time" value={formatTime(overview.learning_time_seconds)} detail="time invested" /><Metric icon={Target} label="Assessment average" value={`${overview.average_quiz_score}%`} detail={`${overview.quizzes_attempted} attempts`} tone="text-sky-500" /><Metric icon={Layers3} label="Practical work" value={`${overview.practicals_completed}`} detail={`of ${overview.practicals_total} complete`} tone="text-violet-500" /></div></Panel>
      </div>

      <div className="mt-5 grid gap-5 lg:grid-cols-2">
        <Panel title="Assignments" subtitle="Continue where you left off" action={<Link href="/learn" className="text-xs font-semibold text-primary hover:underline">View all</Link>}>
          {courses.length ? <div className="grid gap-3 sm:grid-cols-2">{courses.map((course) => <Link key={course.id} href={`/learn/${course.slug}`} className="group rounded-xl border border-border bg-background/50 p-4 transition-colors hover:border-primary/40 hover:bg-primary/[.03]"><div className="flex items-start justify-between gap-3"><div className="grid h-9 w-9 place-items-center rounded-lg bg-primary/10 text-primary"><Code2 className="h-4 w-4" /></div><ChevronRight className="h-4 w-4 text-muted-foreground transition-transform group-hover:translate-x-1 group-hover:text-primary" /></div><p className="mt-4 truncate text-sm font-bold">{course.title}</p><p className="mt-1 text-xs text-muted-foreground">{course.completed_lessons} / {course.total_lessons} lessons</p><div className="mt-3 h-1.5 overflow-hidden rounded-full bg-muted"><div className="h-full rounded-full bg-primary" style={{ width: `${clamp(course.progress_percentage)}%` }} /></div><p className="mt-2 text-right font-mono text-[10px] text-muted-foreground">{course.progress_percentage}%</p></Link>)}</div> : <EmptyState text="Enroll in a course to start your first assignment." href="/learn" linkText="Explore courses" />}
        </Panel>
        <Panel title="Achievements" subtitle="Milestones earned through real work" action={<Link href="/achievements" className="text-xs font-semibold text-primary hover:underline">Collection</Link>}>
          <div className="mb-4 flex items-center gap-3 rounded-xl bg-primary/5 p-3"><Trophy className="h-5 w-5 shrink-0 text-amber-500" /><div className="flex-1"><p className="text-sm font-semibold">{stats.stats.achievements_earned} of {stats.stats.total_achievements} unlocked</p><p className="text-xs text-muted-foreground">{latestAchievement ? `Latest: ${latestAchievement.title}` : "Complete lessons and exercises to earn badges."}</p></div><span className="font-mono text-xs text-primary">{stats.stats.total_achievements ? Math.round(stats.stats.achievements_earned / stats.stats.total_achievements * 100) : 0}%</span></div>
          <div className="grid gap-2 sm:grid-cols-2">{stats.achievements.slice(0, 4).map((achievement) => <div key={achievement.id} className="flex items-center gap-3 rounded-lg border border-border p-3"><div className={`grid h-8 w-8 shrink-0 place-items-center rounded-lg ${achievement.earned ? "bg-amber-500/10 text-amber-500" : "bg-muted text-muted-foreground"}`}>{achievement.earned ? <Award className="h-4 w-4" /> : <LockKeyhole className="h-3.5 w-3.5" />}</div><div className="min-w-0"><p className="truncate text-xs font-semibold">{achievement.title}</p><p className="truncate text-[11px] text-muted-foreground">{achievement.earned ? "Unlocked" : `${achievement.progress?.current ?? 0} / ${achievement.progress?.target ?? 0} progress`}</p></div></div>)}</div>
        </Panel>
      </div>

      <div className="mt-5 grid gap-5 lg:grid-cols-[.8fr_1.2fr]">
        <Panel title="Next milestone" subtitle="One clear step at a time">
          {stats.next_badge ? <div className="rounded-xl border border-primary/20 bg-primary/5 p-4"><div className="flex items-start gap-3"><div className="grid h-10 w-10 place-items-center rounded-lg bg-primary/10 text-primary"><Sparkles className="h-5 w-5" /></div><div><p className="font-bold">{stats.next_badge.title}</p><p className="mt-1 text-xs leading-5 text-muted-foreground">{stats.next_badge.description}</p></div></div><div className="mt-5"><div className="mb-2 flex justify-between text-xs"><span className="text-muted-foreground">Progress</span><span className="font-mono text-primary">{stats.next_badge.progress.current} / {stats.next_badge.progress.target}</span></div><ProgressBar value={stats.next_badge.progress.target ? stats.next_badge.progress.current / stats.next_badge.progress.target * 100 : 0} /></div></div> : <EmptyState text="Complete meaningful learning activity to reveal your next milestone." href="/learn" linkText="Start learning" />}
        </Panel>
        <Panel title="Recent activity" subtitle="Your latest meaningful learning events" action={<Link href="/progress" className="text-xs font-semibold text-primary hover:underline">Refresh</Link>}>
          {progress.activities.length ? <div className="grid gap-x-6 sm:grid-cols-2">{progress.activities.slice(0, 6).map((activity) => <div key={activity.id} className="flex items-center gap-3 border-b border-border py-3 last:border-0"><div className="grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-primary/10 text-primary"><GitBranch className="h-4 w-4" /></div><div className="min-w-0"><p className="truncate text-sm font-semibold">{activity.title}</p><p className="truncate text-xs text-muted-foreground">{activity.associated_title || "Code Yaar"} · {formatDate(activity.date)}</p></div></div>)}</div> : <EmptyState text="Your activity feed will populate as you learn." />}
        </Panel>
      </div>

      <footer className="mt-5 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-border bg-card px-4 py-3 text-xs text-muted-foreground"><span className="inline-flex items-center gap-2"><Layers3 className="h-4 w-4 text-primary" /> Progress is calculated from verified learning activity.</span><span>{overview.average_quiz_score}% average assessment · {overview.practicals_completed} practicals complete</span></footer>
    </main>
  );
}
