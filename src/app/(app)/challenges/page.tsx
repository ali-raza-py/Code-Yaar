'use client';

import { useState, useEffect } from 'react';
import { challenges as challengesApi, ApiError } from '@/lib/api';
import { Challenge } from '@/types';
import { NetworkError, ServerError, EmptyState } from '@/components/learning/workspace/error-states';

type Difficulty = 'all' | 'beginner' | 'intermediate' | 'advanced';

const TOPICS = ['All', 'Arrays', 'Strings', 'Data Structures', 'Algorithms', 'Trees', 'Graphs', 'System Design', 'Dynamic Programming', 'Stacks', 'Linked Lists'];

export default function ChallengesPage() {
  const [challenges, setChallenges] = useState<Challenge[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [difficulty, setDifficulty] = useState<Difficulty>('all');
  const [topic, setTopic] = useState('All');
  const [search, setSearch] = useState('');

  useEffect(() => {
    loadChallenges();
  }, []);

  async function loadChallenges() {
    try {
      setLoading(true);
      const data = await challengesApi.list() as Challenge[];
      setChallenges(data);
      setError(null);
    } catch (e) {
      if (e instanceof ApiError && e.status === 401) {
        setError('auth');
      } else {
        setError('network');
      }
    } finally {
      setLoading(false);
    }
  }

  const filtered = challenges.filter((c) => {
    if (difficulty !== 'all' && c.difficulty !== difficulty) return false;
    if (topic !== 'All' && c.topic !== topic) return false;
    if (search && !c.title.toLowerCase().includes(search.toLowerCase()) && !c.description.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  const difficultyColor = (d: string) => {
    switch (d) {
      case 'beginner': return 'bg-green-100 text-green-700';
      case 'intermediate': return 'bg-yellow-100 text-yellow-700';
      case 'advanced': return 'bg-red-100 text-red-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  if (error === 'network') return <NetworkError />;
  if (error === 'auth') return <div className="p-8 text-center text-gray-500">Please sign in to view challenges.</div>;

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="mb-8">
        <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-purple-200 bg-purple-50 px-3 py-1 text-xs font-medium text-purple-700">
          <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 18.75h-9m9 0a3 3 0 013 3h-15a3 3 0 013-3m9 0v-3.375c0-.621-.503-1.125-1.125-1.125h-.871M7.5 18.75v-3.375c0-.621.504-1.125 1.125-1.125h.872m5.007 0H9.497m5.007 0a7.454 7.454 0 01-.982-3.172M9.497 14.25a7.454 7.454 0 00.981-3.172M5.25 4.236c-.982.143-1.954.317-2.916.52A6.003 6.003 0 007.73 9.728M5.25 4.236V4.5c0 2.108.966 3.99 2.48 5.228M5.25 4.236V2.721C7.456 2.41 9.71 2.25 12 2.25c2.291 0 4.545.16 6.75.47v1.516M18.75 4.236c.982.143 1.954.317 2.916.52A6.003 6.003 0 0116.27 9.728M18.75 4.236V4.5c0 2.108-.966 3.99-2.48 5.228m0 0a6.023 6.023 0 01-2.77.852m0 0l-.5.075a7.48 7.48 0 01-1 .067 7.48 7.48 0 01-1-.067l-.5-.075m3 0a6.022 6.022 0 01-2.77-.852" />
          </svg>
          CHALLENGES
        </div>
        <h1 className="text-3xl font-bold tracking-tight text-gray-900">
          Coding Challenges
        </h1>
        <p className="mt-2 text-gray-600 max-w-2xl">
          Test your skills with focused problems. Each challenge targets a specific concept and builds your engineering intuition.
        </p>
      </div>

      {/* Filters */}
      <div className="mb-6 space-y-4">
        {/* Search */}
        <div className="relative max-w-md">
          <svg className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
          </svg>
          <input
            type="text"
            placeholder="Search challenges..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full rounded-lg border border-gray-300 bg-white py-2 pl-10 pr-4 text-sm text-gray-900 placeholder:text-gray-400 focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
          />
        </div>

        {/* Difficulty Tabs */}
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-medium text-gray-500 mr-1">Difficulty:</span>
          {(['all', 'beginner', 'intermediate', 'advanced'] as Difficulty[]).map((d) => (
            <button
              key={d}
              onClick={() => setDifficulty(d)}
              className={`rounded-full px-3 py-1 text-xs font-medium capitalize transition-colors ${
                difficulty === d
                  ? 'bg-gray-900 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {d}
            </button>
          ))}
        </div>

        {/* Topic Tabs */}
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-medium text-gray-500 mr-1">Topic:</span>
          {TOPICS.map((t) => (
            <button
              key={t}
              onClick={() => setTopic(t)}
              className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
                topic === t
                  ? 'bg-gray-900 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      {/* Results count */}
      <p className="mb-4 text-sm text-gray-500">
        {filtered.length} challenge{filtered.length !== 1 ? 's' : ''} found
      </p>

      {/* Grid */}
      {loading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="rounded-lg border border-gray-200 bg-white p-5 animate-pulse">
              <div className="flex justify-between mb-3">
                <div className="h-5 w-16 rounded bg-gray-200" />
                <div className="h-5 w-12 rounded bg-gray-100" />
              </div>
              <div className="h-5 w-3/4 rounded bg-gray-200 mb-2" />
              <div className="h-3 w-full rounded bg-gray-100 mb-1" />
              <div className="h-3 w-2/3 rounded bg-gray-100" />
            </div>
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <EmptyState
          title="No challenges found"
          message="Try adjusting your filters or search terms."
          action={{ label: 'Clear filters', href: '#' }}
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((c) => (
            <div
              key={c.id}
              className="group rounded-lg border border-gray-200 bg-white p-5 transition-all hover:border-purple-300 hover:shadow-md"
            >
              <div className="flex items-center justify-between mb-3">
                <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium capitalize ${difficultyColor(c.difficulty)}`}>
                  {c.difficulty}
                </span>
                <span className="flex items-center gap-1 text-xs text-gray-500">
                  <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  {c.estimated_minutes}m
                </span>
              </div>
              <h3 className="text-base font-semibold text-gray-900 mb-1 group-hover:text-purple-700 transition-colors">
                {c.title}
              </h3>
              <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                {c.description}
              </p>
              <div className="flex items-center justify-between">
                <span className="inline-flex items-center rounded bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-600">
                  {c.topic}
                </span>
                <button className="inline-flex items-center gap-1 rounded-lg bg-purple-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-purple-700 transition-colors">
                  Start
                  <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
                  </svg>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
