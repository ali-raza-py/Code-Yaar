"use client";

import { useRef } from "react";
import { motion, useScroll, useTransform } from "framer-motion";
import { cn } from "@/lib/utils";

interface ParallaxProps {
  children: React.ReactNode;
  className?: string;
  depth?: number; // -1 to 1, negative = moves slower (further), positive = moves faster (closer)
  offset?: number; // base Y offset in pixels
}

export function Parallax({
  children,
  className,
  depth = 0.5,
  offset = 0,
}: ParallaxProps) {
  const ref = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "end start"],
  });

  // Map scroll progress to Y movement based on depth
  const maxMovement = 80 * Math.abs(depth);
  const y = useTransform(
    scrollYProgress,
    [0, 0.5, 1],
    depth > 0
      ? [maxMovement + offset, offset, -maxMovement + offset]
      : [-maxMovement + offset, offset, maxMovement + offset]
  );

  return (
    <div ref={ref} className={cn("relative", className)}>
      <motion.div style={{ y }}>{children}</motion.div>
    </div>
  );
}
