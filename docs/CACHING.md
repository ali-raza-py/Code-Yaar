# Client caching architecture

Code-Yaar currently reads application data through the Django REST API. There
is no Supabase client or client-side query library in the frontend, so caching
is centralized in [`frontend/src/lib/api.ts`](../frontend/src/lib/api.ts) and
implemented by [`frontend/src/lib/cache.ts`](../frontend/src/lib/cache.ts).

## Policies

| Data | Freshness |
| --- | ---: |
| Courses, tracks | 10 minutes |
| Challenges/programming questions | 10 minutes |
| Practicals and projects | 20 minutes |
| Leaderboard | 2 minutes |
| Profile | 30 seconds |
| Profile analytics | 30 seconds |
| Progress and mutation responses | No cache |

Entries can be used as stale fallbacks for one additional TTL when a refresh
fails. There is no persistent browser cache for API responses, which avoids
putting private learner data into storage and naturally clears data on reload.

## Isolation and invalidation

Cache keys include either `public` or `user:<id>`. Authenticated requests are
not cached until the authenticated user ID is known. Logout, refresh-cookie
failure, and password changes clear the client cache. Profile, enrollment,
lesson, exercise, practical, and challenge mutations invalidate only related
content and user-data categories.

The cache is an optimization only: failures fall back to the API, and expired
entries are never treated as permanently valid. `getCacheMetrics()` exposes
in-memory hit, miss, deduplication, network, stale-fallback, and error counts
for development instrumentation; no benchmark values are fabricated by the
application.
