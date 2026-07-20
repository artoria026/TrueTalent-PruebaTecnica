import { useQuery, type UseQueryResult } from '@tanstack/react-query';
import { fetchRpaExtractions } from '@/features/rpa/api/rpaApi';
import type { RpaExtractionListResponse } from '@/features/rpa/types/rpa';

export const RPA_EXTRACTIONS_QUERY_KEY = 'rpa-extractions';

export function useRpaExtractions(
  page: number,
  limit: number,
): UseQueryResult<RpaExtractionListResponse> {
  return useQuery({
    queryKey: [RPA_EXTRACTIONS_QUERY_KEY, page, limit],
    queryFn: () => fetchRpaExtractions(page, limit),
  });
}
