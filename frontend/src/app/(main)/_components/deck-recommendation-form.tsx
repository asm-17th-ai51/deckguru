import type { RefObject, SubmitEvent } from 'react';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import type { PlayStyle, Tier } from '@/lib/schema';
import { m } from 'motion/react';

const TIER_OPTIONS: Array<{ value: Tier; label: string }> = [
  { value: 'IRON', label: '아이언' },
  { value: 'BRONZE', label: '브론즈' },
  { value: 'SILVER', label: '실버' },
  { value: 'GOLD', label: '골드' },
  { value: 'PLATINUM', label: '플래티넘' },
  { value: 'EMERALD', label: '에메랄드' },
  { value: 'DIAMOND', label: '다이아' },
  { value: 'MASTER+', label: '마스터+' },
];

const PLAY_STYLE_OPTIONS: Array<{ value: PlayStyle; label: string }> = [
  { value: 'flexible', label: '유동적인 운영형' },
  { value: 'stable_top4', label: '안정적인 순방형' },
  { value: 'high_risk_first', label: '고점 높은 1등형' },
  { value: 'easy_beginner', label: '쉬운 초보자형' },
];

const getTierLabel = (value: Tier | null) =>
  TIER_OPTIONS.find((option) => option.value === value)?.label ?? '티어 선택';

const getPlayStyleLabel = (value: PlayStyle | null) =>
  PLAY_STYLE_OPTIONS.find((option) => option.value === value)?.label ??
  '플레이 스타일 선택';

interface DeckRecommendationFormProps {
  inputRef: RefObject<HTMLInputElement | null>;
  query: string;
  tier: Tier | null;
  playStyle: PlayStyle | null;
  isSubmitDisabled: boolean;
  isSubmitting: boolean;
  submitErrorMessage: string | null;
  onQueryChange: (query: string) => void;
  onTierChange: (tier: Tier | null) => void;
  onPlayStyleChange: (playStyle: PlayStyle | null) => void;
  onSubmit: (event: SubmitEvent<HTMLFormElement>) => void;
}

export function DeckRecommendationForm({
  inputRef,
  query,
  tier,
  playStyle,
  isSubmitDisabled,
  isSubmitting,
  submitErrorMessage,
  onQueryChange,
  onTierChange,
  onPlayStyleChange,
  onSubmit,
}: DeckRecommendationFormProps) {
  return (
    <form
      className="mx-auto flex w-full max-w-2xl flex-col gap-2"
      onSubmit={onSubmit}>
      <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
        <Select<Tier>
          name="tier"
          value={tier}
          onValueChange={(value) => onTierChange(value)}>
          <SelectTrigger
            type="button"
            className="h-12 w-full border-4 text-sm"
            aria-label="티어 선택">
            <SelectValue
              className={tier === null ? 'text-muted-foreground' : ''}>
              {(value) => getTierLabel(value as Tier | null)}
            </SelectValue>
          </SelectTrigger>
          <SelectContent align="start">
            {TIER_OPTIONS.map((option) => (
              <SelectItem
                key={option.value}
                value={option.value}
                label={option.label}>
                {option.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select<PlayStyle>
          name="play_style"
          value={playStyle}
          onValueChange={(value) => onPlayStyleChange(value)}>
          <SelectTrigger
            type="button"
            className="h-12 w-full border-4 text-sm"
            aria-label="플레이 스타일 선택">
            <SelectValue
              className={playStyle === null ? 'text-muted-foreground' : ''}>
              {(value) => getPlayStyleLabel(value as PlayStyle | null)}
            </SelectValue>
          </SelectTrigger>
          <SelectContent align="start">
            {PLAY_STYLE_OPTIONS.map((option) => (
              <SelectItem
                key={option.value}
                value={option.value}
                label={option.label}>
                {option.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
        <Input
          ref={inputRef}
          id="deck-recommendation-query"
          type="search"
          placeholder="어떤 덱으로 플레이하고 싶으신가요?"
          className="h-12 border-4 bg-background/95"
          value={query}
          onChange={(event) => onQueryChange(event.target.value)}
          autoComplete="off"
          aria-label="덱 추천을 위한 플레이 스타일 검색어"
          aria-invalid={submitErrorMessage !== null}
          required
        />
        <m.div
          className="w-full sm:w-auto"
          transition={{
            duration: 0.12,
            ease: 'easeOut',
          }}
          whileHover={
            isSubmitDisabled ? undefined : { x: 2, y: 1, scale: 0.98 }
          }
          whileTap={isSubmitDisabled ? undefined : { x: 2, y: 3, scale: 0.96 }}>
          <Button
            type="submit"
            disabled={isSubmitDisabled}
            className="h-12 w-full px-5 font-galmuri11 text-sm font-bold"
            aria-busy={isSubmitting}
            aria-label="덱 추천 검색하기">
            <span>{isSubmitting ? 'LOADING...' : 'GURU!'}</span>
          </Button>
        </m.div>
      </div>
      {submitErrorMessage ? (
        <p
          role="alert"
          className="text-center text-xs font-bold text-destructive sm:text-left">
          {submitErrorMessage}
        </p>
      ) : null}
    </form>
  );
}
