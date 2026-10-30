/**
 * Credential sharing helpers.
 *
 * LinkedIn's supported URL-sharing endpoint (`/sharing/share-offsite/`) takes
 * only the URL — it does not accept prefilled text and it does not upload an
 * image. We therefore:
 *   1. open the official share flow with the public verification URL, and
 *   2. offer the learner the suggested post text to paste alongside it,
 *      plus a manual download so they can attach the certificate image/PDF.
 *
 * Nothing here claims the share URL attaches artwork.
 */

export const HASHTAGS = '#CodeYaar #Learning #Programming #ProfessionalDevelopment';

export interface ShareTarget {
  url: string;
  /** Suggested post text (LinkedIn's share URL cannot prefill it). */
  text: string;
}

/** Official LinkedIn URL-sharing flow. */
export function linkedinShareUrl(url: string): string {
  return `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`;
}

export function certificateShareText(input: {
  courseTitle: string;
  learnerName?: string;
  verificationUrl: string;
}): string {
  const { courseTitle, verificationUrl } = input;
  return [
    'I’m pleased to share that I’ve successfully completed ' +
      `${courseTitle} from Code Yaar Academy.`,
    '',
    'This achievement represents another step in my journey of learning, ' +
      'building, and growing in technology.',
    '',
    `Verify my certificate: ${verificationUrl}`,
    '',
    HASHTAGS,
  ].join('\n');
}

export function badgeShareText(input: {
  badgeTitle: string;
  verificationUrl: string;
}): string {
  const { badgeTitle, verificationUrl } = input;
  return [
    `I’ve earned the "${badgeTitle}" achievement badge from Code Yaar Academy.`,
    '',
    'Every Code Yaar badge is backed by verified, server-recorded progress.',
    '',
    `Verify my badge: ${verificationUrl}`,
    '',
    HASHTAGS,
  ].join('\n');
}

/**
 * Open the LinkedIn share flow in a new tab. Returns false when the browser
 * blocked the popup so the caller can fall back to copying the link.
 */
export function openLinkedInShare(url: string): boolean {
  if (typeof window === 'undefined') return false;
  const win = window.open(linkedinShareUrl(url), '_blank', 'noopener,noreferrer');
  return win !== null;
}

/** Copy text to the clipboard with a legacy fallback. */
export async function copyText(text: string): Promise<boolean> {
  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(text);
      return true;
    }
  } catch {
    /* fall through to the legacy path */
  }
  try {
    const area = document.createElement('textarea');
    area.value = text;
    area.setAttribute('readonly', '');
    area.style.position = 'fixed';
    area.style.opacity = '0';
    document.body.appendChild(area);
    area.select();
    const ok = document.execCommand('copy');
    area.remove();
    return ok;
  } catch {
    return false;
  }
}

export function formatDate(iso: string | null | undefined): string {
  if (!iso) return '—';
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return '—';
  return d.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

export function formatShortDate(iso: string | null | undefined): string {
  if (!iso) return '—';
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return '—';
  return d.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

/** Absolute site URL for a path, preferring the current origin in the browser. */
export function absoluteSiteUrl(path: string): string {
  if (typeof window !== 'undefined' && window.location?.origin) {
    return `${window.location.origin}${path}`;
  }
  const base = process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000';
  return `${base.replace(/\/$/, '')}${path}`;
}
