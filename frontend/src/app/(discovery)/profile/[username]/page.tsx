import type { Metadata } from 'next';
import Link from 'next/link';
import { Award, Globe, Link2, MapPin, UserRoundX } from 'lucide-react';
import {
  fetchPublicProfileServer,
  type PublicProfileResult,
} from '@/lib/server-verify';
import { Avatar } from '@/components/ui/avatar';
import { DifficultyPill } from '@/components/ui/difficulty-pill';
import { AchievementIcon } from '@/components/achievements/achievement-icon';

// Personal data — keep shareable but out of search indexes.
export const dynamic = 'force-dynamic';

function shortDate(value: string): string {
  if (!value) return '—';
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return '—';
  return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
}

async function load(username: string): Promise<PublicProfileResult | null> {
  const res = await fetchPublicProfileServer(username);
  return res.state === 'ok' ? res.data : null;
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ username: string }>;
}): Promise<Metadata> {
  const { username } = await params;
  const profile = await load(username);
  if (!profile) {
    return { title: 'Profile unavailable', robots: { index: false, follow: false } };
  }
  const name = profile.display_name || profile.username;
  return {
    title: `${name} — Code Yaar`,
    description:
      profile.bio ||
      `${name} · Level ${profile.stats.level} on Code Yaar Academy.`,
    // Privacy-honouring: never indexed, though any signed-in learner can view.
    robots: { index: false, follow: false },
    openGraph: {
      title: `${name} — Code Yaar`,
      description:
        profile.bio || `Level ${profile.stats.level} · ${profile.stats.badges_earned} badges earned.`,
      type: 'profile',
    },
  };
}

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-card border border-border bg-background p-3 text-center">
      <p className="text-lg font-bold text-foreground">{value}</p>
      <p className="text-[11px] uppercase tracking-wide text-muted-foreground">{label}</p>
    </div>
  );
}

function SocialLink({ href, label, children }: { href: string; label: string; children: React.ReactNode }) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer nofollow"
      className="focus-ring inline-flex min-h-9 items-center gap-1.5 rounded-lg border border-border bg-card px-3 py-1.5 text-xs font-semibold text-foreground hover:bg-muted"
    >
      {children}
      {label}
    </a>
  );
}

export default async function PublicProfilePage({
  params,
}: {
  params: Promise<{ username: string }>;
}) {
  const { username } = await params;
  const profile = await load(username);

  // Private or unknown — the API answers 404; render a neutral, no-index card.
  if (!profile) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-16 text-center">
        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-muted text-muted-foreground">
          <UserRoundX className="h-6 w-6" aria-hidden="true" />
        </div>
        <h1 className="mt-4 text-xl font-bold text-foreground">Profile unavailable</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          This learner either doesn&apos;t exist or keeps their profile private.
        </p>
        <Link
          href="/leaderboard"
          className="focus-ring mt-6 inline-flex min-h-10 items-center rounded-lg bg-cta px-4 py-2 text-sm font-semibold text-white hover:bg-cta-hover"
        >
          Back to Leaderboard
        </Link>
      </div>
    );
  }

  const name = profile.display_name || profile.username;

  return (
    <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6 lg:px-8">
      {/* ── Identity card ── */}
      <section className="card-hairline p-6">
        <div className="flex items-start gap-4">
          <Avatar
            src={profile.avatar}
            name={name}
            username={profile.username}
            size={80}
            className="ring-1 ring-border"
          />
          <div className="min-w-0 flex-1">
            <h1 className="text-2xl font-bold tracking-tight text-foreground">{name}</h1>
            <p className="text-sm text-muted-foreground">@{profile.username}</p>
            {profile.bio && <p className="mt-2 text-sm text-foreground">{profile.bio}</p>}
            <div className="mt-2 flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
              {profile.location && (
                <span className="inline-flex items-center gap-1">
                  <MapPin className="h-3.5 w-3.5" aria-hidden="true" />
                  {profile.location}
                </span>
              )}
              <span>Joined {shortDate(profile.joined_at)}</span>
            </div>
            {(profile.website_url || profile.github_url || profile.linkedin_url) && (
              <div className="mt-3 flex flex-wrap gap-2">
                {profile.website_url && (
                  <SocialLink href={profile.website_url} label="Website">
                    <Globe className="h-3.5 w-3.5" aria-hidden="true" />
                  </SocialLink>
                )}
                {profile.github_url && (
                  <SocialLink href={profile.github_url} label="GitHub">
                    <Link2 className="h-3.5 w-3.5" aria-hidden="true" />
                  </SocialLink>
                )}
                {profile.linkedin_url && (
                  <SocialLink href={profile.linkedin_url} label="LinkedIn">
                    <Link2 className="h-3.5 w-3.5" aria-hidden="true" />
                  </SocialLink>
                )}
              </div>
            )}
          </div>
        </div>

        {/* ── Stats ── */}
        <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
          <Stat label="Level" value={profile.stats.level} />
          <Stat label="XP" value={profile.stats.xp_points} />
          <Stat label="Streak" value={`${profile.stats.streak_days}d`} />
          <Stat label="Best streak" value={`${profile.stats.longest_streak}d`} />
          <Stat label="Courses" value={profile.stats.courses_completed} />
          <Stat label="Badges" value={profile.stats.badges_earned} />
        </div>
      </section>

      {/* ── Badges (privacy-gated) ── */}
      {profile.show_badges && profile.badges.length > 0 && (
        <section className="mt-6">
          <h2 className="mb-3 flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-muted-foreground">
            <Award className="h-4 w-4" aria-hidden="true" />
            Badges
          </h2>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {profile.badges.map((b) => (
              <a
                key={b.slug}
                href={b.verification_url}
                target="_blank"
                rel="noopener noreferrer nofollow"
                className="focus-ring flex items-start gap-3 rounded-card border border-border bg-card p-4 hover:bg-muted"
              >
                <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
                  <AchievementIcon name={b.icon} className="h-6 w-6" />
                </span>
                <span className="min-w-0">
                  <span className="block text-sm font-bold leading-snug text-foreground">
                    {b.title}
                  </span>
                  <span className="mt-1 flex flex-wrap items-center gap-1.5">
                    <DifficultyPill difficulty={b.difficulty} size="sm" />
                    <span className="text-[11px] text-muted-foreground">
                      {shortDate(b.earned_at)}
                    </span>
                  </span>
                </span>
              </a>
            ))}
          </div>
        </section>
      )}

      {/* ── Tracks (privacy-gated) ── */}
      {profile.show_courses && profile.tracks_completed.length > 0 && (
        <section className="mt-6">
          <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-muted-foreground">
            Completed tracks
          </h2>
          <ul className="flex flex-wrap gap-2">
            {profile.tracks_completed.map((t) => (
              <li
                key={t.slug}
                className="rounded-pill border border-border bg-card px-3 py-1.5 text-sm text-foreground"
              >
                {t.title}
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* ── Activity (privacy-gated) ── */}
      {profile.show_activity && profile.recent_activity.length > 0 && (
        <section className="mt-6">
          <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-muted-foreground">
            Recent activity
          </h2>
          <ul className="divide-y divide-border rounded-card border border-border bg-card">
            {profile.recent_activity.map((a, i) => (
              <li key={i} className="flex items-center justify-between gap-3 px-4 py-2.5 text-sm">
                <span className="text-foreground">{a.description}</span>
                <span className="shrink-0 text-xs text-muted-foreground">{shortDate(a.created_at)}</span>
              </li>
            ))}
          </ul>
        </section>
      )}

      <p className="mt-8 text-center text-xs text-muted-foreground">
        Want your own public profile?{' '}
        <Link href="/sign-up" className="font-semibold text-primary hover:underline">
          Join Code Yaar
        </Link>
      </p>
    </div>
  );
}
