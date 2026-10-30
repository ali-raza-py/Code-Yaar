"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AlertTriangle, ArrowRight, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { FormError, FormField } from "@/components/auth/form-field";
import { ApiError, auth } from "@/lib/api";

/**
 * Password reset confirmation (`/reset-password?token=…`).
 *
 * The token arrives in the URL but is only sent to the API in a POST body, so
 * it never appears in a server log or a referrer header. Successful resets
 * revoke every existing session, so the user must sign in again afterwards.
 */
export default function ResetPasswordPage() {
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string[]> | undefined>();
  const [done, setDone] = useState(false);
  // Read on mount: the token is client-only, and rendering it during the
  // server pass would hydrate a different tree.
  const [token, setToken] = useState<string | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    // Deferred through a microtask so the effect never sets state synchronously.
    Promise.resolve().then(() => {
      setToken(new URLSearchParams(window.location.search).get("token"));
      setReady(true);
    });
  }, []);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (submitting) return;

    setError(null);
    setFieldErrors(undefined);

    if (!token) {
      setError("This reset link is missing its token. Request a new one.");
      return;
    }
    if (password !== confirmPassword) {
      setFieldErrors({ confirm_password: ["Passwords do not match."] });
      return;
    }

    setSubmitting(true);
    try {
      await auth.confirmPasswordReset({
        token,
        password,
        confirm_password: confirmPassword,
      });
      setDone(true);
    } catch (caught) {
      if (caught instanceof ApiError) {
        setError(caught.message);
        setFieldErrors(caught.fieldErrors);
      } else {
        setError("We couldn't reset your password. Please try again.");
      }
    } finally {
      setSubmitting(false);
    }
  };

  if (done) {
    return (
      <div className="text-center">
        <CheckCircle2 className="mx-auto h-12 w-12 text-primary" aria-hidden="true" />
        <h1 className="mt-4 text-2xl font-bold tracking-tight">Password updated</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Every other device has been signed out. Use your new password to continue.
        </p>
        <Link
          href="/sign-in"
          className="mt-6 inline-flex h-11 w-full items-center justify-center gap-2 rounded-md bg-primary text-sm font-semibold text-primary-foreground transition-colors hover:bg-primary/90"
        >
          Sign in
          <ArrowRight className="h-4 w-4" />
        </Link>
      </div>
    );
  }

  if (!ready) {
    return (
      <div className="flex min-h-[160px] items-center justify-center gap-2">
        <span
          aria-hidden="true"
          className="h-6 w-6 animate-spin rounded-full border-2 border-primary/25 border-t-primary"
        />
        <span className="sr-only">Loading reset link</span>
      </div>
    );
  }

  if (!token) {
    return (
      <div className="text-center">
        <AlertTriangle className="mx-auto h-12 w-12 text-destructive" aria-hidden="true" />
        <h1 className="mt-4 text-2xl font-bold tracking-tight">Invalid reset link</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          This link is missing its token. Request a fresh one to continue.
        </p>
        <Link
          href="/forgot-password"
          className="mt-6 inline-flex h-11 w-full items-center justify-center gap-2 rounded-md bg-primary text-sm font-semibold text-primary-foreground transition-colors hover:bg-primary/90"
        >
          Request a new link
          <ArrowRight className="h-4 w-4" />
        </Link>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold tracking-tight">Choose a new password</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Pick something strong that you haven&apos;t used before.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5" noValidate>
        <FormError message={error} />

        <FormField
          label="New password"
          name="password"
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          placeholder="Choose a strong password"
          autoComplete="new-password"
          required
          errors={fieldErrors?.password}
          hint="At least 8 characters, and not a common or numeric-only password."
        />

        <FormField
          label="Confirm new password"
          name="confirm_password"
          type="password"
          value={confirmPassword}
          onChange={(event) => setConfirmPassword(event.target.value)}
          placeholder="Repeat your new password"
          autoComplete="new-password"
          required
          errors={fieldErrors?.confirm_password}
        />

        <Button type="submit" className="h-11 w-full text-sm font-semibold" disabled={submitting}>
          {submitting ? (
            <span className="inline-flex items-center gap-2">
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
              Updating...
            </span>
          ) : (
            <>
              Update password
              <ArrowRight className="h-4 w-4" />
            </>
          )}
        </Button>
      </form>

      <div className="relative my-6">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-border/60" />
        </div>
      </div>

      <p className="text-center text-sm text-muted-foreground">
        <Link
          href="/forgot-password"
          className="font-semibold text-primary transition-colors hover:text-primary/80"
        >
          Request a new reset link
        </Link>
      </p>
    </div>
  );
}
