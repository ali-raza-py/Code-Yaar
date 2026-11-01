"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { AlertCircle, CheckCircle2, ImageUp, Loader2, Trash2 } from "lucide-react";
import { ApiError, avatar as avatarApi } from "@/lib/api";
import { Avatar } from "@/components/ui/avatar";

/**
 * Profile-picture uploader. Pick a JPEG/PNG/WebP (≤5 MB), then crop it to a
 * circle with drag-to-pan and a zoom slider — all rendered on a plain canvas,
 * no image-editing dependency. On save the square crop is re-encoded to a JPEG
 * and posted as multipart; the server re-encodes and centre-crops again as a
 * safety net. Also offers Replace and Remove.
 */

const MAX_BYTES = 5 * 1024 * 1024;
const ACCEPTED = ["image/jpeg", "image/png", "image/webp"];
const PREVIEW_SIZE = 240; // on-screen canvas edge, CSS pixels
const OUTPUT_SIZE = 512; // uploaded edge in pixels (matches the server cap)

type Status = { type: "success" | "error"; text: string } | null;

interface AvatarUploaderProps {
  currentUrl: string;
  username: string;
  displayName: string;
  /** Re-read `/auth/me/` after a successful upload/removal. */
  onChanged: () => void;
}

export function AvatarUploader({
  currentUrl,
  username,
  displayName,
  onChanged,
}: AvatarUploaderProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const imgRef = useRef<HTMLImageElement | null>(null);
  const fileRef = useRef<HTMLInputElement | null>(null);
  const dragRef = useRef<{ x: number; y: number } | null>(null);

  const [zoom, setZoom] = useState(1);
  const [offset, setOffset] = useState({ x: 0, y: 0 });
  const [editing, setEditing] = useState(false);
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState<Status>(null);

  const clampOffset = useCallback(
    (next: { x: number; y: number }, img: HTMLImageElement, zoomValue: number) => {
      const cover = Math.max(PREVIEW_SIZE / img.naturalWidth, PREVIEW_SIZE / img.naturalHeight);
      const drawW = img.naturalWidth * cover * zoomValue;
      const drawH = img.naturalHeight * cover * zoomValue;
      const maxX = Math.max(0, (drawW - PREVIEW_SIZE) / 2);
      const maxY = Math.max(0, (drawH - PREVIEW_SIZE) / 2);
      return {
        x: Math.min(maxX, Math.max(-maxX, next.x)),
        y: Math.min(maxY, Math.max(-maxY, next.y)),
      };
    },
    []
  );

  // Draw the current image with the zoom/pan transform into the preview canvas.
  const renderCanvas = useCallback(() => {
    const canvas = canvasRef.current;
    const img = imgRef.current;
    if (!canvas || !img) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    const dpr = window.devicePixelRatio || 1;
    canvas.width = PREVIEW_SIZE * dpr;
    canvas.height = PREVIEW_SIZE * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, PREVIEW_SIZE, PREVIEW_SIZE);
    const cover = Math.max(PREVIEW_SIZE / img.naturalWidth, PREVIEW_SIZE / img.naturalHeight);
    const scale = cover * zoom;
    const drawW = img.naturalWidth * scale;
    const drawH = img.naturalHeight * scale;
    const dx = (PREVIEW_SIZE - drawW) / 2 + offset.x;
    const dy = (PREVIEW_SIZE - drawH) / 2 + offset.y;
    ctx.drawImage(img, dx, dy, drawW, drawH);
    // Circular crop guide.
    ctx.save();
    ctx.beginPath();
    ctx.arc(PREVIEW_SIZE / 2, PREVIEW_SIZE / 2, PREVIEW_SIZE / 2 - 1, 0, Math.PI * 2);
    ctx.strokeStyle = "rgba(255,255,255,0.85)";
    ctx.lineWidth = 2;
    ctx.stroke();
    ctx.restore();
  }, [offset, zoom]);

  useEffect(() => {
    if (editing) renderCanvas();
  }, [editing, renderCanvas]);

  const handleFile = useCallback(
    (file: File | null | undefined) => {
      setStatus(null);
      if (!file) return;
      if (!ACCEPTED.includes(file.type)) {
        setStatus({ type: "error", text: "Choose a JPEG, PNG or WebP image." });
        return;
      }
      if (file.size > MAX_BYTES) {
        setStatus({ type: "error", text: "That image is larger than 5 MB. Pick a smaller one." });
        return;
      }
      const reader = new FileReader();
      reader.onload = () => {
        const img = new Image();
        img.onload = () => {
          imgRef.current = img;
          setZoom(1);
          setOffset({ x: 0, y: 0 });
          setEditing(true);
        };
        img.onerror = () => setStatus({ type: "error", text: "That file couldn't be read as an image." });
        img.src = String(reader.result);
      };
      reader.onerror = () => setStatus({ type: "error", text: "Couldn't read that file." });
      reader.readAsDataURL(file);
    },
    []
  );

  const onPointerDown = (e: React.PointerEvent<HTMLCanvasElement>) => {
    if (!imgRef.current) return;
    dragRef.current = { x: e.clientX, y: e.clientY };
    e.currentTarget.setPointerCapture(e.pointerId);
  };

  const onPointerMove = (e: React.PointerEvent<HTMLCanvasElement>) => {
    const img = imgRef.current;
    const start = dragRef.current;
    if (!img || !start) return;
    const dx = e.clientX - start.x;
    const dy = e.clientY - start.y;
    dragRef.current = { x: e.clientX, y: e.clientY };
    setOffset((prev) => clampOffset({ x: prev.x + dx, y: prev.y + dy }, img, zoom));
  };

  const onPointerUp = (e: React.PointerEvent<HTMLCanvasElement>) => {
    dragRef.current = null;
    if (e.currentTarget.hasPointerCapture(e.pointerId)) {
      e.currentTarget.releasePointerCapture(e.pointerId);
    }
  };

  // Render the 512² crop to an offscreen canvas and hand back a JPEG blob.
  const buildBlob = (): Promise<Blob | null> => {
    const img = imgRef.current;
    if (!img) return Promise.resolve(null);
    const ratio = OUTPUT_SIZE / PREVIEW_SIZE;
    const out = document.createElement("canvas");
    out.width = OUTPUT_SIZE;
    out.height = OUTPUT_SIZE;
    const ctx = out.getContext("2d");
    if (!ctx) return Promise.resolve(null);
    const cover = Math.max(PREVIEW_SIZE / img.naturalWidth, PREVIEW_SIZE / img.naturalHeight);
    const scale = cover * zoom * ratio;
    const drawW = img.naturalWidth * scale;
    const drawH = img.naturalHeight * scale;
    const dx = (OUTPUT_SIZE - drawW) / 2 + offset.x * ratio;
    const dy = (OUTPUT_SIZE - drawH) / 2 + offset.y * ratio;
    ctx.drawImage(img, dx, dy, drawW, drawH);
    return new Promise((resolve) => out.toBlob((b) => resolve(b), "image/jpeg", 0.9));
  };

  const handleSave = useCallback(async () => {
    setBusy(true);
    setStatus(null);
    try {
      const blob = await buildBlob();
      if (!blob) throw new ApiError(500, "Couldn't prepare the image. Try another file.");
      await avatarApi.upload(blob);
      setEditing(false);
      imgRef.current = null;
      setStatus({ type: "success", text: "Profile picture updated." });
      onChanged();
    } catch (caught) {
      setStatus({
        type: "error",
        text: caught instanceof ApiError ? caught.message : "Upload failed. Please try again.",
      });
    } finally {
      setBusy(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [onChanged]);

  const handleRemove = useCallback(async () => {
    setBusy(true);
    setStatus(null);
    try {
      await avatarApi.remove();
      setEditing(false);
      imgRef.current = null;
      setStatus({ type: "success", text: "Removed — showing your initials instead." });
      onChanged();
    } catch (caught) {
      setStatus({
        type: "error",
        text: caught instanceof ApiError ? caught.message : "Couldn't remove the picture.",
      });
    } finally {
      setBusy(false);
    }
  }, [onChanged]);

  const cancel = () => {
    setEditing(false);
    imgRef.current = null;
    setZoom(1);
    setOffset({ x: 0, y: 0 });
    setStatus(null);
  };

  return (
    <div>
      <input
        ref={fileRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        className="hidden"
        onChange={(e) => handleFile(e.target.files?.[0])}
      />

      {!editing ? (
        <div className="flex flex-wrap items-center gap-4">
          <Avatar src={currentUrl} name={displayName} username={username} size={72} />
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => fileRef.current?.click()}
              disabled={busy}
              className="inline-flex items-center gap-2 rounded-lg border border-border bg-card px-3 py-2 text-sm font-semibold text-foreground transition-colors hover:bg-muted/60 disabled:opacity-50"
            >
              <ImageUp className="h-4 w-4" aria-hidden="true" />
              {currentUrl ? "Replace" : "Upload"} picture
            </button>
            {currentUrl && (
              <button
                type="button"
                onClick={handleRemove}
                disabled={busy}
                className="inline-flex items-center gap-2 rounded-lg border border-destructive/40 px-3 py-2 text-sm font-semibold text-destructive transition-colors hover:bg-destructive/10 disabled:opacity-50"
              >
                {busy ? (
                  <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
                ) : (
                  <Trash2 className="h-4 w-4" aria-hidden="true" />
                )}
                Remove
              </button>
            )}
          </div>
        </div>
      ) : (
        <div className="space-y-3">
          <canvas
            ref={canvasRef}
            onPointerDown={onPointerDown}
            onPointerMove={onPointerMove}
            onPointerUp={onPointerUp}
            onPointerLeave={onPointerUp}
            style={{ width: PREVIEW_SIZE, height: PREVIEW_SIZE, touchAction: "none" }}
            className="cursor-grab rounded-full bg-muted active:cursor-grabbing"
          />
          <div className="flex items-center gap-3" style={{ maxWidth: PREVIEW_SIZE }}>
            <label className="text-xs font-medium text-muted-foreground">Zoom</label>
            <input
              type="range"
              min={1}
              max={3}
              step={0.01}
              value={zoom}
              onChange={(e) => {
                const next = Number(e.target.value);
                const img = imgRef.current;
                setZoom(next);
                if (img) setOffset((prev) => clampOffset(prev, img, next));
              }}
              className="flex-1 accent-[var(--primary)]"
            />
          </div>
          <p className="text-xs text-muted-foreground">Drag the image to reposition it.</p>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={handleSave}
              disabled={busy}
              className="inline-flex items-center gap-2 rounded-lg bg-primary px-3 py-2 text-sm font-semibold text-primary-foreground transition-colors hover:bg-primary/90 disabled:opacity-50"
            >
              {busy ? (
                <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
              ) : (
                <CheckCircle2 className="h-4 w-4" aria-hidden="true" />
              )}
              Save
            </button>
            <button
              type="button"
              onClick={() => fileRef.current?.click()}
              disabled={busy}
              className="rounded-lg border border-border px-3 py-2 text-sm font-medium text-foreground hover:bg-muted/60 disabled:opacity-50"
            >
              Choose another
            </button>
            <button
              type="button"
              onClick={cancel}
              disabled={busy}
              className="rounded-lg border border-border px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-muted/60 disabled:opacity-50"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {status && (
        <p
          role={status.type === "success" ? "status" : "alert"}
          className={`mt-3 flex items-start gap-1.5 text-sm ${
            status.type === "success" ? "text-primary" : "text-destructive"
          }`}
        >
          {status.type === "success" ? (
            <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
          ) : (
            <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
          )}
          <span>{status.text}</span>
        </p>
      )}
    </div>
  );
}
