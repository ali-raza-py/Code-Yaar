"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  AlertTriangle, BookOpen, Calendar, Clock, Eye, EyeOff, FileText, Loader2,
  MessageSquare, RotateCcw, Save, Shield, Tag, Trash2, X,
} from "lucide-react";
import { adminApi } from "@/lib/admin-api";
import type {
  StudioBundle, StudioChapter, StudioLesson, PublishChecklist, AuditLogAdmin, ExerciseAdmin,
} from "@/lib/admin-api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import CurriculumTree from "@/components/admin/studio/curriculum-tree";
import LessonEditor from "@/components/admin/studio/lesson-editor";
import { Input, Label, StudioError, StudioField, Textarea } from "@/components/admin/studio/studio-fields";
import { Skeleton } from "@/components/ui/skeleton";

type TabValue = "curriculum" | "checklist" | "settings" | "audit";

function TabButton({ value, label, activeTab, onClick }: { value: TabValue; label: string; activeTab: TabValue; onClick: (v: TabValue) => void }) {
  return (
    <Button
      variant={activeTab === value ? "default" : "ghost"}
      size="sm"
      onClick={() => onClick(value)}
      className="flex-1"
    >
      {label}
    </Button>
  );
}

function DialogWrapper({ open, onClose, children, title }: {
  open: boolean;
  onClose: () => void;
  children: React.ReactNode;
  title: string;
}) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="w-full max-w-lg rounded-lg bg-card p-6 shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">{title}</h3>
          <Button variant="ghost" size="icon" onClick={onClose}><X className="h-4 w-4" /></Button>
        </div>
        {children}
      </div>
    </div>
  );
}

export default function CourseStudioPage() {
  const params = useParams();
  const router = useRouter();
  const courseId = Number(params.id);

  const [bundle, setBundle] = useState<StudioBundle | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [checklist, setChecklist] = useState<PublishChecklist | null>(null);
  const [checklistLoading, setChecklistLoading] = useState(false);
  const [openLesson, setOpenLesson] = useState<StudioLesson | null>(null);
  const [chapterForLesson, setChapterForLesson] = useState<StudioChapter | null>(null);
  const [saving, setSaving] = useState(false);
  const [scheduleDialogOpen, setScheduleDialogOpen] = useState(false);
  const [scheduleDate, setScheduleDate] = useState("");
  const [archiveDialogOpen, setArchiveDialogOpen] = useState(false);
  const [archiveReason, setArchiveReason] = useState("");
  const [activeTab, setActiveTab] = useState<TabValue>("curriculum");

  // Settings tab state
  const [settingsDraft, setSettingsDraft] = useState<{
    title: string; subtitle: string; description: string;
    difficulty: string; track: number | ""; category: number | "";
  } | null>(null);
  const [settingsSaving, setSettingsSaving] = useState(false);
  const [tracks, setTracks] = useState<Array<{ id: number; title: string }>>([]);
  const [categories, setCategories] = useState<Array<{ id: number; title: string }>>([]);

  // Audit tab state
  const [auditLogs, setAuditLogs] = useState<AuditLogAdmin[]>([]);
  const [auditCount, setAuditCount] = useState(0);
  const [auditLoading, setAuditLoading] = useState(false);
  const [auditSearch, setAuditSearch] = useState("");
  const [auditActionFilter, setAuditActionFilter] = useState("");
  const [auditPage, setAuditPage] = useState(1);
  const AUDIT_PAGE_SIZE = 20;

  const reload = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const data = await adminApi.getStudioBundle(courseId);
      setBundle(data);
      await Promise.all([
        adminApi.listTracks({ page_size: 100 }).then(({ results }) => {
          setTracks((results || []).map((t) => ({ id: t.id, title: t.title })));
        }),
        adminApi.listCategories().then(({ results }) => {
          setCategories((results || []).map((c) => ({ id: c.id, title: c.title })));
        }),
      ]);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not load course studio.");
    } finally {
      setLoading(false);
    }
  }, [courseId]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    reload();
  }, [reload]);

  const handleReload = useCallback(async () => {
    await reload();
    if (openLesson) {
      const updated = bundle?.chapters.flatMap((c) => c.lessons).find((l) => l.id === openLesson.id);
      if (updated) {
        setOpenLesson(updated);
      } else {
        setOpenLesson(null);
      }
    }
  }, [reload, openLesson, bundle]);

  const loadChecklist = useCallback(async () => {
    setChecklistLoading(true);
    try {
      const data = await adminApi.getPublishChecklist(courseId);
      setChecklist(data);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not load checklist.");
    } finally {
      setChecklistLoading(false);
    }
  }, [courseId]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    if (bundle) {
      loadChecklist();
      const c = bundle.course;
      setSettingsDraft({
        title: c.title,
        subtitle: c.subtitle ?? "",
        description: c.description ?? "",
        difficulty: c.difficulty,
        track: c.track ?? "",
        category: c.category ?? "",
      });
    }
  }, [bundle, loadChecklist]);

  const handleSaveCourse = useCallback(async (data: Record<string, unknown>) => {
    setSaving(true);
    setError("");
    try {
      const saved = await adminApi.saveStudioCourse(courseId, data);
      setBundle(saved);
    } catch (caught) {
      if (caught instanceof Error && "status" in caught && (caught as { status: number }).status === 409) {
        setError("This course was changed elsewhere. Please reload.");
      } else {
        setError(caught instanceof Error ? caught.message : "Could not save course.");
      }
    } finally {
      setSaving(false);
    }
  }, [courseId]);

  const handlePublish = useCallback(async (force = false, reason = "") => {
    setSaving(true);
    setError("");
    try {
      await adminApi.publishStudioCourse(courseId, force ? { force: true, override_reason: reason } : {});
      await reload();
    } catch (caught) {
      if (caught instanceof Error && "status" in caught && (caught as { status: number }).status === 400) {
        const err = caught as { data?: { code: string; blocking?: Array<{ code: string; message: string }> } };
        if (err.data?.code === "publish_blocked" && err.data.blocking) {
          await loadChecklist();
        } else if (err.data?.code === "override_reason_required") {
          setError("Override reason is required to force publish.");
        } else {
          setError(caught instanceof Error ? caught.message : "Could not publish course.");
        }
      } else {
        setError(caught instanceof Error ? caught.message : "Could not publish course.");
      }
    } finally {
      setSaving(false);
    }
  }, [courseId, reload, loadChecklist]);

  const handleUnpublish = useCallback(async () => {
    setSaving(true);
    setError("");
    try {
      await adminApi.unpublishStudioCourse(courseId);
      await reload();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not unpublish course.");
    } finally {
      setSaving(false);
    }
  }, [courseId, reload]);

  const handleSchedule = useCallback(async () => {
    if (!scheduleDate) {
      setError("Please select a date and time.");
      return;
    }
    setSaving(true);
    setError("");
    try {
      await adminApi.scheduleStudioCourse(courseId, scheduleDate);
      setScheduleDialogOpen(false);
      setScheduleDate("");
      await reload();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not schedule course.");
    } finally {
      setSaving(false);
    }
  }, [courseId, scheduleDate, reload]);

  const handleUnschedule = useCallback(async () => {
    setSaving(true);
    setError("");
    try {
      await adminApi.unscheduleStudioCourse(courseId);
      await reload();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not unschedule course.");
    } finally {
      setSaving(false);
    }
  }, [courseId, reload]);

  const handleArchive = useCallback(async () => {
    setSaving(true);
    setError("");
    try {
      await adminApi.archiveStudioCourse(courseId, archiveReason || undefined);
      setArchiveDialogOpen(false);
      setArchiveReason("");
      router.replace("/admin/courses");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not archive course.");
    } finally {
      setSaving(false);
    }
  }, [courseId, archiveReason, router]);

  const handleUnarchive = useCallback(async () => {
    setSaving(true);
    setError("");
    try {
      await adminApi.unarchiveStudioCourse(courseId);
      await reload();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not unarchive course.");
    } finally {
      setSaving(false);
    }
  }, [courseId, reload]);

  const loadAuditLogs = useCallback(async () => {
    setAuditLoading(true);
    setError("");
    try {
      const query = new URLSearchParams({
        page: String(auditPage),
        page_size: String(AUDIT_PAGE_SIZE),
        ...(auditSearch ? { search: auditSearch } : {}),
      });
      const data = await adminApi.listAuditLogs({ page: auditPage, page_size: AUDIT_PAGE_SIZE, search: auditSearch || undefined });
      const pageData = typeof data === "object" && "results" in data ? data : { results: [], count: 0 };
      setAuditLogs((pageData as { results: AuditLogAdmin[]; count: number }).results);
      setAuditCount((pageData as { results: AuditLogAdmin[]; count: number }).count ?? 0);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not load audit log.");
    } finally {
      setAuditLoading(false);
    }
  }, [auditPage, auditSearch]);

  useEffect(() => {
    loadAuditLogs();
  }, [auditPage, auditSearch, loadAuditLogs]);

  const handleSaveSettings = useCallback(async () => {
    if (!settingsDraft) return;
    setSettingsSaving(true);
    setError("");
    try {
      const saved = await adminApi.saveStudioCourse(courseId, {
        course: {
          title: settingsDraft.title.trim(),
          subtitle: settingsDraft.subtitle.trim(),
          description: settingsDraft.description.trim(),
          difficulty: settingsDraft.difficulty,
          track: settingsDraft.track === "" ? undefined : settingsDraft.track,
          category: settingsDraft.category === "" ? undefined : settingsDraft.category,
        },
      });
      setBundle(saved);
      setSettingsDraft({
        title: saved.course.title,
        subtitle: saved.course.subtitle ?? "",
        description: saved.course.description ?? "",
        difficulty: saved.course.difficulty,
        track: saved.course.track ?? "",
        category: saved.course.category ?? "",
      });
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not save course settings.");
    } finally {
      setSettingsSaving(false);
    }
  }, [courseId, settingsDraft]);

  const openLessonEditor = useCallback((lesson: StudioLesson, chapter: StudioChapter) => {
    setChapterForLesson(chapter);
    setOpenLesson(lesson);
  }, []);

  const closeLessonEditor = useCallback(() => {
    setOpenLesson(null);
    setChapterForLesson(null);
  }, []);

  const handleLessonSaved = useCallback((savedLesson: StudioLesson) => {
    if (bundle) {
      const updatedChapters = bundle.chapters.map((c) => ({
        ...c,
        lessons: c.lessons.map((l) => (l.id === savedLesson.id ? savedLesson : l)),
      }));
      setBundle({ ...bundle, chapters: updatedChapters });
    }
    closeLessonEditor();
  }, [bundle, closeLessonEditor]);

  const chapterLessons = openLesson && chapterForLesson
    ? chapterForLesson.lessons
    : [];

  if (loading) {
    return (
      <div className="animate-pulse space-y-6">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-96" />
      </div>
    );
  }

  if (error && !bundle) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
        <AlertTriangle className="h-12 w-12 text-destructive" />
        <p className="text-center text-destructive">{error}</p>
        <Button variant="outline" onClick={reload}>Retry</Button>
      </div>
    );
  }

  if (!bundle) return null;

  const course = bundle.course;
  const canEdit = bundle.permissions.can_edit;
  const canPublish = bundle.permissions.can_publish;
  const isArchived = !!course.archived_at;

  const statusBadges = (
    <div className="flex flex-wrap items-center gap-2">
      {isArchived && <Badge variant="secondary">Archived</Badge>}
      {course.is_published && <Badge variant="default">Published</Badge>}
      {course.publish_at && !course.is_published && <Badge variant="outline">Scheduled</Badge>}
      {!course.is_published && !isArchived && !course.publish_at && <Badge variant="secondary">Draft</Badge>}
    </div>
  );

  const metadata = (
    <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
      <span className="flex items-center gap-1"><MessageSquare className="h-4 w-4" />{bundle.stats.chapter_count} chapters</span>
      <span className="flex items-center gap-1"><FileText className="h-4 w-4" />{bundle.stats.lesson_count} lessons</span>
      <span className="flex items-center gap-1"><Shield className="h-4 w-4" />{course.xp_completion_reward} XP</span>
      <span className="flex items-center gap-1"><Clock className="h-4 w-4" />{course.estimated_hours} hrs</span>
      {course.track_title && <span className="flex items-center gap-1"><BookOpen className="h-4 w-4" />{course.track_title}</span>}
      {course.category_title && <span className="flex items-center gap-1"><Tag className="h-4 w-4" />{course.category_title}</span>}
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">{course.title}</h1>
          <p className="mt-1 text-sm text-muted-foreground">{course.subtitle || "No subtitle set"}</p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {statusBadges}
          {canEdit && (
            <Button variant="outline" size="sm" onClick={() => handleSaveCourse({ subtitle: course.subtitle })}>
              <Save className="mr-2 h-4 w-4" />Save
            </Button>
          )}
        </div>
      </div>

      {error && <StudioError message={error} />}

      {/* Tab Navigation */}
      <div className="flex border-b">
        <TabButton value="curriculum" label="Curriculum" activeTab={activeTab} onClick={setActiveTab} />
        <TabButton value="checklist" label="Checklist" activeTab={activeTab} onClick={setActiveTab} />
        <TabButton value="settings" label="Settings" activeTab={activeTab} onClick={setActiveTab} />
        <TabButton value="audit" label="Audit" activeTab={activeTab} onClick={setActiveTab} />
      </div>

      {/* Curriculum Tab */}
      {activeTab === "curriculum" && (
          <CurriculumTree
            bundle={bundle}
            onReload={handleReload}
            onOpenLesson={openLessonEditor}
            onCreateLesson={(chapter: StudioChapter) => {
              const title = window.prompt("Lesson title");
              if (!title) return;
              adminApi.studioCreateLesson(courseId, {
                chapter: chapter.id,
                title: title.trim(),
                order: chapter.lessons.length + 1,
                content_body: "# Introduction\n\nStart writing here...",
                learning_objective: "Understand the key concepts.",
                is_active: false,
                duration_minutes: 10,
              }).then(handleReload).catch((e) => setError(e instanceof Error ? e.message : "Could not create lesson"));
            }}
            onCreateExercise={(lesson: StudioLesson) => {
              const title = window.prompt("Exercise title");
              if (!title) return;
              adminApi.studioCreateExercise(courseId, lesson.id, {
                title: title.trim(),
                exercise_type: "code",
                instructions: "Write your solution here.",
                language: "python",
                is_active: false,
                order: 1,
              }).then(handleReload).catch((e) => setError(e instanceof Error ? e.message : "Could not create exercise"));
            }}
            onUpdateExercise={(exercise) => {
              adminApi.studioUpdateExercise(courseId, exercise.lesson, exercise.id, {
                is_active: !exercise.is_active,
              }).then(handleReload).catch((e) => setError(e instanceof Error ? e.message : "Could not update exercise"));
            }}
            onDeleteExercise={(exercise) => {
              adminApi.studioDeleteExercise(courseId, exercise.lesson, exercise.id).then(handleReload).catch((e) => setError(e instanceof Error ? e.message : "Could not delete exercise"));
            }}
          />
      )}

      {/* Checklist Tab */}
      {activeTab === "checklist" && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              Publication Checklist
              {checklistLoading && <Loader2 className="h-4 w-4 animate-spin" />}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {checklist && (
              <>
                <div className="flex items-center gap-3">
                  <Badge variant={checklist.ok ? "default" : "destructive"}>
                    {checklist.ok ? "Ready to publish" : "Not ready"}
                  </Badge>
                  <span className="text-sm text-muted-foreground">
                    {checklist.blocking.length} blocking, {checklist.warnings.length} warnings
                  </span>
                </div>

                {checklist.blocking.length > 0 && (
                  <div className="space-y-2">
                    <h4 className="font-semibold text-destructive">Blocking issues (must fix)</h4>
                    {checklist.blocking.map((issue, i) => (
                      <div key={i} className="flex items-center gap-2 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700 dark:border-red-800 dark:bg-red-950 dark:text-red-200">
                        <AlertTriangle className="h-4 w-4 shrink-0" />
                        <div>
                          <p className="font-medium">{issue.message}</p>
                          <p className="text-xs text-red-600 dark:text-red-300">Code: {issue.code}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {checklist.warnings.length > 0 && (
                  <div className="space-y-2">
                    <h4 className="font-semibold text-amber-700">Warnings (advisory)</h4>
                    {checklist.warnings.map((issue, i) => (
                      <div key={i} className="flex items-center gap-2 rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-700 dark:border-amber-800 dark:bg-amber-950 dark:text-amber-200">
                        <AlertTriangle className="h-4 w-4 shrink-0" />
                        <div>
                          <p className="font-medium">{issue.message}</p>
                          <p className="text-xs text-amber-600 dark:text-amber-300">Code: {issue.code}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {checklist.ok && checklist.blocking.length === 0 && checklist.warnings.length === 0 && (
                  <p className="text-sm text-muted-foreground">All checks passed. The course is ready to publish.</p>
                )}
              </>
            )}
          </CardContent>
        </Card>
      )}

      {/* Settings Tab */}
      {activeTab === "settings" && (
        <div className="grid gap-6 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Course Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {settingsDraft ? (
                <form onSubmit={(e) => { e.preventDefault(); handleSaveSettings(); }} className="space-y-4">
                  <StudioField label="Title" htmlFor="course-title" required>
                    <Input
                      id="course-title"
                      value={settingsDraft.title}
                      onChange={(e) => setSettingsDraft((d) => d ? { ...d, title: e.target.value } : null)}
                      required
                      disabled={!canEdit}
                    />
                  </StudioField>
                  <StudioField label="Subtitle" htmlFor="course-subtitle">
                    <Input
                      id="course-subtitle"
                      value={settingsDraft.subtitle}
                      onChange={(e) => setSettingsDraft((d) => d ? { ...d, subtitle: e.target.value } : null)}
                      disabled={!canEdit}
                    />
                  </StudioField>
                  <StudioField label="Description" htmlFor="course-description">
                    <Textarea
                      id="course-description"
                      value={settingsDraft.description}
                      onChange={(e) => setSettingsDraft((d) => d ? { ...d, description: e.target.value } : null)}
                      rows={4}
                      disabled={!canEdit}
                    />
                  </StudioField>
                  <StudioField label="Difficulty" htmlFor="course-difficulty">
                    <select
                      id="course-difficulty"
                      className="mt-1 w-full rounded-md border bg-background px-3 py-2 text-sm"
                      value={settingsDraft.difficulty}
                      onChange={(e) => setSettingsDraft((d) => d ? { ...d, difficulty: e.target.value } : null)}
                      disabled={!canEdit}
                    >
                      <option value="beginner">Beginner</option>
                      <option value="elementary">Elementary</option>
                      <option value="intermediate">Intermediate</option>
                      <option value="advanced">Advanced</option>
                      <option value="expert">Expert</option>
                    </select>
                  </StudioField>
                  <StudioField label="Track" htmlFor="course-track">
                    <select
                      id="course-track"
                      className="mt-1 w-full rounded-md border bg-background px-3 py-2 text-sm"
                      value={settingsDraft.track}
                      onChange={(e) => {
                        const v = e.target.value;
                        setSettingsDraft((d) => d ? { ...d, track: v === "" ? "" : Number(v) } : null);
                      }}
                      disabled={!canEdit}
                    >
                      <option value="">— No track —</option>
                      {tracks.map((t) => (
                        <option key={t.id} value={t.id}>{t.title}</option>
                      ))}
                    </select>
                  </StudioField>
                  <StudioField label="Category" htmlFor="course-category">
                    <select
                      id="course-category"
                      className="mt-1 w-full rounded-md border bg-background px-3 py-2 text-sm"
                      value={settingsDraft.category}
                      onChange={(e) => {
                        const v = e.target.value;
                        setSettingsDraft((d) => d ? { ...d, category: v === "" ? "" : Number(v) } : null);
                      }}
                      disabled={!canEdit}
                    >
                      <option value="">— No category —</option>
                      {categories.map((c) => (
                        <option key={c.id} value={c.id}>{c.title}</option>
                      ))}
                    </select>
                  </StudioField>
                  <div className="flex justify-end pt-4 border-t">
                    <Button
                      type="submit"
                      disabled={settingsSaving || !canEdit}
                    >
                      {settingsSaving ? <Save className="mr-2 h-4 w-4 animate-spin" /> : <Save className="mr-2 h-4 w-4" />} Save changes
                    </Button>
                  </div>
                </form>
              ) : (
                <Skeleton className="h-96" />
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Publication Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <h4 className="font-medium">Publish</h4>
                <p className="text-sm text-muted-foreground">
                  {course.is_published
                    ? "This course is live. Unpublishing returns it to draft."
                    : "Publish makes the course visible to learners."}
                </p>
                <div className="flex flex-wrap gap-2">
                  {course.is_published ? (
                    <Button
                      variant="outline"
                      onClick={handleUnpublish}
                      disabled={saving || !canPublish}
                    >
                      <EyeOff className="mr-2 h-4 w-4" />Unpublish
                    </Button>
                  ) : (
                    <>
                      <Button
                        onClick={() => handlePublish(false)}
                        disabled={saving || !canPublish}
                      >
                        <Eye className="mr-2 h-4 w-4" />Publish
                      </Button>
                      {canPublish && (
                        <Button variant="outline" onClick={() => setScheduleDialogOpen(true)}>
                          <Calendar className="mr-2 h-4 w-4" />Schedule
                        </Button>
                      )}
                    </>
                  )}
                </div>
              </div>

              {course.publish_at && !course.is_published && (
                <div className="space-y-2">
                  <h4 className="font-medium">Scheduled Publication</h4>
                  <p className="text-sm text-muted-foreground">Scheduled for {new Date(course.publish_at).toLocaleString()}</p>
                  <Button variant="outline" onClick={handleUnschedule} disabled={saving}>
                    <RotateCcw className="mr-2 h-4 w-4" />Unschedule
                  </Button>
                </div>
              )}

              <div className="space-y-2">
                <h4 className="font-medium">Archive</h4>
                <p className="text-sm text-muted-foreground">
                  {isArchived
                    ? "This course is archived. Unarchiving restores it."
                    : "Archiving hides the course from the catalogue but preserves all content."}
                </p>
                <div className="flex flex-wrap gap-2">
                  {isArchived ? (
                    <Button variant="outline" onClick={handleUnarchive} disabled={saving}>
                      <RotateCcw className="mr-2 h-4 w-4" />Unarchive
                    </Button>
                  ) : (
                    <Button variant="destructive" onClick={() => setArchiveDialogOpen(true)} disabled={saving}>
                      <Trash2 className="mr-2 h-4 w-4" />Archive
                    </Button>
                  )}
                </div>
              </div>

              <div className="space-y-2 pt-4 border-t">
                <h4 className="font-medium">Course Statistics</h4>
                <div className="grid gap-2 sm:grid-cols-2 text-sm">
                  <div className="flex justify-between"><span className="text-muted-foreground">Enrollments</span><span>{bundle.stats.enrollment_count}</span></div>
                  <div className="flex justify-between"><span className="text-muted-foreground">Completions</span><span>{bundle.stats.completion_count}</span></div>
                  <div className="flex justify-between"><span className="text-muted-foreground">Total XP</span><span>{bundle.stats.total_xp}</span></div>
                  <div className="flex justify-between"><span className="text-muted-foreground">Published Lessons</span><span>{bundle.stats.published_lesson_count} / {bundle.stats.lesson_count}</span></div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Audit Tab */}
      {activeTab === "audit" && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              Audit Trail
              {auditLoading && <Loader2 className="h-4 w-4 animate-spin" />}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-wrap gap-2">
              <div className="relative">
                <Input
                  id="audit-search"
                  value={auditSearch}
                  onChange={(e) => { setAuditSearch(e.target.value); setAuditPage(1); }}
                  placeholder="Search admin, action, target…"
                  className="w-full md:w-80"
                />
              </div>
              <select
                value={auditActionFilter}
                onChange={(e) => { setAuditActionFilter(e.target.value); setAuditPage(1); }}
                className="mt-1 w-full rounded-md border bg-background px-3 py-2 text-sm"
              >
                <option value="">All actions</option>
              </select>
            </div>

            {auditLoading ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="h-6 w-6 animate-spin" />
              </div>
            ) : auditLogs.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-8 text-muted-foreground">
                <AlertTriangle className="h-8 w-8 mb-2" />
                <p>No audit records for this course.</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b bg-muted/50">
                      <th className="text-left px-4 py-2 font-medium text-muted-foreground">Admin</th>
                      <th className="text-left px-4 py-2 font-medium text-muted-foreground">Action</th>
                      <th className="text-left px-4 py-2 font-medium text-muted-foreground">Content affected</th>
                      <th className="text-left px-4 py-2 font-medium text-muted-foreground">Date / time</th>
                      <th className="text-left px-4 py-2 font-medium text-muted-foreground">Previous → Updated</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {auditLogs.map((row) => {
                      const detail = row.metadata || {};
                      const fields = detail.fields;
                      const label = typeof detail.label === 'string' ? detail.label : '';
                      const changed = fields && Array.isArray(fields)
                        ? `fields: ${(fields as unknown[]).join(", ")}`
                        : (label || '—');
                      return (
                        <tr key={row.id} className="hover:bg-muted/50 group">
                          <td className="px-4 py-2">{row.admin_name}</td>
                          <td className="px-4 py-2 font-mono text-xs">{row.action}</td>
                          <td className="px-4 py-2">{row.target_repr}</td>
                          <td className="px-4 py-2 text-muted-foreground">{new Date(row.timestamp).toLocaleString()}</td>
                          <td className="px-4 py-2 text-xs text-muted-foreground truncate" style={{ maxWidth: 200 }}>
                            {changed}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
                <div className="flex items-center justify-between mt-3">
                  <span className="text-sm text-muted-foreground">
                    Showing {(auditPage - 1) * AUDIT_PAGE_SIZE + 1} to {Math.min(auditPage * AUDIT_PAGE_SIZE, auditCount)} of {auditCount}
                  </span>
                  <div className="flex items-center gap-1">
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={auditPage === 1}
                      onClick={() => setAuditPage((p) => p - 1)}
                    >
                      ←
                    </Button>
                    <span className="px-2 text-sm text-muted-foreground">Page {auditPage}</span>
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={auditPage * AUDIT_PAGE_SIZE >= auditCount}
                      onClick={() => setAuditPage((p) => p + 1)}
                    >
                      →
                    </Button>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Schedule Dialog */}
      <DialogWrapper open={scheduleDialogOpen} onClose={() => setScheduleDialogOpen(false)} title="Schedule Publication">
        <div className="space-y-4">
          <p className="text-sm text-muted-foreground">Choose when the course should go live.</p>
          <StudioField label="Publish at" htmlFor="schedule-date" required>
            <Input id="schedule-date" type="datetime-local" value={scheduleDate} onChange={(e) => setScheduleDate(e.target.value)} />
          </StudioField>
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setScheduleDialogOpen(false)}>Cancel</Button>
            <Button onClick={handleSchedule} disabled={saving}>Schedule</Button>
          </div>
        </div>
      </DialogWrapper>

      {/* Archive Dialog */}
      <DialogWrapper open={archiveDialogOpen} onClose={() => setArchiveDialogOpen(false)} title="Archive Course">
        <div className="space-y-4">
          <p className="text-sm text-muted-foreground">This hides the course from the catalogue. All content is preserved.</p>
          <StudioField label="Reason (optional)" htmlFor="archive-reason">
            <Textarea id="archive-reason" value={archiveReason} onChange={(e) => setArchiveReason(e.target.value)} rows={3} placeholder="Why are you archiving this course?" />
          </StudioField>
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setArchiveDialogOpen(false)}>Cancel</Button>
            <Button variant="destructive" onClick={handleArchive} disabled={saving}>Archive</Button>
          </div>
        </div>
      </DialogWrapper>

      {/* Lesson Editor Dialog */}
      {openLesson && chapterForLesson && (
        <DialogWrapper open onClose={closeLessonEditor} title={`Editing: ${openLesson.title}`}>
          <LessonEditor
            courseId={courseId}
            lesson={openLesson}
            chapterLessons={chapterLessons}
            onSaved={handleLessonSaved}
            onClose={closeLessonEditor}
          />
        </DialogWrapper>
      )}
    </div>
  );
}