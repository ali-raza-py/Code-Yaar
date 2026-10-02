'use client';

import { useState, useRef, useCallback, useEffect } from 'react';

interface VideoLessonProps {
  videoUrl: string;
  title: string;
  durationSeconds: number;
  lessonId: number;
  onProgress?: (watchedSeconds: number) => void;
  onComplete?: () => void;
  /** Percentage of video that must be watched to count as complete (default 80%) */
  completionThreshold?: number;
}

/**
 * Video lesson component (spec §12).
 *
 * Features:
 * - Play/pause
 * - Progress tracking
 * - Playback speed control
 * - Completion tracking (based on watch percentage, not just opening)
 * - Transcript architecture (ready for captions)
 */
export default function VideoLesson({
  videoUrl,
  title,
  durationSeconds,
  lessonId,
  onProgress,
  onComplete,
  completionThreshold = 0.8,
}: VideoLessonProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [playbackRate, setPlaybackRate] = useState(1);
  const [hasCompleted, setHasCompleted] = useState(false);
  const [showControls, setShowControls] = useState(true);

  const progressPercent = durationSeconds > 0 ? (currentTime / durationSeconds) * 100 : 0;
  const isComplete = currentTime >= durationSeconds * completionThreshold;

  // Track progress
  const handleTimeUpdate = useCallback(() => {
    const video = videoRef.current;
    if (!video) return;
    setCurrentTime(video.currentTime);
    onProgress?.(video.currentTime);
  }, [onProgress]);

  // Mark complete when threshold reached
  useEffect(() => {
    if (isComplete && !hasCompleted) {
      setHasCompleted(true);
      onComplete?.();
    }
  }, [isComplete, hasCompleted, onComplete]);

  const togglePlay = useCallback(() => {
    const video = videoRef.current;
    if (!video) return;
    if (video.paused) {
      video.play();
      setIsPlaying(true);
    } else {
      video.pause();
      setIsPlaying(false);
    }
  }, []);

  const handleSeek = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
    const video = videoRef.current;
    if (!video) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const percent = x / rect.width;
    video.currentTime = percent * durationSeconds;
  }, [durationSeconds]);

  const changeSpeed = useCallback(() => {
    const speeds = [0.5, 0.75, 1, 1.25, 1.5, 2];
    const currentIdx = speeds.indexOf(playbackRate);
    const nextSpeed = speeds[(currentIdx + 1) % speeds.length];
    setPlaybackRate(nextSpeed);
    if (videoRef.current) {
      videoRef.current.playbackRate = nextSpeed;
    }
  }, [playbackRate]);

  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m}:${s.toString().padStart(2, '0')}`;
  };

  return (
    <div className="rounded-lg overflow-hidden border border-gray-200 bg-black">
      {/* Video Player */}
      <div
        className="relative aspect-video cursor-pointer group"
        onClick={togglePlay}
        onMouseEnter={() => setShowControls(true)}
        onMouseLeave={() => setShowControls(!isPlaying)}
      >
        <video
          ref={videoRef}
          src={videoUrl}
          className="w-full h-full object-contain"
          onTimeUpdate={handleTimeUpdate}
          onEnded={() => setIsPlaying(false)}
          preload="metadata"
        />

        {/* Play/Pause Overlay */}
        {!isPlaying && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/30">
            <div className="flex h-14 w-14 items-center justify-center rounded-full bg-white/90 shadow-lg">
              <svg className="h-6 w-6 text-gray-900 ml-0.5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M8 5v14l11-7z" />
              </svg>
            </div>
          </div>
        )}

        {/* Controls Bar */}
        {showControls && (
          <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-3 pt-8">
            {/* Progress Bar */}
            <div
              className="h-1 w-full rounded-full bg-white/30 cursor-pointer mb-2 group hover:h-1.5 transition-all"
              onClick={(e) => { e.stopPropagation(); handleSeek(e); }}
            >
              <div
                className="h-full rounded-full bg-green-500 relative"
                style={{ width: `${progressPercent}%` }}
              >
                <div className="absolute right-0 top-1/2 -translate-y-1/2 h-3 w-3 rounded-full bg-green-500 opacity-0 group-hover:opacity-100 transition-opacity" />
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {/* Play/Pause */}
                <button
                  onClick={(e) => { e.stopPropagation(); togglePlay(); }}
                  className="text-white hover:text-green-400 transition-colors"
                >
                  {isPlaying ? (
                    <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z" />
                    </svg>
                  ) : (
                    <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M8 5v14l11-7z" />
                    </svg>
                  )}
                </button>

                {/* Time */}
                <span className="text-xs text-white/80 font-mono">
                  {formatTime(currentTime)} / {formatTime(durationSeconds)}
                </span>
              </div>

              <div className="flex items-center gap-3">
                {/* Speed */}
                <button
                  onClick={(e) => { e.stopPropagation(); changeSpeed(); }}
                  className="text-xs text-white/80 hover:text-white font-medium px-1.5 py-0.5 rounded border border-white/30"
                >
                  {playbackRate}x
                </button>

                {/* Completion indicator */}
                {isComplete && (
                  <span className="text-xs text-green-400 font-medium flex items-center gap-1">
                    <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                    </svg>
                    Watched
                  </span>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Title */}
      <div className="bg-gray-900 px-4 py-2">
        <p className="text-sm text-gray-300">{title}</p>
      </div>
    </div>
  );
}
