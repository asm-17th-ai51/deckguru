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
    <section className="relative z-10 mx-auto flex w-full max-w-3xl flex-col gap-6 pt-24 pb-10 sm:pt-20 lg:pt-16">
      <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
        <BrandMark />
        <HeroCopy />
      </div>

      <div className="mx-auto flex w-full max-w-3xl flex-col items-center justify-center gap-5 lg:mx-0">
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
    </section>
  );
}
