import type { RefObject, SubmitEvent } from 'react';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { m } from 'motion/react';

interface DeckRecommendationFormProps {
  inputRef: RefObject<HTMLInputElement | null>;
  onSubmit: (event: SubmitEvent<HTMLFormElement>) => void;
}

export function DeckRecommendationForm({
  inputRef,
  onSubmit,
}: DeckRecommendationFormProps) {
  return (
    <form
      className="mx-auto flex w-full max-w-2xl flex-col gap-2 sm:flex-row"
      onSubmit={onSubmit}>
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
  );
}
