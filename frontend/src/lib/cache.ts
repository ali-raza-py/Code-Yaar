export const CACHE_POLICIES = {
  courses: 10 * 60 * 1000,
  questions: 10 * 60 * 1000,
  resources: 20 * 60 * 1000,
  practicals: 20 * 60 * 1000,
  tracks: 10 * 60 * 1000,
  projects: 20 * 60 * 1000,
  leaderboard: 2 * 60 * 1000,
  profile: 30 * 1000,
  progress: 0,
  analytics: 30 * 1000,
} as const;

export type CachePolicy = keyof typeof CACHE_POLICIES;

interface CacheEntry {
  value: unknown;
  expiresAt: number;
  staleUntil: number;
}

interface CacheMetrics {
  hits: number;
  misses: number;
  staleHits: number;
  deduplicatedRequests: number;
  networkRequests: number;
  errors: number;
}

const entries = new Map<string, CacheEntry>();
const inFlight = new Map<string, Promise<unknown>>();
const metrics: CacheMetrics = {
  hits: 0,
  misses: 0,
  staleHits: 0,
  deduplicatedRequests: 0,
  networkRequests: 0,
  errors: 0,
};

function isFresh(entry: CacheEntry, now: number): boolean {
  return entry.expiresAt > now;
}

function isUsableStale(entry: CacheEntry, now: number): boolean {
  return entry.staleUntil > now;
}

export async function cachedRequest<T>(
  key: string,
  policy: CachePolicy,
  fetcher: () => Promise<T>,
): Promise<T> {
  const ttl = CACHE_POLICIES[policy];
  if (ttl <= 0) return fetcher();

  const now = Date.now();
  const existing = entries.get(key);
  if (existing && isFresh(existing, now)) {
    metrics.hits += 1;
    return existing.value as T;
  }

  const running = inFlight.get(key);
  if (running) {
    metrics.deduplicatedRequests += 1;
    return running as Promise<T>;
  }

  metrics.misses += 1;
  metrics.networkRequests += 1;
  const stale = existing && isUsableStale(existing, now) ? existing.value as T : undefined;
  const request = fetcher()
    .then((value) => {
      const fetchedAt = Date.now();
      entries.set(key, {
        value,
        expiresAt: fetchedAt + ttl,
        staleUntil: fetchedAt + ttl * 2,
      });
      return value;
    })
    .catch((error: unknown) => {
      metrics.errors += 1;
      if (stale !== undefined) {
        metrics.staleHits += 1;
        return stale;
      }
      throw error;
    })
    .finally(() => {
      inFlight.delete(key);
    });

  inFlight.set(key, request);
  return request;
}

export function invalidateCache(...patterns: string[]): void {
  if (patterns.length === 0) {
    entries.clear();
    return;
  }
  for (const key of entries.keys()) {
    if (patterns.some((pattern) => key.includes(pattern))) entries.delete(key);
  }
}

export function clearCache(): void {
  entries.clear();
  inFlight.clear();
  for (const key of Object.keys(metrics) as Array<keyof CacheMetrics>) {
    metrics[key] = 0;
  }
}

export function getCacheMetrics(): Readonly<CacheMetrics> {
  return { ...metrics };
}
