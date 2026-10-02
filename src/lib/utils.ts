import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function difficultyColor(difficulty: string) {
  switch (difficulty) {
    case "beginner": return "bg-accent/10 text-accent border-accent/20";
    case "intermediate": return "bg-primary/10 text-primary border-primary/20";
    case "advanced": return "bg-destructive/10 text-destructive border-destructive/20";
    default: return "";
  }
}
