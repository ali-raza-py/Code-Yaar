"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import {
  Activity, Award, BookOpen, CheckCircle2, Clock3, Flame, FlaskConical,
  Target, TrendingUp,
} from "lucide-react";
import { progressDashboard, type ProgressDashboardData } from "@/lib/api";
import { useAuth } from "@/hooks/use-auth";
import { NetworkError } from "@/components/learning/workspace/error-states";

function ProgressBar({ value }: { value: number }) {
  return (
    <div className="h-2 overflow-hidden rounded-full bg-muted" role="progressbar" aria-valuenow={value} aria-valuemin={0} aria-valuemax={100}>
      <div className="h-full rounded-full bg-cta transition-all" style={{ width: `${Math.min(100, Math.max(0, value))}%` }} />
    </div>
  );
}

function Stat({ icon: Icon, label, value, detail }: { icon: typeof Activity; label: string; value: string; detail: string }) {
  return <div className="rounded-card border border-border bg-card p-4"><div className="flex items-center gap-2 text-muted-foreground"><Icon className="h-4 w-4 text-cta" /><span className="text-xs font-semibold">{label}</span></div><p className="mt-3 text-2xl font-bold">{value}</p><p className="mt-1 text-xs text-muted-foreground">{detail}</p></div>;
}

function formatTime(seconds: number) {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  return hours ? `${hours}h ${minutes}m` : `${minutes}m`;
}

export default function ProgressPage() {
  const { user, loading: authLoading } = useAuth();
  const [data, setData] = useState<ProgressDashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [activityType, setActivityType] = useState("");

  const load = useCallback(async () => {
    if (!user) return;
    setLoading(true);
    try {
      setData(await progressDashboard.get(activityType ? { type: activityType } : undefined));
      setError(false);
    } catch {
      setError(true);
    } finally {
      setLoading(false);
    }
  }, [activityType, user]);

  useEffect(() => {
    // The request is the synchronization boundary for server-derived state.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void load();
  }, [load]);

  if (authLoading || loading) {
    return <main className="mx-auto max-w-7xl animate-pulse space-y-6 px-4 py-8 sm:px-6 lg:px-8"><div className="h-32 rounded-card bg-card" /><div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">{[1, 2, 3, 4].map((item) => <div key={item} className="h-28 rounded-card bg-card" />)}</div><div className="h-72 rounded-card bg-card" /></main>;
  }
  if (error || !data) return <NetworkError onRetry={load} />;

  const { overview } = data;
  const maxActivity = Math.max(...data.weekly_activity.map((item) => item.count), 1);
  const activeDateSet = new Set(data.active_dates);

  return (
    <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <header className="rounded-card bg-hero-navy p-6 text-white sm:p-8">
        <div className="flex flex-wrap items-start justify-between gap-5">
          <div><p className="text-xs font-bold uppercase tracking-[0.16em] text-mint-on-navy">Student analytics</p><h1 className="mt-2 text-3xl font-bold">My learning progress</h1><p className="mt-2 max-w-2xl text-sm text-white/70">A clear view of what you have completed, what needs attention, and the momentum you are building.</p></div>
          <span className="rounded-pill bg-cta/15 px-3 py-1 text-xs font-bold text-mint-on-navy">{user?.role === "administrator" ? "Administrator" : "Student"}</span>
        </div>
        <div className="mt-7 max-w-xl"><div className="mb-2 flex items-center justify-between text-sm"><span>Overall learning progress</span><strong>{overview.overall_percentage}%</strong></div><div className="h-3 overflow-hidden rounded-full bg-white/15"><div className="h-full rounded-full bg-cta" style={{ width: `${overview.overall_percentage}%` }} /></div></div>
      </header>

      <section className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Stat icon={BookOpen} label="Courses" value={`${overview.completed_courses}/${overview.total_courses}`} detail={`${overview.in_progress_courses} currently in progress`} />
        <Stat icon={CheckCircle2} label="Lessons completed" value={`${overview.lessons_completed}`} detail={`of ${overview.lessons_total} available lessons`} />
        <Stat icon={FlaskConical} label="Practicals completed" value={`${overview.practicals_completed}`} detail={`of ${overview.practicals_total} available practicals`} />
        <Stat icon={Flame} label="Learning streak" value={`${overview.current_streak} days`} detail={`Longest streak: ${overview.longest_streak} days`} />
      </section>

      <div className="mt-6 grid gap-6 lg:grid-cols-3">
        <section className="rounded-card border border-border bg-card p-5 lg:col-span-2"><div className="flex items-center justify-between"><div><h2 className="font-bold">Course progress</h2><p className="mt-1 text-sm text-muted-foreground">Based on completed lessons recorded by the server.</p></div><Link href="/learn" className="text-sm font-semibold text-cta hover:underline">Browse courses</Link></div><div className="mt-5 space-y-5">{data.courses.length ? data.courses.map((course) => <div key={course.id}><div className="mb-2 flex items-center justify-between gap-3 text-sm"><Link href={`/learn/${course.slug}`} className="truncate font-semibold hover:text-cta">{course.title}</Link><span className="shrink-0 font-semibold">{course.progress_percentage}%</span></div><ProgressBar value={course.progress_percentage} /><p className="mt-1 text-xs text-muted-foreground">{course.completed_lessons} completed · {course.remaining_lessons} remaining{course.last_accessed_at ? ` · Last accessed ${new Date(course.last_accessed_at).toLocaleDateString()}` : ""}</p></div>) : <EmptyState text="Enroll in a course to start tracking your progress." href="/learn" linkText="Explore courses" />}</div></section>

        <section className="rounded-card border border-border bg-card p-5"><div className="flex items-center gap-2"><TrendingUp className="h-5 w-5 text-cta" /><h2 className="font-bold">Your insights</h2></div><div className="mt-5 space-y-3">{data.insights.map((insight) => <div key={insight} className="rounded-lg bg-secondary p-3 text-sm">{insight}</div>)}</div><div className="mt-5 grid grid-cols-2 gap-3"><div className="rounded-lg border border-border p-3"><Clock3 className="h-4 w-4 text-cta" /><p className="mt-2 text-lg font-bold">{formatTime(overview.learning_time_seconds)}</p><p className="text-xs text-muted-foreground">Learning time</p></div><div className="rounded-lg border border-border p-3"><Target className="h-4 w-4 text-cta" /><p className="mt-2 text-lg font-bold">{overview.average_quiz_score}%</p><p className="text-xs text-muted-foreground">Average assessment</p></div></div></section>
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <section className="rounded-card border border-border bg-card p-5"><h2 className="font-bold">Weekly learning activity</h2><div className="mt-6 flex h-44 items-end gap-2 sm:gap-4">{data.weekly_activity.map((item) => <div key={item.date} className="flex min-w-0 flex-1 flex-col items-center gap-2"><div className="flex h-32 w-full items-end"><div title={`${item.count} activities`} className="w-full rounded-t-md bg-cta" style={{ height: `${Math.max(4, (item.count / maxActivity) * 100)}%` }} /></div><span className="text-[11px] text-muted-foreground">{new Date(`${item.date}T12:00:00`).toLocaleDateString(undefined, { weekday: "short" }).slice(0, 1)}</span></div>)}</div><div className="mt-4 border-t border-border pt-4 text-sm text-muted-foreground">{overview.current_streak ? `You are on a ${overview.current_streak}-day streak.` : "Complete a lesson or practical today to start a streak."}</div></section>

        <section className="rounded-card border border-border bg-card p-5"><div className="flex items-center justify-between"><h2 className="font-bold">Practical progress</h2><Link href="/learn/practicals" className="text-sm font-semibold text-cta hover:underline">Open practicals</Link></div><div className="mt-5 space-y-4">{data.classes.map((item) => <div key={item.id}><div className="mb-1 flex justify-between text-sm"><span className="font-semibold">{item.title}</span><span>{item.percentage}%</span></div><ProgressBar value={item.percentage} /><p className="mt-1 text-xs text-muted-foreground">{item.completed}/{item.total} completed across class</p></div>)}{data.subjects.slice(0, 4).map((subject) => <div key={subject.id}><div className="mb-1 flex justify-between text-sm"><span className="font-semibold">{subject.title}</span><span>{subject.percentage}%</span></div><ProgressBar value={subject.percentage} /><p className="mt-1 text-xs text-muted-foreground">{subject.class_title} · {subject.completed}/{subject.total} completed</p></div>)}{!data.classes.length && !data.subjects.length && <EmptyState text="Published practical subjects will appear here." href="/learn/practicals" linkText="View practicals" />}</div></section>
      </div>

      <section className="mt-6 rounded-card border border-border bg-card p-5"><div className="flex flex-wrap items-center justify-between gap-3"><div><h2 className="font-bold">Learning activity</h2><p className="mt-1 text-sm text-muted-foreground">Meaningful events only — opening a page does not count.</p></div><select value={activityType} onChange={(event) => setActivityType(event.target.value)} className="rounded-lg border border-input bg-card px-3 py-2 text-sm"><option value="">All activity</option><option value="lesson_completed">Lessons</option><option value="practical_completed">Practicals</option><option value="quiz_attempted">Assessments</option><option value="course_started">Courses started</option></select></div><div className="mt-5 divide-y divide-border">{data.activities.length ? data.activities.slice(0, 10).map((activity) => <div key={activity.id} className="flex items-center gap-3 py-3"><span className="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-cta/10 text-cta">{activity.type === "practical_completed" ? <FlaskConical className="h-4 w-4" /> : activity.type === "quiz_attempted" ? <Award className="h-4 w-4" /> : <CheckCircle2 className="h-4 w-4" />}</span><div className="min-w-0 flex-1"><p className="truncate text-sm font-semibold">{activity.title}</p><p className="text-xs text-muted-foreground">{activity.associated_title || "Code Yaar"} · {new Date(activity.date).toLocaleString()}</p></div><span className="text-xs capitalize text-muted-foreground">{activity.status.replace("_", " ")}</span></div>) : <EmptyState text="Your meaningful learning activity will appear here." />}</div></section>

      <section className="mt-6 rounded-card border border-border bg-card p-5"><h2 className="font-bold">Learning streak calendar</h2><div className="mt-4 grid grid-cols-7 gap-2 sm:grid-cols-14">{Array.from({ length: 42 }, (_, index) => { const date = new Date(); date.setDate(date.getDate() - (41 - index)); const key = date.toISOString().slice(0, 10); return <div key={key} title={key} className={`h-5 rounded-sm ${activeDateSet.has(key) ? "bg-cta" : "bg-muted"}`} />; })}</div><p className="mt-3 text-xs text-muted-foreground">Green days contain at least one completed lesson, practical, assessment attempt, course start, or saved bookmark.</p></section>
    </main>
  );
}

function EmptyState({ text, href, linkText }: { text: string; href?: string; linkText?: string }) {
  return <div className="rounded-lg border border-dashed border-border p-6 text-center text-sm text-muted-foreground"><p>{text}</p>{href && <Link href={href} className="mt-2 inline-block font-semibold text-cta hover:underline">{linkText}</Link>}</div>;
}
