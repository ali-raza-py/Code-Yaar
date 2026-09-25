"use client";

import { useRef, useMemo } from "react";
import { useFrame } from "@react-three/fiber";
import { Text, Line } from "@react-three/drei";
import * as THREE from "three";

interface CodeCubeProps {
  cursorX?: number;
  cursorY?: number;
  autoRotate?: boolean;
}

const FACE_SYMBOLS = ["</>", "{ }", "( )", "[ ]", "=>", "::"];

function CubeEdges() {
  const s = 1.2;
  const vertices = useMemo(() => [
    // Front face
    [-s, -s, s], [s, -s, s], [s, s, s], [-s, s, s],
    // Back face
    [-s, -s, -s], [s, -s, -s], [s, s, -s], [-s, s, -s],
  ] as [number, number, number][], []);

  const edges: [number, number][] = [
    [0, 1], [1, 2], [2, 3], [3, 0], // front
    [4, 5], [5, 6], [6, 7], [7, 4], // back
    [0, 4], [1, 5], [2, 6], [3, 7], // connections
  ];

  return (
    <group>
      {edges.map(([a, b], i) => (
        <Line
          key={i}
          points={[vertices[a], vertices[b]]}
          color="var(--primary)"
          lineWidth={0.8}
          transparent
          opacity={0.35}
        />
      ))}
    </group>
  );
}

function FaceLabels() {
  const s = 1.2;
  const offset = s + 0.01;

  const faces = useMemo(() => [
    { text: FACE_SYMBOLS[0], position: [0, 0, offset] as [number, number, number], rotation: [0, 0, 0] as [number, number, number] },
    { text: FACE_SYMBOLS[1], position: [0, 0, -offset] as [number, number, number], rotation: [0, Math.PI, 0] as [number, number, number] },
    { text: FACE_SYMBOLS[2], position: [offset, 0, 0] as [number, number, number], rotation: [0, Math.PI / 2, 0] as [number, number, number] },
    { text: FACE_SYMBOLS[3], position: [-offset, 0, 0] as [number, number, number], rotation: [0, -Math.PI / 2, 0] as [number, number, number] },
    { text: FACE_SYMBOLS[4], position: [0, offset, 0] as [number, number, number], rotation: [-Math.PI / 2, 0, 0] as [number, number, number] },
    { text: FACE_SYMBOLS[5], position: [0, -offset, 0] as [number, number, number], rotation: [Math.PI / 2, 0, 0] as [number, number, number] },
  ], [offset]);

  return (
    <group>
      {faces.map((face, i) => (
        <Text
          key={i}
          position={face.position}
          rotation={face.rotation}
          fontSize={0.22}
          color="#5eead4"
          anchorX="center"
          anchorY="middle"
          fillOpacity={0.25}
          font={undefined}
        >
          {face.text}
        </Text>
      ))}
    </group>
  );
}

export function CodeCube({ cursorX = 0, cursorY = 0, autoRotate = true }: CodeCubeProps) {
  const groupRef = useRef<THREE.Group>(null);
  const targetRotation = useRef({ x: 0, y: 0 });

  useFrame((_, delta) => {
    if (!groupRef.current) return;

    if (autoRotate) {
      // Slow auto-rotation
      groupRef.current.rotation.y += delta * 0.15;
      groupRef.current.rotation.x += delta * 0.08;
    }

    // Cursor-driven subtle tilt
    const targetX = (cursorY - 50) * 0.003;
    const targetY = (cursorX - 50) * 0.003;

    targetRotation.current.x += (targetX - targetRotation.current.x) * 0.05;
    targetRotation.current.y += (targetY - targetRotation.current.y) * 0.05;

    groupRef.current.rotation.x += targetRotation.current.x * delta;
    groupRef.current.rotation.y += targetRotation.current.y * delta;
  });

  return (
    <group ref={groupRef}>
      <CubeEdges />
      <FaceLabels />
    </group>
  );
}
