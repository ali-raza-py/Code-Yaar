"use client";

import { useRef, useMemo } from "react";
import { useFrame } from "@react-three/fiber";
import { Text, Line } from "@react-three/drei";
import * as THREE from "three";

const SKILL_LABELS = ["Think", "Learn", "Practice", "Build", "Debug", "Ship", "Prove", "Evolve"];
const CODE_TOKENS = ["{}", "<>", "=>", "::", "fn", "if", "[]", "()"];

interface LearningDNAProps {
  cursorY?: number;
}

function HelixStrand({ offset = 0 }: { offset: number }) {
  const points = useMemo(() => {
    const pts: [number, number, number][] = [];
    for (let i = 0; i < 60; i++) {
      const t = (i / 60) * Math.PI * 4;
      const y = (i / 60) * 6 - 3;
      const x = Math.cos(t + offset) * 0.8;
      const z = Math.sin(t + offset) * 0.8;
      pts.push([x, y, z]);
    }
    return pts;
  }, [offset]);

  return (
    <Line
      points={points}
      color="#5eead4"
      lineWidth={0.6}
      transparent
      opacity={0.2}
    />
  );
}

function ConnectorBars() {
  const bars = useMemo(() => {
    const result: { start: [number, number, number]; end: [number, number, number]; y: number }[] = [];
    for (let i = 0; i < 16; i++) {
      const t = (i / 16) * Math.PI * 4;
      const y = (i / 16) * 6 - 3;
      const x1 = Math.cos(t) * 0.8;
      const z1 = Math.sin(t) * 0.8;
      const x2 = Math.cos(t + Math.PI) * 0.8;
      const z2 = Math.sin(t + Math.PI) * 0.8;
      result.push({
        start: [x1, y, z1],
        end: [x2, y, z2],
        y,
      });
    }
    return result;
  }, []);

  return (
    <group>
      {bars.map((bar, i) => (
        <group key={i}>
          <Line
            points={[bar.start, bar.end]}
            color="#5eead4"
            lineWidth={0.3}
            transparent
            opacity={0.12}
          />
          {/* Node at midpoint */}
          <mesh position={[0, bar.y, 0]}>
            <sphereGeometry args={[0.04, 8, 8]} />
            <meshBasicMaterial color="#5eead4" transparent opacity={0.3} />
          </mesh>
        </group>
      ))}
    </group>
  );
}

function SkillLabels() {
  const labels = useMemo(() => {
    return SKILL_LABELS.map((label, i) => {
      const t = (i / SKILL_LABELS.length) * Math.PI * 4;
      const y = (i / SKILL_LABELS.length) * 6 - 3;
      const x = Math.cos(t) * 1.3;
      const z = Math.sin(t) * 1.3;
      return { text: label, position: [x, y, z] as [number, number, number] };
    });
  }, []);

  return (
    <group>
      {labels.map((label, i) => (
        <Text
          key={i}
          position={label.position}
          fontSize={0.12}
          color="#94a3b8"
          anchorX="center"
          anchorY="middle"
          fillOpacity={0.35}
          font={undefined}
        >
          {label.text}
        </Text>
      ))}
    </group>
  );
}

function CodeTokens() {
  const tokens = useMemo(() => {
    return CODE_TOKENS.map((token, i) => {
      const t = (i / CODE_TOKENS.length) * Math.PI * 4 + Math.PI;
      const y = (i / CODE_TOKENS.length) * 6 - 3;
      const x = Math.cos(t) * 1.1;
      const z = Math.sin(t) * 1.1;
      return { text: token, position: [x, y, z] as [number, number, number] };
    });
  }, []);

  return (
    <group>
      {tokens.map((token, i) => (
        <Text
          key={i}
          position={token.position}
          fontSize={0.09}
          color="#5eead4"
          anchorX="center"
          anchorY="middle"
          fillOpacity={0.2}
          font={undefined}
        >
          {token.text}
        </Text>
      ))}
    </group>
  );
}

export function LearningDNA({ cursorY = 0 }: LearningDNAProps) {
  const groupRef = useRef<THREE.Group>(null);

  useFrame((_, delta) => {
    if (!groupRef.current) return;
    // Slow rotation
    groupRef.current.rotation.y += delta * 0.2;

    // Subtle cursor influence on tilt
    const targetTilt = (cursorY - 50) * 0.001;
    groupRef.current.rotation.x += (targetTilt - groupRef.current.rotation.x * 0.5) * delta * 0.5;
  });

  return (
    <group ref={groupRef}>
      <HelixStrand offset={0} />
      <HelixStrand offset={Math.PI} />
      <ConnectorBars />
      <SkillLabels />
      <CodeTokens />
    </group>
  );
}
