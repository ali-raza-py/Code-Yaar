"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Award, BookOpen, CheckCircle2, Clock3, Flame, FlaskConical,
  Target, TrendingUp,
} from "lucide-react";
import { ContributionGraph } from "@/components/progress/contribution-graph";
import { ProgressBar } from "@/components/progress/progress-bar";
import { useAuth } from "@/hooks/use-auth";
import { NetworkError } from "@/components/learning/workspace/error-states";
import { progressDashboard, type ProgressDashboardData } from "@/lib/api";

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

function Stat({
  icon: Icon,
  label,
  value,
  detail,
}: {
  icon: typeof BookOpen;
  label: string;
  value: string;
  detail: string;
}) {
  return (
    <div className="rounded-card border border-border bg-card p-4">
      <div className="flex items-center gap-2 text-muted-foreground">
        <Icon className="h-4 w-4 text-cta" aria-hidden="true" />
        <span className="text-xs font-semibold">{label}</span>
      </div>
      <p className="mt-3 text-2xl font-bold">{value}</p>
      <p className="mt-1 text-xs text-muted-foreground">{detail}</p>
    </div>
  );
}

function EmptyState({ text, href, linkText }: { text: string; href?: string; linkText?: string }) {
  return (
    <div className="rounded-lg border border-dashed border-border p-6 text-center text-sm text-muted-foreground">
      <p>{text}</p>
      {href && <Link href={href} className="mt-2 inline-block font-semibold text-cta hover:underline">{linkText}</Link>}
    </div>
  );
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

  const sortedCourses = useMemo(() => {
    if (!data) return [];
    const rank = { active: 0, completed: 2, dropped: 3 };
    return [...data.courses].sort((a, b) => (rank[a.status as keyof typeof rank] ?? 1) - (rank[b.status as keyof typeof rank] ?? 1));
  }, [data]);

  if (authLoading || loading) {
    return (
      <main className="mx-auto max-w-7xl animate-pulse space-y-6 px-4 py-8 sm:px-6 lg:px-8">
        <div className="h-32 rounded-card bg-card" />
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">{[1, 2, 3, 4].map((item) => <div key={item} className="h-28 rounded-card bg-card" />)}</div>
        <div className="h-72 rounded-card bg-card" />
      </main>
    );
  }
  if (error || !data) return <NetworkError onRetry={load} />;

  const { overview } = data;
  const maxActivity = Math.max(...data.weekly_activity.map((item) => item.count), 1);
  const maxQuizScore = Math.max(...data.quiz_performance.map((item) => item.score), 100);

  return (
    <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <header className="rounded-card bg-hero-navy p-6 text-white sm:p-8">
        <div className="flex flex-wrap items-start justify-between gap-5">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.16em] text-mint-on-navy">Student analytics</p>
            <h1 className="mt-2 text-3xl font-bold">My learning progress</h1>
            <p className="mt-2 max-w-2xl text-sm text-white/70">A focused view of your learning momentum, completion, and meaningful activity.</p>
          </div>
          <span className="rounded-pill bg-cta/15 px-3 py-1 text-xs font-bold text-mint-on-navy">{user?.role === "administrator" ? "Administrator" : "Student"}</span>
        </div>
        <div className="mt-7 max-w-xl">
          <ProgressBar value={overview.overall_percentage} label="Overall learning progress" showValue size="md" />
        </div>
      </header>

      <section className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Stat icon={TrendingUp} label="Overall progress" value={`${overview.overall_percentage}%`} detail={`${overview.completed_courses} of ${overview.total_courses} courses completed`} />
        <Stat icon={BookOpen} label="Lessons completed" value={`${overview.lessons_completed}`} detail={`of ${overview.lessons_total} available lessons`} />
        <Stat icon={FlaskConical} label="Practicals completed" value={`${overview.practicals_completed}`} detail={`of ${overview.practicals_total} available practicals`} />
        <Stat icon={Flame} label="Current streak" value={`${overview.current_streak} days`} detail={`Longest streak: ${overview.longest_streak} days`} />
      </section>

      <div className="mt-6">
        <ContributionGraph days={data.contribution_data} totalActivities={data.total_learning_activities} />
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-3">
        <section className="rounded-card border border-border bg-card p-5 lg:col-span-2">
          <div className="flex items-center justify-between gap-4">
            <div><h2 className="font-bold">Course progress</h2><p className="mt-1 text-sm text-muted-foreground">Completion is calculated from lessons completed on the server.</p></div>
            <Link href="/learn" className="shrink-0 text-sm font-semibold text-cta hover:underline">Browse courses</Link>
          </div>
          <div className="mt-5 space-y-5">
            {sortedCourses.length ? sortedCourses.map((course) => (
              <div key={course.id}>
                <div className="mb-2 flex items-center justify-between gap-3">
                  <Link href={`/learn/${course.slug}`} className="truncate text-sm font-semibold hover:text-cta">{course.title}</Link>
                  <span className="shrink-0 text-sm font-semibold text-cta">{course.progress_percentage}%</span>
                </div>
                <ProgressBar value={course.progress_percentage} label={`${course.completed_lessons} of ${course.total_lessons} lessons`} showValue={false} />
                <p className="mt-1 text-xs text-muted-foreground">{course.status === "completed" ? "Completed" : `${course.remaining_lessons} lessons remaining`}{course.last_accessed_at ? ` · Last accessed ${formatDate(course.last_accessed_at)}` : ""}</p>
              </div>
            )) : <EmptyState text="Enroll in a course to start tracking your progress." href="/learn" linkText="Explore courses" />}
          </div>
        </section>

        <section className="rounded-card border border-border bg-card p-5">
          <div className="flex items-center gap-2"><TrendingUp className="h-5 w-5 text-cta" aria-hidden="true" /><h2 className="font-bold">Your insights</h2></div>
          <div className="mt-5 space-y-3">{data.insights.map((insight) => <div key={insight} className="rounded-lg bg-secondary p-3 text-sm">{insight}</div>)}</div>
          <div className="mt-5 grid grid-cols-2 gap-3">
            <div className="rounded-lg border border-border p-3"><Clock3 className="h-4 w-4 text-cta" aria-hidden="true" /><p className="mt-2 text-lg font-bold">{formatTime(overview.learning_time_seconds)}</p><p className="text-xs text-muted-foreground">Learning time</p></div>
            <div className="rounded-lg border border-border p-3"><Target className="h-4 w-4 text-cta" aria-hidden="true" /><p className="mt-2 text-lg font-bold">{overview.average_quiz_score}%</p><p className="text-xs text-muted-foreground">Average quiz score</p></div>
          </div>
        </section>
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <section className="rounded-card border border-border bg-card p-5">
          <div className="flex items-center justify-between"><div><h2 className="font-bold">Weekly activity</h2><p className="mt-1 text-sm text-muted-foreground">Meaningful learning events over the last seven days.</p></div><span className="text-xs text-muted-foreground">{data.active_learning_days} active days this year</span></div>
          <div className="mt-6 flex h-44 items-end gap-2 sm:gap-4">
            {data.weekly_activity.map((item) => (
              <div key={item.date} className="flex min-w-0 flex-1 flex-col items-center gap-2">
                <div className="flex h-32 w-full items-end"><div className="w-full rounded-t-md bg-cta transition-[height] motion-reduce:transition-none" role="img" aria-label={`${item.count} activities on ${formatDate(item.date)}`} title={`${item.count} activities`} style={{ height: `${Math.max(item.count ? 6 : 2, (item.count / maxActivity) * 100)}%` }} /></div>
                <span className="text-[11px] text-muted-foreground">{new Date(`${item.date}T12:00:00`).toLocaleDateString(undefined, { weekday: "short" }).slice(0, 1)}</span>
              </div>
            ))}
          </div>
          <p className="mt-4 border-t border-border pt-4 text-sm text-muted-foreground">{overview.current_streak ? `You are on a ${overview.current_streak}-day streak.` : "Complete a lesson, practical, or quiz today to start a streak."}</p>
        </section>

        <section className="rounded-card border border-border bg-card p-5">
          <div className="flex items-center justify-between"><h2 className="font-bold">Quiz performance</h2><span className="text-sm text-muted-foreground">{overview.quizzes_attempted} attempts</span></div>
          <div className="mt-4 grid grid-cols-2 gap-3 text-sm"><div className="rounded-lg bg-secondary p-3"><p className="text-xs text-muted-foreground">Average score</p><p className="mt-1 text-xl font-bold">{overview.average_quiz_score}%</p></div><div className="rounded-lg bg-secondary p-3"><p className="text-xs text-muted-foreground">Highest score</p><p className="mt-1 text-xl font-bold">{overview.highest_quiz_score}%</p></div></div>
          <div className="mt-5 flex h-24 items-end gap-1">{data.quiz_performance.slice(-20).map((item, index) => <div key={`${item.date}-${index}`} className="flex-1 rounded-t-sm bg-cta/70" role="img" aria-label={`${item.score}% on ${formatDate(item.date)}`} title={`${item.score}% · ${formatDate(item.date)}`} style={{ height: `${Math.max(item.score ? 8 : 3, (item.score / maxQuizScore) * 100)}%` }} />)}</div>
          {!data.quiz_performance.length && <p className="mt-4 text-sm text-muted-foreground">Submit an assessment to see performance over time.</p>}
        </section>
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <section className="rounded-card border border-border bg-card p-5">
          <div className="flex items-center justify-between"><h2 className="font-bold">Practical progress</h2><Link href="/learn/practicals" className="text-sm font-semibold text-cta hover:underline">Open practicals</Link></div>
          <div className="mt-5 space-y-4">
            {data.classes.map((item) => <ProgressBar key={`class-${item.id}`} value={item.percentage} label={item.title} showValue />)}
            {data.subjects.slice(0, 4).map((subject) => <div key={subject.id}><ProgressBar value={subject.percentage} label={subject.title} showValue /><p className="mt-1 text-xs text-muted-foreground">{subject.class_title} · {subject.completed}/{subject.total} completed</p></div>)}
            {!data.classes.length && !data.subjects.length && <EmptyState text="Published practical subjects will appear here." href="/learn/practicals" linkText="View practicals" />}
          </div>
        </section>

        <section className="rounded-card border border-border bg-card p-5">
          <div className="flex items-center justify-between gap-3"><div><h2 className="font-bold">Recent learning activity</h2><p className="mt-1 text-sm text-muted-foreground">Only meaningful completions and assessment attempts are shown.</p></div><select aria-label="Filter learning activity" value={activityType} onChange={(event) => setActivityType(event.target.value)} className="rounded-lg border border-input bg-card px-2 py-2 text-xs"><option value="">All activity</option><option value="lesson_completed">Lessons</option><option value="practical_completed">Practicals</option><option value="quiz_attempted">Quizzes</option></select></div>
          <div className="mt-4 divide-y divide-border">{data.activities.length ? data.activities.slice(0, 8).map((activity) => <div key={activity.id} className="flex items-center gap-3 py-3"><span className="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-cta/10 text-cta">{activity.type === "practical_completed" ? <FlaskConical className="h-4 w-4" aria-hidden="true" /> : activity.type === "quiz_attempted" ? <Award className="h-4 w-4" aria-hidden="true" /> : <CheckCircle2 className="h-4 w-4" aria-hidden="true" />}</span><div className="min-w-0 flex-1"><p className="truncate text-sm font-semibold">{activity.title}</p><p className="text-xs text-muted-foreground">{activity.associated_title || "Code Yaar"} · {formatDate(activity.date)}</p></div></div>) : <EmptyState text="Your meaningful learning activity will appear here." />}</div>
        </section>
      </div>
    </main>
  );
}
