import type { Metadata } from "next";
import { LearningEntry } from "@/components/marketing/learning-entry";

export const metadata: Metadata = {
  title: "Code Yaar — Think. Build. Evolve.",
  description:
    "An AI-native computer science education platform: structured learning tracks, hands-on lessons, coding challenges, real projects, XP, badges and verifiable certificates.",
};

export default function HomePage() {
  return <LearningEntry />;
}
