import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright Configuration for E2E Testing
 * Tests the Anki Template Designer in real browsers
 */
export default defineConfig({
  // Test directory
  testDir: './e2e',
  
  // Timeout for each test
  timeout: 30 * 1000,
  
  // Timeout for expect assertions
  expect: {
    timeout: 5000,
  },
  
  // Run tests in parallel
  fullyParallel: true,
  
  // Fail the build on CI if you accidentally left test.only in the source code
  forbidOnly: !!process.env.CI,
  
  // Retry on CI only
  retries: process.env.CI ? 2 : 0,
  
  // Opt out of parallel tests on CI
  workers: process.env.CI ? 1 : undefined,
  
  // Reporter to use
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['list'],
    ['json', { outputFile: 'playwright-results.json' }],
  ],
  
  // Shared settings for all projects
  use: {
    // Base URL for page.goto('/')
    baseURL: 'http://localhost:5173',
    
    // Collect trace when retrying the failed test
    trace: 'on-first-retry',
    
    // Screenshot on failure
    screenshot: 'only-on-failure',
    
    // Video on failure
    video: 'retain-on-failure',
    
    // Ignore HTTPS errors
    ignoreHTTPSErrors: true,
    
    // Viewport size
    viewport: { width: 1280, height: 720 },
  },
  
  // Configure projects for major browsers
  projects: [
    {
      name: 'chromium',
      use: { 
        ...devices['Desktop Chrome'],
        // Use headless mode for faster execution
        headless: true,
      },
    },
    
    {
      name: 'firefox',
      use: { 
        ...devices['Desktop Firefox'],
        headless: true,
      },
    },
    
    // Uncomment to test on WebKit (Safari)
    // {
    //   name: 'webkit',
    //   use: { 
    //     ...devices['Desktop Safari'],
    //     headless: true,
    //   },
    // },
    
    // Test against mobile viewports
    // {
    //   name: 'Mobile Chrome',
    //   use: { ...devices['Pixel 5'] },
    // },
  ],
  
  // Run your local dev server before starting the tests
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
    stdout: 'ignore',
    stderr: 'pipe',
  },
});
