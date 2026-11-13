import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Discovery moved from the guarded (app) shell to the public site. Old
  // track URLs (and any bookmarked/shared links) keep working via redirects.
  async redirects() {
    return [
      { source: '/learn/tracks', destination: '/tracks', permanent: false },
      { source: '/learn/tracks/:slug', destination: '/tracks/:slug', permanent: false },
    ];
  },
  // Image optimization: allow backend media URLs and common CDN hosts so
  // next/image can optimize thumbnails, avatars, course covers, and track art.
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
      {
        protocol: 'http',
        hostname: 'localhost',
        port: '8000',
      },
      {
        protocol: 'http',
        hostname: '127.0.0.1',
        port: '8000',
      },
    ],
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200],
  },
};

export default nextConfig;
