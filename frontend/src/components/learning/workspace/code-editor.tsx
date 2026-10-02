'use client';

import { useCallback, useRef, useEffect, useState } from 'react';

interface CodeEditorProps {
  code: string;
  onChange: (code: string) => void;
  language: string;
  fileName: string;
}

/**
 * Code editor component with line numbers and syntax highlighting.
 * Uses a textarea overlay approach for reliable editing.
 * In production, integrate Monaco Editor or CodeMirror.
 */
export default function CodeEditor({ code, onChange, language, fileName }: CodeEditorProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const lineNumbersRef = useRef<HTMLDivElement>(null);
  const [lineCount, setLineCount] = useState(1);

  useEffect(() => {
    const lines = code.split('\n').length;
    setLineCount(Math.max(lines, 1));
  }, [code]);

  const handleScroll = useCallback(() => {
    if (textareaRef.current && lineNumbersRef.current) {
      lineNumbersRef.current.scrollTop = textareaRef.current.scrollTop;
    }
  }, []);

  const handleKeyDown = useCallback((e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Tab handling
    if (e.key === 'Tab') {
      e.preventDefault();
      const textarea = textareaRef.current;
      if (!textarea) return;

      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      const newCode = code.substring(0, start) + '    ' + code.substring(end);
      onChange(newCode);

      // Restore cursor position
      requestAnimationFrame(() => {
        textarea.selectionStart = textarea.selectionEnd = start + 4;
      });
    }
  }, [code, onChange]);

  return (
    <div className="flex h-full flex-col bg-[#1e1e2e]">
      {/* File Tab */}
      <div className="flex items-center gap-2 border-b border-gray-700 bg-[#181825] px-3 py-1.5">
        <svg className="h-3.5 w-3.5 text-yellow-400" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
        </svg>
        <span className="text-xs text-gray-400">{fileName}</span>
        <span className="ml-auto text-[10px] text-gray-500 uppercase">{language}</span>
      </div>

      {/* Editor Area */}
      <div className="flex flex-1 overflow-hidden">
        {/* Line Numbers */}
        <div
          ref={lineNumbersRef}
          className="w-10 shrink-0 overflow-hidden bg-[#181825] pt-3 text-right pr-2 select-none"
        >
          {Array.from({ length: lineCount }, (_, i) => (
            <div key={i} className="text-xs leading-[1.5rem] text-gray-600 font-mono">
              {i + 1}
            </div>
          ))}
        </div>

        {/* Textarea */}
        <textarea
          ref={textareaRef}
          value={code}
          onChange={(e) => onChange(e.target.value)}
          onScroll={handleScroll}
          onKeyDown={handleKeyDown}
          spellCheck={false}
          className="flex-1 resize-none bg-[#1e1e2e] p-3 text-sm leading-[1.5rem] text-gray-200 font-mono outline-none placeholder:text-gray-600 overflow-auto"
          placeholder="Write your code here..."
        />
      </div>
    </div>
  );
}
