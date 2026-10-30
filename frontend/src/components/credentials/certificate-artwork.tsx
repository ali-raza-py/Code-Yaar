'use client';

import { useLayoutEffect, useRef, useState } from 'react';

/**
 * Premium certificate artwork — the on-screen twin of the server renderers
 * (backend/certificates/pdf.py + png.py). One layout system, three outputs:
 *
 *   ivory paper → burgundy/gold/burgundy triple frame → ornamental corners
 *   faint emblem + wordmark watermark → centred brand band (purple diamond
 *   mark, CODE YAAR wordmark, italic tagline) → burgundy serif designation
 *   over a gold rule → statement, recipient name over a double rule, course
 *   → digital authorisation mark bottom-left → ONE compact verification
 *   block bottom-right (issue date, certificate ID, verification code, QR).
 *
 * The canvas is a fixed 1123 × 794 px — exactly A4 landscape at 96 dpi —
 * and every position is derived from the same millimetre grid the backend
 * uses, so preview, print, PDF and PNG stay compositionally identical.
 */

export const CERT_WIDTH = 1123;
export const CERT_HEIGHT = 794;

/** Backend grid is millimetre-based; 1 mm = 3.7795 px at 96 dpi. */
const MM = 3.7795;
const mm = (v: number) => Math.round(v * MM * 100) / 100;
/** Backend sizes are PostScript points; 1 pt = 1.3333 px at 96 dpi. */
const pt = (v: number) => Math.round(v * (4 / 3) * 100) / 100;

// Palette — mirrors backend/certificates/pdf.py
const BURGUNDY = '#751D2B';
const BURGUNDY_SOFT = '#8C2F3F';
const GOLD = '#C49A48';
const GOLD_DEEP = '#9A7B32';
const PURPLE = '#7528E8';
const INK = '#171717';
const MUTED = '#5C564E';
const IVORY = '#FCFAF3';
const WATERMARK = '#F6F1E7';

const SERIF = "Georgia, 'Times New Roman', 'Nimbus Roman', serif";
const SANS = "'Segoe UI', 'Helvetica Neue', Arial, sans-serif";

export interface CertificateData {
  student_name: string;
  course_title: string;
  credential_id: string;
  issued_at: string;
  final_score: number | null;
  issuer: string;
  verification_url: string;
  /** Base64 PNG data URL of the verification QR code. */
  qr_data_url?: string;
  /** Stable public verification code (certificate public id). */
  verification_code?: string;
  status?: string;
}

function formatDate(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return '—';
  return d.toLocaleDateString('en-GB', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
  });
}

/**
 * Code Yaar brand logo, tinted to `colour` with a CSS mask. The mask asset is
 * the same silhouette the PDF/PNG renderers reuse (see backend `branding.py`),
 * so the on-screen sheet, the download and the print export always match.
 */
function EmblemMark({ size, colour }: { size: number; colour: string }) {
  return (
    <span
      aria-hidden="true"
      style={{
        display: 'block',
        width: size,
        height: size,
        backgroundColor: colour,
        WebkitMaskImage: 'url(/brand/logo-mark.png)',
        maskImage: 'url(/brand/logo-mark.png)',
        WebkitMaskRepeat: 'no-repeat',
        maskRepeat: 'no-repeat',
        WebkitMaskPosition: 'center',
        maskPosition: 'center',
        WebkitMaskSize: 'contain',
        maskSize: 'contain',
      }}
    />
  );
}

/** Line—diamond—line ornamental rule, mirrored from `_ornamental_rule`. */
function OrnamentalRule() {
  const w = mm(84);
  const d = mm(2.4);
  return (
    <svg
      aria-hidden="true"
      width={w}
      height={d + 4}
      viewBox={`0 0 ${w} ${d + 4}`}
      fill="none"
      style={{ display: 'block' }}
    >
      <line x1="0" y1={d / 2 + 2} x2={w / 2 - mm(3.2)} y2={d / 2 + 2} stroke={GOLD} strokeWidth={0.8} />
      <line x1={w / 2 + mm(3.2)} y1={d / 2 + 2} x2={w} y2={d / 2 + 2} stroke={GOLD} strokeWidth={0.8} />
      <path
        d={`M ${w / 2} 2 L ${w / 2 + d / 2} ${d / 2 + 2} L ${w / 2} ${d + 2} L ${w / 2 - d / 2} ${d / 2 + 2} Z`}
        fill={BURGUNDY}
      />
      <circle cx={w / 2 - mm(6.5)} cy={d / 2 + 2} r={mm(0.7)} fill={GOLD} />
      <circle cx={w / 2 + mm(6.5)} cy={d / 2 + 2} r={mm(0.7)} fill={GOLD} />
    </svg>
  );
}

/** Ornamental corner motifs seated on the innermost rule (see _corner_flourish). */
function CornerFlourishes() {
  const p = mm(13);
  const arm = mm(14);
  const d = mm(2.6);
  const dx = mm(4.6);
  // One SVG covers all four corners with mirrored groups.
  const groups = [
    { tx: p, ty: p, sx: 1, sy: 1 },
    { tx: CERT_WIDTH - p, ty: p, sx: -1, sy: 1 },
    { tx: p, ty: CERT_HEIGHT - p, sx: 1, sy: -1 },
    { tx: CERT_WIDTH - p, ty: CERT_HEIGHT - p, sx: -1, sy: -1 },
  ];
  return (
    <svg
      aria-hidden="true"
      className="pointer-events-none absolute inset-0"
      width={CERT_WIDTH}
      height={CERT_HEIGHT}
      viewBox={`0 0 ${CERT_WIDTH} ${CERT_HEIGHT}`}
      fill="none"
    >
      {groups.map((g, i) => (
        <g key={i} transform={`translate(${g.tx} ${g.ty}) scale(${g.sx} ${g.sy})`}>
          {/* Twin hairlines along each edge of the corner */}
          <line x1="0" y1={mm(2.2)} x2={arm} y2={mm(2.2)} stroke={BURGUNDY_SOFT} strokeWidth={0.5} />
          <line x1={mm(2.2)} y1="0" x2={mm(2.2)} y2={arm} stroke={BURGUNDY_SOFT} strokeWidth={0.5} />
          {/* Gold diamond with a centre dot at the vertex */}
          <path
            d={`M ${dx} 0 L ${dx + d / 2} ${d / 2} L ${dx} ${d} L ${dx - d / 2} ${d / 2} Z`}
            fill={GOLD}
          />
          <circle cx={dx + d / 2} cy={d / 2} r={mm(0.45)} fill={BURGUNDY} />
        </g>
      ))}
    </svg>
  );
}

/** Small-caps spaced label used across the footer bands. */
function SpacedCaps({
  text,
  size,
  spacing,
  colour,
  align = 'left',
  style,
}: {
  text: string;
  size: number;
  spacing: number;
  colour: string;
  align?: 'left' | 'center' | 'right';
  style?: React.CSSProperties;
}) {
  return (
    <p
      style={{
        fontFamily: SANS,
        fontSize: size,
        fontWeight: 700,
        letterSpacing: spacing,
        color: colour,
        textAlign: align,
        // CSS adds trailing spacing after the last glyph; pull it back so the
        // visual width matches the backend's per-glyph advance metric.
        marginRight: align === 'right' ? -spacing : undefined,
        marginLeft: align === 'left' ? -spacing / 2 : undefined,
        ...style,
      }}
    >
      {text}
    </p>
  );
}

export default function CertificateSheet({ data }: { data: CertificateData }) {
  const name = (data.student_name || 'Learner').trim();
  const course = (data.course_title || 'Course').trim();
  const hasQr = Boolean(data.qr_data_url);
  const unverified = data.status !== undefined && data.status !== 'active';

  // ── Backend mm-grid anchors, expressed top-down for CSS ──
  const topInset = mm(20); // brand band start
  const footerBaseFromTop = CERT_HEIGHT - mm(20); // backend `base` line

  // Verification block (bottom-right): rows share the backend's top anchor.
  const qrSize = mm(24);
  const rowsTop = footerBaseFromTop - mm(27);

  // Authorisation block (bottom-left).
  const sigTop = footerBaseFromTop - mm(12.5);

  return (
    <div
      className="cy-certificate-sheet relative shrink-0 overflow-hidden"
      style={{
        width: CERT_WIDTH,
        height: CERT_HEIGHT,
        background: IVORY,
        fontFamily: SERIF,
        color: INK,
        WebkitFontSmoothing: 'antialiased',
      }}
      data-certificate-id={data.credential_id}
    >
      {/* ── Triple frame: burgundy → gold → burgundy ── */}
      <div
        className="absolute"
        style={{ inset: mm(8), border: `${2.6}px solid ${BURGUNDY}` }}
      />
      <div
        className="absolute"
        style={{ inset: mm(11.2), border: `${0.9}px solid ${GOLD}` }}
      />
      <div
        className="absolute"
        style={{ inset: mm(13), border: `${0.5}px solid ${BURGUNDY}` }}
      />
      <CornerFlourishes />

      {/* ── Faint watermark: emblem + wordmark behind the content ── */}
      <div
        className="pointer-events-none absolute left-1/2 -translate-x-1/2"
        style={{ top: mm(75.5) }}
      >
        <div className="flex justify-center">
          <EmblemMark size={mm(26)} colour={WATERMARK} />
        </div>
        <p
          style={{
            marginTop: mm(14),
            fontFamily: SERIF,
            fontSize: pt(74),
            fontWeight: 700,
            letterSpacing: pt(10),
            marginRight: -pt(10),
            color: WATERMARK,
            whiteSpace: 'nowrap',
            textAlign: 'center',
          }}
        >
          CODE YAAR
        </p>
      </div>

      {/* ── Brand band (centred, top) ── */}
      <header
        className="absolute inset-x-0 flex flex-col items-center text-center"
        style={{ top: topInset }}
      >
        <EmblemMark size={mm(9.5)} colour={PURPLE} />
        <p
          style={{
            marginTop: mm(2.6),
            fontFamily: SERIF,
            fontSize: pt(25),
            fontWeight: 700,
            letterSpacing: pt(3.2),
            marginRight: -pt(3.2),
            color: INK,
            lineHeight: 1.15,
          }}
        >
          CODE YAAR
        </p>
        <p
          style={{
            marginTop: mm(1.1),
            fontFamily: SERIF,
            fontStyle: 'italic',
            fontSize: pt(11),
            color: GOLD_DEEP,
            lineHeight: 1.3,
          }}
        >
          Think. Build. Evolve.
        </p>
        <div style={{ marginTop: mm(3.9) }}>
          <OrnamentalRule />
        </div>
        <p
          style={{
            marginTop: mm(4.4),
            fontFamily: SERIF,
            fontSize: pt(15.5),
            fontWeight: 700,
            letterSpacing: pt(3.6),
            marginRight: -pt(3.6),
            color: BURGUNDY,
            lineHeight: 1.2,
          }}
        >
          CERTIFICATE OF COMPLETION
        </p>
        <div
          style={{
            marginTop: mm(3.4),
            width: pt(15.5) * 22,
            height: 0.7,
            background: GOLD,
          }}
        />
      </header>

      {/* ── Statement band — centred between brand band and footer ── */}
      <main
        className="absolute flex flex-col items-center justify-center text-center"
        style={{
          left: mm(27),
          right: mm(27),
          top: mm(66),
          bottom: CERT_HEIGHT - footerBaseFromTop + mm(2),
        }}
      >
        <p
          style={{
            fontFamily: SERIF,
            fontStyle: 'italic',
            fontSize: pt(11.5),
            color: MUTED,
            lineHeight: 1.3,
          }}
        >
          This is to certify that
        </p>

        <p
          style={{
            marginTop: mm(3.5),
            maxWidth: CERT_WIDTH - mm(54),
            fontFamily: SERIF,
            fontSize: pt(33),
            fontWeight: 700,
            color: INK,
            lineHeight: 1.15,
            letterSpacing: '0.005em',
            overflowWrap: 'anywhere',
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden',
          }}
        >
          {name}
        </p>

        {/* Double rule under the name: burgundy over gold. Width tracks the
            name like the backend's `min(max(w + 24mm, 70mm), 150mm)` rule. */}
        <div
          style={{
            marginTop: mm(2.4),
            width: 'fit-content',
            minWidth: mm(70),
            maxWidth: mm(150),
            position: 'relative',
            height: mm(1.6),
          }}
        >
          <div style={{ position: 'absolute', inset: 0, bottom: 'auto', height: 1, background: BURGUNDY }} />
          <div
            style={{
              position: 'absolute',
              left: 0,
              right: 0,
              top: mm(1.2),
              height: 0.5,
              background: GOLD,
            }}
          />
        </div>

        <p
          style={{
            marginTop: mm(3.1),
            fontFamily: SERIF,
            fontStyle: 'italic',
            fontSize: pt(11.5),
            color: MUTED,
            lineHeight: 1.3,
          }}
        >
          has successfully completed
        </p>

        <p
          style={{
            marginTop: mm(3.5),
            maxWidth: CERT_WIDTH - mm(60),
            fontFamily: SERIF,
            fontSize: pt(17.5),
            fontWeight: 700,
            color: BURGUNDY,
            lineHeight: 1.25,
            overflowWrap: 'anywhere',
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden',
          }}
        >
          {course}
        </p>

        {data.final_score !== null && (
          <p
            style={{
              marginTop: mm(4.2),
              fontFamily: SANS,
              fontSize: pt(9.5),
              fontWeight: 400,
              color: MUTED,
              letterSpacing: '0.01em',
            }}
          >
            Final assessment score · {data.final_score}%
          </p>
        )}
      </main>

      {/* ── Bottom-left: digital authorisation mark ── */}
      <div
        className="absolute"
        style={{ left: mm(22), top: sigTop, width: mm(60) }}
      >
        <p
          style={{
            fontFamily: SERIF,
            fontStyle: 'italic',
            fontSize: pt(19),
            color: INK,
            lineHeight: 1.1,
          }}
        >
          {'Code Yaar'}
        </p>
        <div
          style={{
            marginTop: mm(1.2),
            height: 0.8,
            width: mm(58),
            background: BURGUNDY,
          }}
        />
        <SpacedCaps
          text="CODE YAAR ACADEMY"
          size={pt(7.2)}
          spacing={pt(1.6)}
          colour={GOLD_DEEP}
          style={{ marginTop: mm(1.8) }}
        />
        <p
          style={{
            marginTop: mm(1.2),
            fontFamily: SANS,
            fontSize: pt(6.6),
            color: MUTED,
          }}
        >
          Authorized by · digitally issued credential
        </p>
      </div>

      {/* ── Bottom-right: the ONLY place identifiers appear ── */}
      <div
        className="absolute flex items-start justify-end"
        style={{
          left: mm(22),
          right: mm(22),
          top: rowsTop,
          paddingBottom: mm(14),
        }}
      >
        {/* Label-above-value rows, right-aligned — mirrors the backend's
            `qr_x - 5mm` edge so long codes shrink instead of wrapping. */}
        <div
          style={{
            width: mm(64),
            marginRight: mm(5),
            textAlign: 'right',
          }}
        >
          <VerifyRow
            label="ISSUE DATE"
            value={formatDate(data.issued_at)}
            valueStyle={{ fontFamily: SANS, fontSize: pt(9.5), fontWeight: 400 }}
          />
          <VerifyRow
            label="CERTIFICATE ID"
            value={data.credential_id}
            valueStyle={{ fontFamily: SANS, fontSize: pt(9.5), fontWeight: 700 }}
          />
          {data.verification_code ? (
            <VerifyRow
              label="VERIFICATION CODE"
              value={data.verification_code}
              valueStyle={{
                fontFamily: "'Courier New', Courier, monospace",
                fontSize: pt(6.8),
                fontWeight: 400,
              }}
            />
          ) : null}
        </div>

        {/* QR + scan hint, packed to the corner */}
        <div className="shrink-0" style={{ width: qrSize + mm(2.4) }}>
          <div
            style={{
              padding: mm(1.2),
              background: '#FFFFFF',
              border: `0.5px solid ${BURGUNDY}`,
            }}
          >
            {hasQr ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={data.qr_data_url}
                alt="QR code linking to the public verification page"
                width={qrSize}
                height={qrSize}
                style={{ display: 'block', width: qrSize, height: qrSize }}
              />
            ) : (
              <div
                style={{
                  width: qrSize,
                  height: qrSize,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: MUTED,
                  fontFamily: SANS,
                  fontSize: pt(7),
                  fontWeight: 700,
                  letterSpacing: '0.08em',
                  textAlign: 'center',
                }}
              >
                QR
                <br />
                UNAVAILABLE
              </div>
            )}
          </div>
          <SpacedCaps
            text="SCAN TO VERIFY"
            size={pt(6.2)}
            spacing={pt(1.2)}
            colour={MUTED}
            align="center"
            style={{
              marginTop: mm(1.2),
            }}
          />
          {unverified && (
            <p
              style={{
                marginTop: mm(0.8),
                fontFamily: SANS,
                fontSize: pt(5.6),
                fontWeight: 700,
                letterSpacing: '0.06em',
                color: BURGUNDY,
                textAlign: 'center',
              }}
            >
              {data.status === 'revoked' ? 'REVOKED' : 'SUPERSEDED'}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

function VerifyRow({
  label,
  value,
  valueStyle,
}: {
  label: string;
  value: string;
  valueStyle: React.CSSProperties;
}) {
  return (
    <div style={{ marginBottom: mm(3.2) }}>
      <SpacedCaps text={label} size={pt(6.2)} spacing={pt(1.0)} colour={GOLD_DEEP} align="right" />
      <FitText
        text={value}
        max={maxFontSize(valueStyle)}
        style={{
          marginTop: mm(0.9),
          color: INK,
          lineHeight: 1.25,
          textAlign: 'right',
          ...valueStyle,
        }}
      />
    </div>
  );
}

function maxFontSize(style: React.CSSProperties): number {
  return typeof style.fontSize === 'number' ? style.fontSize : 12;
}

/**
 * Single-line text that shrinks to fit its box — the DOM twin of the
 * backend's `_fit_font` shrink-to-width behaviour for certificate values.
 * The wrapper is `display: table` so it narrows to the text, capped by the
 * column width; the paragraph then measures itself against that cap.
 */
function FitText({
  text,
  max,
  style,
}: {
  text: string;
  max: number;
  style?: React.CSSProperties;
}) {
  const ref = useRef<HTMLParagraphElement>(null);
  const [size, setSize] = useState(max);
  const min = max * 0.6;

  useLayoutEffect(() => {
    const el = ref.current;
    if (!el) return;
    let s = max;
    el.style.fontSize = `${s}px`;
    while (s > min && el.scrollWidth > el.clientWidth) {
      s -= 0.5;
      el.style.fontSize = `${s}px`;
    }
    setSize(s);
  }, [text, max, min]);

  return (
    <div style={{ display: 'table', maxWidth: '100%', marginLeft: 'auto' }}>
      <p
        ref={ref}
        style={{
          whiteSpace: 'nowrap',
          fontSize: size,
          ...style,
        }}
      >
        {text}
      </p>
    </div>
  );
}
