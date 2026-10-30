"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { AlertCircle, CheckCircle2, MailWarning, ShieldCheck } from "lucide-react";
import { useAuth } from "@/hooks/use-auth";
import { ApiError, auth } from "@/lib/api";

type Tab = "account" | "profile" | "password" | "preferences";

type Message = { type: "success" | "error"; text: string } | null;

const fieldClass =
  "w-full rounded-lg border border-border px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary";

const EDUCATION_LEVELS = [
  { value: "school", label: "School" },
  { value: "high_school", label: "High school" },
  { value: "undergraduate", label: "Undergraduate" },
  { value: "graduate", label: "Graduate" },
  { value: "bootcamp", label: "Bootcamp" },
  { value: "self_taught", label: "Self taught" },
  { value: "other", label: "Other" },
];

const ROLE_LABELS: Record<string, string> = {
  student: "Student",
  instructor: "Instructor",
  administrator: "Administrator",
};

function FieldError({ messages }: { messages?: string[] }) {
  if (!messages?.length) return null;
  return (
    <p className="mt-1 flex items-start gap-1.5 text-xs text-destructive">
      <AlertCircle className="mt-0.5 h-3.5 w-3.5 shrink-0" aria-hidden="true" />
      <span>{messages[0]}</span>
    </p>
  );
}

function Notice({ message }: { message: Message }) {
  if (!message) return null;
  const success = message.type === "success";
  return (
    <p
      role={success ? "status" : "alert"}
      className={`flex items-start gap-1.5 text-sm ${success ? "text-primary" : "text-destructive"}`}
    >
      {success ? (
        <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
      ) : (
        <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
      )}
      <span>{message.text}</span>
    </p>
  );
}

export default function SettingsPage() {
  const { user, profile, emailVerified, updateProfile, refresh } = useAuth();

  const [tab, setTab] = useState<Tab>("account");

  // Account
  const [accountForm, setAccountForm] = useState({
    username: "",
    email: "",
    first_name: "",
    last_name: "",
  });
  const [accountSaving, setAccountSaving] = useState(false);
  const [accountMsg, setAccountMsg] = useState<Message>(null);
  const [accountErrors, setAccountErrors] = useState<Record<string, string[]> | undefined>();

  // Profile
  const [profileForm, setProfileForm] = useState({
    avatar: "",
    bio: "",
    institution: "",
    education_level: "",
    github_url: "",
    linkedin_url: "",
  });
  const [profileSaving, setProfileSaving] = useState(false);
  const [profileMsg, setProfileMsg] = useState<Message>(null);
  const [profileErrors, setProfileErrors] = useState<Record<string, string[]> | undefined>();

  // Password
  const [passwordForm, setPasswordForm] = useState({
    current_password: "",
    new_password: "",
    confirm_password: "",
  });
  const [passwordSaving, setPasswordSaving] = useState(false);
  const [passwordMsg, setPasswordMsg] = useState<Message>(null);
  const [passwordErrors, setPasswordErrors] = useState<Record<string, string[]> | undefined>();

  // Email verification
  const [resendState, setResendState] = useState<"idle" | "sending" | "sent">("idle");

  // Preferences stay local to this browser; they are not account data.
  const [prefs, setPrefs] = useState({
    theme: "light",
    email_notifications: true,
    streak_reminders: true,
    weekly_digest: false,
    language: "en",
    code_font_size: "14",
    auto_save: true,
  });
  const [prefsSaving, setPrefsSaving] = useState(false);
  const [prefsMsg, setPrefsMsg] = useState<Message>(null);

  const requestedProfile = useRef(false);

  // The route guard guarantees a user; the profile payload can still be
  // missing if the first `/auth/me/` call failed. Retry once.
  useEffect(() => {
    if (profile || requestedProfile.current) return;
    requestedProfile.current = true;
    void refresh();
  }, [profile, refresh]);

  useEffect(() => {
    if (!user) return;
    // Deferred through a microtask so the effect never sets state synchronously.
    Promise.resolve().then(() =>
      setAccountForm({
        username: user.username,
        email: user.email,
        first_name: user.first_name ?? "",
        last_name: user.last_name ?? "",
      })
    );
  }, [user]);

  useEffect(() => {
    if (!profile) return;
    Promise.resolve().then(() =>
      setProfileForm({
        avatar: profile.avatar ?? "",
        bio: profile.bio ?? "",
        institution: profile.institution ?? "",
        education_level: profile.education_level ?? "",
        github_url: profile.github_url ?? "",
        linkedin_url: profile.linkedin_url ?? "",
      })
    );
  }, [profile]);

  useEffect(() => {
    let cancelled = false;
    Promise.resolve(window.localStorage.getItem("user_preferences")).then((saved) => {
      if (!saved || cancelled) return;
      try {
        setPrefs((current) => ({ ...current, ...JSON.parse(saved) }));
      } catch {
        /* keep defaults */
      }
    });
    return () => {
      cancelled = true;
    };
  }, []);

  const handleSaveAccount = useCallback(async () => {
    setAccountSaving(true);
    setAccountMsg(null);
    setAccountErrors(undefined);
    try {
      const me = await updateProfile({
        username: accountForm.username.trim(),
        email: accountForm.email.trim(),
        first_name: accountForm.first_name.trim(),
        last_name: accountForm.last_name.trim(),
      });
      setAccountMsg({
        type: "success",
        text: me.email_changed
          ? "Saved. We sent a confirmation link to your new address — verify it to finish the change."
          : "Account settings saved.",
      });
      if (me.email_changed) setResendState("sent");
    } catch (caught) {
      if (caught instanceof ApiError) {
        setAccountMsg({ type: "error", text: caught.message });
        setAccountErrors(caught.fieldErrors);
      } else {
        setAccountMsg({ type: "error", text: "We couldn't save your changes." });
      }
    } finally {
      setAccountSaving(false);
    }
  }, [accountForm, updateProfile]);

  const handleSaveProfile = useCallback(async () => {
    setProfileSaving(true);
    setProfileMsg(null);
    setProfileErrors(undefined);
    try {
      // `role`, `is_staff` and `is_superuser` are rejected by the API on
      // purpose: privilege is granted by administrators, never self-assigned.
      await updateProfile({
        avatar: profileForm.avatar.trim(),
        bio: profileForm.bio,
        institution: profileForm.institution.trim(),
        education_level: profileForm.education_level,
        github_url: profileForm.github_url.trim(),
        linkedin_url: profileForm.linkedin_url.trim(),
      });
      setProfileMsg({ type: "success", text: "Profile updated." });
    } catch (caught) {
      if (caught instanceof ApiError) {
        setProfileMsg({ type: "error", text: caught.message });
        setProfileErrors(caught.fieldErrors);
      } else {
        setProfileMsg({ type: "error", text: "We couldn't save your profile." });
      }
    } finally {
      setProfileSaving(false);
    }
  }, [profileForm, updateProfile]);

  const handleChangePassword = useCallback(async () => {
    setPasswordMsg(null);
    setPasswordErrors(undefined);

    if (passwordForm.new_password !== passwordForm.confirm_password) {
      setPasswordErrors({ confirm_password: ["Passwords do not match."] });
      return;
    }

    setPasswordSaving(true);
    try {
      await auth.changePassword({
        current_password: passwordForm.current_password,
        new_password: passwordForm.new_password,
        confirm_password: passwordForm.confirm_password,
      });
      setPasswordForm({ current_password: "", new_password: "", confirm_password: "" });
      setPasswordMsg({
        type: "success",
        text: "Password changed. Every other device has been signed out.",
      });
    } catch (caught) {
      if (caught instanceof ApiError) {
        setPasswordMsg({ type: "error", text: caught.message });
        setPasswordErrors(caught.fieldErrors);
      } else {
        setPasswordMsg({ type: "error", text: "We couldn't change your password." });
      }
    } finally {
      setPasswordSaving(false);
    }
  }, [passwordForm]);

  const handleResendVerification = useCallback(async () => {
    setResendState("sending");
    try {
      await auth.resendVerification();
    } catch {
      /* the API always answers generically; nothing useful to surface */
    } finally {
      setResendState("sent");
    }
  }, []);

  const handleSavePrefs = useCallback(() => {
    setPrefsSaving(true);
    try {
      window.localStorage.setItem("user_preferences", JSON.stringify(prefs));
      document.documentElement.classList.toggle("dark", prefs.theme === "dark");
      setPrefsMsg({ type: "success", text: "Preferences saved." });
    } catch {
      setPrefsMsg({ type: "error", text: "Failed to save preferences." });
    } finally {
      setPrefsSaving(false);
    }
  }, [prefs]);

  const tabs: { id: Tab; label: string; icon: string }[] = [
    { id: "account", label: "Account", icon: "M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" },
    { id: "profile", label: "Profile", icon: "M17.982 18.725A7.488 7.488 0 0012 15.75a7.488 7.488 0 00-5.982 2.975m11.963 0a9 9 0 10-11.963 0m11.963 0A8.966 8.966 0 0112 21a8.966 8.966 0 01-5.982-2.275M15 9.75a3 3 0 11-6 0 3 3 0 016 0z" },
    { id: "password", label: "Password", icon: "M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" },
    { id: "preferences", label: "Preferences", icon: "M10.343 3.94c.09-.542.56-.94 1.11-.94h1.093c.55 0 1.02.398 1.11.94l.149.894c.07.424.384.764.78.93.398.164.855.142 1.205-.108l.737-.527a1.125 1.125 0 011.45.12l.773.774c.39.389.44 1.002.12 1.45l-.527.737c-.25.35-.272.806-.107 1.204.165.397.505.71.93.78l.893.15c.543.09.94.56.94 1.109v1.094c0 .55-.397 1.02-.94 1.11l-.893.149c-.425.07-.765.383-.93.78-.165.398-.143.854.107 1.204l.527.738c.32.447.269 1.06-.12 1.45l-.774.773a1.125 1.125 0 01-1.449.12l-.738-.527c-.35-.25-.806-.272-1.203-.107-.397.165-.71.505-.781.929l-.149.894c-.09.542-.56.94-1.11.94h-1.094c-.55 0-1.019-.398-1.11-.94l-.148-.894c-.071-.424-.384-.764-.781-.93-.398-.164-.854-.142-1.204.108l-.738.527c-.447.32-1.06.269-1.45-.12l-.773-.774a1.125 1.125 0 01-.12-1.45l.527-.737c.25-.35.273-.806.108-1.204-.165-.397-.505-.71-.93-.78l-.894-.15c-.542-.09-.94-.56-.94-1.109v-1.094c0-.55.398-1.02.94-1.11l.894-.149c.424-.07.765-.383.93-.78.165-.398.143-.854-.107-1.204l-.527-.738a1.125 1.125 0 01.12-1.45l.773-.773a1.125 1.125 0 011.45-.12l.737.527c.35.25.807.272 1.204.107.397-.165.71-.505.78-.929l.15-.894z" },
  ];

  const displayName = user?.full_name || user?.username || "";
  const memberSince = user?.date_joined
    ? new Date(user.date_joined).toLocaleDateString(undefined, {
        year: "numeric",
        month: "long",
        day: "numeric",
      })
    : null;

  return (
    <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-8">
        <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-primary/25 bg-primary/10 px-3 py-1 text-xs font-medium text-primary">
          <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.324.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 011.37.49l1.296 2.247a1.125 1.125 0 01-.26 1.431l-1.003.827c-.293.24-.438.613-.431.992a6.759 6.759 0 010 .255c-.007.378.138.75.43.99l1.005.828c.424.35.534.954.26 1.43l-1.298 2.247a1.125 1.125 0 01-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.57 6.57 0 01-.22.128c-.331.183-.581.495-.644.869l-.213 1.28c-.09.543-.56.941-1.11.941h-2.594c-.55 0-1.02-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 01-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 01-1.369-.49l-1.297-2.247a1.125 1.125 0 01.26-1.431l1.004-.827c.292-.24.437-.613.43-.992a6.932 6.932 0 010-.255c.007-.378-.138-.75-.43-.99l-1.004-.828a1.125 1.125 0 01-.26-1.43l1.297-2.247a1.125 1.125 0 011.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.087.22-.128.332-.183.582-.495.644-.869l.214-1.281z" />
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          SETTINGS
        </div>
        <h1 className="text-3xl font-bold tracking-tight text-foreground">Settings</h1>
        <p className="mt-2 text-muted-foreground">
          Manage your account, public profile, and security.
        </p>
      </div>

      {!emailVerified && (
        <div className="mb-6 flex flex-col gap-3 rounded-xl border border-amber-300/60 bg-amber-50 p-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-start gap-3">
            <MailWarning className="mt-0.5 h-5 w-5 shrink-0 text-amber-600" aria-hidden="true" />
            <div>
              <p className="text-sm font-semibold text-amber-900">Verify your email address</p>
              <p className="text-xs text-amber-800">
                We sent a confirmation link when you signed up. Some features stay locked until your
                address is confirmed.
              </p>
            </div>
          </div>
          {resendState === "sent" ? (
            <span className="text-xs font-medium text-amber-800">Link sent — check your inbox.</span>
          ) : (
            <button
              type="button"
              onClick={handleResendVerification}
              disabled={resendState === "sending"}
              className="shrink-0 rounded-lg border border-amber-300 bg-white px-3 py-2 text-xs font-semibold text-amber-900 transition-colors hover:bg-amber-100 disabled:opacity-60"
            >
              {resendState === "sending" ? "Sending…" : "Resend link"}
            </button>
          )}
        </div>
      )}

      <div className="flex flex-col gap-8 sm:flex-row">
        <div className="shrink-0 sm:w-48">
          <nav className="flex gap-1 overflow-x-auto sm:flex-col">
            {tabs.map((t) => (
              <button
                key={t.id}
                onClick={() => setTab(t.id)}
                className={`flex items-center gap-2 whitespace-nowrap rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                  tab === t.id
                    ? "bg-primary/10 text-primary"
                    : "text-muted-foreground hover:bg-muted/60 hover:text-foreground"
                }`}
              >
                <svg className="h-4 w-4 shrink-0" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d={t.icon} />
                </svg>
                {t.label}
              </button>
            ))}
          </nav>
        </div>

        <div className="min-w-0 flex-1">
          {tab === "account" && (
            <div className="rounded-xl border border-border bg-card p-6">
              <h2 className="mb-1 text-lg font-semibold text-foreground">Account settings</h2>
              <p className="mb-6 text-sm text-muted-foreground">
                Update your username, email address, and display name.
              </p>

              <div className="space-y-4">
                <div>
                  <label className="mb-1 block text-sm font-medium text-muted-foreground">
                    Username
                  </label>
                  <input
                    type="text"
                    value={accountForm.username}
                    onChange={(e) => setAccountForm((f) => ({ ...f, username: e.target.value }))}
                    className={fieldClass}
                    autoComplete="username"
                  />
                  <FieldError messages={accountErrors?.username} />
                </div>

                <div>
                  <label className="mb-1 block text-sm font-medium text-muted-foreground">
                    Email
                  </label>
                  <input
                    type="email"
                    value={accountForm.email}
                    onChange={(e) => setAccountForm((f) => ({ ...f, email: e.target.value }))}
                    className={fieldClass}
                    autoComplete="email"
                  />
                  <FieldError messages={accountErrors?.email} />
                  <p className="mt-1 flex items-center gap-1.5 text-xs text-muted-foreground">
                    {emailVerified ? (
                      <>
                        <ShieldCheck className="h-3.5 w-3.5 text-primary" aria-hidden="true" />
                        Verified
                      </>
                    ) : (
                      "Not verified yet"
                    )}
                  </p>
                </div>

                <div className="grid gap-4 sm:grid-cols-2">
                  <div>
                    <label className="mb-1 block text-sm font-medium text-muted-foreground">
                      First name
                    </label>
                    <input
                      type="text"
                      value={accountForm.first_name}
                      onChange={(e) => setAccountForm((f) => ({ ...f, first_name: e.target.value }))}
                      className={fieldClass}
                      autoComplete="given-name"
                    />
                    <FieldError messages={accountErrors?.first_name} />
                  </div>
                  <div>
                    <label className="mb-1 block text-sm font-medium text-muted-foreground">
                      Last name
                    </label>
                    <input
                      type="text"
                      value={accountForm.last_name}
                      onChange={(e) => setAccountForm((f) => ({ ...f, last_name: e.target.value }))}
                      className={fieldClass}
                      autoComplete="family-name"
                    />
                    <FieldError messages={accountErrors?.last_name} />
                  </div>
                </div>

                <Notice message={accountMsg} />

                <button
                  onClick={handleSaveAccount}
                  disabled={accountSaving}
                  className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground transition-colors hover:bg-primary/90 disabled:opacity-50"
                >
                  {accountSaving ? "Saving..." : "Save changes"}
                </button>
              </div>
            </div>
          )}

          {tab === "profile" && (
            <div className="rounded-xl border border-border bg-card p-6">
              <h2 className="mb-1 text-lg font-semibold text-foreground">Public profile</h2>
              <p className="mb-6 text-sm text-muted-foreground">
                Customize how others see you on Code-Yaar.
              </p>

              <div className="space-y-4">
                <div>
                  <label className="mb-1 block text-sm font-medium text-muted-foreground">
                    Avatar URL
                  </label>
                  <input
                    type="url"
                    value={profileForm.avatar}
                    onChange={(e) => setProfileForm((p) => ({ ...p, avatar: e.target.value }))}
                    placeholder="https://example.com/avatar.jpg"
                    className={fieldClass}
                  />
                  <FieldError messages={profileErrors?.avatar} />
                  {profileForm.avatar && (
                    <div className="mt-2 flex items-center gap-3">
                      <div className="h-12 w-12 overflow-hidden rounded-full bg-muted">
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img
                          src={profileForm.avatar}
                          alt="Avatar preview"
                          className="h-full w-full object-cover"
                        />
                      </div>
                      <span className="text-xs text-muted-foreground">Preview</span>
                    </div>
                  )}
                </div>

                <div>
                  <label className="mb-1 block text-sm font-medium text-muted-foreground">Bio</label>
                  <textarea
                    value={profileForm.bio}
                    onChange={(e) => setProfileForm((p) => ({ ...p, bio: e.target.value }))}
                    rows={3}
                    placeholder="Tell us about yourself..."
                    className={`${fieldClass} resize-none`}
                  />
                  <FieldError messages={profileErrors?.bio} />
                </div>

                <div className="grid gap-4 sm:grid-cols-2">
                  <div>
                    <label className="mb-1 block text-sm font-medium text-muted-foreground">
                      Institution
                    </label>
                    <input
                      type="text"
                      value={profileForm.institution}
                      onChange={(e) =>
                        setProfileForm((p) => ({ ...p, institution: e.target.value }))
                      }
                      placeholder="University or company"
                      className={fieldClass}
                    />
                    <FieldError messages={profileErrors?.institution} />
                  </div>
                  <div>
                    <label className="mb-1 block text-sm font-medium text-muted-foreground">
                      Education level
                    </label>
                    <select
                      value={profileForm.education_level}
                      onChange={(e) =>
                        setProfileForm((p) => ({ ...p, education_level: e.target.value }))
                      }
                      className={fieldClass}
                    >
                      <option value="">Not specified</option>
                      {EDUCATION_LEVELS.map((level) => (
                        <option key={level.value} value={level.value}>
                          {level.label}
                        </option>
                      ))}
                    </select>
                    <FieldError messages={profileErrors?.education_level} />
                  </div>
                </div>

                <div className="grid gap-4 sm:grid-cols-2">
                  <div>
                    <label className="mb-1 block text-sm font-medium text-muted-foreground">
                      GitHub
                    </label>
                    <input
                      type="url"
                      value={profileForm.github_url}
                      onChange={(e) => setProfileForm((p) => ({ ...p, github_url: e.target.value }))}
                      placeholder="https://github.com/you"
                      className={fieldClass}
                    />
                    <FieldError messages={profileErrors?.github_url} />
                  </div>
                  <div>
                    <label className="mb-1 block text-sm font-medium text-muted-foreground">
                      LinkedIn
                    </label>
                    <input
                      type="url"
                      value={profileForm.linkedin_url}
                      onChange={(e) =>
                        setProfileForm((p) => ({ ...p, linkedin_url: e.target.value }))
                      }
                      placeholder="https://linkedin.com/in/you"
                      className={fieldClass}
                    />
                    <FieldError messages={profileErrors?.linkedin_url} />
                  </div>
                </div>

                <div className="rounded-lg border border-border bg-muted/40 p-3">
                  <p className="text-xs text-muted-foreground">
                    <span className="font-semibold text-foreground">
                      {ROLE_LABELS[profile?.role ?? user?.role ?? "student"] ?? "Student"}
                    </span>
                    {memberSince ? ` · Member since ${memberSince}` : ""}
                  </p>
                  <p className="mt-1 text-xs text-muted-foreground">
                    Your role is assigned by Code-Yaar and can&apos;t be changed from your profile.
                  </p>
                </div>

                <Notice message={profileMsg} />

                <button
                  onClick={handleSaveProfile}
                  disabled={profileSaving}
                  className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground transition-colors hover:bg-primary/90 disabled:opacity-50"
                >
                  {profileSaving ? "Saving..." : "Save profile"}
                </button>
              </div>
            </div>
          )}

          {tab === "password" && (
            <div className="rounded-xl border border-border bg-card p-6">
              <h2 className="mb-1 text-lg font-semibold text-foreground">Change password</h2>
              <p className="mb-6 text-sm text-muted-foreground">
                Changing your password signs out every other device.
              </p>

              <div className="max-w-md space-y-4">
                <div>
                  <label className="mb-1 block text-sm font-medium text-muted-foreground">
                    Current password
                  </label>
                  <input
                    type="password"
                    value={passwordForm.current_password}
                    onChange={(e) =>
                      setPasswordForm((f) => ({ ...f, current_password: e.target.value }))
                    }
                    className={fieldClass}
                    autoComplete="current-password"
                  />
                  <FieldError messages={passwordErrors?.current_password} />
                </div>

                <div>
                  <label className="mb-1 block text-sm font-medium text-muted-foreground">
                    New password
                  </label>
                  <input
                    type="password"
                    value={passwordForm.new_password}
                    onChange={(e) =>
                      setPasswordForm((f) => ({ ...f, new_password: e.target.value }))
                    }
                    className={fieldClass}
                    autoComplete="new-password"
                  />
                  <FieldError messages={passwordErrors?.new_password} />
                  <p className="mt-1 text-xs text-muted-foreground">
                    At least 8 characters, and not a common or numeric-only password.
                  </p>
                </div>

                <div>
                  <label className="mb-1 block text-sm font-medium text-muted-foreground">
                    Confirm new password
                  </label>
                  <input
                    type="password"
                    value={passwordForm.confirm_password}
                    onChange={(e) =>
                      setPasswordForm((f) => ({ ...f, confirm_password: e.target.value }))
                    }
                    className={fieldClass}
                    autoComplete="new-password"
                  />
                  <FieldError
                    messages={
                      passwordErrors?.confirm_password ??
                      (passwordForm.confirm_password &&
                      passwordForm.new_password !== passwordForm.confirm_password
                        ? ["Passwords do not match."]
                        : undefined)
                    }
                  />
                </div>

                <Notice message={passwordMsg} />

                <button
                  onClick={handleChangePassword}
                  disabled={
                    passwordSaving ||
                    !passwordForm.current_password ||
                    !passwordForm.new_password ||
                    !passwordForm.confirm_password
                  }
                  className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground transition-colors hover:bg-primary/90 disabled:opacity-50"
                >
                  {passwordSaving ? "Changing..." : "Change password"}
                </button>
              </div>
            </div>
          )}

          {tab === "preferences" && (
            <div className="rounded-xl border border-border bg-card p-6">
              <h2 className="mb-1 text-lg font-semibold text-foreground">Preferences</h2>
              <p className="mb-6 text-sm text-muted-foreground">
                Customize your learning experience. These stay on this device.
              </p>

              <div className="space-y-6">
                <div>
                  <label className="mb-2 block text-sm font-medium text-muted-foreground">
                    Theme
                  </label>
                  <div className="flex gap-3">
                    {(["light", "dark", "system"] as const).map((theme) => (
                      <button
                        key={theme}
                        onClick={() => setPrefs((p) => ({ ...p, theme }))}
                        className={`rounded-lg border px-4 py-2 text-sm font-medium capitalize transition-colors ${
                          prefs.theme === theme
                            ? "border-primary/30 bg-primary/10 text-primary"
                            : "border-border bg-card text-muted-foreground hover:bg-muted/60"
                        }`}
                      >
                        {theme}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="mb-1 block text-sm font-medium text-muted-foreground">
                    Code editor font size
                  </label>
                  <select
                    value={prefs.code_font_size}
                    onChange={(e) => setPrefs((p) => ({ ...p, code_font_size: e.target.value }))}
                    className="rounded-lg border border-border px-3 py-2 text-sm text-foreground focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
                  >
                    <option value="12">12px</option>
                    <option value="14">14px</option>
                    <option value="16">16px</option>
                    <option value="18">18px</option>
                  </select>
                </div>

                <div className="space-y-3">
                  {[
                    { key: "email_notifications" as const, label: "Email notifications", desc: "Receive updates about your progress" },
                    { key: "streak_reminders" as const, label: "Streak reminders", desc: "Get reminded to maintain your streak" },
                    { key: "weekly_digest" as const, label: "Weekly digest", desc: "Weekly summary of community activity" },
                    { key: "auto_save" as const, label: "Auto-save code", desc: "Automatically save your code while editing" },
                  ].map((item) => (
                    <div key={item.key} className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-foreground">{item.label}</p>
                        <p className="text-xs text-muted-foreground">{item.desc}</p>
                      </div>
                      <button
                        onClick={() => setPrefs((p) => ({ ...p, [item.key]: !p[item.key] }))}
                        aria-pressed={prefs[item.key]}
                        aria-label={item.label}
                        className={`relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors ${
                          prefs[item.key] ? "bg-primary" : "bg-muted"
                        }`}
                      >
                        <span
                          className={`pointer-events-none inline-block h-4 w-4 rounded-full bg-card shadow transition-transform ${
                            prefs[item.key] ? "translate-x-4" : "translate-x-0"
                          }`}
                        />
                      </button>
                    </div>
                  ))}
                </div>

                <Notice message={prefsMsg} />

                <button
                  onClick={handleSavePrefs}
                  disabled={prefsSaving}
                  className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground transition-colors hover:bg-primary/90 disabled:opacity-50"
                >
                  {prefsSaving ? "Saving..." : "Save preferences"}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      <p className="mt-8 text-center text-xs text-muted-foreground">
        Signed in as {displayName}
      </p>
    </div>
  );
}
