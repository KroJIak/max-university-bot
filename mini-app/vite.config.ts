import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import { fileURLToPath, URL } from 'node:url';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');

  const cloudpubUrl =
    env.CLOUDPUB_URL ||
    env.CLOUDPUB_DOMAIN_URL ||
    env.VITE_CLOUDPUB_URL ||
    env.CLOUDPUB_PUBLIC_URL;

  const allowedHosts: string[] = [];

  if (cloudpubUrl) {
    try {
      const { host } = new URL(cloudpubUrl);
      if (host) {
        allowedHosts.push(host);
      }
    } catch (error) {
      console.warn(
        '[vite-config] CLOUDPUB URL в .env не распознан. Проверьте формат (ожидаем полный URL со схемой).'
      );
    }
  }

  return {
    plugins: [react()],
    resolve: {
      alias: {
        '@components': fileURLToPath(new URL('./src/components', import.meta.url)),
      },
    },
    server: allowedHosts.length
      ? {
          allowedHosts,
        }
      : undefined,
  };
});