/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    // Durante el build, ignora los errores de ESLint
    ignoreDuringBuilds: true,
  },
  typescript: {
    // Durante el build, ignora los errores de TypeScript
    ignoreBuildErrors: true,
  },
  webpack: (config) => {
    // Configurar alias para resolver las importaciones
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': require('path').resolve(__dirname),
      '@/lib': require('path').resolve(__dirname, 'lib'),
    };
    return config;
  },
  images: {
    remotePatterns: [
      {
        protocol: 'http',
        hostname: 'localhost',
        port: '8000',
        pathname: '/uploads/**',
      },
    ],
  },
}

module.exports = nextConfig