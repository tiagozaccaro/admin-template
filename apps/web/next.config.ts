import type { NextConfig } from "next"

const nextConfig: NextConfig = {
  output: "standalone",
  transpilePackages: ["@workspace/ui"],
  experimental: {
    agentUpgrade: "security",
  },
}

export default nextConfig
