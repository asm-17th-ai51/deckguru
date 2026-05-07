import { MainHero } from '@/app/(main)/_components/main-hero';
import { PatchStatusHeader } from '@/app/(main)/_components/patch-status-header';

export default function MainPage() {
  return (
    <main className="pixel-background relative isolate flex min-h-svh w-full flex-col items-center justify-center overflow-hidden p-6 px-5 sm:px-4">
      <PatchStatusHeader />
      <MainHero />
    </main>
  );
}
