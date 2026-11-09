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
};

export default nextConfig;
