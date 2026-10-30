"use client";

import { useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, MailCheck } from "lucide-react";
import { Button } from "@/components/ui/button";
import { buttonVariants } from "@/components/ui/button-variants";
import { useAuth } from "@/hooks/use-auth";
import { FormError, FormField, FormSuccess } from "@/components/auth/form-field";
import { RedirectIfAuthenticated } from "@/components/auth/require-auth";
import { auth, describeResendError } from "@/lib/api";
interface FormState {
  full_name: string;
  username: string;
  email: string;
  password: string;
  confirm_password: string;
}

const EMPTY: FormState = {
  full_name: "",
  username: "",
  email: "",
  password: "",
  confirm_password: "",
};

export default function SignUpPage() {
  const [form, setForm] = useState<FormState>(EMPTY);
  const [errors, setErrors] = useState<Record<string, string[]> | undefined>();
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [created, setCreated] = useState<{ email: string; verificationSent: boolean } | null>(null);
  const [resendState, setResendState] = useState<"idle" | "sending" | "sent">("idle");
  const [resendError, setResendError] = useState<string | null>(null);
  const { signUp } = useAuth();

  const update = (field: keyof FormState) => (event: React.ChangeEvent<HTMLInputElement>) => {
    setForm((current) => ({ ...current, [field]: event.target.value }));
    setErrors((current) => (current ? { ...current, [field]: [] } : current));
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (submitting) return;

    setError(null);
    setErrors(undefined);

    // Mirror the server's own checks so obvious mistakes never cost a request.
    if (form.password !== form.confirm_password) {
      setErrors({ confirm_password: ["Passwords do not match."] });
      return;
    }
    if (!form.full_name.trim()) {
      setErrors({ full_name: ["Enter your full name."] });
      return;
    }

    setSubmitting(true);
    const result = await signUp({
      full_name: form.full_name.trim(),
      username: form.username.trim(),
      email: form.email.trim(),
      password: form.password,
      confirm_password: form.confirm_password,
    });
    setSubmitting(false);

    if (result.error) {
      setError(result.error);
      setErrors(result.fieldErrors);
      return;
    }

    setCreated({
      email: form.email.trim(),
      verificationSent: result.verificationEmailSent,
    });
  };

  if (created) {
    return (
      <motion.div initial={{ opacity: 0, scale: 0.96 }} animate={{ opacity: 1, scale: 1 }}>
        <div className="text-center">
          <MailCheck className="mx-auto h-12 w-12 text-primary" aria-hidden="true" />
          <h1 className="mt-4 text-2xl font-bold tracking-tight">
            {created.verificationSent ? "Check your email" : "Account created"}
          </h1>
          <p className="mt-2 text-sm text-muted-foreground">
            {created.verificationSent ? (
              <>
                We sent a confirmation link to <strong>{created.email}</strong>. It expires in 24
                hours.
              </>
            ) : (
              <>
                Your account is ready. We couldn&apos;t send the confirmation email to{" "}
                <strong>{created.email}</strong> right now — you can request it again from your
                settings.
              </>
            )}
          </p>
        </div>

        <div className="mt-6 space-y-3">
          <Link
            href="/dashboard"
            className={buttonVariants({ className: "h-11 w-full text-sm font-semibold" })}
          >
            Continue to dashboard
            <ArrowRight className="h-4 w-4" />
          </Link>

          {created.verificationSent && (
            <div className="text-center">
              {resendState === "sent" ? (
                <FormSuccess message="A new confirmation link is on its way." />
              ) : (
                <button
                  type="button"
                  disabled={resendState === "sending"}
                  onClick={async () => {
                    setResendState("sending");
                    setResendError(null);
                    try {
                      const result = await auth.resendVerification(created.email);
                      if (result.verification_email_sent === false) {
                        setResendState("idle");
                        setResendError(
                          "The server could not hand the message to the mail service. Check the API's SMTP settings and try again."
                        );
                        return;
                      }
                      setResendState("sent");
                    } catch (caught) {
                      setResendState("idle");
                      setResendError(describeResendError(caught));
                    }
                  }}
                  className="text-xs font-medium text-primary transition-colors hover:text-primary/80 disabled:opacity-60"
                >
                  {resendState === "sending" ? "Sending…" : "Didn't get it? Resend the email"}
                </button>
              )}
              {resendState !== "sent" && resendError && (
                <p className="mt-2 text-xs text-destructive" role="alert">
                  {resendError}
                </p>
              )}
            </div>
          )}
        </div>
      </motion.div>
    );
  }

  return (
    <RedirectIfAuthenticated>
      <div>
        <div className="mb-8">
          <h1 className="text-2xl font-bold tracking-tight">Create your account</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Start your engineering journey with Code-Yaar.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5" noValidate>
          <FormError message={error} />

          <FormField
            label="Full name"
            name="full_name"
            type="text"
            value={form.full_name}
            onChange={update("full_name")}
            placeholder="Ada Lovelace"
            autoComplete="name"
            required
            errors={errors?.full_name}
          />

          <FormField
            label="Username"
            name="username"
            type="text"
            value={form.username}
            onChange={update("username")}
            placeholder="ada"
            autoComplete="username"
            autoCapitalize="none"
            spellCheck={false}
            required
            errors={errors?.username}
            hint="Letters, digits and @/./+/-/_ only."
          />

          <FormField
            label="Email address"
            name="email"
            type="email"
            value={form.email}
            onChange={update("email")}
            placeholder="you@example.com"
            autoComplete="email"
            inputMode="email"
            required
            errors={errors?.email}
          />

          <FormField
            label="Password"
            name="password"
            type="password"
            value={form.password}
            onChange={update("password")}
            placeholder="Choose a strong password"
            autoComplete="new-password"
            required
            errors={errors?.password}
            hint="At least 8 characters, and not a common or numeric-only password."
          />

          <FormField
            label="Confirm password"
            name="confirm_password"
            type="password"
            value={form.confirm_password}
            onChange={update("confirm_password")}
            placeholder="Repeat your password"
            autoComplete="new-password"
            required
            errors={errors?.confirm_password}
          />

          <Button type="submit" className="h-11 w-full text-sm font-semibold" disabled={submitting}>
            {submitting ? (
              <span className="inline-flex items-center gap-2">
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                Creating account...
              </span>
            ) : (
              <>
                Create Account
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
          Already have an account?{" "}
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
