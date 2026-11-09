"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";

/**
 * Doorway to the credential resolver at /verify/[publicId]: the code is a
 * dynamic path segment, so this forwards client-side instead of a plain GET
 * form. Empty input never leaves the page.
 */
export function VerifyForm() {
  const router = useRouter();
  const [code, setCode] = useState("");

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = code.trim();
    if (!trimmed) return;
    router.push(`/verify/${encodeURIComponent(trimmed)}`);
  }

  return (
    <form onSubmit={handleSubmit} className="mt-6 flex flex-col gap-3 sm:flex-row">
      <label htmlFor="credential-code" className="sr-only">Credential code</label>
      <input
        id="credential-code"
        value={code}
        onChange={(event) => setCode(event.target.value)}
        type="text"
        required
        placeholder="Paste the credential code"
        className="h-11 min-w-0 flex-1 rounded-lg border border-border bg-card px-4 text-sm text-foreground outline-none transition-colors focus:border-primary"
      />
      <button
        type="submit"
        className="inline-flex h-11 items-center justify-center rounded-lg bg-cta px-5 text-sm font-bold text-cta-fg transition-colors hover:bg-cta-hover"
      >
        Verify
      </button>
    </form>
  );
}
