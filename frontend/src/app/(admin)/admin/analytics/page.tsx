"use client";

import { useCallback, useEffect, useState } from "react";
import { Download, RefreshCw } from "lucide-react";
import { adminApi } from "@/lib/admin-api";
import type { AnalyticsOverview, AdminDashboardStats } from "@/lib/admin-api";
import { ANALYTICS_REPORTS, downloadAnalyticsCsv } from "@/lib/admin-api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";

const COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899"];

function TimeSeriesChart({ data, title, color, reportId }: {
  data: Array<{ period: string; value: number }>;
  title: string;
  color: string;
  reportId: string;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          {title}
          <Badge variant="secondary">{data.length} periods</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="period" tick={{ fontSize: 12 }} />
              <YAxis />
              <Tooltip
                formatter={(value: unknown) => [Number(value).toLocaleString(), ""]}
              />
              <Line type="monotone" dataKey="value" stroke={color} strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="flex justify-end mt-2">
          <Button variant="outline" size="sm" onClick={() => downloadAnalyticsCsv(reportId, {})}>
            <Download className="mr-2 h-4 w-4" />Export CSV
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

export default function AnalyticsPage() {
  const [overview, setOverview] = useState<AnalyticsOverview | null>(null);
  const [stats, setStats] = useState<AdminDashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [from, setFrom] = useState("");
  const [to, setTo] = useState("");
  const [bucket, setBucket] = useState("day");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [overviewData, statsData] = await Promise.all([
        adminApi.getAnalyticsOverview({ from, to, bucket }),
        adminApi.getDashboardStats(),
      ]);
      setOverview(overviewData);
      setStats(statsData);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not load analytics.");
    } finally {
      setLoading(false);
    }
  }, [from, to, bucket]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    load();
  }, [load]);

  if (loading) {
    return (
      <div className="animate-pulse space-y-6">
        <div className="grid gap-4 md:grid-cols-4">
          <Skeleton className="h-24" />
          <Skeleton className="h-24" />
          <Skeleton className="h-24" />
          <Skeleton className="h-24" />
        </div>
        <Skeleton className="h-96" />
        <Skeleton className="h-96" />
      </div>
    );
  }

  if (error && !overview) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
        <p className="text-center text-destructive">{error}</p>
        <Button onClick={load}><RefreshCw className="mr-2 h-4 w-4" />Retry</Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Analytics Dashboard</h1>
          <p className="mt-1 text-sm text-muted-foreground">Platform-wide metrics and trends</p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium">From</span>
            <input type="date" value={from} onChange={(e) => setFrom(e.target.value)} className="rounded-md border border-input bg-background px-3 py-2 text-sm" />
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium">To</span>
            <input type="date" value={to} onChange={(e) => setTo(e.target.value)} className="rounded-md border border-input bg-background px-3 py-2 text-sm" />
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium">Bucket</span>
            <select value={bucket} onChange={(e) => setBucket(e.target.value)} className="rounded-md border border-input bg-background px-3 py-2 text-sm">
              <option value="hour">Hour</option>
              <option value="day">Day</option>
              <option value="week">Week</option>
              <option value="month">Month</option>
            </select>
          </div>
          <Button onClick={load} variant="outline"><RefreshCw className="mr-2 h-4 w-4" />Reload</Button>
        </div>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid gap-4 md:grid-cols-4 lg:grid-cols-6">
          <Card>
            <CardContent className="p-4">
              <div className="text-sm text-muted-foreground">Total Students</div>
              <div className="text-2xl font-bold">{stats.totalStudents.toLocaleString()}</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="text-sm text-muted-foreground">Active Students</div>
              <div className="text-2xl font-bold">{stats.activeStudents.toLocaleString()}</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="text-sm text-muted-foreground">Total Courses</div>
              <div className="text-2xl font-bold">{stats.totalCourses.toLocaleString()}</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="text-sm text-muted-foreground">Published Courses</div>
              <div className="text-2xl font-bold">{stats.publishedCourses.toLocaleString()}</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="text-sm text-muted-foreground">Total Enrollments</div>
              <div className="text-2xl font-bold">{stats.totalEnrollments.toLocaleString()}</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="text-sm text-muted-foreground">Certificates Issued</div>
              <div className="text-2xl font-bold">{stats.certificatesIssued.toLocaleString()}</div>
            </CardContent>
          </Card>
        </div>
      )}

      {overview && (
        <>
          {/* Time Series Charts */}
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            <TimeSeriesChart
              data={overview.students.registrations}
              title="Student Registrations"
              color={COLORS[0]}
              reportId="registrations"
            />
            <TimeSeriesChart
              data={overview.education.enrollments}
              title="Course Enrolments"
              color={COLORS[1]}
              reportId="enrollments"
            />
            <TimeSeriesChart
              data={overview.education.completions}
              title="Course Completions"
              color={COLORS[2]}
              reportId="completions"
            />
            <TimeSeriesChart
              data={overview.education.lesson_completions}
              title="Lesson Completions"
              color={COLORS[3]}
              reportId="lesson_completions"
            />
            <TimeSeriesChart
              data={overview.education.exercise_submissions}
              title="Exercise Submissions"
              color={COLORS[4]}
              reportId="exercise_submissions"
            />
            <TimeSeriesChart
              data={overview.education.activity}
              title="Student Activity"
              color={COLORS[0]}
              reportId="registrations"
            />
            <TimeSeriesChart
              data={overview.competitions.registrations}
              title="Competition Registrations"
              color={COLORS[5]}
              reportId="competition_registrations"
            />
          </div>

          {/* Education & Engagement Breakdown */}
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Education Overview</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {overview.education && (
                  <>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Enrollment Completion Rate</span>
                      <span className="font-medium">{(overview.education.enrollment_completion_rate * 100).toFixed(1)}%</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Exercise Pass Rate</span>
                      <span className="font-medium">{(overview.education.exercise_pass_rate * 100).toFixed(1)}%</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Exercise Attempts (Total)</span>
                      <span className="font-medium">{overview.education.exercise_attempts?.total?.toLocaleString() || 0}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Exercise Attempts (Correct)</span>
                      <span className="font-medium">{overview.education.exercise_attempts?.correct?.toLocaleString() || 0}</span>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Engagement Overview</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {overview.students && (
                  <>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Total Students</span>
                      <span className="font-medium">{overview.students.total_students.toLocaleString()}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Engagement Rate</span>
                      <span className="font-medium">{(overview.students.engagement_rate * 100).toFixed(1)}%</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Active Students (Period)</span>
                      <span className="font-medium">{overview.students.active.length} data points</span>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Top Courses */}
          {overview.education?.top_courses && overview.education.top_courses.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Top Courses by Enrollment</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left px-4 py-2 font-medium text-muted-foreground">Course</th>
                        <th className="text-left px-4 py-2 font-medium text-muted-foreground">Track</th>
                        <th className="text-right px-4 py-2 font-medium text-muted-foreground">Learners</th>
                        <th className="text-right px-4 py-2 font-medium text-muted-foreground">Finishers</th>
                        <th className="text-right px-4 py-2 font-medium text-muted-foreground">Lessons</th>
                        <th className="text-right px-4 py-2 font-medium text-muted-foreground">Completion Rate</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y">
                      {overview.education.top_courses.map((course) => (
                        <tr key={course.id} className="hover:bg-muted/50">
                          <td className="px-4 py-2 font-medium">{course.title}</td>
                          <td className="px-4 py-2 text-muted-foreground">—</td>
                          <td className="text-right px-4 py-2">{course.learners.toLocaleString()}</td>
                          <td className="text-right px-4 py-2">{course.finishers.toLocaleString()}</td>
                          <td className="text-right px-4 py-2">{course.lesson_count}</td>
                          <td className="text-right px-4 py-2">{course.completion_rate.toFixed(1)}%</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Export All Reports */}
          <Card>
            <CardHeader>
              <CardTitle>Export Reports</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <p className="text-sm text-muted-foreground">
                Download any report as CSV for offline analysis.
              </p>
              <div className="flex flex-wrap gap-2">
                {ANALYTICS_REPORTS.map((report) => (
                  <Button
                    key={report.id}
                    variant="outline"
                    size="sm"
                    onClick={() => downloadAnalyticsCsv(report.id, { from, to })}
                  >
                    <Download className="mr-2 h-4 w-4" />
                    {report.label}
                  </Button>
                ))}
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}