'use client';

import { useEffect, useRef, useState } from 'react';
import { Check, Copy, Download, Printer, Share2 } from 'lucide-react';
import {
  copyText,
  linkedinShareUrl,
  openLinkedInShare,
} from '@/lib/share';

/** LinkedIn mark (lucide no longer ships brand icons). */
function LinkedInGlyph({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="currentColor"
      aria-hidden="true"
      className={className ?? 'h-4 w-4'}
    >
      <path d="M20.45 20.45h-3.56v-5.57c0-1.33-.03-3.04-1.85-3.04-1.86 0-2.14 1.45-2.14 2.94v5.67H9.35V9h3.41v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28zM5.34 7.43a2.06 2.06 0 1 1 0-4.13 2.06 2.06 0 0 1 0 4.13zM7.12 20.45H3.56V9h3.56v11.45z" />
    </svg>
  );
}

/** Transient inline confirmation without pulling in a toast system. */
function useConfirm(message: string) {
  const [shown, setShown] = useState(false);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => () => { if (timer.current) clearTimeout(timer.current); }, []);

  const show = () => {
    setShown(true);
    if (timer.current) clearTimeout(timer.current);
    timer.current = setTimeout(() => setShown(false), 2600);
  };

  return { shown, show, message };
}

const baseBtn =
  'focus-ring inline-flex min-h-10 items-center justify-center gap-2 rounded-lg px-4 text-sm font-semibold transition-colors disabled:opacity-60';

/**
 * Opens LinkedIn's official URL-sharing flow with the public verification URL.
 *
 * LinkedIn's share endpoint accepts only a URL — it cannot prefill text or
 * attach an image — so the suggested post text is copied to the clipboard
 * first, and the learner is told exactly that. They can attach the downloaded
 * certificate manually.
 */
export function LinkedInShareButton({
  url,
  text,
  label = 'Share on LinkedIn',
  variant = 'primary',
}: {
  url: string;
  text: string;
  label?: string;
  variant?: 'primary' | 'outline';
}) {
  const [blocked, setBlocked] = useState(false);
  const confirm = useConfirm('Post text copied — paste it into your LinkedIn post.');

  const handleClick = async () => {
    const copied = await copyText(text);
    const opened = openLinkedInShare(url);
    if (copied) confirm.show();
    setBlocked(!opened);
  };

  return (
    <div className="flex flex-col gap-1">
      <button
        type="button"
        onClick={handleClick}
        className={`${baseBtn} ${
          variant === 'primary'
            ? 'bg-[#0A66C2] text-white hover:bg-[#084e96]'
            : 'border border-border bg-card text-foreground hover:bg-muted'
        }`}
      >
        <LinkedInGlyph className="h-4 w-4" />
        {label}
      </button>
      {confirm.shown && (
        <p role="status" className="text-xs text-success">
          {confirm.message}
        </p>
      )}
      {blocked && (
        <p role="alert" className="text-xs text-warning">
          Pop-up blocked —{' '}
          <a
            className="underline"
            href={linkedinShareUrl(url)}
            target="_blank"
            rel="noopener noreferrer"
          >
            open the LinkedIn share window
          </a>
        </p>
      )}
    </div>
  );
}

export function CopyLinkButton({
  url,
  label = 'Copy verification link',
}: {
  url: string;
  label?: string;
}) {
  const confirm = useConfirm('Verification link copied.');
  return (
    <div className="flex flex-col gap-1">
      <button
        type="button"
        onClick={async () => {
          if (await copyText(url)) confirm.show();
        }}
        className={`${baseBtn} border border-border bg-card text-foreground hover:bg-muted`}
      >
        {confirm.shown ? (
          <Check className="h-4 w-4 text-success" aria-hidden="true" />
        ) : (
          <Copy className="h-4 w-4" aria-hidden="true" />
        )}
        {confirm.shown ? 'Copied' : label}
      </button>
      {confirm.shown && (
        <p role="status" className="text-xs text-success">
          {confirm.message}
        </p>
      )}
    </div>
  );
}

export function DownloadButton({
  onClick,
  busy,
  label = 'Download',
  icon = 'download',
  variant = 'primary',
}: {
  onClick: () => void;
  busy?: boolean;
  label?: string;
  icon?: 'download' | 'share' | 'print';
  variant?: 'primary' | 'outline';
}) {
  const Icon =
    icon === 'share' ? Share2 : icon === 'print' ? Printer : Download;
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={busy}
      className={`${baseBtn} ${
        variant === 'primary'
          ? 'bg-cta text-white hover:bg-cta-hover'
          : 'border border-border bg-card text-foreground hover:bg-muted'
      }`}
    >
      <Icon className="h-4 w-4" aria-hidden="true" />
      {busy ? 'Preparing…' : label}
    </button>
  );
}
