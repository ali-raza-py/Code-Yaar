/**
 * Block model for the lesson editor, and the round-trip to the markdown subset that
 * `components/learning/workspace/lesson-content.tsx` renders.
 *
 * The platform stores lesson bodies as markdown in `Lesson.content_body` and 800+
 * seeded lessons already live in that column. A block editor that wrote HTML, or a new
 * `content_blocks` column, would mean migrating every lesson and keeping two sources of
 * truth in step forever. So the editor is a *view* over the same markdown: parse on
 * load, serialize on save. Anything the parser does not recognise survives as a
 * paragraph, and anything hand-written in the markdown field still renders.
 */

export type LessonBlock =
  | { kind: 'heading'; level: 1 | 2 | 3 | 4; text: string }
  | { kind: 'paragraph'; text: string }
  | { kind: 'list'; ordered: boolean; items: string[] }
  | { kind: 'code'; language: string; code: string }
  | { kind: 'quote'; text: string }
  | { kind: 'table'; header: string[]; rows: string[][] }
  | { kind: 'rule' };

export const BLOCK_LANGUAGE_OPTIONS = [
  '', 'python', 'cpp', 'javascript', 'sql', 'bash', 'json', 'html', 'output',
];

export const NEW_BLOCK_DEFAULTS: Record<LessonBlock['kind'], () => LessonBlock> = {
  heading: () => ({ kind: 'heading', level: 2, text: '' }),
  paragraph: () => ({ kind: 'paragraph', text: '' }),
  list: () => ({ kind: 'list', ordered: false, items: [''] }),
  code: () => ({ kind: 'code', language: 'python', code: '' }),
  quote: () => ({ kind: 'quote', text: '' }),
  table: () => ({ kind: 'table', header: ['Column', 'Value'], rows: [['', '']] }),
  rule: () => ({ kind: 'rule' }),
};

function isTableLine(line: string): boolean {
  return line.trim().startsWith('|') && line.trim().endsWith('|') && line.includes('|');
}

function splitRow(line: string): string[] {
  return line.trim().replace(/^\|/, '').replace(/\|$/, '').split('|').map((cell) => cell.trim());
}

/** Markdown -> blocks. Blank lines separate blocks; consecutive markers merge into one. */
export function parseLessonBlocks(body: string): LessonBlock[] {
  const lines = (body || '').replace(/\r\n/g, '\n').split('\n');
  const blocks: LessonBlock[] = [];
  let index = 0;

  while (index < lines.length) {
    const line = lines[index];
    const trimmed = line.trim();

    if (!trimmed) {
      index += 1;
      continue;
    }

    // Fenced code, including the ``` fence itself when the body is truncated.
    if (trimmed.startsWith('```')) {
      const language = trimmed.slice(3).trim();
      const code: string[] = [];
      index += 1;
      while (index < lines.length && !lines[index].trim().startsWith('```')) {
        code.push(lines[index]);
        index += 1;
      }
      index += 1;
      blocks.push({ kind: 'code', language, code: code.join('\n') });
      continue;
    }

    const heading = /^(#{1,4})\s+(.*)$/.exec(trimmed);
    if (heading) {
      blocks.push({
        kind: 'heading',
        level: heading[1].length as 1 | 2 | 3 | 4,
        text: heading[2],
      });
      index += 1;
      continue;
    }

    if (trimmed === '---' || trimmed === '***') {
      blocks.push({ kind: 'rule' });
      index += 1;
      continue;
    }

    if (trimmed.startsWith('> ')) {
      const quote: string[] = [];
      while (index < lines.length && lines[index].trim().startsWith('> ')) {
        quote.push(lines[index].trim().slice(2));
        index += 1;
      }
      blocks.push({ kind: 'quote', text: quote.join(' ') });
      continue;
    }

    if (isTableLine(line)) {
      const header = splitRow(line);
      index += 1;
      // The markdown separator row (| --- | --- |) is structure, not content.
      if (index < lines.length && /^[\s|:-]+$/.test(lines[index].trim()) && lines[index].includes('|')) {
        index += 1;
      }
      const rows: string[][] = [];
      while (index < lines.length && isTableLine(lines[index])) {
        rows.push(splitRow(lines[index]));
        index += 1;
      }
      blocks.push({ kind: 'table', header, rows });
      continue;
    }

    const bullet = /^[-*]\s+(.*)$/.exec(trimmed);
    const numbered = /^\d+[.)]\s+(.*)$/.exec(trimmed);
    if (bullet || numbered) {
      const ordered = Boolean(numbered);
      const items: string[] = [];
      while (index < lines.length) {
        const current = lines[index].trim();
        const nextBullet = /^[-*]\s+(.*)$/.exec(current);
        const nextNumbered = /^\d+[.)]\s+(.*)$/.exec(current);
        if (ordered ? nextNumbered : nextBullet) {
          items.push((ordered ? nextNumbered : nextBullet)![1]);
          index += 1;
          continue;
        }
        if (!ordered && nextNumbered) break;
        if (ordered && nextBullet) break;
        break;
      }
      blocks.push({ kind: 'list', ordered, items });
      continue;
    }

    // Paragraph: one line each, matching the learner renderer's line-based parser.
    blocks.push({ kind: 'paragraph', text: trimmed });
    index += 1;
  }

  return blocks;
}

/** Blocks -> markdown. Output is stable so a save without edits changes nothing. */
export function serializeLessonBlocks(blocks: LessonBlock[]): string {
  const out: string[] = [];

  for (const block of blocks) {
    switch (block.kind) {
      case 'heading':
        if (block.text.trim()) out.push(`${'#'.repeat(block.level)} ${block.text.trim()}`);
        break;
      case 'paragraph':
        if (block.text.trim()) out.push(block.text.trim());
        break;
      case 'list':
        block.items
          .map((item) => item.trim())
          .filter(Boolean)
          .forEach((item, i) => out.push(block.ordered ? `${i + 1}. ${item}` : `- ${item}`));
        break;
      case 'code':
        out.push('```' + (block.language || ''));
        if (block.code) out.push(...block.code.replace(/\r\n/g, '\n').split('\n'));
        out.push('```');
        break;
      case 'quote':
        if (block.text.trim()) out.push(...block.text.trim().split('\n').map((line) => `> ${line}`));
        break;
      case 'table': {
        if (block.header.length) {
          out.push(`| ${block.header.join(' | ')} |`);
          out.push(`| ${block.header.map(() => '---').join(' | ')} |`);
          block.rows.forEach((row) => {
            const cells = [...row];
            while (cells.length < block.header.length) cells.push('');
            out.push(`| ${cells.slice(0, block.header.length).join(' | ')} |`);
          });
        }
        break;
      }
      case 'rule':
        out.push('---');
        break;
    }
    out.push('');
  }

  return out.join('\n').trim() + (out.length ? '\n' : '');
}

/** Word count for the editor's status line; code is excluded because it is not read. */
export function countBlockWords(blocks: LessonBlock[]): number {
  const text = blocks
    .filter((block) => block.kind !== 'code')
    .map((block) => {
      switch (block.kind) {
        case 'heading':
        case 'paragraph':
        case 'quote':
          return block.text;
        case 'list':
          return block.items.join(' ');
        case 'table':
          return [block.header, ...block.rows].flat().join(' ');
        default:
          return '';
      }
    })
    .join(' ');
  return text.split(/\s+/).filter(Boolean).length;
}
