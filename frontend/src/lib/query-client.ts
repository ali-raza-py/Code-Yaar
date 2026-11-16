'use client';

import { QueryClient } from '@tanstack/react-query';

export function makeQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        // Semi-static catalogue data changes only when admins publish/edit.
        // Keep a generous staleTime so navigation between pages does not
        // refetch, and let the per-query overrides below win where needed.
        staleTime: 10 * 60 * 1000, // 10 minutes
        gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
        retry: 1,
        refetchOnWindowFocus: false,
        refetchOnReconnect: false,
        // Structural sharing is on by default in v5 — keep it so unchanged
        // list items are not re-rendered when only the tail of a page shifts.
        structuralSharing: true,
      },
      mutations: {
        retry: false,
      },
    },
  });
}

/**
 * Per-query default overrides keyed by the cache policy used in lib/api.ts.
 * Pages that build their own useQuery can pass these through:
 *   useQuery({ queryKey: [...], queryFn: ..., ...queryDefaults['courses'] })
 */
export const queryDefaults = {
  courses: { staleTime: 10 * 60 * 1000 }, // 10 minutes
  tracks: { staleTime: 10 * 60 * 1000 }, // 10 minutes
  leaderboard: { staleTime: 45 * 1000 }, // 45 seconds
  challenges: { staleTime: 5 * 60 * 1000 }, // 5 minutes
  announcements: { staleTime: 2 * 60 * 1000 }, // 2 minutes
  practicals: { staleTime: 5 * 60 * 1000 }, // 5 minutes
  projects: { staleTime: 60 * 1000 }, // 1 minute
  profile: { staleTime: 60 * 1000 }, // 1 minute
  progress: { staleTime: 0, gcTime: 0 }, // never cache personal data
  analytics: { staleTime: 60 * 1000 }, // 1 minute
} as const;

export type QueryPolicy = keyof typeof queryDefaults;
