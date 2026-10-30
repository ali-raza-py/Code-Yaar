"use client";

import { useId, useState } from "react";
import { AlertCircle, CheckCircle2, Eye, EyeOff } from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * Shared form primitives for every auth screen.
 *
 * Keeping the markup and error rendering in one place means the sign-in,
 * sign-up, verification, password-reset and settings forms stay visually and
 * behaviourally identical, and field errors returned by DRF render the same
 * way everywhere.
 */

export const inputClass =
  "flex h-11 w-full rounded-lg border border-input bg-background px-3.5 py-2 text-sm transition-colors placeholder:text-muted-foreground/40 focus:border-primary/40 focus:outline-none focus:ring-2 focus:ring-primary/10 disabled:cursor-not-allowed disabled:opacity-60";

interface FormFieldProps
  extends Omit<React.InputHTMLAttributes<HTMLInputElement>, "id" | "className"> {
  label: string;
  /** DRF field errors for this input. */
  errors?: string[];
  hint?: string;
  /** Rendered on the right side of the label row, e.g. a "Forgot password?" link. */
  labelAction?: React.ReactNode;
  className?: string;
}

export function FormField({
  label,
  errors,
  hint,
  labelAction,
  className,
  type = "text",
  ...props
}: FormFieldProps) {
  const id = useId();
  const [revealed, setRevealed] = useState(false);
  const isPassword = type === "password";
  const invalid = Boolean(errors?.length);
  const describedBy = errors?.length
    ? `${id}-error`
    : hint
      ? `${id}-hint`
      : undefined;

  return (
    <div className={cn("space-y-2", className)}>
      <div className="flex items-baseline justify-between gap-3">
        <label htmlFor={id} className="text-sm font-medium text-foreground">
          {label}
        </label>
        {labelAction}
      </div>

      <div className="relative">
        <input
          {...props}
          id={id}
          type={isPassword && revealed ? "text" : type}
          aria-invalid={invalid || undefined}
          aria-describedby={describedBy}
          className={cn(
            inputClass,
            isPassword && "pr-11",
            invalid && "border-destructive/50 focus:border-destructive/60 focus:ring-destructive/10"
          )}
        />
        {isPassword && (
          <button
            type="button"
            onClick={() => setRevealed((current) => !current)}
            aria-label={revealed ? "Hide password" : "Show password"}
            aria-pressed={revealed}
            className="absolute inset-y-0 right-0 flex w-11 items-center justify-center rounded-r-lg text-muted-foreground transition-colors hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30"
          >
            {revealed ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
          </button>
        )}
      </div>

      {errors?.length ? (
        <p id={`${id}-error`} className="flex items-start gap-1.5 text-xs text-destructive">
          <AlertCircle className="mt-0.5 h-3.5 w-3.5 shrink-0" aria-hidden="true" />
          <span>{errors[0]}</span>
        </p>
      ) : hint ? (
        <p id={`${id}-hint`} className="text-xs text-muted-foreground">
          {hint}
        </p>
      ) : null}
    </div>
  );
}

/** Form-level error banner. */
export function FormError({ message }: { message: string | null }) {
  if (!message) return null;
  return (
    <div
      role="alert"
      className="flex items-start gap-3 rounded-lg border border-destructive/15 bg-destructive/[0.04] p-3.5 text-sm text-destructive"
    >
      <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
      <span>{message}</span>
    </div>
  );
}

/** Form-level success banner. */
export function FormSuccess({ message }: { message: string | null }) {
  if (!message) return null;
  return (
    <div
      role="status"
      className="flex items-start gap-3 rounded-lg border border-primary/20 bg-primary/[0.06] p-3.5 text-sm text-foreground"
    >
      <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-primary" aria-hidden="true" />
      <span>{message}</span>
    </div>
  );
}

/**
 * Pulls the messages for one field out of a DRF error payload.
 * Accepts the flat `fieldErrors` map produced by `ApiError`.
 */
export function fieldErrors(
  errors: Record<string, string[]> | undefined,
  field: string
): string[] | undefined {
  return errors?.[field];
}
