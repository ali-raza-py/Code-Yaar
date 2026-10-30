import * as React from "react";
import { cn } from "@/lib/utils";

interface ProgressRingProps extends React.SVGAttributes<SVGSVGElement> {
  /** 0–100 */
  value: number;
  size?: number;
  strokeWidth?: number;
  /** Track + indicator colors default to governed tokens. */
  trackClassName?: string;
  indicatorClassName?: string;
  children?: React.ReactNode;
  label?: string;
}

/**
 * Accessible circular progress indicator (progress ring).
 * Uses a single token-driven stroke; the filled portion is an
 * overlay so it adapts to light + dark surfaces automatically.
 */
export function ProgressRing({
  value,
  size = 112,
  strokeWidth = 8,
  trackClassName = "text-border",
  indicatorClassName = "text-cta",
  children,
  label = "Progress",
  className,
  ...props
}: ProgressRingProps) {
  const clamped = Math.max(0, Math.min(100, value));
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (clamped / 100) * circumference;

  return (
    <div
      className={cn("relative inline-flex items-center justify-center", className)}
      style={{ width: size, height: size }}
    >
      <svg
        width={size}
        height={size}
        role="progressbar"
        aria-label={label}
        aria-valuenow={Math.round(clamped)}
        aria-valuemin={0}
        aria-valuemax={100}
        className="-rotate-90"
        {...props}
      >
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          strokeWidth={strokeWidth}
          className={cn("stroke-[currentColor]", trackClassName)}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className={cn("stroke-[currentColor] transition-[stroke-dashoffset] duration-500", indicatorClassName)}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
        {children}
      </div>
    </div>
  );
}
