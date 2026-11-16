import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async redirects() {
    return [
      { source: '/learn/tracks', destination: '/tracks', permanent: false },
      { source: '/learn/tracks/:slug', destination: '/tracks/:slug', permanent: false },
    ];
  },
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'code-yaar.ethiodeploy.app',
      },
      {
        protocol: 'https',
        hostname: '*.ethiodeploy.app',
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
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  },
};

export default nextConfig;
