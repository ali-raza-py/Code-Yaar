"use client";

import { useRef } from "react";
import {
  Bold,
  Italic,
  Underline,
  List,
  ListOrdered,
  Link2,
  Braces,
} from "lucide-react";

const VARIABLE_OPTIONS = [
  { token: "{{student_name}}", label: "student_name" },
  { token: "{{student_email}}", label: "student_email" },
  { token: "{{student_id}}", label: "student_id" },
  { token: "{{current_date}}", label: "current_date" },
  { token: "{{organization_name}}", label: "organization_name" },
];

function ToolbarButton({
  onClick,
  title,
  children,
}: {
  onClick: () => void;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      title={title}
      onMouseDown={(event) => event.preventDefault()}
      onClick={onClick}
      className="rounded-md border p-1.5 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
    >
      {children}
    </button>
  );
}

/**
 * Minimal rich-text editor for admin-composed emails. The HTML produced here
 * is never trusted: the backend allowlist-sanitizes it before storage, so
 * this component only has to give administrators formatting tools — bold,
 * italic, underline, lists, links and personalization variables. Inline CTA
 * buttons are not part of the body: the branded CTA comes from the dedicated
 * button fields below the editor and is rendered by the email layout itself.
 */
export default function RichTextEditor({
  value,
  onChange,
  disabled,
}: {
  value: string;
  onChange: (html: string) => void;
  disabled?: boolean;
}) {
  const editorRef = useRef<HTMLDivElement>(null);

  function runCommand(command: string, arg?: string) {
    editorRef.current?.focus();
    document.execCommand(command, false, arg);
    if (editorRef.current) onChange(editorRef.current.innerHTML);
  }

  function insertLink() {
    const url = window.prompt("Link address (https://… or mailto:…):", "https://");
    if (url) runCommand("createLink", url);
  }

  function insertVariable(token: string) {
    // insertText keeps the caret after the token and marks the edit cleanly.
    runCommand("insertText", token);
  }

  return (
    <div className={`rounded-lg border ${disabled ? "opacity-60" : ""}`}>
      <div className="flex flex-wrap items-center gap-1.5 border-b bg-muted/40 px-2 py-1.5">
        <ToolbarButton title="Bold" onClick={() => runCommand("bold")}>
          <Bold className="h-4 w-4" />
        </ToolbarButton>
        <ToolbarButton title="Italic" onClick={() => runCommand("italic")}>
          <Italic className="h-4 w-4" />
        </ToolbarButton>
        <ToolbarButton title="Underline" onClick={() => runCommand("underline")}>
          <Underline className="h-4 w-4" />
        </ToolbarButton>
        <span className="mx-1 h-5 w-px bg-border" />
        <ToolbarButton title="Bulleted list" onClick={() => runCommand("insertUnorderedList")}>
          <List className="h-4 w-4" />
        </ToolbarButton>
        <ToolbarButton title="Numbered list" onClick={() => runCommand("insertOrderedList")}>
          <ListOrdered className="h-4 w-4" />
        </ToolbarButton>
        <ToolbarButton title="Insert link" onClick={insertLink}>
          <Link2 className="h-4 w-4" />
        </ToolbarButton>
        <span className="mx-1 h-5 w-px bg-border" />
        <label className="flex items-center gap-1 text-xs text-muted-foreground">
          <Braces className="h-4 w-4" />
          <select
            defaultValue=""
            disabled={disabled}
            onChange={(event) => {
              const option = VARIABLE_OPTIONS.find((v) => v.token === event.target.value);
              if (option) insertVariable(option.token);
              event.target.value = "";
            }}
            className="rounded-md border bg-background px-1.5 py-0.5 text-xs"
          >
            <option value="">Insert variable…</option>
            {VARIABLE_OPTIONS.map((option) => (
              <option key={option.token} value={option.token}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
      </div>
      <div
        ref={editorRef}
        contentEditable={!disabled}
        suppressContentEditableWarning
        role="textbox"
        aria-multiline="true"
        aria-label="Email body"
        onInput={() => editorRef.current && onChange(editorRef.current.innerHTML)}
        onBlur={() => editorRef.current && onChange(editorRef.current.innerHTML)}
        // dangerouslySetInnerHTML seeds the editable region once per mount;
        // the stored value is already sanitized server-side, and everything
        // typed afterwards is read back with innerHTML on input/blur.
        dangerouslySetInnerHTML={{ __html: value }}
        className="min-h-[220px] px-4 py-3 text-sm leading-relaxed focus:outline-none [&_a]:text-primary [&_ol]:list-decimal [&_ol]:pl-6 [&_ul]:list-disc [&_ul]:pl-6"
      />
    </div>
  );
}
