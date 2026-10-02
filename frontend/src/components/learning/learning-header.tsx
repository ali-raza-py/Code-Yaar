"use client";

import { Reveal } from "@/components/motion/reveal";
import dynamic from "next/dynamic";

const LearningDNALazy = dynamic(
  () => import("@/components/3d/learning-dna").then((m) => m.LearningDNA),
  { ssr: false }
);

const SceneWrapperLazy = dynamic(
  () => import("@/components/3d/scene-wrapper").then((m) => m.SceneWrapper),
  { ssr: false }
);

function DNAFallback() {
  return (
    <div className="flex h-full w-full items-center justify-center" aria-hidden="true">
      <div className="relative h-48 w-48">
        {/* CSS fallback: concentric rings */}
        {[...Array(4)].map((_, i) => (
          <div
            key={i}
            className="absolute inset-0 rounded-full border border-primary/10"
            style={{
              transform: `scale(${0.4 + i * 0.2})`,
              animation: `spin ${8 + i * 4}s linear infinite ${i % 2 === 0 ? "normal" : "reverse"}`,
            }}
          />
        ))}
      </div>
    </div>
  );
}

export function LearningHeader() {
  return (
    <div className="relative overflow-hidden border-b bg-white">
      {/* 3D DNA visualization — background */}
      <div className="absolute right-0 top-0 h-full w-1/3 opacity-20 hidden lg:block">
        <SceneWrapperLazy
          fallback={<DNAFallback />}
          camera={{ position: [0, 0, 6], fov: 35 }}
        >
          <LearningDNALazy />
        </SceneWrapperLazy>
      </div>

      <div className="relative mx-auto max-w-7xl px-4 py-20 sm:px-6 sm:py-28 lg:px-8 lg:py-32">
        <Reveal variant="fade-in">
          <div className="mb-3 text-xs font-semibold uppercase tracking-wider text-primary">
            Learn
          </div>
        </Reveal>

        <Reveal variant="fade-up" delay={0.1}>
          <h1 className="text-4xl font-bold tracking-tight sm:text-5xl lg:text-6xl">
            Build your
            <br />
            <span className="text-primary">foundation.</span>
          </h1>
          <p className="mt-2 text-2xl font-bold tracking-tight text-muted-foreground/70 sm:text-3xl lg:text-4xl">
            Then build something real.
          </p>
        </Reveal>

        <Reveal variant="fade-up" delay={0.2}>
          <p className="mt-6 max-w-lg text-base leading-relaxed text-muted-foreground sm:text-lg">
            A structured path from fundamentals to real engineering.
            Each stage connects to the next — learn concepts, practice them,
            then prove what you can build.
          </p>
        </Reveal>
      </div>
    </div>
  );
}
