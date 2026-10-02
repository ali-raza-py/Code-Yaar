import Image from "next/image";
import Link from "next/link";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-background px-4 py-12">
      {/* Logo */}
      <Link href="/" className="mb-8 flex items-center gap-2 transition-opacity hover:opacity-80">
        <div className="relative h-8 w-8">
          <Image
            src="/logo-light.png"
            alt="Code-Yaar"
            fill
            className="object-contain"
            priority
          />
        </div>
        <span className="text-lg font-bold tracking-tight">Code-Yaar</span>
      </Link>

      {/* Auth card */}
      <div className="w-full max-w-sm rounded-xl border border-border/60 bg-card p-7 shadow-lg">
        {children}
      </div>

      {/* Footer detail */}
      <p className="mt-8 font-mono text-xs text-muted-foreground/40">
        think. build. evolve.
      </p>
    </div>
  );
}
