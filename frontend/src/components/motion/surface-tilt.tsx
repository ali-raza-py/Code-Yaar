"use client";

import { useRef, useState, useCallback, useSyncExternalStore } from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface SurfaceTiltProps {
  children: React.ReactNode;
  className?: string;
  maxDeg?: number;
  enabled?: boolean;
}

export function SurfaceTilt({
  children,
  className,
  maxDeg = 2,
  enabled = true,
}: SurfaceTiltProps) {
  const ref = useRef<HTMLDivElement>(null);
  const [tilt, setTilt] = useState({ x: 0, y: 0 });

  // Detect desktop via matchMedia subscription
  const isDesktop = useSyncExternalStore(
    (cb) => {
      const mq = window.matchMedia("(pointer: fine)");
      mq.addEventListener("change", cb);
      return () => mq.removeEventListener("change", cb);
    },
    () => {
      if (!enabled) return false;
      const isFine = window.matchMedia("(pointer: fine)").matches;
      const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      return isFine && !reducedMotion;
    },
    () => false
  );

  const handleMouseMove = useCallback(
    (e: React.MouseEvent) => {
      if (!ref.current || !isDesktop) return;
      const rect = ref.current.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width - 0.5;
      const y = (e.clientY - rect.top) / rect.height - 0.5;
      setTilt({ x: y * maxDeg * -1, y: x * maxDeg });
    },
    [maxDeg, isDesktop]
  );

  const handleMouseLeave = useCallback(() => {
    setTilt({ x: 0, y: 0 });
  }, []);

  if (!isDesktop) return <div className={className}>{children}</div>;

  return (
    <motion.div
      ref={ref}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      animate={{
        rotateX: tilt.x,
        rotateY: tilt.y,
      }}
      transition={{ type: "spring", stiffness: 300, damping: 30 }}
      style={{ transformStyle: "preserve-3d" }}
      className={cn("will-change-transform", className)}
    >
      {children}
    </motion.div>
  );
}
