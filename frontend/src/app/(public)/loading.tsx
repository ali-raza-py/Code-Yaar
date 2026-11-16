import { CometSpinner } from "@/components/ui/comet-spinner";

export default function PublicLoading() {
  return (
    <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8 flex flex-col gap-6">
      <div className="flex items-center gap-3">
        <CometSpinner className="h-8 w-8" />
        <h2 className="h-10 w-32 rounded bg-muted animate-pulse" />
      </div>
      <div className="space-y-4">
        <div className="h-4 w-1/2 rounded bg-muted/60 animate-pulse" />
        <div className="h-16 w-2/3 rounded bg-muted animate-pulse" />
        <div className="h-4 w-1/3 rounded bg-muted/60 animate-pulse" />
        <div className="h-4 w-1/4 rounded bg-muted/60 animate-pulse" />
      </div>
      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <div key={i} className="h-64 animate-pulse rounded-card border border-border bg-card" />
        ))}
      </div>
    </div>
  );
}
