'use client';

// Standalone route kept alive for bookmarks and inbound links; it renders the
// same shared achievements body as the My Progress > Achievements tab.
import { AchievementsTabBody } from '@/components/progress/achievements-tab';

export default function AchievementsPage() {
  return <AchievementsTabBody />;
}
