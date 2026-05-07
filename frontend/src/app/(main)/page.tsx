'use client';

import { useDeckRecommendationForm } from '@/app/(main)/_hooks/use-deck-recommendation-form';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { m } from 'motion/react';

export const EXAMPLE_QUESTIONS = [
  '지금 골드가 티어 올리기 좋은 덱 3개 추천해줘',
  '이번 패치에서 메타에 영향이 큰 변경점만 알려줘',
  '요즘 많이 나오는 덱의 운영법을 알려줘',
  '초반에 곡궁이 많이 나왔는데 어떤 덱으로 가면 좋아?',
];

export default function MainPage() {
  const { inputRef, handleExampleQuestionClick, handleSubmit } =
    useDeckRecommendationForm();

  return (
    <main className="pixel-background relative isolate flex min-h-svh w-full flex-col items-center justify-center overflow-hidden p-6 px-5 sm:px-4">
      <header className="absolute top-0 right-0 z-20 flex justify-end p-4 sm:p-6">
        {/** 패치 배너 */}
        <div className="flex flex-row gap-2">
          <Badge variant="outline" className="h-auto border-2 px-3 py-2">
            PATCH VERSION 14.9
          </Badge>
          <Badge variant="outline" className="h-auto border-2 px-3 py-2">
            LAST UPDATED 2026-05-04
          </Badge>
        </div>
      </header>

      <div className="relative z-10 flex w-full max-w-3xl flex-col items-center gap-8">
        {/** 서비스 이름 */}
        <m.div
          className="flex cursor-default flex-col"
          transition={{
            duration: 0.12,
            ease: 'easeOut',
          }}
          whileHover={{ y: -4, scale: 1.08 }}>
          <h1 className="text-xl">DECK</h1>
          <h1 className="text-xl">GURU</h1>
        </m.div>

        <div className="flex w-full flex-col items-center justify-center gap-6">
          {/** 보조 문구 */}
          <div className="flex flex-col text-center leading-relaxed">
            <p>메타를 읽고, 덱을 고르세요</p>
            <p className="text-sm text-muted-foreground">
              티어와 스타일에 맞는 <br className="block sm:hidden" />덱 운영
              가이드를 제공합니다
            </p>
          </div>

          {/** 인풋 폼, 제출 버튼 */}
          <form
            className="mx-auto flex w-full max-w-2xl flex-col gap-2 sm:flex-row"
            onSubmit={handleSubmit}>
            <Input
              ref={inputRef}
              id="deck-recommendation-query"
              type="search"
              placeholder="어떤 덱으로 플레이하고 싶으신가요?"
              className="h-12 border-4"
              autoComplete="off"
              aria-label="덱 추천을 위한 플레이 스타일 검색어"
              required
            />
            <m.div
              className="w-full sm:w-auto"
              transition={{
                duration: 0.12,
                ease: 'easeOut',
              }}
              whileHover={{ x: 2, y: 1, scale: 0.98 }}
              whileTap={{ x: 2, y: 3, scale: 0.96 }}>
              <Button
                type="submit"
                className="h-12 w-full px-5 font-galmuri11 text-sm font-bold"
                aria-label="덱 추천 검색하기">
                <span>GURU!</span>
              </Button>
            </m.div>
          </form>

          {/** 질문 예시 칩 */}
          <div className="flex flex-wrap items-center justify-center gap-2">
            {EXAMPLE_QUESTIONS.map((question, index) => (
              <m.div
                key={question}
                initial={{ opacity: 0, y: 6, scale: 0.96 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                transition={{
                  delay: index * 0.06,
                  duration: 0.24,
                  ease: 'easeOut',
                }}
                whileHover={{
                  x: 2,
                  y: 1,
                  scale: 0.96,
                  transition: { delay: 0, duration: 0.12, ease: 'easeOut' },
                }}
                whileTap={{
                  x: 2,
                  y: 3,
                  scale: 0.96,
                  transition: { delay: 0, duration: 0.12, ease: 'easeOut' },
                }}>
                <Button
                  type="button"
                  variant="secondary"
                  size="lg"
                  onClick={() => handleExampleQuestionClick(question)}
                  className="text-center">
                  {question}
                </Button>
              </m.div>
            ))}
          </div>
        </div>
      </div>
    </main>
  );
}
