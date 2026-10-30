'use client';

import { MotionConfig } from 'framer-motion';
import * as React from 'react';

/**
 * Honors the user's OS-level "reduce motion" preference for all
 * framer-motion JS-driven animations (transform/layout animations are
 * driven off the main thread and bypass CSS `prefers-reduced-motion`
 * guards). Value/opacity animations still run; transforms are skipped.
 */
export function MotionProvider({ children }: { children: React.ReactNode }) {
  return <MotionConfig reducedMotion="user">{children}</MotionConfig>;
}
