'use client';

import { useState, useEffect, useCallback } from 'react';
import { settings as settingsApi, auth, ApiError, setToken, type SettingsAccountData } from '@/lib/api';
import { NetworkError } from '@/components/learning/workspace/error-states';

type Tab = 'account' | 'profile' | 'password' | 'preferences';

interface ProfileData {
  avatar: string;
  bio: string;
  role: string;
}

export default function SettingsPage() {
  const [tab, setTab] = useState<Tab>('account');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Account state
  const [account, setAccount] = useState<SettingsAccountData | null>(null);
  const [accountForm, setAccountForm] = useState({ username: '', email: '', first_name: '', last_name: '' });
  const [accountSaving, setAccountSaving] = useState(false);
  const [accountMsg, setAccountMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Profile state
  const [profile, setProfile] = useState<ProfileData>({ avatar: '', bio: '', role: 'student' });
  const [profileForm, setProfileForm] = useState<ProfileData>({ avatar: '', bio: '', role: 'student' });
  const [profileSaving, setProfileSaving] = useState(false);
  const [profileMsg, setProfileMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Password state
  const [passwordForm, setPasswordForm] = useState({ current_password: '', new_password: '', confirm_password: '' });
  const [passwordSaving, setPasswordSaving] = useState(false);
  const [passwordMsg, setPasswordMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Preferences state (localStorage)
  const [prefs, setPrefs] = useState({
    theme: 'light',
    email_notifications: true,
    streak_reminders: true,
    weekly_digest: false,
    language: 'en',
    code_font_size: '14',
    auto_save: true,
  });
  const [prefsSaving, setPrefsSaving] = useState(false);
  const [prefsMsg, setPrefsMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    loadSettings();
    loadPrefs();
  }, []);

  function loadPrefs() {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('user_preferences');
      if (saved) {
        try {
          setPrefs(JSON.parse(saved));
        } catch { /* use defaults */ }
      }
    }
  }

  async function loadSettings() {
    try {
      setLoading(true);
      const [accountData, profileData] = await Promise.all([
        settingsApi.getAccount(),
        auth.getProfile() as Promise<ProfileData & { user: unknown }>,
      ]);
      setAccount(accountData);
      setAccountForm({
        username: accountData.username,
        email: accountData.email,
        first_name: accountData.first_name,
        last_name: accountData.last_name,
      });
      const p = profileData as unknown as ProfileData & { user: { avatar?: string; bio?: string; role?: string } };
      const pd: ProfileData = {
        avatar: p.user?.avatar ?? p.avatar ?? '',
        bio: p.user?.bio ?? p.bio ?? '',
        role: p.user?.role ?? p.role ?? 'student',
      };
      setProfile(pd);
      setProfileForm(pd);
      setError(null);
    } catch (e) {
      if (e instanceof ApiError && e.status === 401) {
        setError('auth');
      } else {
        setError('network');
      }
    } finally {
      setLoading(false);
    }
  }

  const handleSaveAccount = useCallback(async () => {
    setAccountSaving(true);
    setAccountMsg(null);
    try {
      const result = await settingsApi.updateAccount(accountForm);
      setAccount({ ...account!, username: result.username, email: result.email, first_name: result.first_name, last_name: result.last_name });
      setAccountMsg({ type: 'success', text: 'Account settings saved.' });
      setTimeout(() => setAccountMsg(null), 3000);
    } catch (e) {
      setAccountMsg({ type: 'error', text: e instanceof ApiError ? e.message : 'Failed to save.' });
    } finally {
      setAccountSaving(false);
    }
  }, [accountForm, account]);

  const handleSaveProfile = useCallback(async () => {
    setProfileSaving(true);
    setProfileMsg(null);
    try {
      await settingsApi.updateProfile(profileForm);
      setProfile(profileForm);
      setProfileMsg({ type: 'success', text: 'Profile updated.' });
      setTimeout(() => setProfileMsg(null), 3000);
    } catch (e) {
      setProfileMsg({ type: 'error', text: e instanceof ApiError ? e.message : 'Failed to save.' });
    } finally {
      setProfileSaving(false);
    }
  }, [profileForm]);

  const handleSavePassword = useCallback(async () => {
    if (passwordForm.new_password !== passwordForm.confirm_password) {
      setPasswordMsg({ type: 'error', text: 'Passwords do not match.' });
      return;
    }
    if (passwordForm.new_password.length < 8) {
      setPasswordMsg({ type: 'error', text: 'Password must be at least 8 characters.' });
      return;
    }
    setPasswordSaving(true);
    setPasswordMsg(null);
    try {
      const result = await settingsApi.updateAccount({
        current_password: passwordForm.current_password,
        new_password: passwordForm.new_password,
      });
      if (result.token) {
        setToken(result.token);
      }
      setPasswordForm({ current_password: '', new_password: '', confirm_password: '' });
      setPasswordMsg({ type: 'success', text: 'Password changed successfully.' });
      setTimeout(() => setPasswordMsg(null), 3000);
    } catch (e) {
      setPasswordMsg({ type: 'error', text: e instanceof ApiError ? e.message : 'Failed to change password.' });
    } finally {
      setPasswordSaving(false);
    }
  }, [passwordForm]);

  const handleSavePrefs = useCallback(() => {
    setPrefsSaving(true);
    setPrefsMsg(null);
    try {
      localStorage.setItem('user_preferences', JSON.stringify(prefs));
      if (prefs.theme === 'dark') {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
      setPrefsMsg({ type: 'success', text: 'Preferences saved.' });
      setTimeout(() => setPrefsMsg(null), 3000);
    } catch {
      setPrefsMsg({ type: 'error', text: 'Failed to save preferences.' });
    } finally {
      setPrefsSaving(false);
    }
  }, [prefs]);

  if (error === 'network') return <NetworkError />;
  if (error === 'auth') return (
    <div className="mx-auto max-w-3xl px-4 py-12 text-center">
      <p className="text-gray-500">Please sign in to access settings.</p>
    </div>
  );

  const tabs: { id: Tab; label: string; icon: string }[] = [
    { id: 'account', label: 'Account', icon: 'M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z' },
    { id: 'profile', label: 'Profile', icon: 'M17.982 18.725A7.488 7.488 0 0012 15.75a7.488 7.488 0 00-5.982 2.975m11.963 0a9 9 0 10-11.963 0m11.963 0A8.966 8.966 0 0112 21a8.966 8.966 0 01-5.982-2.275M15 9.75a3 3 0 11-6 0 3 3 0 016 0z' },
    { id: 'password', label: 'Password', icon: 'M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z' },
    { id: 'preferences', label: 'Preferences', icon: 'M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.324.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 011.37.49l1.296 2.247a1.125 1.125 0 01-.26 1.431l-1.003.827c-.293.24-.438.613-.431.992a6.759 6.759 0 010 .255c-.007.378.138.75.43.99l1.005.828c.424.35.534.954.26 1.43l-1.298 2.247a1.125 1.125 0 01-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.57 6.57 0 01-.22.128c-.331.183-.581.495-.644.869l-.213 1.28c-.09.543-.56.941-1.11.941h-2.594c-.55 0-1.02-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 01-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 01-1.369-.49l-1.297-2.247a1.125 1.125 0 01.26-1.431l1.004-.827c.292-.24.437-.613.43-.992a6.932 6.932 0 010-.255c.007-.378-.138-.75-.43-.99l-1.004-.828a1.125 1.125 0 01-.26-1.43l1.297-2.247a1.125 1.125 0 011.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.087.22-.128.332-.183.582-.495.644-.869l.214-1.281z M15 12a3 3 0 11-6 0 3 3 0 016 0z' },
  ];

  return (
    <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="mb-8">
        <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-purple-200 bg-purple-50 px-3 py-1 text-xs font-medium text-purple-700">
          <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.324.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 011.37.49l1.296 2.247a1.125 1.125 0 01-.26 1.431l-1.003.827c-.293.24-.438.613-.431.992a6.759 6.759 0 010 .255c-.007.378.138.75.43.99l1.005.828c.424.35.534.954.26 1.43l-1.298 2.247a1.125 1.125 0 01-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.57 6.57 0 01-.22.128c-.331.183-.581.495-.644.869l-.213 1.28c-.09.543-.56.941-1.11.941h-2.594c-.55 0-1.02-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 01-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 01-1.369-.49l-1.297-2.247a1.125 1.125 0 01.26-1.431l1.004-.827c.292-.24.437-.613.43-.992a6.932 6.932 0 010-.255c.007-.378-.138-.75-.43-.99l-1.004-.828a1.125 1.125 0 01-.26-1.43l1.297-2.247a1.125 1.125 0 011.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.087.22-.128.332-.183.582-.495.644-.869l.214-1.281z" />
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          SETTINGS
        </div>
        <h1 className="text-3xl font-bold tracking-tight text-gray-900">Settings</h1>
        <p className="mt-2 text-gray-600">Manage your account, profile, and preferences.</p>
      </div>

      {loading ? (
        <div className="animate-pulse space-y-4">
          <div className="flex gap-2">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="h-9 w-24 rounded-full bg-gray-200" />
            ))}
          </div>
          <div className="h-64 rounded-xl bg-gray-200" />
        </div>
      ) : (
        <div className="flex flex-col gap-8 sm:flex-row">
          {/* Sidebar Tabs */}
          <div className="sm:w-48 shrink-0">
            <nav className="flex gap-1 sm:flex-col overflow-x-auto">
              {tabs.map((t) => (
                <button
                  key={t.id}
                  onClick={() => setTab(t.id)}
                  className={`flex items-center gap-2 whitespace-nowrap rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                    tab === t.id
                      ? 'bg-purple-50 text-purple-700'
                      : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
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

          {/* Content */}
          <div className="flex-1 min-w-0">
            {/* Account Tab */}
            {tab === 'account' && (
              <div className="rounded-xl border border-gray-200 bg-white p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-1">Account Settings</h2>
                <p className="text-sm text-gray-500 mb-6">Update your username, email, and display name.</p>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Username</label>
                    <input
                      type="text"
                      value={accountForm.username}
                      onChange={(e) => setAccountForm(f => ({ ...f, username: e.target.value }))}
                      className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-900 focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                    <input
                      type="email"
                      value={accountForm.email}
                      onChange={(e) => setAccountForm(f => ({ ...f, email: e.target.value }))}
                      className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-900 focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">First Name</label>
                      <input
                        type="text"
                        value={accountForm.first_name}
                        onChange={(e) => setAccountForm(f => ({ ...f, first_name: e.target.value }))}
                        className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-900 focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
                      <input
                        type="text"
                        value={accountForm.last_name}
                        onChange={(e) => setAccountForm(f => ({ ...f, last_name: e.target.value }))}
                        className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-900 focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
                      />
                    </div>
                  </div>

                  {accountMsg && (
                    <p className={`text-sm ${accountMsg.type === 'success' ? 'text-green-600' : 'text-red-600'}`}>
                      {accountMsg.text}
                    </p>
                  )}

                  <button
                    onClick={handleSaveAccount}
                    disabled={accountSaving}
                    className="rounded-lg bg-purple-600 px-4 py-2 text-sm font-semibold text-white hover:bg-purple-700 disabled:opacity-50 transition-colors"
                  >
                    {accountSaving ? 'Saving...' : 'Save Changes'}
                  </button>
                </div>
              </div>
            )}

            {/* Profile Tab */}
            {tab === 'profile' && (
              <div className="rounded-xl border border-gray-200 bg-white p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-1">Public Profile</h2>
                <p className="text-sm text-gray-500 mb-6">Customize how others see you on Code-Yaar.</p>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Avatar URL</label>
                    <input
                      type="url"
                      value={profileForm.avatar}
                      onChange={(e) => setProfileForm(p => ({ ...p, avatar: e.target.value }))}
                      placeholder="https://example.com/avatar.jpg"
                      className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-900 placeholder:text-gray-400 focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
                    />
                    {profileForm.avatar && (
                      <div className="mt-2 flex items-center gap-3">
                        <div className="h-12 w-12 overflow-hidden rounded-full bg-gray-100">
                          {/* eslint-disable-next-line @next/next/no-img-element */}
                          <img src={profileForm.avatar} alt="Avatar preview" className="h-full w-full object-cover" />
                        </div>
                        <span className="text-xs text-gray-500">Preview</span>
                      </div>
                    )}
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Bio</label>
                    <textarea
                      value={profileForm.bio}
                      onChange={(e) => setProfileForm(p => ({ ...p, bio: e.target.value }))}
                      rows={3}
                      placeholder="Tell us about yourself..."
                      className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-900 placeholder:text-gray-400 focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500 resize-none"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Role</label>
                    <select
                      value={profileForm.role}
                      onChange={(e) => setProfileForm(p => ({ ...p, role: e.target.value }))}
                      className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-900 focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
                    >
                      <option value="student">Student</option>
                      <option value="mentor">Mentor</option>
                    </select>
                  </div>

                  {profileMsg && (
                    <p className={`text-sm ${profileMsg.type === 'success' ? 'text-green-600' : 'text-red-600'}`}>
                      {profileMsg.text}
                    </p>
                  )}

                  <button
                    onClick={handleSaveProfile}
                    disabled={profileSaving}
                    className="rounded-lg bg-purple-600 px-4 py-2 text-sm font-semibold text-white hover:bg-purple-700 disabled:opacity-50 transition-colors"
                  >
                    {profileSaving ? 'Saving...' : 'Save Profile'}
                  </button>
                </div>
              </div>
            )}

            {/* Password Tab */}
            {tab === 'password' && (
              <div className="rounded-xl border border-gray-200 bg-white p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-1">Change Password</h2>
                <p className="text-sm text-gray-500 mb-6">Update your password to keep your account secure.</p>

                <div className="space-y-4 max-w-md">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Current Password</label>
                    <input
                      type="password"
                      value={passwordForm.current_password}
                      onChange={(e) => setPasswordForm(f => ({ ...f, current_password: e.target.value }))}
                      className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-900 focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">New Password</label>
                    <input
                      type="password"
                      value={passwordForm.new_password}
                      onChange={(e) => setPasswordForm(f => ({ ...f, new_password: e.target.value }))}
                      className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-900 focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
                    />
                    {passwordForm.new_password && passwordForm.new_password.length < 8 && (
                      <p className="mt-1 text-xs text-red-500">Minimum 8 characters</p>
                    )}
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Confirm New Password</label>
                    <input
                      type="password"
                      value={passwordForm.confirm_password}
                      onChange={(e) => setPasswordForm(f => ({ ...f, confirm_password: e.target.value }))}
                      className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-900 focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
                    />
                    {passwordForm.confirm_password && passwordForm.new_password !== passwordForm.confirm_password && (
                      <p className="mt-1 text-xs text-red-500">Passwords do not match</p>
                    )}
                  </div>

                  {passwordMsg && (
                    <p className={`text-sm ${passwordMsg.type === 'success' ? 'text-green-600' : 'text-red-600'}`}>
                      {passwordMsg.text}
                    </p>
                  )}

                  <button
                    onClick={handleSavePassword}
                    disabled={passwordSaving || !passwordForm.current_password || !passwordForm.new_password || passwordForm.new_password !== passwordForm.confirm_password}
                    className="rounded-lg bg-purple-600 px-4 py-2 text-sm font-semibold text-white hover:bg-purple-700 disabled:opacity-50 transition-colors"
                  >
                    {passwordSaving ? 'Changing...' : 'Change Password'}
                  </button>
                </div>
              </div>
            )}

            {/* Preferences Tab */}
            {tab === 'preferences' && (
              <div className="rounded-xl border border-gray-200 bg-white p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-1">Preferences</h2>
                <p className="text-sm text-gray-500 mb-6">Customize your learning experience.</p>

                <div className="space-y-6">
                  {/* Theme */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Theme</label>
                    <div className="flex gap-3">
                      {(['light', 'dark', 'system'] as const).map((theme) => (
                        <button
                          key={theme}
                          onClick={() => setPrefs(p => ({ ...p, theme }))}
                          className={`rounded-lg border px-4 py-2 text-sm font-medium capitalize transition-colors ${
                            prefs.theme === theme
                              ? 'border-purple-300 bg-purple-50 text-purple-700'
                              : 'border-gray-200 bg-white text-gray-600 hover:bg-gray-50'
                          }`}
                        >
                          {theme}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Code Font Size */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Code Editor Font Size</label>
                    <select
                      value={prefs.code_font_size}
                      onChange={(e) => setPrefs(p => ({ ...p, code_font_size: e.target.value }))}
                      className="rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-900 focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
                    >
                      <option value="12">12px</option>
                      <option value="14">14px</option>
                      <option value="16">16px</option>
                      <option value="18">18px</option>
                    </select>
                  </div>

                  {/* Toggles */}
                  <div className="space-y-3">
                    {[
                      { key: 'email_notifications' as const, label: 'Email Notifications', desc: 'Receive updates about your progress' },
                      { key: 'streak_reminders' as const, label: 'Streak Reminders', desc: 'Get reminded to maintain your streak' },
                      { key: 'weekly_digest' as const, label: 'Weekly Digest', desc: 'Weekly summary of community activity' },
                      { key: 'auto_save' as const, label: 'Auto-save Code', desc: 'Automatically save your code while editing' },
                    ].map((item) => (
                      <div key={item.key} className="flex items-center justify-between">
                        <div>
                          <p className="text-sm font-medium text-gray-900">{item.label}</p>
                          <p className="text-xs text-gray-500">{item.desc}</p>
                        </div>
                        <button
                          onClick={() => setPrefs(p => ({ ...p, [item.key]: !p[item.key] }))}
                          className={`relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors ${
                            prefs[item.key] ? 'bg-purple-600' : 'bg-gray-200'
                          }`}
                        >
                          <span
                            className={`pointer-events-none inline-block h-4 w-4 rounded-full bg-white shadow transform transition-transform ${
                              prefs[item.key] ? 'translate-x-4' : 'translate-x-0'
                            }`}
                          />
                        </button>
                      </div>
                    ))}
                  </div>

                  {prefsMsg && (
                    <p className={`text-sm ${prefsMsg.type === 'success' ? 'text-green-600' : 'text-red-600'}`}>
                      {prefsMsg.text}
                    </p>
                  )}

                  <button
                    onClick={handleSavePrefs}
                    disabled={prefsSaving}
                    className="rounded-lg bg-purple-600 px-4 py-2 text-sm font-semibold text-white hover:bg-purple-700 disabled:opacity-50 transition-colors"
                  >
                    {prefsSaving ? 'Saving...' : 'Save Preferences'}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
