export const APP_PATH = {
  MAIN: '/',
} as const;

export const APP_BASE_URL =
  process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000';
