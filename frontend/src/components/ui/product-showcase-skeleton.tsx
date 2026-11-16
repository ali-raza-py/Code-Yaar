export function ProductShowcaseSkeleton() {
  return (
    <section
      id="product-showcase"
      aria-labelledby="product-showcase-title"
      className="border-y border-border bg-card animate-pulse"
    >
      <div className="mx-auto grid max-w-7xl gap-10 px-5 py-16 sm:px-8 sm:py-20 lg:grid-cols-[0.78fr_1.22fr] lg:items-center lg:gap-14 lg:px-10 lg:py-24">
        <div className="space-y-6">
          <div className="h-4 w-48 rounded bg-muted" />
          <h2 className="mt-4 h-12 w-5/6 rounded bg-muted" />
          <p className="mt-5 h-6 w-3/4 rounded bg-muted/60" />
          <div role="tablist" className="mt-8 space-y-1">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="min-h-16 border-b border-border py-3" />
            ))}
          </div>
          <p className="mt-4 h-20 w-3/4 rounded bg-muted/60" />
        </div>
        <div className="relative min-w-0 rounded-[var(--radius-card)] border border-border p-3 sm:p-5 lg:p-7">
          <div className="h-8 w-32 rounded bg-muted" />
          <div className="mt-3 h-[200px] rounded-[var(--radius-card)] border border-border bg-muted/50" />
          <div className="mt-3 flex items-center gap-4 px-1 text-[9px] text-muted-foreground">
            <div className="h-1.5 w-2 rounded-full bg-muted" />
            <div className="h-1.5 w-16 rounded-full bg-muted/60" />
          </div>
        </div>
      </div>
    </section>
  );
}
