'use client';

import { useEffect, useRef } from 'react';
import { EditorState, Compartment, type Extension } from '@codemirror/state';
import {
  EditorView,
  keymap,
  lineNumbers,
  highlightActiveLine,
  highlightActiveLineGutter,
  drawSelection,
  rectangularSelection,
} from '@codemirror/view';
import {
  history,
  defaultKeymap,
  historyKeymap,
  indentWithTab,
} from '@codemirror/commands';
import {
  syntaxHighlighting,
  defaultHighlightStyle,
  bracketMatching,
  indentOnInput,
  HighlightStyle,
} from '@codemirror/language';
import { python } from '@codemirror/lang-python';
import { javascript } from '@codemirror/lang-javascript';
import { sql } from '@codemirror/lang-sql';
import { tags as t } from '@lezer/highlight';

interface CursorPosition {
  line: number;
  col: number;
}

interface CodeEditorProps {
  code: string;
  onChange: (code: string) => void;
  language: string;
  fileName?: string;
  readOnly?: boolean;
  onRun?: () => void;
  onSubmit?: () => void;
  onCursor?: (pos: CursorPosition) => void;
  /** Configurable keymap strings (CodeMirror key syntax). */
  runKey?: string;
  submitKey?: string;
  /** Hide the file-tab chrome (used by static in-lesson read-only fences). */
  showChrome?: boolean;
  /** Hide the line-number gutter (compact / static variant). */
  showGutter?: boolean;
}

function languageExtension(lang: string): Extension {
  switch (lang.toLowerCase()) {
    case 'python':
    case 'py':
      return python();
    case 'javascript':
    case 'js':
    case 'typescript':
    case 'ts':
    case 'jsx':
    case 'tsx':
      return javascript({ typescript: lang.toLowerCase().startsWith('ts'), jsx: true });
    case 'sql':
      return sql();
    default:
      return [];
  }
}

// Theme reads the governed editor tokens from globals.css.
const editorTheme = EditorView.theme({
  '&': {
    height: '100%',
    backgroundColor: 'var(--editor-bg)',
    fontSize: 'var(--editor-font-size)',
    color: 'var(--editor-text)',
  },
  '&.cm-focused': { outline: 'none' },
  '.cm-scroller': {
    fontFamily: 'var(--font-mono)',
    lineHeight: 'var(--editor-line-height)',
  },
  '.cm-gutters': {
    backgroundColor: 'var(--editor-gutter)',
    color: 'var(--editor-gutter-fg)',
    border: 'none',
    minWidth: 'var(--editor-gutter-width)',
  },
  '.cm-lineNumbers .cm-gutterElement': { padding: '0 10px 0 12px' },
  '.cm-activeLineGutter': { backgroundColor: 'transparent', color: 'var(--editor-text)' },
  '.cm-activeLine': { backgroundColor: 'var(--editor-active-line)' },
  '.cm-cursor': { borderLeftColor: 'var(--color-cta-green)' },
  '.cm-selectionBackground, ::selection': {
    backgroundColor: 'var(--editor-selection)',
  },
});

/** Auto-height variant for static in-lesson fences (no fixed editor viewport). */
const autoHeightTheme = EditorView.theme({
  '&': { height: 'auto' },
  '.cm-scroller': { overflow: 'visible' },
});

const codeHighlight = HighlightStyle.define([
  { tag: t.keyword, color: 'var(--syn-keyword)' },
  { tag: t.operator, color: 'var(--syn-operator)' },
  { tag: t.string, color: 'var(--syn-string)' },
  { tag: t.special(t.string), color: 'var(--syn-string-special)' },
  { tag: t.number, color: 'var(--syn-number)' },
  { tag: t.comment, color: 'var(--syn-comment)', fontStyle: 'italic' },
  { tag: t.variableName, color: 'var(--syn-variable)' },
  { tag: t.definition(t.variableName), color: 'var(--syn-definition)' },
  { tag: t.function(t.variableName), color: 'var(--syn-definition)' },
  { tag: t.propertyName, color: 'var(--syn-property)' },
  { tag: t.bool, color: 'var(--syn-bool)' },
  { tag: t.className, color: 'var(--syn-class)' },
  { tag: t.invalid, color: 'var(--syn-invalid)' },
]);

/** Render a CodeMirror key string (e.g. "Shift-Mod-Enter") as a compact kbd label. */
function keyLabel(key: string): string {
  const parts = key.split('-');
  const out: string[] = [];
  for (const p of parts) {
    if (p === 'Mod') out.push('⌘/Ctrl');
    else if (p === 'Shift') out.push('⇧');
    else if (p === 'Alt') out.push('⌥');
    else if (p === 'Enter') out.push('↵');
    else out.push(p);
  }
  return out.join(' ');
}

/**
 * CodeMirror 6 editor with real syntax highlighting, a quiet gutter,
 * and Run/Submit keyboard shortcuts surfaced in the chrome.
 */
export default function CodeEditor({
  code,
  onChange,
  language: lang,
  fileName,
  readOnly = false,
  onRun,
  onSubmit,
  onCursor,
  runKey = 'Mod-Enter',
  submitKey = 'Shift-Mod-Enter',
  showChrome = true,
  showGutter = true,
}: CodeEditorProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const viewRef = useRef<EditorView | null>(null);
  const langConfRef = useRef(new Compartment());
  const editConfRef = useRef(new Compartment());

  // Keep latest callbacks/props in refs so the effect's extensions stay stable.
  const cbRef = useRef({ onChange, onRun, onSubmit, onCursor });
  useEffect(() => {
    cbRef.current = { onChange, onRun, onSubmit, onCursor };
  }, [onChange, onRun, onSubmit, onCursor]);

  const reportCursor = (state: EditorState) => {
    const head = state.selection.main.head;
    const line = state.doc.lineAt(head);
    cbRef.current.onCursor?.({ line: line.number, col: head - line.from + 1 });
  };

  // Build the editor once.
  useEffect(() => {
    if (!containerRef.current) return;

    const startState = EditorState.create({
      doc: code,
      extensions: [
        ...(showGutter ? [lineNumbers(), highlightActiveLineGutter()] : []),
        highlightActiveLine(),
        history(),
        drawSelection(),
        rectangularSelection(),
        indentOnInput(),
        bracketMatching(),
        EditorView.lineWrapping,
        langConfRef.current.of(languageExtension(lang)),
        editConfRef.current.of([
          EditorState.readOnly.of(readOnly),
          EditorView.editable.of(!readOnly),
        ]),
        syntaxHighlighting(codeHighlight),
        syntaxHighlighting(defaultHighlightStyle, { fallback: true }),
        editorTheme,
        ...(showChrome ? [] : [autoHeightTheme]),
        keymap.of([
          { key: submitKey, preventDefault: true, run: () => { cbRef.current.onSubmit?.(); return true; } },
          { key: runKey, preventDefault: true, run: () => { cbRef.current.onRun?.(); return true; } },
          indentWithTab,
          ...defaultKeymap,
          ...historyKeymap,
        ]),
        EditorView.updateListener.of((update) => {
          if (update.docChanged) {
            cbRef.current.onChange(update.state.doc.toString());
          }
          if (update.selectionSet || update.docChanged) {
            reportCursor(update.state);
          }
        }),
      ],
    });

    const view = new EditorView({ state: startState, parent: containerRef.current });
    viewRef.current = view;
    reportCursor(view.state);

    return () => {
      view.destroy();
      viewRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Sync language when it changes.
  useEffect(() => {
    const view = viewRef.current;
    if (!view) return;
    view.dispatch({
      effects: [
        langConfRef.current.reconfigure(languageExtension(lang)),
        editConfRef.current.reconfigure([
          EditorState.readOnly.of(readOnly),
          EditorView.editable.of(!readOnly),
        ]),
      ],
    });
  }, [lang, readOnly]);

  // Sync external doc changes (e.g. Reset button).
  useEffect(() => {
    const view = viewRef.current;
    if (!view) return;
    const current = view.state.doc.toString();
    if (current !== code) {
      view.dispatch({ changes: { from: 0, to: current.length, insert: code } });
    }
  }, [code]);

  return (
    <div className={showChrome ? 'flex h-full flex-col editor-surface' : 'editor-surface'}>
      {/* File tab — active tab is the only filled element in the chrome */}
      {showChrome && (
        <div className="flex items-center gap-2 border-b editor-chrome px-3 py-1.5">
          <span className="seg-tab seg-tab-active">{fileName}</span>
          {!readOnly && (
            <span className="hidden items-center gap-2 text-[10px] text-white/40 md:flex">
              <kbd className="font-mono" aria-keyshortcuts={runKey}>{keyLabel(runKey)}</kbd>
              <span>Run</span>
              <kbd className="font-mono" aria-keyshortcuts={submitKey}>{keyLabel(submitKey)}</kbd>
              <span>Submit</span>
            </span>
          )}
          <span className="ml-auto text-[10px] uppercase tracking-wider text-white/50">{lang}</span>
        </div>
      )}

      {/* Editor mount */}
      <div ref={containerRef} className={showChrome ? 'min-h-0 flex-1 overflow-hidden' : 'overflow-hidden'} />
    </div>
  );
}
