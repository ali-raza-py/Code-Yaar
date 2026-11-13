"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import {
  Award,
  BookOpen,
  Code2,
  GraduationCap,
  Medal,
  Trophy,
  Users,
  TrendingUp,
  Target,
  FileText,
} from "lucide-react";
import { adminApi } from "@/lib/admin-api";
import { ApiError } from "@/lib/api";
import type {
  AdminDashboardStats,
  AdminRecentActivity,
  AdminTopCourse,
} from "@/lib/admin-api";
import { useAuth } from "@/hooks/use-auth";
import {
  NetworkError,
  ServerError,
  UnauthorizedError,
} from "@/components/learning/workspace/error-states";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

const statCards = [
  { key: "totalStudents", label: "Total Students", icon: Users },
  { key: "activeStudents", label: "Active Students", icon: TrendingUp },
  { key: "totalCourses", label: "Published Courses", icon: BookOpen },
  { key: "totalTracks", label: "Learning Tracks", icon: GraduationCap },
  { key: "totalEnrollments", label: "Total Enrollments", icon: Target },
  { key: "completedCourses", label: "Completed Courses", icon: Award },
  { key: "totalAssessments", label: "Assessments", icon: FileText },
  { key: "totalChallenges", label: "Coding Challenges", icon: Code2 },
  { key: "certificatesIssued", label: "Certificates Issued", icon: Medal },
  { key: "activeCompetitions", label: "Active Competitions", icon: Trophy },
] as const;

function StatCard({
  label,
  value,
  icon: Icon,
  trend,
}: {
  label: string;
  value: number | string;
  icon: React.ElementType;
  trend?: string;
}) {
  return (
    <Card className="overflow-hidden">
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-muted-foreground">{label}</p>
            <p className="mt-1 text-3xl font-bold text-foreground">{value}</p>
            {trend && (
              <p className="mt-1 text-xs text-primary-foreground dark:text-primary-foreground">{trend}</p>
            )}
          </div>
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary">
            <Icon className="h-6 w-6" aria-hidden="true" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function StatCardSkeleton() {
  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <Skeleton className="h-4 w-24" />
            <Skeleton className="mt-2 h-8 w-16" />
          </div>
          <Skeleton className="h-12 w-12 rounded-xl" />
        </div>
      </CardContent>
    </Card>
  );
}

function RecentActivityTable({ activities }: { activities: AdminRecentActivity[] }) {
  if (activities.length === 0) {
    return (
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-lg">Recent Activity</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-center text-muted-foreground py-8">No recent activity</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-lg">Recent Activity</CardTitle>
        <Link href="/admin/audit-logs" className="text-sm text-primary hover:underline">
          View all
        </Link>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[var(--color-section-border)]">
                <th className="text-left py-3 font-medium text-muted-foreground">Action</th>
                <th className="text-left py-3 font-medium text-muted-foreground">User</th>
                <th className="text-left py-3 font-medium text-muted-foreground">Target</th>
                <th className="text-left py-3 font-medium text-muted-foreground">Time</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--color-section-border)]">
              {activities.map((activity) => (
                <tr key={activity.id} className="hover:bg-[var(--color-section-light)]">
                  <td className="py-3">
                    <Badge variant="outline" className="text-xs">
                      {activity.action}
                    </Badge>
                  </td>
                  <td className="py-3 font-medium">{activity.admin}</td>
                  <td className="py-3 text-muted-foreground">{activity.target}</td>
                  <td className="py-3 text-muted-foreground">
                    {new Date(activity.timestamp).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}

function TopCoursesTable({ courses }: { courses: AdminTopCourse[] }) {
  if (courses.length === 0) {
    return (
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-lg">Top Courses by Enrollment</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-center text-muted-foreground py-8">No course data available</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-lg">Top Courses by Enrollment</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[var(--color-section-border)]">
                <th className="text-left py-3 font-medium text-muted-foreground">Course</th>
                <th className="text-left py-3 font-medium text-muted-foreground">Track</th>
                <th className="text-left py-3 font-medium text-muted-foreground">Enrollments</th>
                <th className="text-left py-3 font-medium text-muted-foreground">Completion Rate</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--color-section-border)]">
              {courses.map((course) => (
                <tr key={course.id} className="hover:bg-[var(--color-section-light)]">
                  <td className="py-3 font-medium">{course.title}</td>
                  <td className="py-3 text-muted-foreground">{course.track}</td>
                  <td className="py-3">{course.enrollments.toLocaleString()}</td>
                  <td className="py-3">
                    <div className="flex items-center gap-2">
                      <div className="flex-1 h-2 bg-[var(--color-section-border)] rounded-full overflow-hidden">
                        <div
                          className="h-full bg-primary rounded-full"
                          style={{ width: `${course.completionRate}%` }}
                        />
                      </div>
                      <span className="text-xs text-muted-foreground w-12">
                        {course.completionRate}%
                      </span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}

export default function AdminDashboardPage() {
  const { user, loading: authLoading } = useAuth();
  const [stats, setStats] = useState<AdminDashboardStats | null>(null);
  const [recentActivity, setRecentActivity] = useState<AdminRecentActivity[]>([]);
  const [topCourses, setTopCourses] = useState<AdminTopCourse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<"network" | "server" | "auth" | null>(null);

  const load = useCallback(async () => {
    if (!user) return;
    try {
      const [statsData, activityData, coursesData] = await Promise.all([
        adminApi.getDashboardStats(),
        adminApi.getRecentActivity({ limit: 10 }),
        adminApi.getTopCourses({ limit: 5 }),
      ]);
      setStats(statsData);
      setRecentActivity(activityData);
      setTopCourses(coursesData);
      setError(null);
    } catch (caught) {
      if (caught instanceof ApiError && (caught.status === 401 || caught.status === 403)) {
        setError("auth");
      } else if (caught instanceof ApiError && caught.status >= 500) {
        setError("server");
      } else {
        setError("network");
      }
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    (async () => { await load(); })();
  }, [load]);

  if (authLoading || (loading && user)) {
    return (
      <div className="mx-auto max-w-7xl animate-pulse space-y-6">
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
          {[...Array(5)].map((_, i) => (
            <StatCardSkeleton key={i} />
          ))}
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
          {[...Array(5)].map((_, i) => (
            <StatCardSkeleton key={i + 5} />
          ))}
        </div>
        <div className="grid gap-6 lg:grid-cols-2">
          <Skeleton className="h-64" />
          <Skeleton className="h-64" />
        </div>
      </div>
    );
  }

  if (error === "auth") {
    return <UnauthorizedError />;
  }

  if (error === "server") {
    return <ServerError onRetry={load} />;
  }

  if (error === "network") {
    return <NetworkError onRetry={load} />;
  }

  if (!user) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-16 text-center">
        <h1 className="text-2xl font-bold text-foreground">Admin Dashboard</h1>
        <p className="mt-3 text-sm text-muted-foreground">Sign in as an administrator to access the dashboard.</p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">Admin Dashboard</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Platform overview and key metrics
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="secondary" className="text-xs">
            Last updated: {new Date().toLocaleTimeString()}
          </Badge>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
        {statCards.map(({ key, label, icon: Icon }) => (
          <StatCard
            key={key}
            label={label}
            value={stats?.[key as keyof AdminDashboardStats] ?? 0}
            icon={Icon}
          />
        ))}
      </div>

      {/* Charts & Tables */}
      <div className="grid gap-6 lg:grid-cols-2">
        <RecentActivityTable activities={recentActivity} />
        <TopCoursesTable courses={topCourses} />
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="mb-4 text-lg font-bold text-foreground">Quick Actions</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Link
            href="/admin/courses/create"
            className="group card-hairline p-5 transition-colors hover:border-primary"
          >
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10 text-primary">
              <BookOpen className="h-6 w-6" />
            </div>
            <h3 className="mt-4 font-semibold text-foreground group-hover:text-primary">Create Course</h3>
            <p className="mt-1 text-sm text-muted-foreground">Build a new course with chapters and lessons</p>
          </Link>
          <Link
            href="/admin/tracks/create"
            className="group card-hairline p-5 transition-colors hover:border-primary"
          >
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10 text-primary">
              <GraduationCap className="h-6 w-6" />
            </div>
            <h3 className="mt-4 font-semibold text-foreground group-hover:text-primary">Create Track</h3>
            <p className="mt-1 text-sm text-muted-foreground">Set up a new learning track</p>
          </Link>
          <Link
            href="/admin/announcements/create"
            className="group card-hairline p-5 transition-colors hover:border-primary"
          >
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10 text-primary">
              <FileText className="h-6 w-6" />
            </div>
            <h3 className="mt-4 font-semibold text-foreground group-hover:text-primary">Post Announcement</h3>
            <p className="mt-1 text-sm text-muted-foreground">Send a platform-wide announcement</p>
          </Link>
          <Link
            href="/admin/competitions/create"
            className="group card-hairline p-5 transition-colors hover:border-primary"
          >
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10 text-primary">
              <Trophy className="h-6 w-6" />
            </div>
            <h3 className="mt-4 font-semibold text-foreground group-hover:text-primary">Create Competition</h3>
            <p className="mt-1 text-sm text-muted-foreground">Launch a new coding competition</p>
          </Link>
        </div>
      </div>
    </div>
  );
}