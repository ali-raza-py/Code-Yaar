"use client";

type ProgressBarProps = {
  value: number;
  label?: string;
  showValue?: boolean;
  size?: "sm" | "md";
};

export function ProgressBar({
  value,
  label,
  showValue = false,
  size = "sm",
}: ProgressBarProps) {
  const clampedValue = Math.min(100, Math.max(0, value));
  const height = size === "md" ? "h-3" : "h-2";

  return (
    <div>
      {(label || showValue) && (
        <div className="mb-2 flex items-center justify-between gap-3 text-sm">
          {label && <span className="font-medium">{label}</span>}
          {showValue && <span className="font-semibold text-cta">{Math.round(clampedValue)}%</span>}
        </div>
      )}
      <div
        className={`${height} overflow-hidden rounded-full bg-muted`}
        role="progressbar"
        aria-label={label || "Progress"}
        aria-valuenow={clampedValue}
        aria-valuemin={0}
        aria-valuemax={100}
      >
        <div
          className="h-full rounded-full bg-cta transition-[width] duration-500 motion-reduce:transition-none"
          style={{ width: `${clampedValue}%` }}
        />
      </div>
    </div>
  );
}
