'use client';

import React from 'react';
import { QueryClientProvider } from '@tanstack/react-query';
import { makeQueryClient } from '@/lib/query-client';
import { onApiCacheInvalidated } from '@/lib/api';

/**
 * Cache-invalidation prefixes emitted by `lib/api.ts` mutations, mapped to the
 * root of the TanStack Query keys that read the same data.
 */
const API_PREFIX_TO_QUERY_ROOT: Record<string, string> = {
  courses: 'courses',
  tracks: 'tracks',
  questions: 'challenges',
  leaderboard: 'leaderboard',
  practicals: 'practicals',
  projects: 'projects',
  progress: 'progress',
  profileStats: 'profile',
};

function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = React.useState(() => makeQueryClient());

  // Keep both caches in step: a mutation that invalidates an HTTP response
  // must also drop the mounted query that rendered it, otherwise the mutation
  // appears to have no effect until the query's staleTime runs out. A `*`
  // invalidation also arrives on sign-in/sign-out, where clearing everything
  // keeps one account's cached rows from being shown to the next.
  React.useEffect(
    () =>
      onApiCacheInvalidated((patterns) => {
        if (patterns.includes('*')) {
          queryClient.clear();
          return;
        }
        const roots = new Set(
          patterns
            .map((pattern) => API_PREFIX_TO_QUERY_ROOT[pattern.replace(/:$/, '')])
            .filter(Boolean),
        );
        if (roots.size === 0) return;
        queryClient.invalidateQueries({
          predicate: (query) => roots.has(String(query.queryKey[0])),
        });
      }),
    [queryClient],
  );

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}

export default Providers;
