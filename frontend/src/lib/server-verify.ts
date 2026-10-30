/**
 * Server-side credential verification lookups.
 *
 * Used by the public `/verify/*` pages so the HTML (and the Open Graph
 * metadata) reflects the real registry record — never a client-side guess.
 * Only privacy-safe fields are consumed; nothing account-related is exposed.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export interface CertificateVerifyResult {
  found: boolean;
  valid: boolean;
  credential_id?: string;
  public_id?: string;
  student_name?: string;
  course_title?: string;
  issued_at?: string;
  completion_verified_at?: string | null;
  status?: string;
  revoked?: boolean;
  superseded?: boolean;
  issuer?: string;
  verification_url?: string;
  qr_data_url?: string;
  final_score?: number | null;
  detail?: string;
}

export interface BadgeVerifyResult {
  found: boolean;
  valid: boolean;
  kind?: 'badge';
  credential_id?: string;
  public_id?: string;
  recipient_name?: string;
  title?: string;
  description?: string;
  category?: string;
  category_label?: string;
  level_label?: string;
  issued_at?: string | null;
  issuer?: string;
  status?: string;
  revoked?: boolean;
  verification_url?: string;
  detail?: string;
}

export type VerifyOutcome<T> =
  | { state: 'ok'; data: T }
  | { state: 'missing' }
  | { state: 'unavailable' };

async function lookup<T>(path: string): Promise<VerifyOutcome<T>> {
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

export function verifyCertificateServer(id: string) {
  return lookup<CertificateVerifyResult>(
    `/certificates/verify/${encodeURIComponent(id)}/`
  );
}

export function verifyBadgeServer(id: string) {
  return lookup<BadgeVerifyResult>(
    `/badges/verify/${encodeURIComponent(id)}/`
  );
}

export function badgeOgImageUrl(id: string): string {
  // LinkedIn-ready achievement graphic (badge + branding + verify URL), not
  // the bare medallion — so a shared badge link previews as a real credential.
  return `${API_BASE}/badges/verify/${encodeURIComponent(id)}/share.png?preset=square`;
}

/** Public badge medallion artwork (the same file the download endpoints ship). */
export function badgeMedallionImageUrl(id: string): string {
  return `${API_BASE}/badges/verify/${encodeURIComponent(id)}/image.png`;
}

/** Public certificate PNG used as the Open Graph link-preview image. */
export function certificateOgImageUrl(id: string): string {
  return `${API_BASE}/certificates/verify/${encodeURIComponent(id)}/image.png`;
}
