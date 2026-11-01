import type { Metadata } from "next";
import Link from "next/link";
import { ShieldCheck } from "lucide-react";
import { VerifyForm } from "@/components/credentials/verify-form";

export const metadata: Metadata = {
  title: "Verify a certificate or badge | Code Yaar",
  description:
    "Check any Code Yaar certificate or badge against the credential registry. Share a credential ID or the link printed on the certificate.",
};

/**
 * Public credential verifier: the trust story of the platform, reachable
 * without an account. Submitting a code forwards to the legacy resolver at
 * /verify/[publicId], which looks the identifier up in both registries.
 */
export default function VerifyHubPage() {
  return (
    <div className="bg-section-light">
      <section className="bg-hero-navy text-white">
        <div className="mx-auto max-w-6xl px-4 py-16 sm:px-6 lg:px-8 lg:py-20">
          <p className="tech-label text-mint-on-navy">CREDENTIAL REGISTRY</p>
          <h1 className="mt-4 max-w-2xl text-4xl font-extrabold leading-tight sm:text-5xl">
            Verify any Code Yaar credential
          </h1>
          <p className="mt-4 max-w-2xl text-base leading-relaxed text-white/70">
            Every certificate and badge carries a unique code printed on it and embedded
            in its share link. Enter one below to confirm it against the registry — no
            account required.
          </p>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 py-14 sm:px-6 lg:px-8">
        <div className="card-hairline mx-auto max-w-xl border-[var(--color-section-border)] bg-card p-8">
          <span className="grid h-11 w-11 place-items-center rounded-lg bg-primary/10">
            <ShieldCheck aria-hidden="true" className="h-6 w-6 text-primary" />
          </span>
          <h2 className="mt-5 text-xl font-bold text-foreground">Check a credential code</h2>
          <p className="mt-2 text-sm text-muted-foreground">
            Codes look like the one printed at the bottom of a certificate, e.g.{" "}
            <span className="font-mono text-xs">CY-…</span>.
          </p>
          {/* The resolver route owns the lookup; this form is a doorway to it. */}
          <VerifyForm />
          <p className="mt-4 text-xs text-muted-foreground">
            Received a share link instead? Open it directly — it verifies itself on load.
          </p>
        </div>

        <div className="mx-auto mt-10 max-w-xl text-center text-sm text-muted-foreground">
          Earning credentials happens inside the student platform.{" "}
          <Link href="/courses" className="font-semibold text-primary hover:underline">
            Browse courses
          </Link>{" "}
          or{" "}
          <Link href="/tracks" className="font-semibold text-primary hover:underline">
            explore learning tracks
          </Link>{" "}
          to see how they are earned.
        </div>
      </section>
    </div>
  );
}
