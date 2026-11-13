import Image from "next/image";
import Link from "next/link";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-background px-4 py-12">
      {/* Logo */}
      <Link href="/" className="mb-8 flex items-center gap-2.5 rounded-md transition-opacity hover:opacity-90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background">
        <div className="relative h-8 w-8">
          <Image
            src="/brand/logo-mark.png"
            alt="Code Yaar"
            fill
            sizes="32px"
            className="object-contain"
            priority
          />
        </div>
        <span className="text-lg font-semibold tracking-tight text-foreground">Code Yaar</span>
      </Link>

      {/* Auth card */}
      <div className="w-full max-w-sm rounded-xl border border-border bg-card p-6 shadow-sm sm:p-7">
        {children}
      </div>

      {/* Footer detail */}
      <p className="mt-8 font-mono text-xs text-muted-foreground/60">
        think. build. evolve.
      </p>
    </div>
  );
}
