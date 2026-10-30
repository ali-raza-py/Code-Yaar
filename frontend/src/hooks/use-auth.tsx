"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import {
  ApiError,
  clearToken,
  getAccessToken,
  restoreSession,
  auth,
  type AuthUser,
  type MePayload,
  type RegisterPayload,
  type UpdateProfilePayload,
} from "@/lib/api";

/**
 * Single source of truth for authentication state.
 *
 * Nothing else in the app reads tokens or calls the auth endpoints directly:
 * the access token stays inside `lib/api.ts`, and the refresh cookie is
 * HttpOnly. This provider only exposes the resulting user and the actions.
 */

interface SignInResult {
  error: string | null;
  /** Machine-readable reason, e.g. `email_not_verified`. */
  code?: string;
  /** Address a verification link can be resent to, when the API asks for it. */
  email?: string;
}

interface SignUpResult {
  error: string | null;
  user: AuthUser | null;
  /** False when the verification email could not be sent (e.g. mail outage). */
  verificationEmailSent: boolean;
  /** Per-field validation messages returned by the API. */
  fieldErrors?: Record<string, string[]>;
}

interface AuthContextValue {
  user: AuthUser | null;
  /** Full `/auth/me/` payload — profile fields, XP, verification state. */
  profile: MePayload | null;
  loading: boolean;
  error: string | null;
  isAuthenticated: boolean;
  emailVerified: boolean;
  /** True once the API is reachable but the address is still unverified. */
  needsEmailVerification: boolean;
  signIn: (identifier: string, password: string) => Promise<SignInResult>;
  signUp: (payload: RegisterPayload) => Promise<SignUpResult>;
  signOut: () => Promise<void>;
  /** Re-read the current user (after a profile save, verification, etc.). */
  refresh: () => Promise<MePayload | null>;
  updateProfile: (data: UpdateProfilePayload) => Promise<MePayload>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

function messageFor(error: unknown, fallback: string): string {
  if (error instanceof ApiError) return error.message;
  if (error instanceof Error && error.message) return error.message;
  return fallback;
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [profile, setProfile] = useState<MePayload | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Session restore: exchange the HttpOnly refresh cookie for an in-memory
  // access token, then load the user. Skipped entirely for first-time visitors.
  useEffect(() => {
    let cancelled = false;

    (async () => {
      const restored = await restoreSession();
      if (cancelled) return;
      if (restored) {
        setUser(restored.user);
        setProfile(restored);
      }
      setLoading(false);
    })();

    return () => {
      cancelled = true;
    };
  }, []);

  const signIn = useCallback(async (identifier: string, password: string): Promise<SignInResult> => {
    setError(null);
    try {
      const session = await auth.login({ identifier: identifier.trim(), password });
      setUser(session.user);
      // Best-effort: a failed `/me/` must not undo a successful sign-in.
      const me = await auth.me().catch(() => null);
      setProfile(me);
      return { error: null };
    } catch (caught) {
      const message = messageFor(caught, "We couldn't sign you in. Please try again.");
      setError(message);
      const code = caught instanceof ApiError ? caught.code : undefined;
      return {
        error: message,
        code,
        // The server names the barrier after a correct password; the address the
        // user typed is enough to offer a resend without another round trip.
        email: code === "email_not_verified" ? identifier.trim() : undefined,
      };
    }
  }, []);

  const signUp = useCallback(async (payload: RegisterPayload): Promise<SignUpResult> => {
    setError(null);
    try {
      const session = await auth.register(payload);
      if (!session.access) {
        // Verification is enforced, so the API withheld the session: the account
        // exists but stays signed out until the emailed link is confirmed.
        return {
          error: null,
          user: session.user,
          verificationEmailSent: session.verification_email_sent !== false,
        };
      }
      setUser(session.user);
      const me = await auth.me().catch(() => null);
      setProfile(me);
      return {
        error: null,
        user: session.user,
        verificationEmailSent: session.verification_email_sent !== false,
      };
    } catch (caught) {
      const message = messageFor(caught, "We couldn't create your account. Please try again.");
      setError(message);
      return {
        error: message,
        user: null,
        verificationEmailSent: false,
        fieldErrors: caught instanceof ApiError ? caught.fieldErrors : undefined,
      };
    }
  }, []);

  const signOut = useCallback(async () => {
    try {
      await auth.logout();
    } catch {
      // The cookie may already be gone; local state is cleared either way.
    }
    clearToken();
    setUser(null);
    setProfile(null);
    setError(null);
  }, []);

  const refresh = useCallback(async (): Promise<MePayload | null> => {
    if (!getAccessToken()) {
      setUser(null);
      setProfile(null);
      return null;
    }
    try {
      const me = await auth.me();
      setUser(me.user);
      setProfile(me);
      return me;
    } catch {
      return null;
    }
  }, []);

  const updateProfile = useCallback(async (data: UpdateProfilePayload): Promise<MePayload> => {
    const me = await auth.updateMe(data);
    setUser(me.user);
    setProfile(me);
    return me;
  }, []);

  const value = useMemo<AuthContextValue>(() => {
    const emailVerified = Boolean(profile?.email_verified ?? user?.email_verified);
    return {
      user,
      profile,
      loading,
      error,
      isAuthenticated: Boolean(user),
      emailVerified,
      needsEmailVerification: Boolean(user) && !emailVerified,
      signIn,
      signUp,
      signOut,
      refresh,
      updateProfile,
    };
  }, [user, profile, loading, error, signIn, signUp, signOut, refresh, updateProfile]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
