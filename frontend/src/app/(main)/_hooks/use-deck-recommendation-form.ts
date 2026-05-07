import { type SubmitEvent, useRef, useState } from 'react';

import type { PlayStyle, Tier } from '@/lib/schema';

export function useDeckRecommendationForm() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [query, setQuery] = useState('');
  const [tier, setTier] = useState<Tier | null>(null);
  const [playStyle, setPlayStyle] = useState<PlayStyle | null>(null);
  const isSubmitDisabled =
    query.trim().length === 0 || tier === null || playStyle === null;

  const handleExampleQuestionClick = (question: string) => {
    setQuery(question);

    if (!inputRef.current) {
      return;
    }

    inputRef.current.focus();
  };

  const handleSubmit = (e: SubmitEvent<HTMLFormElement>) => {
    e.preventDefault();

    const trimmedQuery = query.trim();

    if (!trimmedQuery || tier === null || playStyle === null) {
      return;
    }

    console.log('폼 입력 값: ', {
      question: trimmedQuery,
      tier,
      play_style: playStyle,
    });
  };

  return {
    inputRef,
    query,
    tier,
    playStyle,
    isSubmitDisabled,
    setQuery,
    setTier,
    setPlayStyle,
    handleExampleQuestionClick,
    handleSubmit,
  };
}
