"use client";

import { useRef, useEffect, useState } from "react";
import { motion, useInView } from "framer-motion";

interface RoadmapConnectionsProps {
  nodePositions: { x: number; y: number }[];
}

export function RoadmapConnections({ nodePositions }: RoadmapConnectionsProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const isInView = useInView(svgRef, { once: true, margin: "-100px" });
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });

  useEffect(() => {
    if (!svgRef.current) return;
    const rect = svgRef.current.getBoundingClientRect();
    setDimensions({ width: rect.width, height: rect.height });
  }, []);

  if (nodePositions.length < 2) return null;

  // Convert percentage positions to pixel positions
  const toPixel = (pct: { x: number; y: number }) => ({
    x: (pct.x / 100) * dimensions.width,
    y: (pct.y / 100) * dimensions.height,
  });

  const connections: { from: { x: number; y: number }; to: { x: number; y: number }; index: number }[] = [];
  for (let i = 0; i < nodePositions.length - 1; i++) {
    connections.push({
      from: toPixel(nodePositions[i]),
      to: toPixel(nodePositions[i + 1]),
      index: i,
    });
  }

  return (
    <svg
      ref={svgRef}
      className="absolute inset-0 h-full w-full pointer-events-none"
      aria-hidden="true"
    >
      {connections.map((conn, i) => {
        const dx = conn.to.x - conn.from.x;
        const dy = conn.to.y - conn.from.y;
        const length = Math.sqrt(dx * dx + dy * dy);

        // Curved path with control point
        const midX = (conn.from.x + conn.to.x) / 2;
        const midY = (conn.from.y + conn.to.y) / 2;
        const offsetX = dy * 0.15;
        const offsetY = -dx * 0.15;

        const path = `M ${conn.from.x} ${conn.from.y} Q ${midX + offsetX} ${midY + offsetY} ${conn.to.x} ${conn.to.y}`;

        return (
          <g key={i}>
            {/* Connection line */}
            <motion.path
              d={path}
              fill="none"
              stroke="var(--primary)"
              strokeWidth="1.5"
              strokeOpacity={0.2}
              strokeDasharray={length}
              initial={{ strokeDashoffset: length }}
              animate={isInView ? { strokeDashoffset: 0 } : { strokeDashoffset: length }}
              transition={{
                duration: 0.8,
                delay: 0.3 + i * 0.2,
                ease: [0.25, 0.1, 0.25, 1],
              }}
            />
            {/* Traveling particle dot */}
            {isInView && (
              <motion.circle
                r="2.5"
                fill="var(--primary)"
                opacity={0.5}
                initial={{ offsetDistance: "0%" }}
                animate={{ offsetDistance: "100%" }}
                transition={{
                  duration: 2,
                  delay: 0.8 + i * 0.3,
                  repeat: Infinity,
                  repeatDelay: 3,
                  ease: "easeInOut",
                }}
                style={{
                  offsetPath: `path('${path}')`,
                }}
              />
            )}
          </g>
        );
      })}
    </svg>
  );
}
