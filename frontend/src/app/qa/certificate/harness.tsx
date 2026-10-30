'use client';

import CertificateSheet, {
  CERT_HEIGHT,
  CERT_WIDTH,
  type CertificateData,
} from '@/components/credentials/certificate-artwork';

/** Dev-only sample data — never persisted, never shown to real users. */
const SAMPLES: Array<{ name: string; data: CertificateData }> = [
  {
    name: 'Typical',
    data: {
      student_name: 'Aarav Sharma',
      course_title: 'Python Fundamentals',
      credential_id: 'CY-PY-2026-000123',
      verification_code: 'f7Ab9Kd2Lm8Nq4Rt',
      issued_at: '2026-02-14T10:30:00Z',
      final_score: 92,
      issuer: 'Code Yaar Academy',
      verification_url: 'http://localhost:8000/api/verify/f7Ab9Kd2Lm8Nq4Rt/',
      qr_data_url: fakeQr(),
      status: 'active',
    },
  },
  {
    name: 'Long names / no score',
    data: {
      student_name: 'Christopher Maximilian von Habsburg-Lothringen',
      course_title:
        'Full-Stack Web Development with React, Next.js and Distributed Systems',
      credential_id: 'CY-WEB-2026-99887766',
      verification_code: 'pV3xQ8qO6mY2uH9w',
      issued_at: '2026-10-01T08:00:00Z',
      final_score: null,
      issuer: 'Code Yaar Academy',
      verification_url: 'http://localhost:8000/api/verify/pV3xQ8qO6mY2uH9w/',
      qr_data_url: fakeQr(),
      status: 'active',
    },
  },
];

function fakeQr(): string {
  // Deterministic QR-like placeholder so the layout can be validated.
  const cells = 25;
  let rects = '';
  let seed = 42;
  const rnd = () => ((seed = (seed * 1103515245 + 12345) % 2147483648) / 2147483648);
  for (let y = 0; y < cells; y++) {
    for (let x = 0; x < cells; x++) {
      if (rnd() > 0.5) rects += `<rect x="${x * 4}" y="${y * 4}" width="4" height="4"/>`;
    }
  }
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${cells * 4}" height="${cells * 4}" fill="#171717"><rect width="100%" height="100%" fill="#fff"/>${rects}</svg>`;
  return `data:image/svg+xml;base64,${btoa(svg)}`;
}

export default function CertificateQAHarness() {
  return (
    <div style={{ padding: 24, background: '#222', minHeight: '100vh' }}>
      {SAMPLES.map(({ name, data }) => (
        <section key={name} style={{ marginBottom: 40 }}>
          <h2 style={{ color: '#fff', fontFamily: 'monospace', marginBottom: 12 }}>
            QA — {name}
          </h2>
          <div style={{ transform: 'scale(0.62)', transformOrigin: 'top left', width: CERT_WIDTH * 0.62, height: CERT_HEIGHT * 0.62 }}>
            <CertificateSheet data={data} />
          </div>
        </section>
      ))}
    </div>
  );
}
