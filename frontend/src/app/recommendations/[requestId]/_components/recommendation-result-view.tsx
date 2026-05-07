'use client';

import type { ComponentType, ReactNode } from 'react';

import { useRecommendationResultQuery } from '@/api/post-recommend/query';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { APP_PATH } from '@/constants/app-path';
import type {
  Confidence,
  DeckRecommendation,
  Difficulty,
  Intent,
  Phase,
  RecommendationResponse,
  Source,
} from '@/lib/schema';
import {
  ArrowLeftIcon,
  ArrowSquareOutIcon,
  FlagCheckeredIcon,
  GameControllerIcon,
  GaugeIcon,
  LightningIcon,
  ListChecksIcon,
  ShieldCheckIcon,
  SparkleIcon,
  TargetIcon,
  TreeStructureIcon,
  TrendUpIcon,
  WarningIcon,
} from '@phosphor-icons/react';
import { m } from 'motion/react';
import Link from 'next/link';

interface RecommendationResultViewProps {
  requestId: string;
}

type IconComponent = ComponentType<{
  'aria-hidden'?: boolean;
  className?: string;
  weight?: 'bold' | 'duotone' | 'fill' | 'regular';
}>;

const INTENT_LABEL: Record<Intent, string> = {
  recommend_deck: '덱 추천',
  deck_playstyle: '운영법',
  item_pivot: '아이템 피벗',
  patch_summary: '패치 요약',
  other: '기타',
};

const CONFIDENCE_CONFIG: Record<
  Confidence,
  { className: string; label: string }
> = {
  high: {
    label: '높음',
    className: 'border-emerald-300/70 bg-emerald-300/15 text-emerald-100',
  },
  medium: {
    label: '보통',
    className: 'border-primary/70 bg-primary/15 text-primary',
  },
  low: {
    label: '낮음',
    className: 'border-rose-300/70 bg-rose-300/15 text-rose-100',
  },
};

const DIFFICULTY_CONFIG: Record<
  Difficulty,
  { blocks: number; className: string; label: string; summary: string }
> = {
  easy: {
    label: '쉬움',
    blocks: 1,
    summary: '순서대로 따라가기 좋음',
    className: 'border-emerald-300/70 bg-emerald-300/15 text-emerald-100',
  },
  medium: {
    label: '보통',
    blocks: 2,
    summary: '중반 판단이 중요함',
    className: 'border-primary/70 bg-primary/15 text-primary',
  },
  hard: {
    label: '어려움',
    blocks: 3,
    summary: '경제와 피벗 숙련도 필요',
    className: 'border-rose-300/70 bg-rose-300/15 text-rose-100',
  },
};

const PHASE_CONFIG: Record<
  Phase,
  { label: string; icon: IconComponent; accentClassName: string }
> = {
  early: {
    label: '초반',
    icon: LightningIcon,
    accentClassName: 'text-emerald-200',
  },
  mid: {
    label: '중반',
    icon: TargetIcon,
    accentClassName: 'text-primary',
  },
  late: {
    label: '후반',
    icon: FlagCheckeredIcon,
    accentClassName: 'text-rose-200',
  },
};

const SOURCE_KIND_LABEL: Record<NonNullable<Source['source_kind']>, string> = {
  patch_note_official: '공식 패치',
  meta_site: '메타 사이트',
  community_post: '커뮤니티',
  youtube: '영상',
};

const PANEL_CLASS_NAME =
  'border-4 border-border bg-background/95 shadow-[8px_8px_0_0_rgb(0_0_0_/_0.45)] backdrop-blur';

const formatDateTime = (value: string | null | undefined) => {
  if (!value) {
    return '날짜 없음';
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat('ko-KR', {
    timeZone: 'Asia/Seoul',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
};

const getSourceDomain = (url: string) => {
  try {
    return new URL(url).hostname.replace(/^www\./, '');
  } catch {
    return url;
  }
};

const getSourceKindLabel = (kind: Source['source_kind']) => {
  if (!kind) {
    return '출처';
  }

  return SOURCE_KIND_LABEL[kind];
};

export function RecommendationResultView({
  requestId,
}: RecommendationResultViewProps) {
  const { data: recommendation } = useRecommendationResultQuery(requestId);

  if (!recommendation) {
    return <EmptyResultState />;
  }

  return (
    <main className="pixel-background relative isolate min-h-dvh w-full overflow-x-hidden px-4 py-6 text-foreground sm:px-6 lg:px-8">
      <section className="relative z-10 mx-auto flex w-full max-w-6xl flex-col gap-6 pb-12">
        <ResultHeader recommendation={recommendation} />
        <MetaBrief recommendation={recommendation} />

        <section
          className="grid gap-5"
          aria-labelledby="recommendation-decks-title">
          <div className="flex flex-col gap-2">
            <div className="flex flex-col gap-1">
              <p className="font-galmuri11 text-xs font-bold text-primary">
                DECK ROUTES
              </p>
              <h2
                id="recommendation-decks-title"
                className="font-galmuri11 text-lg font-bold sm:text-xl">
                추천 덱 경로
              </h2>
            </div>
          </div>

          {recommendation.decks.length > 0 ? (
            recommendation.decks.map((deck, index) => (
              <DeckCard
                deck={deck}
                index={index}
                key={`${deck.name}-${index}`}
              />
            ))
          ) : (
            <NoDeckPanel />
          )}
        </section>

        <WarningsPanel warnings={recommendation.warnings} />
        <SourcesPanel sources={recommendation.sources} />
        <DebugPanel debug={recommendation.debug} />
      </section>
    </main>
  );
}

function EmptyResultState() {
  return (
    <main className="pixel-background relative isolate flex min-h-dvh w-full flex-col items-center justify-center overflow-hidden px-5 py-10 text-center">
      <section className="relative z-10 flex w-full max-w-xl flex-col items-center gap-6">
        <div className="grid size-14 place-items-center border-4 border-primary bg-background/95 text-primary shadow-[6px_6px_0_0_rgb(0_0_0/0.45)]">
          <WarningIcon aria-hidden className="size-7" weight="bold" />
        </div>
        <div className="flex flex-col gap-3">
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
        </div>
        <ActionButton href={APP_PATH.MAIN} label="메인으로 돌아가기" />
      </section>
    </main>
  );
}

function ResultHeader({
  recommendation,
}: {
  recommendation: RecommendationResponse;
}) {
  return (
    <header className="flex flex-col gap-5 pt-2 lg:flex-row lg:items-end lg:justify-between">
      <div className="flex flex-col gap-3">
        <Badge
          variant="outline"
          className="h-auto max-w-full border-2 border-primary/70 text-xs text-primary">
          REQUEST {recommendation.request_id}
        </Badge>
        <div className="flex flex-col gap-2">
          <h1 className="font-galmuri11 text-2xl font-bold text-foreground sm:text-3xl">
            추천 결과
          </h1>
          <p className="text-sm leading-6 text-muted-foreground sm:text-base">
            메타 요약, 덱별 운영 순서, 좋은 조건과 피해야 할 조건을 한 화면에서
            바로 비교할 수 있게 정리했습니다.
          </p>
        </div>
      </div>

      <ActionButton href={APP_PATH.MAIN} label="다시 추천받기" />
    </header>
  );
}

function MetaBrief({
  recommendation,
}: {
  recommendation: RecommendationResponse;
}) {
  const confidence = CONFIDENCE_CONFIG[recommendation.confidence];

  return (
    <section
      className={`${PANEL_CLASS_NAME} overflow-hidden`}
      aria-labelledby="meta-brief-title">
      <div className="grid gap-0 lg:grid-cols-[minmax(0,1.35fr)_minmax(17rem,0.65fr)]">
        <div className="flex flex-col gap-4 p-5 sm:p-6">
          <SectionEyebrow icon={SparkleIcon}>META BRIEF</SectionEyebrow>
          <div className="flex flex-col gap-3">
            <h2
              id="meta-brief-title"
              className="font-galmuri11 text-lg font-bold sm:text-xl">
              이번 판의 큰 방향
            </h2>
            <p className="text-sm leading-7 text-foreground/90 sm:text-base">
              {recommendation.meta_summary}
            </p>
          </div>
        </div>

        <dl className="grid grid-cols-2 gap-x-5 gap-y-4 border-t-4 border-border bg-muted/20 p-5 sm:p-6 lg:border-t-0 lg:border-l-4">
          <ResultMetric
            icon={GameControllerIcon}
            label="패치"
            value={recommendation.patch_version}
          />
          <ResultMetric
            icon={GaugeIcon}
            label="신뢰도"
            value={confidence.label}
            valueClassName={confidence.className}
          />
          <ResultMetric
            icon={TreeStructureIcon}
            label="요청 유형"
            value={INTENT_LABEL[recommendation.intent]}
          />
          <ResultMetric
            icon={ListChecksIcon}
            label="추천 수"
            value={`${recommendation.decks.length}개`}
          />
          <div className="col-span-2 border-t-2 border-border/70 pt-4">
            <dt className="mb-1 font-galmuri11 text-[10px] font-bold text-muted-foreground">
              생성 시각
            </dt>
            <dd className="text-sm leading-6 text-foreground">
              {formatDateTime(recommendation.generated_at)}
            </dd>
          </div>
        </dl>
      </div>
    </section>
  );
}

function ResultMetric({
  icon: Icon,
  label,
  value,
  valueClassName,
}: {
  icon: IconComponent;
  label: string;
  value: string;
  valueClassName?: string;
}) {
  return (
    <div className="flex min-w-0 flex-col gap-2">
      <dt className="flex items-center gap-1.5 font-galmuri11 text-[10px] font-bold text-muted-foreground">
        <Icon aria-hidden className="size-3.5 text-primary" weight="bold" />
        {label}
      </dt>
      <dd
        className={
          valueClassName
            ? `w-fit border-2 px-2 py-1 font-galmuri11 text-xs font-bold ${valueClassName}`
            : 'truncate font-galmuri11 text-sm font-bold text-foreground'
        }>
        {value}
      </dd>
    </div>
  );
}

function DeckCard({
  deck,
  index,
}: {
  deck: DeckRecommendation;
  index: number;
}) {
  const difficulty = DIFFICULTY_CONFIG[deck.difficulty];

  return (
    <article className={`${PANEL_CLASS_NAME} overflow-hidden`}>
      <div className="flex flex-col gap-4 border-b-4 border-border bg-muted/20 p-5 sm:p-6 lg:flex-row lg:items-start lg:justify-between">
        <div className="flex min-w-0 gap-4">
          <div className="grid size-12 shrink-0 place-items-center border-4 border-primary bg-primary font-galmuri11 text-sm font-bold text-primary-foreground shadow-[4px_4px_0_0_rgb(0_0_0/0.45)]">
            {String(index + 1).padStart(2, '0')}
          </div>
          <div className="flex min-w-0 flex-col gap-2">
            <div className="flex flex-wrap items-center gap-2">
              <Badge
                variant="outline"
                className={`h-auto border-2 px-2 py-1 font-galmuri11 text-[10px] font-bold ${difficulty.className}`}>
                {difficulty.label}
              </Badge>
              <span className="font-galmuri11 text-[10px] font-bold text-muted-foreground">
                {difficulty.summary}
              </span>
            </div>
            <h3 className="font-galmuri11 text-xl font-bold break-keep text-foreground sm:text-2xl">
              {deck.name}
            </h3>
            <p className="max-w-3xl text-sm leading-6 text-muted-foreground">
              {deck.rationale}
            </p>
          </div>
        </div>

        <DifficultyMeter difficulty={deck.difficulty} />
      </div>

      <div className="grid gap-0 lg:grid-cols-[minmax(0,1fr)_19rem]">
        <div className="flex flex-col divide-y-4 divide-border/70">
          <DeckInfoSection icon={ShieldCheckIcon} title="핵심 유닛">
            <ChipList items={deck.core_units} />
          </DeckInfoSection>

          <DeckInfoSection icon={SparkleIcon} title="주요 아이템">
            <ChipList items={deck.key_items} tone="primary" />
          </DeckInfoSection>

          <DeckInfoSection icon={TrendUpIcon} title="증강체 방향">
            <p className="text-sm leading-6 text-foreground/90">
              {deck.augment_direction}
            </p>
          </DeckInfoSection>

          <DeckInfoSection icon={ListChecksIcon} title="운영 타임라인">
            <div className="grid gap-3 md:grid-cols-3">
              {deck.playbook.map((step) => (
                <PhaseStep
                  instruction={step.instruction}
                  key={`${deck.name}-${step.phase}`}
                  phase={step.phase}
                />
              ))}
            </div>
          </DeckInfoSection>
        </div>

        <aside className="flex flex-col gap-5 border-t-4 border-border bg-background/55 p-5 sm:p-6 lg:border-t-0 lg:border-l-4">
          <ConditionList
            icon={TargetIcon}
            items={deck.good_conditions}
            title="좋은 조건"
          />
          <ConditionList
            icon={WarningIcon}
            items={deck.avoid_conditions}
            title="주의 조건"
          />
          <div className="border-t-2 border-border/70 pt-5">
            <SectionEyebrow icon={FlagCheckeredIcon}>FALLBACK</SectionEyebrow>
            <p className="mt-3 text-sm leading-6 text-foreground/90">
              {deck.fallback_plan}
            </p>
          </div>
        </aside>
      </div>
    </article>
  );
}

function DifficultyMeter({ difficulty }: { difficulty: Difficulty }) {
  const config = DIFFICULTY_CONFIG[difficulty];

  return (
    <div
      className="flex shrink-0 items-center gap-2"
      aria-label={`운영 난이도 ${config.label}`}>
      <span className="font-galmuri11 text-[10px] font-bold text-muted-foreground">
        PILOT
      </span>
      <div className="flex gap-1" aria-hidden="true">
        {Array.from({ length: 3 }).map((_, index) => (
          <span
            className={`block h-4 w-5 border-2 ${
              index < config.blocks
                ? 'border-primary bg-primary'
                : 'border-border bg-background/70'
            }`}
            key={index}
          />
        ))}
      </div>
    </div>
  );
}

function DeckInfoSection({
  children,
  icon,
  title,
}: {
  children: ReactNode;
  icon: IconComponent;
  title: string;
}) {
  return (
    <section className="flex flex-col gap-3 p-5 sm:p-6">
      <SectionEyebrow icon={icon}>{title}</SectionEyebrow>
      {children}
    </section>
  );
}

function ChipList({
  items,
  tone = 'default',
}: {
  items: string[];
  tone?: 'default' | 'primary';
}) {
  return (
    <ul className="flex flex-wrap gap-2">
      {items.map((item) => (
        <li key={item}>
          <Badge
            variant="outline"
            className={`h-auto max-w-full border-2 px-2.5 py-1.5 text-xs leading-5 break-keep whitespace-normal ${
              tone === 'primary'
                ? 'border-primary/70 bg-primary/15 text-primary'
                : 'border-border bg-muted/40 text-foreground'
            }`}>
            {item}
          </Badge>
        </li>
      ))}
    </ul>
  );
}

function PhaseStep({
  instruction,
  phase,
}: {
  instruction: string;
  phase: Phase;
}) {
  const config = PHASE_CONFIG[phase];
  const Icon = config.icon;

  return (
    <div className="min-w-0 bg-muted/25 px-3 py-2.5">
      <div className="mb-2 flex items-center gap-1.5 font-galmuri11 text-[10px] font-bold">
        <Icon
          aria-hidden
          className={`size-3.5 ${config.accentClassName}`}
          weight="bold"
        />
        <span className={config.accentClassName}>{config.label}</span>
      </div>
      <p className="text-sm leading-6 text-foreground/90">{instruction}</p>
    </div>
  );
}

function ConditionList({
  icon: Icon,
  items,
  title,
}: {
  icon: IconComponent;
  items: string[];
  title: string;
}) {
  return (
    <section className="flex flex-col gap-3">
      <SectionEyebrow icon={Icon}>{title}</SectionEyebrow>
      {items.length > 0 ? (
        <ul className="flex flex-col gap-2">
          {items.map((item) => (
            <li
              className="flex gap-2 text-sm leading-6 text-foreground/90"
              key={item}>
              <span
                className="mt-2 block size-1.5 shrink-0 bg-primary"
                aria-hidden="true"
              />
              <span>{item}</span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-sm leading-6 text-muted-foreground">
          별도 주의 조건이 없습니다.
        </p>
      )}
    </section>
  );
}

function NoDeckPanel() {
  return (
    <section className={`${PANEL_CLASS_NAME} p-6 text-center`}>
      <SectionEyebrow icon={WarningIcon}>NO DECK DATA</SectionEyebrow>
      <p className="mt-3 text-sm leading-6 text-muted-foreground">
        이번 응답에는 추천 덱이 포함되지 않았습니다. 메타 요약과 출처를 먼저
        확인해 주세요.
      </p>
    </section>
  );
}

function WarningsPanel({ warnings }: { warnings: string[] }) {
  if (warnings.length === 0) {
    return null;
  }

  return (
    <section
      className="border-4 border-destructive/70 bg-destructive/10 p-5 shadow-[8px_8px_0_0_rgb(0_0_0/0.45)]"
      aria-labelledby="recommendation-warnings-title">
      <SectionEyebrow icon={WarningIcon}>WARNING</SectionEyebrow>
      <h2
        id="recommendation-warnings-title"
        className="mt-3 font-galmuri11 text-base font-bold text-foreground">
        확인이 필요한 안내
      </h2>
      <ul className="mt-3 flex flex-col gap-2">
        {warnings.map((warning) => (
          <li className="text-sm leading-6 text-foreground/90" key={warning}>
            {warning}
          </li>
        ))}
      </ul>
    </section>
  );
}

function SourcesPanel({ sources }: { sources: Source[] }) {
  if (sources.length === 0) {
    return null;
  }

  return (
    <section
      className="grid gap-5"
      aria-labelledby="recommendation-sources-title">
      <div className="flex flex-col gap-2">
        <div className="flex flex-col gap-1">
          <p className="font-galmuri11 text-xs font-bold text-primary">
            EVIDENCE
          </p>
          <h2
            id="recommendation-decks-title"
            className="font-galmuri11 text-lg font-bold sm:text-xl">
            추천 근거
          </h2>
        </div>
      </div>

      <div className="grid gap-3 md:grid-cols-2">
        {sources.map((source) => (
          <SourceCard key={`${source.title}-${source.url}`} source={source} />
        ))}
      </div>
    </section>
  );
}

function SourceCard({ source }: { source: Source }) {
  return (
    <article className={`${PANEL_CLASS_NAME} flex min-w-0 flex-col gap-4 p-5`}>
      <div className="flex flex-wrap items-center gap-2">
        <Badge
          variant="outline"
          className="h-auto border-2 border-primary/70 bg-primary/15 px-2 py-1 font-galmuri11 text-[10px] font-bold text-primary">
          {getSourceKindLabel(source.source_kind)}
        </Badge>
        <span className="text-xs text-muted-foreground">
          {formatDateTime(source.published_at)}
        </span>
      </div>

      <div className="flex flex-col gap-2">
        <h3 className="font-galmuri11 text-base leading-7 font-bold break-keep text-foreground">
          {source.title}
        </h3>
        <p className="text-sm leading-6 text-muted-foreground">
          {source.snippet}
        </p>
      </div>

      <Button
        type="button"
        nativeButton={false}
        variant="outline"
        className="mt-auto h-11 w-full justify-between border-2 bg-background/80 px-3 font-galmuri11 text-xs font-bold"
        aria-label={`${source.title} 출처 열기`}
        render={
          <a href={source.url} target="_blank" rel="noreferrer noopener" />
        }>
        <span className="truncate">{getSourceDomain(source.url)}</span>
        <ArrowSquareOutIcon aria-hidden className="size-4" weight="bold" />
      </Button>
    </article>
  );
}

function DebugPanel({ debug }: { debug: RecommendationResponse['debug'] }) {
  if (!debug) {
    return null;
  }

  return (
    <details className={`${PANEL_CLASS_NAME} p-5`}>
      <summary className="cursor-pointer font-galmuri11 text-sm font-bold text-primary">
        진단 정보
      </summary>
      <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-2 lg:grid-cols-4">
        <DebugMetric label="React 단계" value={`${debug.react_steps}`} />
        <DebugMetric
          label="RAG 평균 점수"
          value={debug.rag_avg_score.toFixed(2)}
        />
        <DebugMetric
          label="Tier 2 검색"
          value={debug.tier2_triggered ? '사용' : '미사용'}
        />
        <DebugMetric
          label="노드 수"
          value={`${Object.keys(debug.node_latencies_ms).length}`}
        />
      </dl>
    </details>
  );
}

function DebugMetric({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="font-galmuri11 text-[10px] font-bold text-muted-foreground">
        {label}
      </dt>
      <dd className="mt-1 text-foreground">{value}</dd>
    </div>
  );
}

function SectionEyebrow({
  children,
  icon: Icon,
}: {
  children: ReactNode;
  icon: IconComponent;
}) {
  return (
    <p className="flex items-center gap-1.5 font-galmuri11 text-[10px] font-bold text-primary">
      <Icon aria-hidden className="size-3.5" weight="bold" />
      <span>{children}</span>
    </p>
  );
}

function ActionButton({ href, label }: { href: string; label: string }) {
  return (
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
        className="h-12 w-full gap-2 px-5 font-galmuri11 text-sm font-bold sm:w-auto"
        aria-label={label}
        render={<Link href={href} />}>
        <ArrowLeftIcon aria-hidden className="size-4" weight="bold" />
        {label}
      </Button>
    </m.div>
  );
}
