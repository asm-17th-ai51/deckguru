import './globals.css';

import { galmuri9, galmuri11 } from '@/assets/fonts/font';
import { ThemeProvider } from '@/components/providers/theme-provider';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'DECK GURU - 최신 메타에 맞는 덱을 확인하세요',
  description: '최신 메타와 티어, 스타일에 맞는 덱 운영 가이드를 제공합니다',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko" suppressHydrationWarning>
      <body
        className={`${galmuri11.variable} ${galmuri9.variable} antialiased`}>
        <ThemeProvider>{children}</ThemeProvider>
      </body>
    </html>
  );
}
