"use client";

import { Suspense } from "react";
import { Canvas } from "@react-three/fiber";
import { cn } from "@/lib/utils";

interface SceneWrapperProps {
  children: React.ReactNode;
  className?: string;
  fallback?: React.ReactNode;
  camera?: { position: [number, number, number]; fov: number };
}

function LoadingFallback() {
  return (
    <div className="flex h-full w-full items-center justify-center">
      <div className="h-8 w-8 rounded-full border border-primary/20 border-t-primary/60 animate-spin" />
    </div>
  );
}

export function SceneWrapper({
  children,
  className,
  fallback,
  camera = { position: [0, 0, 5], fov: 45 },
}: SceneWrapperProps) {
  return (
    <div className={cn("relative", className)}>
      <Suspense fallback={fallback || <LoadingFallback />}>
        <Canvas
          dpr={[1, 1.5]}
          camera={camera}
          gl={{
            antialias: true,
            alpha: true,
            powerPreference: "high-performance",
          }}
          style={{ background: "transparent" }}
          aria-label="3D visualization"
        >
          {children}
        </Canvas>
      </Suspense>
    </div>
  );
}
