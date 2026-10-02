"use client";

import { useRef } from "react";
import { motion, useInView } from "framer-motion";
import { RoadmapNode } from "./roadmap-node";
import type { RoadmapStage as RoadmapStageType } from "@/types";

interface RoadmapStageProps {
  stage: RoadmapStageType;
  index: number;
  isLast: boolean;
}

export function RoadmapStage({ stage, index, isLast }: RoadmapStageProps) {
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true, margin: "-80px" });

  // Alternating depth offsets for spatial feel
  const depthOffset = index % 2 === 0 ? -8 : 8;

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 40, rotateX: 4 }}
      animate={isInView ? { opacity: 1, y: 0, rotateX: 0 } : { opacity: 0, y: 40, rotateX: 4 }}
      transition={{
        duration: 0.7,
        ease: [0.25, 0.1, 0.25, 1],
        type: "spring",
        stiffness: 100,
        damping: 20,
      }}
      className="relative perspective-card"
    >
      {/* The node with depth transform */}
      <motion.div
        style={{
          transform: `translateZ(${depthOffset}px)`,
        }}
      >
        <RoadmapNode stage={stage} index={index} />
      </motion.div>

      {/* Connection to next node */}
      {!isLast && (
        <div className="relative mx-auto hidden h-20 w-px lg:block">
          <motion.div
            className="absolute inset-0 bg-gradient-to-b from-primary/25 via-primary/15 to-transparent"
            initial={{ scaleY: 0, opacity: 0 }}
            animate={isInView ? { scaleY: 1, opacity: 1 } : { scaleY: 0, opacity: 0 }}
            transition={{ duration: 0.6, delay: 0.4, ease: "easeOut" }}
            style={{ transformOrigin: "top" }}
          />
          {/* Small dot at midpoint */}
          <motion.div
            className="absolute left-1/2 top-1/2 h-1.5 w-1.5 -translate-x-1/2 -translate-y-1/2 rounded-full bg-primary/30"
            initial={{ scale: 0 }}
            animate={isInView ? { scale: 1 } : { scale: 0 }}
            transition={{ duration: 0.3, delay: 0.7 }}
          />
        </div>
      )}

      {/* Mobile connection */}
      {!isLast && (
        <div className="relative ml-[23px] h-10 w-px lg:hidden">
          <motion.div
            className="absolute inset-0 bg-gradient-to-b from-primary/25 to-primary/10"
            initial={{ scaleY: 0 }}
            animate={isInView ? { scaleY: 1 } : { scaleY: 0 }}
            transition={{ duration: 0.4, delay: 0.3, ease: "easeOut" }}
            style={{ transformOrigin: "top" }}
          />
        </div>
      )}
    </motion.div>
  );
}
