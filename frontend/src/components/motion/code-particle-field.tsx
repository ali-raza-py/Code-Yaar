"use client";

import { useMemo } from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

const CODE_TOKENS = ["{}", "<>", "()", "[]", "=>", "::", "&&", "||", ";", "->", "fn", "if", "0x", "++"];

interface Particle {
  id: string;
  token: string;
  x: number;
  y: number;
  size: number;
  opacity: number;
  blur: number;
  duration: number;
  delay: number;
  drift: number;
}

interface CodeParticleFieldProps {
  className?: string;
  density?: "sparse" | "normal" | "dense";
  cursorX?: number;
}

const densityConfig = {
  sparse: { count: 8, maxOpacity: 0.06 },
  normal: { count: 14, maxOpacity: 0.08 },
  dense: { count: 22, maxOpacity: 0.1 },
};

export function CodeParticleField({
  className,
  density = "normal",
  cursorX = 0,
}: CodeParticleFieldProps) {
  const config = densityConfig[density];

  const particles = useMemo<Particle[]>(() => {
    return Array.from({ length: config.count }, (_, i) => ({
      id: `p-${i}`,
      token: CODE_TOKENS[i % CODE_TOKENS.length],
      x: 5 + ((i * 17 + 23) % 90),
      y: 5 + ((i * 13 + 7) % 85),
      size: 10 + (i % 3) * 2,
      opacity: 0.02 + ((i * 7) % 5) * 0.01,
      blur: i % 3 === 0 ? 1 : i % 3 === 1 ? 0.5 : 0,
      duration: 6 + (i % 5) * 2,
      delay: i * 0.4,
      drift: 8 + (i % 4) * 4,
    }));
  }, [config.count]);

  return (
    <div
      className={cn("absolute inset-0 overflow-hidden pointer-events-none select-none", className)}
      aria-hidden="true"
    >
      {particles.map((p) => {
        // Subtle cursor influence
        const influenceX = cursorX ? (cursorX - 50) * 0.02 : 0;

        return (
          <motion.span
            key={p.id}
            className="absolute font-mono text-primary"
            style={{
              left: `${p.x}%`,
              top: `${p.y}%`,
              fontSize: `${p.size}px`,
              filter: p.blur > 0 ? `blur(${p.blur}px)` : undefined,
            }}
            animate={{
              y: [0, -p.drift, 0],
              x: [0, influenceX * p.drift * 0.3, 0],
              opacity: [p.opacity, p.opacity * 1.5, p.opacity],
            }}
            transition={{
              duration: p.duration,
              repeat: Infinity,
              ease: "easeInOut",
              delay: p.delay,
            }}
          >
            {p.token}
          </motion.span>
        );
      })}
    </div>
  );
}
