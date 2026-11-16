export function FoundingTeamSkeleton() {
  return (
    <section
      id="team"
      aria-labelledby="team-heading"
      className="border-y border-border bg-card animate-pulse py-16 lg:py-20"
    >
      <div className="mx-auto max-w-7xl px-5 sm:px-8 lg:px-10">
        <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
          <div className="space-y-3">
            <div className="h-4 w-32 rounded bg-muted" />
            <h2 className="mt-3 h-10 w-48 rounded bg-muted" />
            <p className="mt-3 h-6 w-2/3 rounded bg-muted/60" />
          </div>
        </div>
        <div className="relative mt-12 overflow-hidden" aria-roledescription="carousel" aria-label="Founding team members">
          <div className="flex w-max py-8 gap-6 px-3">
            {[1, 2, 3, 4].map((copy) => (
              <div key={copy} className="flex gap-6 px-3">
                {[1, 2, 3].map((i) => (
                  <article key={i} className="shrink-0 w-[264px] sm:w-[280px] rounded-[20px] border border-white/10 bg-[#0b2a1e]">
                    <div className="h-[258px] shrink-0 overflow-hidden rounded-t-[16px] bg-[#16342b] animate-pulse" />
                    <div className="relative z-10 flex min-h-[310px] flex-1 flex-col bg-[#0b2a1e] px-5 pb-6 pt-4 animate-pulse">
                      <div className="h-4 w-20 rounded bg-[#16342b]/60" />
                      <h3 className="mt-2.5 h-6 w-24 rounded bg-[#16342b]/60" />
                      <div className="mt-3 h-4 w-1/2 rounded bg-[#16342b]/40" />
                      <ul className="mt-2 space-y-1.5">
                        {[1, 2, 3].map((j) => (
                          <li key={j} className="flex gap-2">
                            <div className="mt-[0.55rem] h-1 w-1 shrink-0 rounded-full bg-[#16342b]" />
                            <div className="h-4 w-40 rounded bg-[#16342b]/40" />
                          </li>
                        ))}
                      </ul>
                    </div>
                  </article>
                ))}
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
