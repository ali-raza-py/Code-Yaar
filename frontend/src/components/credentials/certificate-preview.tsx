'use client';

import { useCallback, useEffect, useLayoutEffect, useRef, useState } from 'react';
import { Maximize2, Minus, Plus } from 'lucide-react';
import { CERT_HEIGHT, CERT_WIDTH } from './certificate-artwork';

/**
 * Fit-to-screen / zoom wrapper for the fixed-size certificate canvas.
 * Prevents horizontal overflow of the page: at "fit" the sheet always
 * matches the available width, and zooming scrolls inside the frame only.
 */
export default function CertificatePreview({
  children,
  zoom,
  onZoomChange,
}: {
  children: React.ReactNode;
  zoom: number; // 0 = fit
  onZoomChange: (z: number) => void;
}) {
  const viewportRef = useRef<HTMLDivElement>(null);
  const [fitScale, setFitScale] = useState(1);

  const measure = useCallback(() => {
    const el = viewportRef.current;
    if (!el) return;
    // clientWidth includes the frame padding — subtract it so "fit" never
    // produces a horizontal scrollbar at 100%-fit.
    const style = window.getComputedStyle(el);
    const padX =
      (parseFloat(style.paddingLeft) || 0) + (parseFloat(style.paddingRight) || 0);
    const available = el.clientWidth - padX;
    if (available > 0) setFitScale(Math.min(1, available / CERT_WIDTH));
  }, []);

  useLayoutEffect(() => {
    measure();
    const el = viewportRef.current;
    if (!el || typeof ResizeObserver === 'undefined') return;
    const ro = new ResizeObserver(measure);
    ro.observe(el);
    return () => ro.disconnect();
  }, [measure]);

  // Re-measure when the browser font metrics settle (print/export fonts).
  useEffect(() => {
    window.addEventListener('resize', measure);
    return () => window.removeEventListener('resize', measure);
  }, [measure]);

  const scale = zoom === 0 ? fitScale : zoom;
  const step = 0.15;
  const min = Math.min(0.3, fitScale);
  const max = 2;

  return (
    <div className="w-full">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2 cy-no-print">
        <p className="text-xs text-muted-foreground">
          {zoom === 0 ? 'Fit to screen' : `${Math.round(scale * 100)}%`}
          <span className="ml-2 hidden sm:inline">
            · A4 landscape · {CERT_WIDTH} × {CERT_HEIGHT}px
          </span>
        </p>
        <div className="flex items-center gap-1 rounded-pill border border-border bg-card px-1 py-1">
          <button
            type="button"
            aria-label="Zoom out"
            onClick={() => onZoomChange(Math.max(min, Number((scale - step).toFixed(2))))}
            className="focus-ring flex h-8 w-8 items-center justify-center rounded-full text-foreground hover:bg-muted"
          >
            <Minus className="h-4 w-4" />
          </button>
          <button
            type="button"
            aria-label="Fit to screen"
            onClick={() => onZoomChange(0)}
            className={`focus-ring flex h-8 items-center gap-1.5 rounded-full px-3 text-xs font-medium ${
              zoom === 0 ? 'bg-primary text-primary-foreground' : 'text-foreground hover:bg-muted'
            }`}
          >
            <Maximize2 className="h-3.5 w-3.5" />
            Fit
          </button>
          <button
            type="button"
            aria-label="Zoom in"
            onClick={() => onZoomChange(Math.min(max, Number((scale + step).toFixed(2))))}
            className="focus-ring flex h-8 w-8 items-center justify-center rounded-full text-foreground hover:bg-muted"
          >
            <Plus className="h-4 w-4" />
          </button>
        </div>
      </div>

      <div
        ref={viewportRef}
        className="cy-cert-viewport w-full overflow-x-auto overflow-y-hidden rounded-card border border-border bg-[#eceff4] p-3 sm:p-5"
      >
        {/* Sized box keeps the layout height correct even though the sheet is transformed. */}
        <div
          className="cy-cert-box"
          style={{
            width: Math.ceil(CERT_WIDTH * scale),
            height: Math.ceil(CERT_HEIGHT * scale),
          }}
        >
          <div
            className="cy-cert-scale origin-top-left"
            style={{
              transform: `scale(${scale})`,
              width: CERT_WIDTH,
              height: CERT_HEIGHT,
            }}
          >
            {children}
          </div>
        </div>
      </div>
    </div>
  );
}
