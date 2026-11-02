/**
 * Server-side portfolio lookups for the public `/profile/[username]/...` routes.
 *
 * Mirrors `server-verify.ts`: every page renders from the real API answer so
 * the HTML and Open Graph metadata reflect what the owner actually published —
 * never a client-side guess. A 404 (unknown user, private account, or an
 * unpublished portfolio) resolves to `missing`, which the page turns into a
 * neutral card plus `robots: noindex` so private work is never indexed or
 * leaked through SSR.
 */

import type { PublicPortfolioData, PublicProject } from '@/lib/api';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export type PortfolioOutcome<T> =
  | { state: 'ok'; data: T }
  | { state: 'missing' }
  | { state: 'unavailable' };

async function lookup<T>(path: string): Promise<PortfolioOutcome<T>> {
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      cache: 'no-store',
      headers: { Accept: 'application/json' },
    });
    if (res.status === 404) return { state: 'missing' };
    if (!res.ok) return { state: 'unavailable' };
    const data = (await res.json()) as T;
    return { state: 'ok', data };
  } catch {
    return { state: 'unavailable' };
  }
}

export function fetchPublicPortfolioServer(username: string) {
  return lookup<PublicPortfolioData>(`/portfolio/${encodeURIComponent(username)}/`);
}

export function fetchPublicProjectServer(username: string, slug: string) {
  return lookup<PublicProject>(
    `/portfolio/${encodeURIComponent(username)}/projects/${encodeURIComponent(slug)}/`,
  );
}
