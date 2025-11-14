/// <reference types="node" />
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import { fileURLToPath, URL } from 'node:url';
import { resolve } from 'node:path';

export default defineConfig(({ mode }) => {
  const projectRoot = fileURLToPath(new URL('.', import.meta.url));
  const rootEnv = loadEnv(mode, resolve(projectRoot, '..'), '');
  const env = loadEnv(mode, projectRoot, '');
  
  // Используем MAX_API_DOMAIN_URL из корневого .env, если VITE_API_BASE_URL не задан
  const apiBaseUrl = env.VITE_API_BASE_URL || rootEnv.MAX_API_DOMAIN_URL || '';

  const cloudpubUrl =
    env.CLOUDPUB_URL ||
    env.CLOUDPUB_DOMAIN_URL ||
    env.VITE_CLOUDPUB_URL ||
    env.CLOUDPUB_PUBLIC_URL;

  const allowedHostsSet = new Set<string>(['localhost', '127.0.0.1', '[::1]']);

  if (cloudpubUrl) {
    try {
      const { hostname } = new URL(cloudpubUrl);
      if (hostname) {
        allowedHostsSet.add(hostname);
      }
    } catch (error) {
      console.warn(
        '[vite-config] CLOUDPUB URL в .env не распознан. Проверьте формат (ожидаем полный URL со схемой).'
      );
    }
  }

  if (env.VITE_ALLOWED_HOSTS) {
    env.VITE_ALLOWED_HOSTS.split(',')
      .map((value) => value.trim())
      .filter(Boolean)
      .forEach((host) => allowedHostsSet.add(host));
  }

  const allowedHosts = Array.from(allowedHostsSet);
  const isProdLikeMode = mode !== 'development';

  const parseUrl = (raw?: string | null) => {
    if (!raw) {
      return null;
    }
    try {
      return new URL(raw.includes('://') ? raw : `https://${raw}`);
    } catch {
      return null;
    }
  };

  const cloudpubParsed = parseUrl(
    cloudpubUrl ||
      env.MINI_APP_DOMAIN_URL ||
      env.MINI_APP_PUBLIC_URL ||
      env.VITE_APP_ORIGIN,
  );

  const cloudpubHostname = cloudpubParsed?.hostname ?? null;
  const cloudpubProtocol = cloudpubParsed?.protocol ?? null;

  const hmrConfig =
    env.VITE_HMR_DISABLED === 'true'
      ? false
      : {
          protocol: env.VITE_HMR_PROTOCOL
            ? env.VITE_HMR_PROTOCOL
            : isProdLikeMode || cloudpubProtocol === 'https:'
            ? 'wss'
            : 'ws',
          host:
            env.VITE_HMR_HOST ||
            cloudpubHostname ||
            (isProdLikeMode ? undefined : 'localhost'),
          port: env.VITE_HMR_PORT
            ? Number(env.VITE_HMR_PORT)
            : undefined,
          clientPort:
            env.VITE_HMR_CLIENT_PORT && env.VITE_HMR_CLIENT_PORT.length > 0
              ? Number(env.VITE_HMR_CLIENT_PORT)
              : (isProdLikeMode || cloudpubProtocol === 'https:')
              ? 443
              : undefined,
        };

  return {
    plugins: [react()],
    define: {
      'import.meta.env.VITE_API_BASE_URL': JSON.stringify(apiBaseUrl),
    },
    resolve: {
      alias: {
        '@components': fileURLToPath(new URL('./src/components', import.meta.url)),
        '@shared': fileURLToPath(new URL('./src/shared', import.meta.url)),
      },
    },
    server: {
      host: '0.0.0.0',
      port: 5177,
      strictPort: true,
      cors: true,
      ...(isProdLikeMode && allowedHosts.length > 0
        ? {
            allowedHosts,
          }
        : {
            allowedHosts: true,
          }),
      hmr: hmrConfig,
    },
  };
});