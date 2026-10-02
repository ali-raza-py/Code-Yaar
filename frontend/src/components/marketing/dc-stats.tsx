"use client";

import { stats } from "@/data/tracks";

export function DcStats() {
  return (
    <section className="dc-dark-section relative py-14">
      <div className="absolute inset-0 bg-gradient-to-r from-[#1b2631] via-[#1e2d3d] to-[#1b2631]" />
      <div className="relative mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 gap-8 sm:grid-cols-4">
          {stats.map((stat) => (
            <div key={stat.label} className="text-center">
              <div className="text-3xl font-bold text-white sm:text-4xl">
                {stat.value}
              </div>
              <div className="mt-1 text-sm text-[var(--color-text-dark-muted)]">
                {stat.label}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
