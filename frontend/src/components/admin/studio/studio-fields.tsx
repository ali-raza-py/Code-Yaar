'use client';

/**
 * Form primitives for the Course Creation Studio, matching the idiom the existing admin
 * forms already use (a shared `inputClass`, a native control inside a `<label>`). They
 * live here rather than in `components/ui` because they are studio-specific: the studio
 * has autosave state to surface, so every control carries disabled/loading semantics.
 */

import type {
  InputHTMLAttributes, ReactNode, SelectHTMLAttributes, TextareaHTMLAttributes,
} from 'react';

export const inputClass =
  'mt-1 w-full rounded-md border bg-background px-3 py-2 text-sm';

export const labelClass = 'block text-sm font-medium';

export const hintClass = 'mt-1 text-xs text-muted-foreground';

interface StudioFieldProps {
  label: string;
  htmlFor?: string;
  hint?: string;
  required?: boolean;
  className?: string;
  children: ReactNode;
}

/** A labelled row: title above, control, then any server-hint or validation message. */
export function StudioField({ label, htmlFor, hint, required, className, children }: StudioFieldProps) {
  return (
    <label htmlFor={htmlFor} className={className ?? 'block'}>
      <span className={labelClass}>
        {label}
        {required && <span className="ml-1 text-destructive">*</span>}
      </span>
      {children}
      {hint && <span className={hintClass}>{hint}</span>}
    </label>
  );
}

export function StudioError({ message }: { message: string }) {
  if (!message) return null;
  return (
    <p role="alert" className="rounded-md border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700 dark:border-red-800 dark:bg-red-950 dark:text-red-200">
      {message}
    </p>
  );
}

/**
 * Thin native-control wrappers. The studio edits a lot of fields, so it uses the same
 * element types the rest of the admin panel uses (`input`, `textarea`, `label`) instead
 * of a component library the project does not have.
 */
export function Input({ className = '', ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return <input className={`${inputClass} ${className}`} {...props} />;
}

export function Textarea({ className = '', ...props }: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return <textarea className={`${inputClass} ${className}`} {...props} />;
}

export function Label({ className = '', ...props }: { className?: string; htmlFor?: string; children: ReactNode }) {
  return (
    <label htmlFor={props.htmlFor} className={`${labelClass} ${className}`}>
      {props.children}
    </label>
  );
}

export function Select({ className = '', children, ...props }: SelectHTMLAttributes<HTMLSelectElement>) {
  return (
    <select className={`${inputClass} ${className}`} {...props}>
      {children}
    </select>
  );
}
