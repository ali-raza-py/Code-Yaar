"use client";

import { useMemo, useState } from "react";
import type { ProgressDashboardData } from "@/lib/api";

type ContributionDay = ProgressDashboardData["contribution_data"][number];

const monthFormatter = new Intl.DateTimeFormat(undefined, { month: "short" });
const dateFormatter = new Intl.DateTimeFormat(undefined, {
  month: "long",
  day: "numeric",
  year: "numeric",
});
const colors = ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"];

function dayLabel(day: ContributionDay) {
  const activity = `${day.total_activities} learning activit${day.total_activities === 1 ? "y" : "ies"}`;
  return `${dateFormatter.format(new Date(`${day.date}T12:00:00`))} — ${activity}`;
}

export function ContributionGraph({
  days,
  totalActivities,
}: {
  days: ContributionDay[];
  totalActivities: number;
}) {
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const weeks = useMemo(() => {
    if (!days.length) return [];
    const firstDate = new Date(`${days[0].date}T12:00:00`);
    const leadingEmpty = firstDate.getDay();
    const padded = [...Array<ContributionDay | null>(leadingEmpty).fill(null), ...days];
    while (padded.length % 7) padded.push(null);
    return Array.from({ length: padded.length / 7 }, (_, index) =>
      padded.slice(index * 7, index * 7 + 7),
    );
  }, [days]);
  const selected = days.find((day) => day.date === selectedDate);

  return (
    <section className="rounded-card border border-border bg-card p-5 sm:p-6" aria-labelledby="contribution-heading">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 id="contribution-heading" className="font-bold">Learning activity</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            {totalActivities.toLocaleString()} meaningful activities in the last 12 months
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs text-muted-foreground" aria-label="Activity intensity legend">
          <span>Less</span>
          {colors.map((color, index) => (
            <span
              key={color}
              className="progress-cell h-3.5 w-3.5 rounded-sm border border-black/5"
              data-level={index}
              style={{ backgroundColor: color }}
              aria-label={`Intensity ${index}`}
            />
          ))}
          <span>More</span>
        </div>
      </div>

      <div className="mt-5 overflow-x-auto pb-2">
        <div className="min-w-[700px]">
          <div className="mb-2 ml-8 grid grid-flow-col auto-cols-[14px] gap-1 text-[10px] text-muted-foreground">
            {weeks.map((week, index) => {
              const firstDay = week.find(Boolean);
              const date = firstDay ? new Date(`${firstDay.date}T12:00:00`) : null;
              return (
                <span key={index} className="h-4">
                  {date && date.getDate() <= 7 ? monthFormatter.format(date) : ""}
                </span>
              );
            })}
          </div>
          <div className="flex gap-2">
            <div className="grid w-6 grid-rows-7 gap-1 text-[10px] leading-[14px] text-muted-foreground">
              <span />
              <span>Mon</span>
              <span />
              <span>Wed</span>
              <span />
              <span>Fri</span>
              <span />
            </div>
            <div className="grid grid-flow-col grid-rows-7 auto-cols-[14px] gap-1">
              {weeks.flatMap((week, weekIndex) =>
                week.map((day, dayIndex) =>
                  day ? (
                    <button
                      key={day.date}
                      type="button"
                      className="progress-cell h-3.5 w-3.5 rounded-sm border border-black/5 transition-transform hover:scale-125 focus-visible:z-10 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring"
                      data-level={day.intensity}
                      style={{ backgroundColor: colors[day.intensity] }}
                      title={dayLabel(day)}
                      aria-label={dayLabel(day)}
                      onClick={() => setSelectedDate(day.date)}
                    />
                  ) : (
                    <span key={`empty-${weekIndex}-${dayIndex}`} className="h-3.5 w-3.5" aria-hidden="true" />
                  ),
                ),
              )}
            </div>
          </div>
        </div>
      </div>

      {selected && (
        <div className="mt-4 rounded-lg border border-border bg-secondary p-3 text-sm" role="status">
          <p className="font-semibold">{dayLabel(selected)}</p>
          <p className="mt-1 text-xs text-muted-foreground">
            {selected.lessons_completed} lessons · {selected.practicals_completed} practicals · {selected.quizzes_completed} quizzes
          </p>
        </div>
      )}
    </section>
  );
}
