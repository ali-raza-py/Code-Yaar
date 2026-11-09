import {
  Award,
  BookOpen,
  Braces,
  CheckCircle2,
  Flame,
  GraduationCap,
  Layers,
  Sparkles,
  Star,
  Trophy,
  Users,
  Zap,
  type LucideIcon,
} from "lucide-react";

/**
 * Resolves the `icon` string stored on a badge/achievement (server-defined) to
 * a Lucide component. Unknown or empty names fall back to `Award` so a new
 * registry icon never renders as a blank or crashes the page.
 */
const ICONS: Record<string, LucideIcon> = {
  award: Award,
  book: BookOpen,
  bolt: Zap,
  braces: Braces,
  check: CheckCircle2,
  fire: Flame,
  graduation: GraduationCap,
  layers: Layers,
  medal: Award,
  sparkle: Sparkles,
  star: Star,
  trophy: Trophy,
  users: Users,
};

export function AchievementIcon({
  name,
  className,
}: {
  name?: string | null;
  className?: string;
}) {
  const key = (name ?? "").toLowerCase().trim();
  const Comp = ICONS[key] ?? Award;
  return <Comp className={className} aria-hidden="true" />;
}
