"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { AlertTriangle, Loader2, MailCheck, MailWarning } from "lucide-react";
import { buttonVariants } from "@/components/ui/button-variants";
import { auth, ApiError, sendResend } from "@/lib/api";
import { useAuth } from "@/hooks/use-auth";

/**
 * Landing page for the link in the verification email
 * (`/verify-email?token=…`). The token is single-use, so the exchange runs
 * exactly once per mount — retrying after a network failure would burn it.
 */

type State =
  | { status: "checking" }
  | { status: "success" }
  | { status: "error"; message: string; code?: string }
  | { status: "missing" };

export default function VerifyEmailPage() {
  const [state, setState] = useState<State>({ status: "checking" });
  const [resend, setResend] = useState<"idle" | "sending" | "sent">("idle");
  const [resendError, setResendError] = useState<string | null>(null);
  const attempted = useRef(false);
  const { user, refresh } = useAuth();

  // Shared by both resend entry points: a failed request is shown as a failure
  // instead of being reported as "on its way".
  const sendResendHere = async (email: string) => {
    setResend("sending");
    setResendError(null);
    const outcome = await sendResend(email);
    if (!outcome.sent) {
      setResend("idle");
      setResendError(outcome.reason);
      return;
    }
    setResend("sent");
  };

  useEffect(() => {
    if (attempted.current) return;
    attempted.current = true;

    // Deferred through a microtask so the effect never sets state synchronously.
    Promise.resolve().then(async () => {
      const token = new URLSearchParams(window.location.search).get("token");
      if (!token) {
        setState({ status: "missing" });
        return;
      }

      try {
        await auth.verifyEmail(token);
        setState({ status: "success" });
        // Keep the header/sidebar badge honest without a reload.
        if (user) await refresh();
      } catch (caught) {
        setState({
          status: "error",
          message:
            caught instanceof ApiError
              ? caught.message
              : "We couldn't verify that link. Please try again.",
          code: caught instanceof ApiError ? caught.code : undefined,
        });
      }
    });
  }, [user, refresh]);

  if (state.status === "checking") {
    return (
      <div className="text-center">
        <Loader2 className="mx-auto h-10 w-10 animate-spin text-primary" aria-hidden="true" />
        <h1 className="mt-4 text-xl font-bold tracking-tight">Verifying your email</h1>
        <p className="mt-2 text-sm text-muted-foreground">This only takes a moment.</p>
      </div>
    );
  }

  if (state.status === "success") {
    return (
      <div className="text-center">
        <MailCheck className="mx-auto h-12 w-12 text-primary" aria-hidden="true" />
        <h1 className="mt-4 text-2xl font-bold tracking-tight">Email verified</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Your address is confirmed. Everything on Code-Yaar is unlocked.
        </p>
        <Link
          href={user ? "/dashboard" : "/sign-in"}
          className={buttonVariants({ className: "mt-6 h-11 w-full text-sm font-semibold" })}
        >
          {user ? "Go to dashboard" : "Sign in"}
        </Link>
      </div>
    );
  }

  if (state.status === "missing") {
    return (
      <div className="text-center">
        <MailWarning className="mx-auto h-12 w-12 text-muted-foreground" aria-hidden="true" />
        <h1 className="mt-4 text-2xl font-bold tracking-tight">Verification link missing</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Open the link from your confirmation email, or request a new one below.
        </p>
        <ResendControl
          email={user?.email}
          state={resend}
          error={resendError}
          onSend={sendResendHere}
        />
        <Link
          href="/sign-in"
          className={buttonVariants({
            variant: "outline",
            className: "mt-3 h-11 w-full text-sm font-semibold",
          })}
        >
          Back to sign in
        </Link>
      </div>
    );
  }

  return (
    <div className="text-center">
      <AlertTriangle className="mx-auto h-12 w-12 text-destructive" aria-hidden="true" />
      <h1 className="mt-4 text-2xl font-bold tracking-tight">We couldn&apos;t verify that link</h1>
      <p className="mt-2 text-sm text-muted-foreground">{state.message}</p>
      <ResendControl
        email={user?.email}
        state={resend}
        error={resendError}
        onSend={sendResendHere}
      />
      <Link
        href="/sign-in"
        className={buttonVariants({
          variant: "outline",
          className: "mt-3 h-11 w-full text-sm font-semibold",
        })}
      >
        Back to sign in
      </Link>
    </div>
  );
}

function ResendControl({
  email,
  state,
  error,
  onSend,
}: {
  email?: string;
  state: "idle" | "sending" | "sent";
  error?: string | null;
  onSend: (email: string) => Promise<void>;
}) {
  if (state === "sent") {
    return (
      <p className="mt-5 text-xs text-muted-foreground">
        If that account still needs verification, a new link is on its way.
      </p>
    );
  }

  return (
    <div className="mt-5 space-y-2">
      {email ? (
        <button
          type="button"
          disabled={state === "sending"}
          onClick={() => void onSend(email)}
          className="text-xs font-semibold text-primary transition-colors hover:text-primary/80 disabled:opacity-60"
        >
          {state === "sending" ? "Sending…" : `Resend the link to ${email}`}
        </button>
      ) : (
        <p className="text-xs text-muted-foreground">
          Sign in and request a new link from{" "}
          <Link href="/settings" className="font-semibold text-primary hover:text-primary/80">
            settings
          </Link>
          .
        </p>
      )}
      {error && (
        <p className="text-xs text-destructive" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}
