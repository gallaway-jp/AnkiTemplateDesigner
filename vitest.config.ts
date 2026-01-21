/**
 * Vitest Configuration for Performance Testing
 * 
 * Configures the test environment, globals, and performance testing utilities.
 * Usage: npm run test:perf
 */

import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    // Test environment setup
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/tests/setup.ts'],

    // Performance testing configuration
    include: ['src/tests/**/*.test.ts', 'src/tests/**/*.test.tsx'],
    exclude: ['node_modules', 'dist', 'build'],

    // Timeout configuration
    testTimeout: 30000,
    hookTimeout: 30000,

    // Coverage configuration (optional)
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/tests/',
      ],
    },

    // Benchmark configuration
    benchmark: {
      include: ['src/tests/**/*.bench.ts'],
      exclude: ['node_modules', 'dist'],
    },

    // Reporter configuration
    reporters: ['verbose'],

    // Parallel execution
    threads: true,
    maxThreads: 4,
    minThreads: 1,
  },

  // Path alias configuration
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@/components': path.resolve(__dirname, './src/components'),
      '@/stores': path.resolve(__dirname, './src/stores'),
      '@/services': path.resolve(__dirname, './src/services'),
      '@/types': path.resolve(__dirname, './src/types'),
      '@/utils': path.resolve(__dirname, './src/utils'),
      '@/tests': path.resolve(__dirname, './src/tests'),
    },
  },
});
