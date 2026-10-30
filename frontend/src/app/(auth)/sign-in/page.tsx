"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, FlaskConical, MailWarning } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/use-auth";
import { auth, describeResendError } from "@/lib/api";
import { FormError, FormField } from "@/components/auth/form-field";
import { RedirectIfAuthenticated, readNextPath } from "@/components/auth/require-auth";

// Development-only shortcut for exploring seeded content. Never rendered in a
// production build, so no credentials ship with the app.
const DEMO =
  process.env.NODE_ENV === "production"
    ? null
    : { identifier: "demo@codeyaar.dev", password: "demo123" };

export default function SignInPage() {
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  // Set when the API refused the sign-in because the address is unverified.
  const [verifyTarget, setVerifyTarget] = useState<string | null>(null);
  const [resend, setResend] = useState<"idle" | "sending" | "sent">("idle");
  // Why the last resend attempt failed, if it did. Rendered instead of the
  // "on its way" note so a failed send is never reported as a success.
  const [resendError, setResendError] = useState<string | null>(null);
  const [nextPath, setNextPath] = useState("/dashboard");
  const { signIn } = useAuth();
  const router = useRouter();

  // Read the redirect target on the client so the page needs no Suspense
  // boundary, and validate it before use to avoid an open redirect.
  useEffect(() => {
    // Deferred through a microtask so the effect never sets state synchronously.
    Promise.resolve().then(() => setNextPath(readNextPath()));
  }, []);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (submitting) return;

    setError(null);
    setSubmitting(true);
    const result = await signIn(identifier, password);
    setSubmitting(false);

    if (result.error) {
      setError(result.error);
      setVerifyTarget(result.code === "email_not_verified" ? result.email ?? null : null);
      setResend("idle");
      setResendError(null);
      return;
    }
    router.replace(nextPath);
  };

  return (
    <RedirectIfAuthenticated>
      <div>
        <div className="mb-8">
          <h1 className="text-2xl font-bold tracking-tight">Welcome back</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Sign in to your account to continue your engineering journey.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5" noValidate>
          {DEMO && (
            <motion.div
              initial={{ opacity: 0, y: -8 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-start gap-3 rounded-lg border border-primary/20 bg-primary/[0.05] p-3.5 text-sm"
            >
              <FlaskConical className="mt-0.5 h-4 w-4 shrink-0 text-primary" aria-hidden="true" />
              <div className="space-y-1.5">
                <p className="text-foreground">Just exploring? Use the demo account:</p>
                <p className="font-mono text-xs text-muted-foreground">
                  {DEMO.identifier} / {DEMO.password}
                </p>
                <button
                  type="button"
                  onClick={() => {
                    setIdentifier(DEMO.identifier);
                    setPassword(DEMO.password);
                    setError(null);
                  }}
                  className="text-xs font-semibold text-primary transition-colors hover:text-primary/80"
                >
                  Fill demo credentials
                </button>
              </div>
            </motion.div>
          )}

          <FormError message={error} />

          {verifyTarget && (
            <div className="flex items-start gap-3 rounded-lg border border-border/60 bg-muted/40 p-3.5">
              <MailWarning className="mt-0.5 h-4 w-4 shrink-0 text-primary" aria-hidden="true" />
              {resend === "sent" ? (
                <p className="text-xs text-muted-foreground">
                  If that account still needs verification, a new link is on its way.
                </p>
              ) : (
                <div className="space-y-1.5">
                  <button
                    type="button"
                    disabled={resend === "sending"}
                    onClick={async () => {
                      if (!verifyTarget) return;
                      setResend("sending");
                      setResendError(null);
                      try {
                        const result = await auth.resendVerification(verifyTarget);
                        if (result.verification_email_sent === false) {
                          // The API reached its mail transport and the transport
                          // refused the message: say so rather than claim success.
                          setResend("idle");
                          setResendError(
                            "The server could not hand the message to the mail service. Check the API's SMTP settings and try again."
                          );
                          return;
                        }
                        setResend("sent");
                      } catch (caught) {
                        setResend("idle");
                        setResendError(describeResendError(caught));
                      }
                    }}
                    className="text-left text-xs font-semibold text-primary transition-colors hover:text-primary/80 disabled:opacity-60"
                  >
                    {resend === "sending"
                      ? "Sending a new link…"
                      : `Resend the verification link to ${verifyTarget}`}
                  </button>
                  {resendError && (
                    <p className="text-xs text-destructive" role="alert">
                      {resendError}
                    </p>
                  )}
                </div>
              )}
            </div>
          )}

          <FormField
            label="Email or username"
            name="identifier"
            type="text"
            value={identifier}
            onChange={(event) => setIdentifier(event.target.value)}
            placeholder="you@example.com"
            autoComplete="username"
            autoCapitalize="none"
            spellCheck={false}
            required
          />

          <FormField
            label="Password"
            name="password"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            placeholder="Enter your password"
            autoComplete="current-password"
            required
            labelAction={
              <Link
                href="/forgot-password"
                className="text-xs font-medium text-primary transition-colors hover:text-primary/80"
              >
                Forgot password?
              </Link>
            }
          />

          <Button type="submit" className="h-11 w-full text-sm font-semibold" disabled={submitting}>
            {submitting ? (
              <span className="inline-flex items-center gap-2">
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                Signing in...
              </span>
            ) : (
              <>
                Sign In
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
          Don&apos;t have an account?{" "}
          <Link
            href="/sign-up"
            className="font-semibold text-primary transition-colors hover:text-primary/80"
          >
            Create account
          </Link>
        </p>
      </div>
    </RedirectIfAuthenticated>
  );
}
