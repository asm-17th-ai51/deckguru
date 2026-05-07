'use client';

import { useRecommendationResultQuery } from '@/api/post-recommend/query';
import { Button } from '@/components/ui/button';
import { APP_PATH } from '@/constants/app-path';
import { m } from 'motion/react';
import Link from 'next/link';

interface RecommendationResultViewProps {
  requestId: string;
}

export function RecommendationResultView({
  requestId,
}: RecommendationResultViewProps) {
  const { data: recommendation } = useRecommendationResultQuery(requestId);

  if (!recommendation) {
    return (
      <main className="pixel-background relative isolate flex h-dvh w-full flex-col items-center justify-center overflow-hidden px-5 py-10 text-center">
        <section className="relative z-10 flex w-full max-w-xl flex-col items-center gap-6">
          <h1 className="font-galmuri11 text-xl font-bold text-primary sm:text-2xl">
            결과를 찾을 수 없습니다
          </h1>
          <div className="flex flex-col text-center text-sm leading-relaxed text-muted-foreground">
            <p>
              새로고침했거나 결과 주소로 바로 접근하면
              <br className="block sm:hidden" /> 임시 추천 결과가 사라집니다.
            </p>
            <p>메인에서 다시 추천을 요청해 주세요.</p>
          </div>
          <m.div
            transition={{
              duration: 0.12,
              ease: 'easeOut',
            }}
            whileHover={{ x: 2, y: 1, scale: 0.98 }}
            whileTap={{ x: 2, y: 3, scale: 0.96 }}>
            <Button
              type="button"
              nativeButton={false}
              className="h-12 px-5 font-galmuri11 text-sm font-bold"
              aria-label="메인 화면으로 돌아가기"
              render={<Link href={APP_PATH.MAIN} />}>
              메인으로 돌아가기
            </Button>
          </m.div>
        </section>
      </main>
    );
  }

  return (
    <main className="pixel-background relative isolate flex h-dvh w-full overflow-hidden p-10 px-5 sm:px-4">
      <section className="relative z-10 mx-auto flex h-full min-h-0 w-full max-w-4xl flex-col gap-5">
        <div className="flex shrink-0 flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div className="flex flex-col gap-2">
            <p className="font-galmuri11 text-xs font-bold text-primary">
              {recommendation.request_id}
            </p>
            <h1 className="font-galmuri11 text-xl font-bold text-foreground sm:text-2xl">
              추천 결과
            </h1>
          </div>

          <m.div
            className="w-full sm:w-auto"
            transition={{
              duration: 0.12,
              ease: 'easeOut',
            }}
            whileHover={{ x: 2, y: 1, scale: 0.98 }}
            whileTap={{ x: 2, y: 3, scale: 0.96 }}>
            <Button
              type="button"
              nativeButton={false}
              className="h-12 px-5 font-galmuri11 text-sm font-bold"
              aria-label="다시 추천받기"
              render={<Link href={APP_PATH.MAIN} />}>
              다시 추천받기
            </Button>
          </m.div>
        </div>

        <pre className="min-h-0 flex-1 overflow-auto border-4 border-border bg-background/95 p-4 text-left font-mono text-xs leading-6 text-foreground">
          {JSON.stringify(recommendation, null, 2)}
        </pre>
      </section>
    </main>
  );
}
