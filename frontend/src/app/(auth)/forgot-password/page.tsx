"use client";

import { useState } from "react";
import Link from "next/link";
import { ArrowLeft, ArrowRight, MailCheck } from "lucide-react";
import { Button } from "@/components/ui/button";
import { FormError, FormField } from "@/components/auth/form-field";
import { RedirectIfAuthenticated } from "@/components/auth/require-auth";
import { ApiError, auth } from "@/lib/api";

/**
 * Password reset request.
 *
 * The API answers with the same generic message whether or not the address
 * exists, so this page must not word its success state any differently.
 */
export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fieldError, setFieldError] = useState<string[] | undefined>();
  const [sent, setSent] = useState(false);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (submitting) return;

    setError(null);
    setFieldError(undefined);
    setSubmitting(true);

    try {
      await auth.requestPasswordReset(email.trim());
      setSent(true);
    } catch (caught) {
      if (caught instanceof ApiError) {
        setError(caught.message);
        setFieldError(caught.fieldErrors?.email);
      } else {
        setError("We couldn't send the reset email. Please try again.");
      }
    } finally {
      setSubmitting(false);
    }
  };

  if (sent) {
    return (
      <div className="text-center">
        <MailCheck className="mx-auto h-12 w-12 text-primary" aria-hidden="true" />
        <h1 className="mt-4 text-2xl font-bold tracking-tight">Check your email</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          If an account exists for <strong>{email.trim()}</strong>, a password reset link is on its
          way. The link expires in 60 minutes.
        </p>
        <Link
          href="/sign-in"
          className="mt-6 inline-flex items-center gap-2 text-sm font-semibold text-primary transition-colors hover:text-primary/80"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to sign in
        </Link>
      </div>
    );
  }

  return (
    <RedirectIfAuthenticated>
      <div>
        <div className="mb-8">
          <h1 className="text-2xl font-bold tracking-tight">Reset your password</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Enter the email address on your account and we&apos;ll send you a reset link.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5" noValidate>
          <FormError message={error} />

          <FormField
            label="Email address"
            name="email"
            type="email"
            value={email}
            onChange={(event) => {
              setEmail(event.target.value);
              setFieldError(undefined);
            }}
            placeholder="you@example.com"
            autoComplete="email"
            inputMode="email"
            required
            errors={fieldError}
          />

          <Button type="submit" className="h-11 w-full text-sm font-semibold" disabled={submitting}>
            {submitting ? (
              <span className="inline-flex items-center gap-2">
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                Sending...
              </span>
            ) : (
              <>
                Send reset link
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
          Remembered it?{" "}
          <Link
            href="/sign-in"
            className="font-semibold text-primary transition-colors hover:text-primary/80"
          >
            Sign in
          </Link>
        </p>
      </div>
    </RedirectIfAuthenticated>
  );
}
