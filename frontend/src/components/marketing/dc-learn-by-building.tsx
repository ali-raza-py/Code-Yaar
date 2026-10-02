"use client";

import Link from "next/link";
import { ArrowRight, Terminal, CheckCircle } from "lucide-react";

export function DcLearnByBuilding() {
  return (
    <section className="bg-white py-16 sm:py-20">
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
        <div className="grid items-center gap-12 lg:grid-cols-2">
          {/* Left — Content */}
          <div className="order-2 lg:order-1">
            <div className="inline-flex items-center gap-2 rounded-full bg-[var(--color-cta-green)]/10 px-3 py-1 text-sm font-medium text-[var(--color-cta-green)]">
              <Terminal className="h-3.5 w-3.5" />
              Learn by doing
            </div>

            <h2 className="mt-4 text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
              Learn by building.
              <br />
              <span className="text-muted-foreground">Because tutorials aren&apos;t enough.</span>
            </h2>

            <p className="mt-4 text-lg text-muted-foreground">
              Every concept comes with a hands-on project. Write real code, solve real problems,
              and build a portfolio that proves what you can do.
            </p>

            <ul className="mt-6 space-y-3">
              {[
                "Interactive coding exercises in every lesson",
                "Guided projects with step-by-step milestones",
                "Coding challenges with instant feedback",
                "Build a portfolio of real, deployable projects",
              ].map((item) => (
                <li key={item} className="flex items-start gap-3">
                  <CheckCircle className="mt-0.5 h-5 w-5 shrink-0 text-[var(--color-cta-green)]" />
                  <span className="text-sm text-foreground">{item}</span>
                </li>
              ))}
            </ul>

            <div className="mt-8 flex gap-3">
              <Link href="/projects" className="dc-btn-primary">
                Browse Projects <ArrowRight className="h-4 w-4" />
              </Link>
              <Link href="/challenges" className="dc-btn-outline">
                Try a Challenge
              </Link>
            </div>
          </div>

          {/* Right — Code Editor Mockup */}
          <div className="order-1 lg:order-2">
            <div className="rounded-xl border border-[var(--color-section-border)] bg-[#1e1e2e] p-0 shadow-xl overflow-hidden">
              {/* Title bar */}
              <div className="flex items-center justify-between border-b border-white/10 px-4 py-2.5">
                <div className="flex items-center gap-1.5">
                  <div className="h-3 w-3 rounded-full bg-[#ff5f57]" />
                  <div className="h-3 w-3 rounded-full bg-[#febc2e]" />
                  <div className="h-3 w-3 rounded-full bg-[#28c840]" />
                </div>
                <span className="font-mono text-xs text-white/40">solution.py</span>
                <div className="w-12" />
              </div>

              {/* Code content */}
              <div className="p-5 font-mono text-sm leading-relaxed">
                <div>
                  <span className="text-[#c678dd]">def</span>{" "}
                  <span className="text-[#61afef]">two_sum</span>
                  <span className="text-white/60">(</span>
                  <span className="text-[#e5c07b]">nums</span>
                  <span className="text-white/40">,</span>{" "}
                  <span className="text-[#e5c07b]">target</span>
                  <span className="text-white/60">):</span>
                </div>
                <div className="mt-1">
                  <span className="text-white/30">    </span>
                  <span className="text-white/50"># Your solution here</span>
                </div>
                <div className="mt-1">
                  <span className="text-white/30">    </span>
                  <span className="text-white/60">seen = {"{}"}</span>
                </div>
                <div className="mt-1">
                  <span className="text-white/30">    </span>
                  <span className="text-[#c678dd]">for</span>
                  <span className="text-white/60"> i, num </span>
                  <span className="text-[#c678dd]">in</span>
                  <span className="text-white/60"> enumerate(nums):</span>
                </div>
                <div className="mt-1">
                  <span className="text-white/30">        </span>
                  <span className="text-white/60">complement = target - num</span>
                </div>
                <div className="mt-1">
                  <span className="text-white/30">        </span>
                  <span className="text-[#c678dd]">if</span>
                  <span className="text-white/60"> complement </span>
                  <span className="text-[#c678dd]">in</span>
                  <span className="text-white/60"> seen:</span>
                </div>
                <div className="mt-1">
                  <span className="text-white/30">            </span>
                  <span className="text-[#c678dd]">return</span>
                  <span className="text-white/60"> [seen[complement], i]</span>
                </div>
                <div className="mt-1">
                  <span className="text-white/30">        </span>
                  <span className="text-white/60">seen[num] = i</span>
                </div>

                {/* Test output */}
                <div className="mt-4 border-t border-white/10 pt-3">
                  <div className="flex items-center gap-2 text-[var(--color-cta-green)]">
                    <CheckCircle className="h-3.5 w-3.5" />
                    <span className="text-xs font-medium">All tests passed</span>
                  </div>
                  <div className="mt-1 text-xs text-white/30">
                    Runtime: 52ms | Memory: 14.2MB
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
