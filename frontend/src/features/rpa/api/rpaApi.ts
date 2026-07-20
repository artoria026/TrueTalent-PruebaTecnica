import { apiClient } from '@/shared/lib/axios';
import type { RpaExtractionListResponse } from '@/features/rpa/types/rpa';

export async function fetchRpaExtractions(
  page: number,
  limit: number,
): Promise<RpaExtractionListResponse> {
  const response = await apiClient.get<RpaExtractionListResponse>('/rpa/extractions', {
    params: { page, limit },
  });
  return response.data;
}
