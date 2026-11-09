"use client";

import { useState } from "react";
import { ApiError, social } from "@/lib/api";
import { useAuth } from "@/hooks/use-auth";

export function FollowButton({
  username,
  initialFollowing,
  onChange,
}: {
  username: string;
  initialFollowing: boolean;
  onChange?: (following: boolean, followers: number) => void;
}) {
  const { user } = useAuth();
  const [following, setFollowing] = useState(initialFollowing);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!user || user.username === username) return null;

  async function toggle() {
    setBusy(true);
    setError(null);
    try {
      const result = following
        ? await social.unfollow(username)
        : await social.follow(username);
      setFollowing(result.following);
      onChange?.(result.following, result.followers_count);
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : "Could not update follow status.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex flex-col items-end gap-1">
      <button
        type="button"
        onClick={toggle}
        disabled={busy}
        className="rounded-lg border border-primary/30 px-4 py-2 text-sm font-semibold text-primary transition-colors hover:bg-primary/10 disabled:opacity-60"
      >
        {busy ? "Saving..." : following ? "Following" : "Follow"}
      </button>
      {error && <p className="max-w-40 text-right text-xs text-destructive">{error}</p>}
    </div>
  );
}
