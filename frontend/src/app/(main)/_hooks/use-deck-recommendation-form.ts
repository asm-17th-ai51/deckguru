'use client';

import { type SubmitEvent, useRef } from 'react';

export function useDeckRecommendationForm() {
  const inputRef = useRef<HTMLInputElement>(null);

  const handleExampleQuestionClick = (question: string) => {
    if (!inputRef.current) {
      return;
    }

    inputRef.current.value = question;
    inputRef.current.focus();
  };

  const handleSubmit = (e: SubmitEvent<HTMLFormElement>) => {
    e.preventDefault();

    const query = inputRef.current?.value.trim() ?? '';

    console.log('폼 입력 쿼리: ', query);
  };

  return {
    inputRef,
    handleExampleQuestionClick,
    handleSubmit,
  };
}
