"use client";

import { useState } from "react";
import Link from "next/link";
import { Star, Clock, Users, ArrowRight } from "lucide-react";
import { catalogItems, catalogCategories } from "@/data/tracks";

function DifficultyBadge({ difficulty }: { difficulty: string }) {
  return (
    <span className={`dc-badge dc-badge-${difficulty}`}>
      {difficulty.charAt(0).toUpperCase() + difficulty.slice(1)}
    </span>
  );
}

export function DcCatalog() {
  const [activeCategory, setActiveCategory] = useState("All");

  const filtered =
    activeCategory === "All"
      ? catalogItems
      : catalogItems.filter((item) => item.category === activeCategory);

  return (
    <section className="dc-light-section py-16 sm:py-20">
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center">
          <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
            Explore projects & challenges.
          </h2>
          <p className="mx-auto mt-3 max-w-2xl text-lg text-muted-foreground">
            Browse our library of hands-on projects and coding challenges.
            Filter by category to find what matches your goals.
          </p>
        </div>

        {/* Category Tabs */}
        <div className="mt-8 flex flex-wrap items-center justify-center gap-2">
          {catalogCategories.map((cat) => (
            <button
              key={cat}
              onClick={() => setActiveCategory(cat)}
              className={`dc-tab ${activeCategory === cat ? "dc-tab-active" : ""}`}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Catalog Grid */}
        <div className="mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {filtered.map((item) => (
            <Link
              key={item.slug}
              href={item.type === "project" ? `/projects/${item.slug}` : `/challenges`}
              className="dc-card group flex flex-col overflow-hidden"
            >
              {/* Card top — colored bar by type */}
              <div
                className={`h-1.5 ${
                  item.type === "project"
                    ? "bg-[var(--primary)]"
                    : "bg-[var(--color-cta-green)]"
                }`}
              />

              <div className="flex flex-1 flex-col p-5">
                {/* Type + Difficulty */}
                <div className="flex items-center justify-between">
                  <span className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
                    {item.type}
                  </span>
                  <DifficultyBadge difficulty={item.difficulty} />
                </div>

                {/* Title */}
                <h3 className="mt-3 text-base font-semibold text-foreground group-hover:text-[var(--primary)]">
                  {item.title}
                </h3>

                {/* Description */}
                <p className="mt-2 flex-1 text-sm leading-relaxed text-muted-foreground">
                  {item.description}
                </p>

                {/* Meta row */}
                <div className="mt-4 flex items-center gap-3 text-xs text-muted-foreground">
                  <span className="flex items-center gap-1">
                    <Clock className="h-3.5 w-3.5" />
                    {item.estimatedHours}h
                  </span>
                  <span className="flex items-center gap-1">
                    <Users className="h-3.5 w-3.5" />
                    {item.learnerCount.toLocaleString()}
                  </span>
                  <span className="flex items-center gap-1">
                    <Star className="h-3.5 w-3.5 fill-[#f59e0b] text-[#f59e0b]" />
                    {item.rating}
                  </span>
                </div>
              </div>
            </Link>
          ))}
        </div>

        {/* View all */}
        <div className="mt-10 text-center">
          <Link href="/projects" className="dc-btn-outline">
            View all projects <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </div>
    </section>
  );
}
