"use client";

import { useEffect, useRef, useCallback, useState } from "react";

interface Particle {
  ox: number; // original x
  oy: number; // original y
  x: number;  // current x
  y: number;  // current y
  z: number;  // depth
  vx: number; // velocity x
  vy: number; // velocity y
  vz: number; // velocity z
  size: number;
  opacity: number;
  brightness: number;
  color: string;
}

interface ParticleLogoProps {
  className?: string;
  density?: "low" | "medium" | "high";
}

const DENSITY_CONFIG = {
  low: { gap: 5, maxParticles: 1000 },
  medium: { gap: 4, maxParticles: 2000 },
  high: { gap: 3, maxParticles: 4000 },
};

// Spring physics constants
const SPRING_STRENGTH = 0.06;
const DAMPING = 0.85;
const CURSOR_RADIUS = 80;
const CURSOR_FORCE = 15;
const Z_DEPTH_RANGE = 50;
const AMBIENT_NOISE = 0.1;

export function ParticleLogo({ className = "", density = "medium" }: ParticleLogoProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const particlesRef = useRef<Particle[]>([]);
  const mouseRef = useRef({ x: -1000, y: -1000, active: false });
  const animFrameRef = useRef<number>(0);
  const imageLoadedRef = useRef(false);
  const [isReady, setIsReady] = useState(false);
  const reducedMotionRef = useRef(false);
  const entranceProgressRef = useRef(0);
  const entranceStartRef = useRef<number | null>(null);

  // Detect reduced motion
  useEffect(() => {
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    reducedMotionRef.current = mq.matches;
    const handler = (e: MediaQueryListEvent) => {
      reducedMotionRef.current = e.matches;
    };
    mq.addEventListener("change", handler);
    return () => mq.removeEventListener("change", handler);
  }, []);

  // Sample logo image into particles — uses theme primary color for visibility
  const sampleLogo = useCallback(
    (img: HTMLImageElement, canvasWidth: number, canvasHeight: number) => {
      const config = DENSITY_CONFIG[density];
      const offscreen = document.createElement("canvas");
      const ctx = offscreen.getContext("2d", { willReadFrequently: true });
      if (!ctx) return [];

      // Fit logo into canvas with minimal padding
      const padding = 20;
      const availableW = canvasWidth - padding * 2;
      const availableH = canvasHeight - padding * 2;
      const scale = Math.min(availableW / img.width, availableH / img.height);
      const drawW = img.width * scale;
      const drawH = img.height * scale;
      const offsetX = (canvasWidth - drawW) / 2;
      const offsetY = (canvasHeight - drawH) / 2;

      offscreen.width = canvasWidth;
      offscreen.height = canvasHeight;
      ctx.drawImage(img, offsetX, offsetY, drawW, drawH);

      const imageData = ctx.getImageData(0, 0, canvasWidth, canvasHeight);
      const data = imageData.data;
      const gap = config.gap;
      const particles: Particle[] = [];

      // Detect background color from corners
      const cornerSamples = [
        [0, 0], [canvasWidth - 1, 0], [0, canvasHeight - 1], [canvasWidth - 1, canvasHeight - 1],
      ];
      let bgR = 0, bgG = 0, bgB = 0;
      for (const [cx, cy] of cornerSamples) {
        const ci = (cy * canvasWidth + cx) * 4;
        bgR += data[ci];
        bgG += data[ci + 1];
        bgB += data[ci + 2];
      }
      bgR = Math.round(bgR / 4);
      bgG = Math.round(bgG / 4);
      bgB = Math.round(bgB / 4);

      const bgBrightness = (bgR + bgG + bgB) / 3;
      const brightnessThreshold = bgBrightness + 25;

      // Get theme primary color from CSS variable
      const themeR = 120;
      const themeG = 40;
      const themeB = 180;

      for (let y = 0; y < canvasHeight; y += gap) {
        for (let x = 0; x < canvasWidth; x += gap) {
          const idx = (y * canvasWidth + x) * 4;
          const r = data[idx];
          const g = data[idx + 1];
          const b = data[idx + 2];
          const a = data[idx + 3];

          // Skip transparent pixels
          if (a < 128) continue;

          const brightness = (r + g + b) / 3;

          // Skip background-colored pixels
          if (brightness < brightnessThreshold) continue;

          // Also check color distance from background
          const colorDist = Math.sqrt(
            (r - bgR) ** 2 + (g - bgG) ** 2 + (b - bgB) ** 2
          );
          if (colorDist < 30) continue;

          const sizeVariation = 0.6 + Math.random() * 0.8;
          // Use theme purple color with brightness-based variation
          const colorVariation = 0.7 + (brightness / 255) * 0.3;
          const pr = Math.round(themeR * colorVariation);
          const pg = Math.round(themeG * colorVariation);
          const pb = Math.round(themeB * colorVariation);

          particles.push({
            ox: x,
            oy: y,
            x: x,
            y: y,
            z: (Math.random() - 0.5) * Z_DEPTH_RANGE,
            vx: 0,
            vy: 0,
            vz: 0,
            size: Math.max(1, gap * 0.6 * sizeVariation),
            opacity: 0.6 + (brightness / 255) * 0.4,
            brightness,
            color: `rgb(${pr},${pg},${pb})`,
          });
        }
      }

      // Limit particle count
      if (particles.length > config.maxParticles) {
        const step = particles.length / config.maxParticles;
        const sampled: Particle[] = [];
        for (let i = 0; i < config.maxParticles; i++) {
          sampled.push(particles[Math.floor(i * step)]);
        }
        return sampled;
      }

      return particles;
    },
    [density]
  );

  // Animation loop
  const animate = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const particles = particlesRef.current;
    const mouse = mouseRef.current;
    const reducedMotion = reducedMotionRef.current;

    // Entrance animation
    if (entranceStartRef.current === null) {
      entranceStartRef.current = performance.now();
    }
    const elapsed = performance.now() - entranceStartRef.current;
    const entranceDuration = reducedMotion ? 0 : 1200; // ms
    entranceProgressRef.current = Math.min(1, elapsed / entranceDuration);
    const entranceEase = 1 - Math.pow(1 - entranceProgressRef.current, 3); // ease-out cubic

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    for (let i = 0; i < particles.length; i++) {
      const p = particles[i];

      if (!reducedMotion) {
        // Entrance: lerp toward original position
        if (entranceProgressRef.current < 1) {
          const targetX = p.ox;
          const targetY = p.oy;
          p.x += (targetX - p.x) * 0.06 * entranceEase;
          p.y += (targetY - p.y) * 0.06 * entranceEase;
          p.z *= 0.92;
        } else {
          // Cursor displacement force
          const dx = p.x - mouse.x;
          const dy = p.y - mouse.y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < CURSOR_RADIUS && mouse.active) {
            const force = (1 - dist / CURSOR_RADIUS) * CURSOR_FORCE;
            const angle = Math.atan2(dy, dx);
            p.vx += Math.cos(angle) * force * 0.5;
            p.vy += Math.sin(angle) * force * 0.5;
            p.vz += force * 0.3;
          }

          // Spring back to original position
          const springX = (p.ox - p.x) * SPRING_STRENGTH;
          const springY = (p.oy - p.y) * SPRING_STRENGTH;
          const springZ = (0 - p.z) * SPRING_STRENGTH;

          // Ambient noise
          const noiseX = (Math.random() - 0.5) * AMBIENT_NOISE;
          const noiseY = (Math.random() - 0.5) * AMBIENT_NOISE;

          p.vx += springX + noiseX;
          p.vy += springY + noiseY;
          p.vz += springZ;

          // Apply damping
          p.vx *= DAMPING;
          p.vy *= DAMPING;
          p.vz *= DAMPING;

          // Update position
          p.x += p.vx;
          p.y += p.vy;
          p.z += p.vz;
        }
      }

      // Render particle with depth-based sizing and opacity
      const depthScale = 1 + p.z / (Z_DEPTH_RANGE * 3);
      const renderSize = p.size * depthScale;
      const renderOpacity = p.opacity * (0.7 + depthScale * 0.3);

      // Cursor proximity brightness boost
      let brightnessBoost = 0;
      if (mouse.active) {
        const dx = p.x - mouse.x;
        const dy = p.y - mouse.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < CURSOR_RADIUS * 1.5) {
          brightnessBoost = (1 - dist / (CURSOR_RADIUS * 1.5)) * 40;
        }
      }

      ctx.globalAlpha = Math.min(1, renderOpacity);
      ctx.fillStyle = p.color;

      // Draw rounded square particle
      const halfSize = renderSize / 2;
      ctx.beginPath();
      ctx.roundRect(
        p.x - halfSize,
        p.y - halfSize,
        renderSize,
        renderSize,
        renderSize * 0.2
      );
      ctx.fill();

      // Brightness overlay for cursor-affected particles
      if (brightnessBoost > 0) {
        ctx.globalAlpha = brightnessBoost / 255;
        ctx.fillStyle = "#ffffff";
        ctx.beginPath();
        ctx.roundRect(
          p.x - halfSize,
          p.y - halfSize,
          renderSize,
          renderSize,
          renderSize * 0.2
        );
        ctx.fill();
      }
    }

    ctx.globalAlpha = 1;
    animFrameRef.current = requestAnimationFrame(animate);
  }, []);

  // Initialize
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const logoSrc = "/logo-light.png";
    const img = new Image();
    img.crossOrigin = "anonymous";

    const initCanvas = () => {
      const container = canvas.parentElement;
      if (!container) return;

      const rect = container.getBoundingClientRect();
      const w = rect.width;
      const h = rect.height;

      if (w === 0 || h === 0) return;

      // Use CSS pixel dimensions (browser handles DPR scaling)
      canvas.width = w;
      canvas.height = h;

      particlesRef.current = sampleLogo(img, w, h);
      imageLoadedRef.current = true;
      setIsReady(true);
      entranceProgressRef.current = 0;
      entranceStartRef.current = null;

      // Scatter particles initially for entrance animation
      if (!reducedMotionRef.current) {
        for (const p of particlesRef.current) {
          const angle = Math.random() * Math.PI * 2;
          const dist = 100 + Math.random() * 200;
          p.x = p.ox + Math.cos(angle) * dist;
          p.y = p.oy + Math.sin(angle) * dist;
          p.z = (Math.random() - 0.5) * Z_DEPTH_RANGE * 3;
        }
      }

      // Start animation
      cancelAnimationFrame(animFrameRef.current);
      animFrameRef.current = requestAnimationFrame(animate);
    };

    img.onload = () => {
      initCanvas();
    };

    img.src = logoSrc;

    // Handle resize
    const handleResize = () => {
      if (imageLoadedRef.current) {
        initCanvas();
      }
    };
    window.addEventListener("resize", handleResize);

    return () => {
      cancelAnimationFrame(animFrameRef.current);
      window.removeEventListener("resize", handleResize);
    };
  }, [density, sampleLogo, animate]);

  // Mouse/touch handlers
  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    mouseRef.current = {
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
      active: true,
    };
  }, []);

  const handleMouseLeave = useCallback(() => {
    mouseRef.current = { x: -1000, y: -1000, active: false };
  }, []);

  const handleTouchMove = useCallback((e: React.TouchEvent) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const touch = e.touches[0];
    if (touch) {
      mouseRef.current = {
        x: touch.clientX - rect.left,
        y: touch.clientY - rect.top,
        active: true,
      };
    }
  }, []);

  const handleTouchEnd = useCallback(() => {
    mouseRef.current = { x: -1000, y: -1000, active: false };
  }, []);

  return (
    <div className={`relative ${className}`}>
      <canvas
        ref={canvasRef}
        className="h-full w-full"
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
        aria-label="Interactive Code-Yaar logo"
        role="img"
      />
      {!isReady && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="h-8 w-8 rounded-full border-2 border-primary/20 border-t-primary/60 animate-spin" />
        </div>
      )}
    </div>
  );
}
