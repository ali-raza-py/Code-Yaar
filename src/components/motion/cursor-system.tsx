"use client";

import { createContext, useContext, useEffect, useRef, useState, useCallback, useSyncExternalStore } from "react";
import { motion, AnimatePresence } from "framer-motion";

type CursorVariant = "default" | "interactive" | "roadmap" | "code" | "drag";

interface CursorContextValue {
  x: number;
  y: number;
  xPercent: number;
  yPercent: number;
  variant: CursorVariant;
  setVariant: (v: CursorVariant) => void;
  isDesktop: boolean;
}

const CursorContext = createContext<CursorContextValue>({
  x: 0,
  y: 0,
  xPercent: 50,
  yPercent: 50,
  variant: "default",
  setVariant: () => {},
  isDesktop: false,
});

export function useCursor() {
  return useContext(CursorContext);
}

export function CursorProvider({ children }: { children: React.ReactNode }) {
  const [x, setX] = useState(0);
  const [y, setY] = useState(0);
  const [xPercent, setXPercent] = useState(50);
  const [yPercent, setYPercent] = useState(50);
  const [variant, setVariant] = useState<CursorVariant>("default");
  const [visible, setVisible] = useState(false);
  const rafRef = useRef<number>(0);
  const targetRef = useRef({ x: 0, y: 0 });

  // Detect desktop via matchMedia subscription (no setState in effect)
  const isDesktop = useSyncExternalStore(
    (cb) => {
      const mq = window.matchMedia("(pointer: fine)");
      mq.addEventListener("change", cb);
      return () => mq.removeEventListener("change", cb);
    },
    () => {
      const isFine = window.matchMedia("(pointer: fine)").matches;
      const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      return isFine && !reducedMotion;
    },
    () => false // SSR fallback
  );

  const handleMouseMove = useCallback((e: MouseEvent) => {
    targetRef.current = { x: e.clientX, y: e.clientY };
    const xPct = (e.clientX / window.innerWidth) * 100;
    const yPct = (e.clientY / window.innerHeight) * 100;

    if (!visible) setVisible(true);

    // Use RAF for smooth updates
    cancelAnimationFrame(rafRef.current);
    rafRef.current = requestAnimationFrame(() => {
      setX(targetRef.current.x);
      setY(targetRef.current.y);
      setXPercent(xPct);
      setYPercent(yPct);
    });
  }, [visible]);

  const handleMouseLeave = useCallback(() => {
    setVisible(false);
  }, []);

  const handleMouseEnter = useCallback(() => {
    setVisible(true);
  }, []);

  useEffect(() => {
    if (!isDesktop) return;

    window.addEventListener("mousemove", handleMouseMove);
    document.addEventListener("mouseleave", handleMouseLeave);
    document.addEventListener("mouseenter", handleMouseEnter);

    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("mouseleave", handleMouseLeave);
      document.removeEventListener("mouseenter", handleMouseEnter);
      cancelAnimationFrame(rafRef.current);
    };
  }, [isDesktop, handleMouseMove, handleMouseLeave, handleMouseEnter]);

  return (
    <CursorContext.Provider value={{ x, y, xPercent, yPercent, variant, setVariant, isDesktop }}>
      {children}
      {isDesktop && (
        <>
          <CursorGlow x={x} y={y} visible={visible} />
          <CursorRenderer x={x} y={y} variant={variant} visible={visible} />
        </>
      )}
    </CursorContext.Provider>
  );
}

interface CursorRendererProps {
  x: number;
  y: number;
  variant: CursorVariant;
  visible: boolean;
}

function CursorRenderer({ x, y, variant, visible }: CursorRendererProps) {
  const sizes: Record<CursorVariant, number> = {
    default: 6,
    interactive: 32,
    roadmap: 24,
    code: 20,
    drag: 16,
  };

  const size = sizes[variant];

  return (
    <motion.div
      className="fixed top-0 left-0 pointer-events-none z-[9999] mix-blend-difference"
      aria-hidden="true"
      animate={{
        x: x - size / 2,
        y: y - size / 2,
        width: size,
        height: size,
      }}
      transition={{ type: "spring", stiffness: 500, damping: 28, mass: 0.5 }}
    >
      <AnimatePresence mode="wait">
        {variant === "default" && (
          <motion.div
            key="default"
            className="h-full w-full rounded-full bg-white"
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: visible ? 1 : 0 }}
            exit={{ scale: 0, opacity: 0 }}
            transition={{ duration: 0.15 }}
          />
        )}
        {variant === "interactive" && (
          <motion.div
            key="interactive"
            className="h-full w-full rounded-full border-2 border-white/80"
            initial={{ scale: 0.5, opacity: 0 }}
            animate={{ scale: 1, opacity: visible ? 1 : 0 }}
            exit={{ scale: 0.5, opacity: 0 }}
            transition={{ duration: 0.2 }}
          />
        )}
        {variant === "roadmap" && (
          <motion.div
            key="roadmap"
            className="relative h-full w-full"
            initial={{ scale: 0.5, opacity: 0 }}
            animate={{ scale: 1, opacity: visible ? 1 : 0 }}
            exit={{ scale: 0.5, opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <div className="absolute inset-0 rounded-full border border-white/60" />
            <div className="absolute inset-[30%] rounded-full bg-white/80" />
          </motion.div>
        )}
        {variant === "code" && (
          <motion.div
            key="code"
            className="flex h-full w-full items-center justify-center"
            initial={{ scale: 0.5, opacity: 0 }}
            animate={{ scale: 1, opacity: visible ? 1 : 0 }}
            exit={{ scale: 0.5, opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <span className="font-mono text-[8px] font-bold text-white">&lt;/&gt;</span>
          </motion.div>
        )}
        {variant === "drag" && (
          <motion.div
            key="drag"
            className="h-full w-full rounded-sm border-2 border-white/70 rotate-45"
            initial={{ scale: 0.5, opacity: 0 }}
            animate={{ scale: 1, opacity: visible ? 1 : 0 }}
            exit={{ scale: 0.5, opacity: 0 }}
            transition={{ duration: 0.2 }}
          />
        )}
      </AnimatePresence>
    </motion.div>
  );
}

function CursorGlow({ x, y, visible }: { x: number; y: number; visible: boolean }) {
  return (
    <motion.div
      className="fixed top-0 left-0 pointer-events-none z-[1] mix-blend-screen"
      aria-hidden="true"
      animate={{
        x: x - 300,
        y: y - 300,
        opacity: visible ? 1 : 0,
      }}
      transition={{ type: "spring", stiffness: 50, damping: 30 }}
      style={{
        width: 600,
        height: 600,
        borderRadius: "50%",
        background: "radial-gradient(circle, var(--glow-primary, oklch(0.62 0.15 195 / 0.06)) 0%, transparent 70%)",
      }}
    />
  );
}
