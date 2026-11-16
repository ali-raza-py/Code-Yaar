export default function TracksLoading() {
  return (
    <div className="mx-auto max-w-6xl px-4 py-6 sm:px-6 lg:px-8">
      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {[1, 2, 3].map((item) => (
          <div key={item} className="h-72 animate-pulse rounded-card border border-border bg-card" />
        ))}
      </div>
    </div>
  );
}
