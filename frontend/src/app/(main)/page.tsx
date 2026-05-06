'use client';

import { useDeckRecommendationForm } from '@/app/(main)/_hooks/use-deck-recommendation-form';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

export default function MainPage() {
  const { inputRef, handleSubmit } = useDeckRecommendationForm();

  return (
    <main className="pixel-background relative isolate flex min-h-svh w-full flex-col items-center justify-center overflow-hidden p-6 px-5 sm:px-4">
      <div className="relative z-10 flex w-full max-w-3xl flex-col items-center gap-8">
        {/* 서비스 이름 */}
        <div className="flex flex-col">
          <h1 className="text-xl">DECK</h1>
          <h1 className="text-xl">GURU</h1>
        </div>

        {/* 사용자 인풋 폼 */}
        <div className="flex w-full flex-col gap-6">
          {/* 보조 문구 */}
          <div className="flex flex-col text-center leading-relaxed">
            <p>메타를 읽고, 덱을 고르세요</p>
            <p className="text-sm text-muted-foreground">
              티어와 스타일에 맞는 <br className="block sm:hidden" />덱 운영
              가이드를 제공합니다
            </p>
          </div>

          {/* 인풋 폼, 제출 버튼 */}
          <div className="flex flex-col items-center justify-center gap-4">
            <form
              className="mx-auto flex w-full max-w-xl flex-col gap-2 sm:flex-row"
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
              <Button
                type="submit"
                className="h-12 w-full px-5 font-galmuri11 text-sm font-bold hover:scale-95 sm:w-auto"
                aria-label="덱 추천 검색하기">
                <span>GURU!</span>
              </Button>
            </form>
          </div>
        </div>
      </div>
    </main>
  );
}
