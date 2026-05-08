import { MainHero } from '@/app/(main)/_components/main-hero';
import { PatchStatusHeader } from '@/app/(main)/_components/patch-status-header';

export default function MainPage() {
  return (
    <main className="pixel-background relative isolate flex min-h-dvh w-full flex-col items-center justify-center overflow-x-hidden px-4 py-6 text-foreground sm:px-6 lg:px-8">
      <PatchStatusHeader />
      <MainHero />
    </main>
  );
}
