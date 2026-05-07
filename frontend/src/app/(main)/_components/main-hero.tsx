'use client';

import { BrandMark } from '@/app/(main)/_components/brand-mark';
import { DeckRecommendationForm } from '@/app/(main)/_components/deck-recommendation-form';
import { ExampleQuestionChips } from '@/app/(main)/_components/example-question-chips';
import { HeroCopy } from '@/app/(main)/_components/hero-copy';
import { EXAMPLE_QUESTIONS } from '@/app/(main)/_constants/example-questions';
import { useDeckRecommendationForm } from '@/app/(main)/_hooks/use-deck-recommendation-form';

export function MainHero() {
  const {
    inputRef,
    query,
    tier,
    playStyle,
    isSubmitDisabled,
    isSubmitting,
    submitErrorMessage,
    setQuery,
    setTier,
    setPlayStyle,
    handleExampleQuestionClick,
    handleSubmit,
  } = useDeckRecommendationForm();

  return (
    <div className="relative z-10 flex w-full max-w-3xl flex-col items-center gap-8">
      <BrandMark />

      <div className="flex w-full flex-col items-center justify-center gap-6">
        <HeroCopy />
        <DeckRecommendationForm
          inputRef={inputRef}
          query={query}
          tier={tier}
          playStyle={playStyle}
          isSubmitDisabled={isSubmitDisabled}
          isSubmitting={isSubmitting}
          submitErrorMessage={submitErrorMessage}
          onQueryChange={setQuery}
          onTierChange={setTier}
          onPlayStyleChange={setPlayStyle}
          onSubmit={handleSubmit}
        />
        <ExampleQuestionChips
          questions={EXAMPLE_QUESTIONS}
          onQuestionClick={handleExampleQuestionClick}
        />
      </div>
    </div>
  );
}
