'use client';

import dynamic from "next/dynamic";
import { FoundingTeamSkeleton } from "./founding-team-skeleton";

const FoundingTeam = dynamic(
  () => import("@/components/marketing/founding-team").then((mod) => mod.FoundingTeam),
  { ssr: false, loading: () => <FoundingTeamSkeleton /> },
);

export function FoundingTeamLazy() {
  return <FoundingTeam />;
}
