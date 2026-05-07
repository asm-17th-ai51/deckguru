import { RecommendationResultView } from '@/app/recommendations/[requestId]/_components/recommendation-result-view';

interface RecommendationResultPageProps {
  params: Promise<{
    requestId: string;
  }>;
}

export default async function RecommendationResultPage({
  params,
}: RecommendationResultPageProps) {
  const { requestId } = await params;

  return <RecommendationResultView requestId={requestId} />;
}
