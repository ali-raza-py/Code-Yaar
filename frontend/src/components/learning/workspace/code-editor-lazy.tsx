'use client';

import dynamic from 'next/dynamic';

/**
 * CodeMirror is ~203 KB gzip - by far the largest script on the learner
 * routes. Importing it eagerly made every lesson and challenge page download
 * and parse the editor before it was ever shown. This wrapper loads it
 * client-side only, so it drops out of each route's initial JS graph and is
 * fetched just before an editor mounts. The placeholder keeps the editor
 * surface's footprint so swapping in the real editor does not shift layout.
 */
const CodeEditorLazy = dynamic(() => import('./code-editor'), {
  ssr: false,
  loading: () => (
    <div
      className="editor-surface flex min-h-[200px] w-full items-center justify-center text-xs text-white/40"
      role="status"
      aria-live="polite"
    >
      Loading editor...
    </div>
  ),
});

export default CodeEditorLazy;
